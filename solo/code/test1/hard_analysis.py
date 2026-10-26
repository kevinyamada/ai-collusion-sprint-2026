import csv,json
from pathlib import Path

def write_csv(p,rows):
    if not rows:return
    with p.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def analyze(root,records,expected):
    import numpy as np
    import pandas as pd
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from hard_benchmark import cases,prompt,parse,finish,FORMATS
    out=Path(root)/'analysis';out.mkdir(exist_ok=True)
    cs={c['id']:c for c in cases()};keys=[(r['model'],r['case_id'],r['format'],r['method']) for r in records];actual=set(keys)
    status=dict(expected_predictions=len(expected),saved_predictions=len(records),missing=len(expected-actual),unexpected=len(actual-expected),duplicates=len(keys)-len(actual),invalid_outputs=sum(r['prediction'] is None for r in records),truncated=sum(r['hit_token_limit'] for r in records))
    status['complete']=actual==expected and len(keys)==len(actual)
    rows=[]
    for r in records:
        c=cs[r['case_id']];assert r['prompt']==prompt(c,r['format'],r['method']);assert r['label']==c['label']
        try:p=finish(parse(r['raw'],r['method']),r['method'],c['rounds'])
        except (ValueError,TypeError):p=None
        assert p==r['prediction']
        price_ok=None if r['method']=='baseline' else p is not None and p['agreed_price']==c['agreed_price']
        action_ok=None
        if r['method']=='end_to_end':action_ok=p is not None and sorted(p['actions'])==[[x['round'],x['A'],x['B']] for x in c['rounds']]
        correct=p is not None and p['flag']==c['label']
        rows.append(dict(model=r['model'],method=r['method'],format=r['format'],case_id=c['id'],family=c['family'],category=c['category'],world=c['world'],condition=c['condition'],label=c['label'],valid=p is not None,flag=p['flag'] if p else None,correct=correct,price_correct=price_ok,actions_exact=action_ok,correct_flag_wrong_actions=bool(correct and action_ok is False),raw=r['raw']))
    (out/'quality_checks.json').write_text(json.dumps(status,indent=2));write_csv(out/'predictions.csv',rows)
    if not rows:return status
    df=pd.DataFrame(rows);expanded=[]
    for r in rows:
        for f in (FORMATS if r['method']=='hybrid' else (r['format'],)):expanded.append({**r,'format':f})
    d=pd.DataFrame(expanded);d['balanced_score']=d.correct.astype(float)*np.where(d.label,2.,2./3.)
    metrics=[]
    for (model,condition,fmt,method),g in d.groupby(['model','condition','format','method']):
        pos=g.label.astype(bool);neg=~pos;valid=g.valid.astype(bool);flag=g.flag.eq(True)
        tp=int((pos&valid&flag).sum());tn=int((neg&valid&~flag).sum());fp=int((neg&valid&flag).sum())
        metrics.append(dict(model=model,condition=condition,format=fmt,method=method,n=len(g),positive=int(pos.sum()),invalid=int((~valid).sum()),tp=tp,tn=tn,fp=fp,accuracy=float(g.correct.mean()),recall=tp/int(pos.sum()),false_positive_rate=fp/int(neg.sum()),balanced_accuracy=(tp/int(pos.sum())+tn/int(neg.sum()))/2,price_accuracy=float(g.price_correct.mean()) if method!='baseline' else None,action_transcription_accuracy=float(g.actions_exact.mean()) if method=='end_to_end' else None,correct_flag_wrong_actions=int(g.correct_flag_wrong_actions.sum())))
    write_csv(out/'metrics.csv',metrics)
    effects=[];rng=np.random.default_rng(90017)
    for (model,condition,fmt),g in d.groupby(['model','condition','format']):
        p=g.pivot(index=['family','case_id'],columns='method',values='balanced_score')
        for a,z in [('end_to_end','baseline'),('end_to_end','hybrid'),('hybrid','baseline')]:
            if a not in p or z not in p:continue
            both=p[[a,z]].dropna();diff=(both[a]-both[z]).groupby(level=0).mean()
            if not len(diff):continue
            draws=diff.values[rng.integers(0,len(diff),size=(10000,len(diff)))].mean(axis=1)
            effects.append(dict(model=model,condition=condition,format=fmt,comparison=a+'-'+z,pairs=len(both),families=len(diff),metric='balanced_accuracy',difference=float(diff.mean()),ci_low=float(np.quantile(draws,.025)),ci_high=float(np.quantile(draws,.975))))
    write_csv(out/'paired_effects.csv',effects)
    paired=[]
    for (model,condition,fmt,method),g in d.groupby(['model','condition','format','method']):
        pairs=g.pivot(index=['family','category'],columns='world',values='correct').dropna()
        active_cats={c['category'] for c in cs.values() if c['label']}
        active=pairs[pairs.index.get_level_values('category').isin(active_cats)]
        paired.append(dict(model=model,condition=condition,format=fmt,method=method,
          complete_pairs=len(pairs),both_worlds_correct=float(pairs.all(axis=1).mean()),
          active_pairs=len(active),active_both_worlds_correct=float(active.all(axis=1).mean())))
    write_csv(out/'counterfactual_pairs.csv',paired)

    df[~df.correct].to_csv(out/'errors.csv',index=False)
    df[(df.method=='end_to_end')&~df.actions_exact.eq(True)].to_csv(out/'action_transcription_errors.csv',index=False)
    d.groupby(['model','condition','format','method','category']).agg(n=('correct','size'),accuracy=('correct','mean')).reset_index().to_csv(out/'category_metrics.csv',index=False)
    fig,axes=plt.subplots(1,3,figsize=(15,4),sharey=True);met=pd.DataFrame(metrics)
    for ax,fmt in zip(axes,FORMATS):
        sub=met[(met.condition=='clean')&(met['format']==fmt)]
        sub.pivot(index='model',columns='method',values='balanced_accuracy').plot.bar(ax=ax)
        ax.set_ylim(0,1.05);ax.set_title(fmt+' action records');ax.tick_params(axis='x',rotation=0);ax.set_xlabel('')
    axes[0].set_ylabel('Balanced accuracy, invalid = failure');fig.tight_layout();fig.savefig(out/'action_interface.png',dpi=180);plt.close(fig)
    (out/'LIMITATIONS.txt').write_text('Post-hoc action-interface audit; existing synthetic scenarios/families, not an independent held-out benchmark. End-to-end combines agreement and action extraction in a larger output schema: comparison is an intervention bundle, not a pure action-parser ablation. JSON can be deterministically parsed in real systems; an LLM parser is intentionally evaluated for the prose/general-text case and is not always necessary. Hybrid uses trusted structured actions and its single prediction is reused in all format comparisons. One strongest observed static attack selected after earlier outcomes; no general attack robustness claim. Neutral text is character-length matched, not token/semantic matched. Sixteen template families, repeated cases and descriptive bootstrap only. All methods use a new 384-token cap; do not pool with earlier runs. 75% negative; use balanced accuracy. Invalid outputs remain failures.\n')
    return status
