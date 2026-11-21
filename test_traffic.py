import unittest
from traffic import Edge, classic, assign, analyze_addition

class TrafficTests(unittest.TestCase):
    def test_classic(self):
        r=analyze_addition(classic(False),Edge('B','C',0,0),4)
        self.assertAlmostEqual(r['before'],65,places=4)
        self.assertAlmostEqual(r['after'],80,places=4)
        self.assertAlmostEqual(r['optimal'],64.6875,places=4)
    def test_nepal(self):
        r=analyze_addition(classic(False,80),Edge('B','C',0,0),4)
        self.assertAlmostEqual(r['before'],70,places=4)
        self.assertAlmostEqual(r['after'],90,places=4)
    def test_us(self):
        r=analyze_addition(classic(False,160),Edge('B','C',0,0),4)
        self.assertAlmostEqual(r['before'],57.5,places=4)
        self.assertAlmostEqual(r['after'],50,places=4)
    def test_optimal_not_worse(self):
        r=analyze_addition(classic(False),Edge('B','C',0,0),4)
        self.assertLessEqual(r['optimal'],r['after']+1e-5)

if __name__=='__main__': unittest.main()
