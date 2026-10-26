import unittest
from collections import defaultdict
import hard_benchmark as b
class Tests(unittest.TestCase):
    def test_size(self):
        cc=b.cases();self.assertEqual(len(cc),4800);self.assertEqual(len(b.jobs()),9600);self.assertEqual(len({c['id'] for c in cc}),4800)
    def test_all_attacks_cross_all_cases(self):
        groups=defaultdict(list)
        for c in b.cases():groups[c['family'],c['category'],c['world']].append(c)
        self.assertEqual(len(groups),192)
        for variants in groups.values():
            self.assertEqual({c['condition'] for c in variants},set(b.CONDITIONS))
            self.assertEqual(len({str(c['messages']) for c in variants}),1)
            self.assertEqual(len({str(c['rounds']) for c in variants}),1)
            self.assertEqual(len({c['label'] for c in variants}),1)
            notes={c['condition']:c['note'] for c in variants}
            for i in range(12):self.assertEqual(len(notes[f'attack_{i:02}']),len(notes[f'neutral_{i:02}']))
    def test_labels(self):
        active={'initial','replacement','rejected_replacement','reinstatement','condition_met','counteroffer'}
        for c in b.cases():
            self.assertEqual(c['label'],c['category'] in active and c['world']=='matched')
            self.assertEqual(c['label'],b.verify(c['agreed_price'],c['rounds'])['flag'])
    def test_annotations_not_in_prompt(self):
        c=b.cases()[0];s=b.prompt(c,'json','baseline')
        c={**c,'id':'LEAK','label':not c['label'],'agreed_price':999,'category':'LEAK','condition':'LEAK'}
        self.assertEqual(s,b.prompt(c,'json','baseline'))
if __name__=='__main__':unittest.main()
