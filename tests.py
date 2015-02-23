import unittest

import os

import jetstream

class JetStreamTestCase(unittest.TestCase):

    def test_swallow_flight_plan(self):
        # European or African? That's really the question.
        js = jetstream.JetStream.from_file(
            os.path.join(os.path.dirname(__file__), 'sample_paths.txt'))
        self.assertEqual(js.path_length, 24)
        js.find_optimal_path()
        self.assertEqual(js.optimal_path,
                         [(0,5), (6,11), (14,17), (19,24)])
        self.assertEqual(js.optimal_path_cost, 352)

if __name__ == '__main__':
    unittest.main()
