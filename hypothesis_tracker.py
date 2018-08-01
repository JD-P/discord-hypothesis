import time
import json
import h_annot

class HypothesisTracker:
    """Run the Hypothesis search in a separate thread to prevent timing issues
    with async Discord library."""
    def __init__(self, results_list, list_lock, api_key, group_id):
        self.results_list = results_list
        self.list_lock = list_lock
        self.api_key = api_key
        self.group_id = group_id
        # Track processed annotation ID's so we don't double report
        try:
            with open("processed.json") as infile:
                self.processed = json.load(infile)
        except IOError:
            print("Failed to open processed entries!")
            self.processed = [] 

    def get_rows(self, new_results):
        # Remove previous results
        self.results_list.clear()
        
        for row in new_results["rows"]:
            if row["id"] in self.processed:
                    continue
            else:
                self.results_list.append(row)
        #TODO: Figure out why this had double-report issues when recording 10 id's
        self.processed = [row["id"] for row in new_results["rows"]]
        print(self.processed)
        with open("processed.json", "w") as outfile:
            json.dump(self.processed, outfile)
                
    def get_loop(self):
        while 1:
            self.list_lock.acquire()
            new_results = json.loads(
            h_annot.api.search(self.api_key,
                               group=self.group_id,
                               limit=10)
            )
            self.get_rows(new_results)
            self.list_lock.release()
            time.sleep(240)
