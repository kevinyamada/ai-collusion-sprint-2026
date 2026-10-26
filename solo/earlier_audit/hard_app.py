import hashlib,io,json,re,time,zipfile
from pathlib import Path
import modal
app=modal.App('kevin-injection-audit-b200')
volume=modal.Volume.from_name('kevin-collusion-injection-audit',create_if_missing=True)
cache=modal.Volume.from_name('kevin-collusion-model-cache',create_if_missing=True)
base=(modal.Image.debian_slim(python_version='3.11').pip_install('numpy==2.2.5','pandas==2.2.3','matplotlib==3.10.1')
)
gpu_image=(base.pip_install('torch==2.7.0',index_url='https://download.pytorch.org/whl/cu128')
           .pip_install('transformers==4.51.3','accelerate==1.6.0','sentencepiece==0.2.0')
           .env({'HF_HOME':'/models','TOKENIZERS_PARALLELISM':'false'})
           .add_local_python_source('hard_benchmark','hard_analysis','fast_batch_utils','frozen_hard_base'))
base=base.add_local_python_source('hard_benchmark','hard_analysis','fast_batch_utils','frozen_hard_base')
MODELS={
'qwen7':('Qwen/Qwen2.5-7B-Instruct','a09a35458c702b33eeacc393d103063234e8bc28'),
'qwen32':('Qwen/Qwen2.5-32B-Instruct','5ede1c97bbab6ce5cda5812749b4c0bdf79b18dd'),
}
BATCH=16
HARD_SECONDS=3500
SOFT_SECONDS=3200
RATE_ESTIMATE=9.0 # B200 + requested CPU/RAM, margin; not an invoice cap

@app.function(image=gpu_image,gpu='B200',cpu=8,memory=65536,volumes={'/results':volume,'/models':cache},timeout=HARD_SECONDS,max_containers=2,retries=0,scaledown_window=2)
def collect(config,key):
    import torch,transformers
    from transformers import AutoTokenizer,AutoModelForCausalLM
    from hard_benchmark import jobs,prompt,parse,verify
    from fast_batch_utils import trim_generated
    started=time.monotonic();volume.reload();root=Path('/results')/config['run_id']/key;root.mkdir(parents=True,exist_ok=True)
    cp=root/'config.json'
    if cp.exists() and json.loads(cp.read_text())!=config:raise ValueError('Frozen configuration changed')
    cp.write_text(json.dumps(config,indent=2))
    saved=[]
    for p in sorted(root.glob('batch_*.jsonl')):saved += [json.loads(s) for s in p.read_text().splitlines() if s]
    done={(r['case_id'],r['format'],r['method']) for r in saved}
    pending=[j for j in jobs() if (j[0]['id'],j[1],j[2]) not in done]
    if not pending:return dict(model=key,remaining=0,complete=True)
    # One paid attempt per model/run. A failed attempt cannot silently spend a second reservation.
    reservation=root/'reservation.json'
    if reservation.exists():raise RuntimeError('A previous paid attempt is incomplete. Export checkpoints with --download-only; do not create another run blindly.')
    reservation.write_text(json.dumps(dict(max_seconds=HARD_SECONDS,reserved_estimate=HARD_SECONDS/3600*RATE_ESTIMATE,started=time.time())))
    volume.commit()
    gpu=torch.cuda.get_device_name(0)
    torch.ones((32,32),device='cuda',dtype=torch.bfloat16).matmul(torch.ones((32,32),device='cuda',dtype=torch.bfloat16));torch.cuda.synchronize()
    print(f'{key}: GPU={gpu}; torch={torch.__version__}; CUDA={torch.version.cuda}; {len(pending)} pending',flush=True)
    model_name,revision=MODELS[key]
    tokenizer=AutoTokenizer.from_pretrained(model_name,revision=revision,padding_side='left')
    if tokenizer.pad_token_id is None:tokenizer.pad_token=tokenizer.eos_token
    model=AutoModelForCausalLM.from_pretrained(model_name,revision=revision,torch_dtype=torch.bfloat16,device_map={'':0},attn_implementation='sdpa').eval()
    cache.commit()
    eos=model.generation_config.eos_token_id or tokenizer.eos_token_id
    eos_ids=[eos] if isinstance(eos,int) else list(eos)
    runtime=dict(gpu=gpu,torch=torch.__version__,cuda=torch.version.cuda,transformers=transformers.__version__,model=model_name,revision=revision,batch_size=BATCH,dtype='bfloat16',max_new_tokens=192)
    (root/'runtime.json').write_text(json.dumps(runtime,indent=2));volume.commit()
    # Seeded shuffle avoids placing every hard condition at the end of a time-limited attempt.
    import random
    random.Random(91203).shuffle(pending)
    completed=0
    for start in range(0,len(pending),BATCH):
        if time.monotonic()-started>SOFT_SECONDS:break
        batch=pending[start:start+BATCH];contents=[prompt(c,f,m) for c,f,m in batch]
        formatted=[tokenizer.apply_chat_template([{'role':'user','content':s}],tokenize=False,add_generation_prompt=True) for s in contents]
        inp=tokenizer(formatted,return_tensors='pt',padding=True,truncation=False).to('cuda')
        if inp.input_ids.shape[1]>12000:raise ValueError('Unexpected prompt length')
        t=time.monotonic()
        with torch.inference_mode():output=model.generate(**inp,max_new_tokens=192,do_sample=False,temperature=None,top_p=None,top_k=None,pad_token_id=tokenizer.pad_token_id)
        elapsed=time.monotonic()-t;records=[]
        for i,(c,fmt,method) in enumerate(batch):
            tokens=trim_generated(output[i,inp.input_ids.shape[1]:].tolist(),eos_ids)
            raw=tokenizer.decode(tokens,skip_special_tokens=True).strip();err=None
            try:
                parsed=parse(raw,method);prediction={**parsed,**verify(parsed['agreed_price'],c['rounds'])} if method=='hybrid' else parsed
            except (ValueError,TypeError) as exc:prediction=None;err=str(exc)
            records.append(dict(model=key,case_id=c['id'],format=fmt,method=method,label=c['label'],family=c['family'],category=c['category'],condition=c['condition'],world=c['world'],prompt=contents[i],raw=raw,prediction=prediction,parse_error=err,generated_tokens=len(tokens),hit_token_limit=len(tokens)>=192 and tokens[-1] not in eos_ids,batch_seconds=elapsed,revision=revision))
        # One durable checkpoint per batch; commit before progress is reported.
        target=root/f'batch_{start//BATCH:06}.jsonl'
        if target.exists():raise ValueError('Checkpoint collision')
        target.write_text('\n'.join(json.dumps(r) for r in records)+'\n');volume.commit();completed+=len(records)
        if completed%128==0 or completed==len(pending):print(f'{key}: {completed}/{len(pending)} saved',flush=True)
    status=dict(model=key,remaining=len(pending)-completed,complete=completed==len(pending),seconds=time.monotonic()-started)
    status['compute_estimate']=status['seconds']/3600*RATE_ESTIMATE
    (root/'status.json').write_text(json.dumps(status,indent=2));volume.commit();return status

@app.function(image=base,cpu=4,memory=8192,volumes={'/results':volume},timeout=1800,retries=0)
def export(config):
    import tempfile
    from concurrent.futures import ThreadPoolExecutor
    from hard_benchmark import jobs,cases
    from hard_analysis import analyze
    volume.reload();source=Path('/results')/config['run_id']
    if not source.exists():raise ValueError('No saved run')
    print('Copying saved checkpoints to CPU disk...',flush=True)
    files=[p for p in source.rglob('*') if p.is_file()]
    with tempfile.TemporaryDirectory() as td:
        local=Path(td)
        def copy(p):
            q=local/p.relative_to(source);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
        with ThreadPoolExecutor(max_workers=16) as pool:list(pool.map(copy,files))
        records=[]
        for cp in local.glob('*/config.json'):
            if json.loads(cp.read_text())!=config:raise ValueError('Saved configuration differs from current source; restore the original files before export.')
        for p in local.rglob('batch_*.jsonl'):records += [json.loads(s) for s in p.read_text().splitlines() if s]
        (local/'config.json').write_text(json.dumps(config,indent=2))
        (local/'cases_with_labels.json').write_text(json.dumps(cases(),indent=2))
        expected={(m,c['id'],f,t) for m in MODELS for c,f,t in jobs()}
        print(f'Analyzing {len(records)}/{len(expected)} raw outputs...',flush=True)
        status=analyze(local,records,expected)
        target=source/'analysis';target.mkdir(exist_ok=True)
        for p in (local/'analysis').iterdir():(target/p.name).write_bytes(p.read_bytes())
        volume.commit();print('Packing results ZIP...',flush=True)
        b=io.BytesIO()
        with zipfile.ZipFile(b,'w',zipfile.ZIP_DEFLATED) as z:
            for p in local.rglob('*'):
                if p.is_file():z.write(p,p.relative_to(local))
        return b.getvalue(),status

@app.local_entrypoint()
def main(run_id:str='injection-audit-v1',download_only:bool=False):
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,60}',run_id):raise ValueError('Invalid run id')
    names=['hard_app.py','hard_benchmark.py','hard_analysis.py','fast_batch_utils.py','frozen_hard_base.py']
    src=Path(__file__).parent
    digest=hashlib.sha256(b''.join((src/n).read_bytes() for n in names)).hexdigest()
    config=dict(run_id=run_id,protocol='crossed-static-injection-audit-v1',models=list(MODELS),source_sha256=digest,gpu='B200',batch_size=BATCH,rate_estimate=RATE_ESTIMATE,max_gpu_estimate=17.5)
    errors=[]
    if not download_only:
        handles=[]
        try:
            for key in MODELS:handles.append((key,collect.spawn(config,key)))
            for key,h in handles:
                try:print(h.get(),flush=True)
                except Exception as exc:errors.append(f'{key}: {exc}');print(errors[-1],flush=True)
        except BaseException:
            for _,h in handles:h.cancel()
            raise
    blob,status=export.remote(config)
    p=Path(f'{run_id}-results-{time.time_ns()}.zip');p.write_bytes(blob)
    print(json.dumps(status,indent=2));print('RESULTS SAVED:',p.resolve())
    if errors or not status['complete']:raise RuntimeError('Partial run exported; send ZIP and terminal output. No automatic paid retries.')
