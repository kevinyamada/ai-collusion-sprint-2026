import unittest,json
from collections import defaultdict
import hard_benchmark as b
from new_cases import reduce_events

class Tests(unittest.TestCase):
    def test_coverage(self):
        cc=b.cases()
        self.assertEqual(len(cc),864)
        self.assertEqual(len(b.jobs()),6048)
        self.assertEqual(len({c['id'] for c in cc}),864)
        self.assertEqual(sum(c['label'] for c in cc),216)
    def test_truth_and_pairs(self):
        groups=defaultdict(list)
        for c in b.cases():
            self.assertEqual(reduce_events(c['events']),c['agreed_price'])
            self.assertEqual(b.verify(c['agreed_price'],c['rounds'])['flag'],c['label'])
            groups[c['family'],c['category']].append(c)
        for gg in groups.values():
            self.assertEqual(len(gg),6)
            self.assertEqual(len({json.dumps(c['messages']) for c in gg}),1)
            for world in ('matched','unmatched'):
                subset=[c for c in gg if c['world']==world]
                self.assertEqual(len({json.dumps(c['rounds']) for c in subset}),1)
                notes={c['condition']:c['note'] for c in subset}
                self.assertEqual(len(notes['attack']),len(notes['neutral']))
    def test_state_machine_cancellation(self):
        self.assertIsNone(reduce_events([('offer',20),('accept',20),('withdraw',20)]))
        self.assertEqual(reduce_events([('offer',20),('accept',20),('offer',40),('reject',40)]),20)
        self.assertIsNone(reduce_events([('offer',20),('conditional',20),('deny',20)]))
    def test_labels_not_in_prompt(self):
        for c in b.cases()[::13]:
            for m in b.METHODS:
                altered={**c,'label':not c['label'],'events':[],'category':'SECRET','agreed_price':999,'id':'SECRET'}
                self.assertEqual(b.prompt(c,'prose',m),b.prompt(altered,'prose',m))
    def test_extracted_actions_are_used(self):
        p={'agreed_price':30,'actions':[[i,20,20] for i in range(1,7)]}
        reference=[dict(round=i,A=30,B=30) for i in range(1,7)]
        self.assertFalse(b.finish(p,'end_to_end',reference)['flag'])
        self.assertTrue(b.finish(p,'hybrid',reference)['flag'])
        with self.assertRaises(ValueError):b.parse(json.dumps({**p,'actions':[[1,20,20]]*6}),'end_to_end')
if __name__=='__main__':unittest.main()
