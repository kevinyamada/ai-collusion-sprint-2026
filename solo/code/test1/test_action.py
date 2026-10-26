import unittest
from collections import defaultdict
import hard_benchmark as b
class Tests(unittest.TestCase):
    def test_size(self):
        self.assertEqual(len(b.cases()),1152);self.assertEqual(len(b.jobs()),8064)
        self.assertEqual(len({c['id'] for c in b.cases()}),1152)
    def test_truth_and_controls(self):
        active={'initial','replacement','rejected_replacement','reinstatement','condition_met','counteroffer'};groups=defaultdict(list)
        for c in b.cases():
            self.assertEqual(c['label'],c['category'] in active and c['world']=='matched')
            self.assertEqual(c['label'],b.verify(c['agreed_price'],c['rounds'])['flag'])
            groups[c['family'],c['category'],c['world']].append(c)
        for vv in groups.values():
            self.assertEqual(len({str(c['messages']) for c in vv}),1);self.assertEqual(len({str(c['rounds']) for c in vv}),1)
    def test_end_to_end_uses_extracted_actions_only(self):
        trusted=[dict(round=i,A=50,B=50) for i in range(1,7)]
        p={'agreed_price':50,'actions':[[i,20,20] for i in range(1,7)]}
        self.assertFalse(b.finish(p,'end_to_end',trusted)['flag'])
        self.assertTrue(b.finish(p,'hybrid',trusted)['flag'])
        self.assertEqual(b.finish(p,'end_to_end',trusted),b.finish(p,'end_to_end',[]))
    def test_reject_missing_or_duplicate_rows(self):
        import json
        for a in [[],[[1,50,50]]*6,[[i,50,50] for i in range(1,6)]]:
            with self.assertRaises(ValueError):b.parse(json.dumps({'agreed_price':50,'actions':a}),'end_to_end')
    def test_no_label_leak(self):
        c=b.cases()[0]
        for m in b.METHODS:
            s=b.prompt(c,'json',m);modified={**c,'id':'LEAK','agreed_price':999,'label':False,'category':'LEAK'}
            self.assertEqual(s,b.prompt(modified,'json',m))
if __name__=='__main__':unittest.main()
