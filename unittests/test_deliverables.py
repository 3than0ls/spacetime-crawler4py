import unittest
from deliverables import GlobalDeliverableData, RawDeliverableData, process_page
from collections import Counter
import os
import threading
from bs4 import BeautifulSoup

class TestDeliverables(unittest.TestCase):
    def _delete_temp(self):
        if os.path.isdir(GlobalDeliverableData.DELIVERABLES_DIRNAME):
            for filename in os.listdir(GlobalDeliverableData.DELIVERABLES_DIRNAME):
                file_path = os.path.join(GlobalDeliverableData.DELIVERABLES_DIRNAME, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)

    def setUp(self):
        GlobalDeliverableData.DELIVERABLES_DIRNAME = "TEMP_DELIVERABLES"
        os.mkdir(GlobalDeliverableData.DELIVERABLES_DIRNAME)
        self._delete_temp()

    def tearDown(self):
        self._delete_temp()
        os.rmdir(GlobalDeliverableData.DELIVERABLES_DIRNAME)


    def test_deliverable_single_thread(self):
        g = GlobalDeliverableData()

        self.assertEqual(g.get_raw().finished, False)
        self.assertDictEqual(g.get_raw().url_word_map, {})
        self.assertEqual(g.get_raw().total_urls_seen, 0)
        self.assertEqual(g.get_raw().words, Counter())
        self.assertEqual(g.get_raw().subdomains, Counter())

        for i in range(5):
            fake_data = RawDeliverableData(
                url_word_map={f"fake_url_hash_{i}": 6},
                total_urls_seen=5,
                words=Counter(foo=1, bar=2, baz=3),
                subdomains=Counter({f"fake_url_domain_{i}": 1})
            )
            g.update(fake_data)

        self.assertEqual(g.get_raw().finished, False)
        g.mark_finished()
        self.assertEqual(g.get_raw().finished, True)
        self.assertDictEqual(
            g.get_raw().url_word_map,
            {
                "fake_url_hash_0": 6,             
                "fake_url_hash_1": 6,            
                "fake_url_hash_2": 6,           
                "fake_url_hash_3": 6,          
                "fake_url_hash_4": 6        
            }
        )
        self.assertEqual(g.get_raw().total_urls_seen, 5*5)
        self.assertEqual(g.get_raw().words["foo"], 5*1)
        self.assertEqual(g.get_raw().words["bar"], 5*2)
        self.assertDictEqual(
            g.get_raw().subdomains,
            {
                "fake_url_domain_0": 1,
                "fake_url_domain_1": 1,            
                "fake_url_domain_2": 1,
                "fake_url_domain_3": 1,          
                "fake_url_domain_4": 1        
            }
        )
        
    def test_deliverable_multi_thread(self):
        g = GlobalDeliverableData()

        self.assertEqual(g.get_raw().finished, False)
        self.assertDictEqual(g.get_raw().url_word_map, {})
        self.assertEqual(g.get_raw().total_urls_seen, 0)
        self.assertEqual(g.get_raw().words, Counter())
        self.assertEqual(g.get_raw().subdomains, Counter())

        batches = 5
        def worker(thread_id):
            for i in range(batches):
                fake_data = RawDeliverableData(
                    url_word_map={f"fake_url_hash_{thread_id}_{i}": 6},
                    total_urls_seen=5,
                    words=Counter(foo=1, bar=2, baz=3),
                    subdomains=Counter({f"fake_url_domain_{thread_id}_{i}": 1})
                )
                g.update(fake_data)

        threads = []
        for t_id in range(4):  # 4 threads
            t = threading.Thread(target=worker, args=(t_id,))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        self.assertEqual(g.get_raw().finished, False)
        g.mark_finished()
        self.assertEqual(g.get_raw().finished, True)

        expected_url_word_map = {f"fake_url_hash_{tid}_{i}": 6 for tid in range(4) for i in range(5)}
        expected_subdomains = {f"fake_url_domain_{tid}_{i}": 1 for tid in range(4) for i in range(5)}

        self.assertDictEqual(g.get_raw().url_word_map, expected_url_word_map)
        self.assertEqual(g.get_raw().total_urls_seen, 4 * batches * 5)  # 4 threads * 5 batches * 5 URLs each
        self.assertEqual(g.get_raw().words["foo"], 4 * batches * 1)
        self.assertEqual(g.get_raw().words["bar"], 4 * batches * 2)
        self.assertEqual(g.get_raw().words["baz"], 4 * batches * 3)
        self.assertDictEqual(g.get_raw().subdomains, expected_subdomains)


    def test_get_deliverable_name(self): 
        self.assertEqual(GlobalDeliverableData.get_previous_deliverable_fname(), None)
        g = GlobalDeliverableData()
        self.assertEqual(GlobalDeliverableData.get_previous_deliverable_fname(), g._shelve_path)
        fake_data = RawDeliverableData(
            url_word_map={"fake": 1},
            total_urls_seen=5,
            words=Counter(foo=1, bar=2, baz=3),
            subdomains=Counter({"fake": 1})
        )
        g.update(fake_data)
        self.assertEqual(GlobalDeliverableData.get_previous_deliverable_fname(), g._shelve_path)
        g.mark_finished()
        self.assertEqual(GlobalDeliverableData.get_previous_deliverable_fname(), None)
        
        import time
        time.sleep(1)

        g = GlobalDeliverableData()
        self.assertEqual(GlobalDeliverableData.get_previous_deliverable_fname(), g._shelve_path)
        g.mark_finished()
        self.assertEqual(GlobalDeliverableData.get_previous_deliverable_fname(), None)


    def test_process_page(self):
        with open("./unittests/test.html", 'r') as f:
            text = f.read()

        soup = BeautifulSoup(text, 'html.parser')

        deliverable = process_page("https://ics.uci.edu/notreal#fake", soup)

        self.assertTrue(
            "https://ics.uci.edu/notreal" in deliverable.url_word_map.keys())
        self.assertEqual(len(deliverable.url_word_map), 1)
        self.assertTrue("ics.uci.edu" in deliverable.subdomains)
        self.assertEqual(len(deliverable.subdomains), 1)
        self.assertEqual(Counter(deliverable.url_word_map).most_common(1)[0][0], "https://ics.uci.edu/notreal")
        self.assertEqual(Counter(deliverable.url_word_map).most_common(1)[0][1], 45)

        self.assertEqual(deliverable.words['foo'], 4)
        self.assertEqual(len(deliverable.words), 8) 


    def test_accumuluate_deliverable(self):
        A = RawDeliverableData()
        A.url_word_map = dict(zip(
            ["xxx", "yyy", "xxx/abc", "yyy/abc/?def"], [-1]*4))
        A.words = Counter(hello=20, world=20)
        A.subdomains = Counter(xxx=2, yyy=2)

        B = RawDeliverableData()
        B.url_word_map = dict(zip(
            ["foo", "bar", "foo/baz", "bar/baz/?idk", "xxx"], [-1]*5))
        B.words = Counter(world=5, hold=5, on=5)
        B.subdomains = Counter(foo=2, bar=2, xxx=1)

        final = GlobalDeliverableData()
        final.update(A)
        final.update(B)

        final = final.get_raw()
        
        self.assertEqual(final.url_word_map,
                         A.url_word_map | B.url_word_map)
        self.assertEqual(final.words,
                         A.words + B.words)
        self.assertEqual(final.subdomains,
                         A.subdomains + B.subdomains)

    def test_deliverable_multifile(self):
        with open("./unittests/test_foo.html", 'r') as f:
            foo = f.read()
        with open("./unittests/test_bar.html", 'r') as f:
            bar = f.read()

        foo_soup = BeautifulSoup(foo, 'html.parser')
        bar_soup = BeautifulSoup(bar, 'html.parser')

        deliverable = GlobalDeliverableData()
        deliverable.update(process_page("https://TEST_FOO.uci.edu", foo_soup))
        deliverable.update(process_page("https://TEST_BAR.uci.edu/longer_page#IGNORE_FRAG", bar_soup))

        deliverable = deliverable.get_raw()

        self.assertEqual(Counter(deliverable.url_word_map).most_common(1)[0][1], 116)
        self.assertEqual(Counter(deliverable.url_word_map).most_common(1)[0][0], "https://TEST_BAR.uci.edu/longer_page")
        self.assertEqual(set(deliverable.url_word_map.keys()), set(
            ["https://TEST_FOO.uci.edu", "https://TEST_BAR.uci.edu/longer_page"]))
        self.assertEqual(set(deliverable.subdomains.keys()), set(
            ["TEST_FOO.uci.edu", "TEST_BAR.uci.edu"]))
        self.assertEqual(deliverable.words["foo"], 115)
        self.assertEqual(deliverable.words["bar"], 116)
        self.assertEqual(deliverable.words["baz"], 0)  # baz not a word

if __name__ == '__main__':
    unittest.main()
