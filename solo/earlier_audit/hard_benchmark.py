"""Exploratory crossed attack/neutral-text follow-up, frozen before new inference."""
import copy
from frozen_hard_base import cases as original_cases,prompt,parse,verify,ATTACKS
FORMATS=('json',)
FAMILIES=8
CONDITIONS=('clean',)+tuple(x for i in range(12) for x in (f'attack_{i:02}',f'neutral_{i:02}'))
def neutral_note(length):
    # Exactly matched characters, not exact tokenizer length. This is a nuisance-text control.
    s='Routine packaging notes describe cardboard cartons and paper wrapping. '
    return (s*((length//len(s))+1))[:length]
def cases():
    result=[]
    for original in original_cases():
        if original['condition']!='clean' or original['family']>=FAMILIES:continue
        for condition in CONDITIONS:
            c=copy.deepcopy(original);c['condition']=condition
            c['id']=f"audit_f{c['family']:02}_{c['category']}_{c['world']}_{condition}"
            if condition=='clean':c['note']='No attached material.'
            else:
                attack=ATTACKS[int(condition.split('_')[1])]
                c['note']=attack if condition.startswith('attack_') else neutral_note(len(attack))
            result.append(c)
    return result
def jobs():
    return [(c,'structured' if m=='hybrid' else 'json',m) for c in cases() for m in ('baseline','hybrid')]
