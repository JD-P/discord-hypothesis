import unittest
import threading
import queue
import json
from hypothesis_tracker import HypothesisTracker

class TestHypothesisTracker(unittest.TestCase):
    def setUp(self):
        with open("my_config.json") as infile:
            try:
                config = json.load(infile)
            except IOError:
                print("Couldn't find the config file, make sure you have config.json in the bot directory!")
                exit()
        self.tracker = HypothesisTracker([0], threading.Lock(), config["hypo-api-key"], config["hypo-group-id"])

    def test_get_rows_buffer(self):
        """Test that the buffer on the HypothesisTracker (self.processed) correctly 
        reflects the last results fetched from Hypothesis server."""
        fake_results = {"rows":[{"id":i, "text":"test"} for i in range(11)]}
        self.tracker.processed = []
        self.tracker.get_rows(fake_results)
        self.tracker.results_list = fake_results["rows"]
        fake_results_2 = {"rows":[{"id":i, "text":"test"} for i in range(3,14)]}
        self.tracker.get_rows(fake_results_2)
        for test_item in fake_results_2["rows"]:
            self.assertTrue(test_item["id"] in self.tracker.processed)

if __name__ == '__main__':
    unittest.main()
