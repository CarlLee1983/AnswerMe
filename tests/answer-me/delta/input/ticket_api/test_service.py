import unittest
from service import FakeRepo, TicketService

class TicketTests(unittest.TestCase):
    def test_repeat_hit(self):
        repo = FakeRepo({"T1": {"title": "hello"}})
        service = TicketService(repo)
        self.assertEqual(service.handle_get("T1")[0], 200)
        self.assertEqual(service.handle_get("T1")[0], 200)
        self.assertEqual(repo.reads, 1)

    def test_missing(self):
        service = TicketService(FakeRepo({}))
        self.assertEqual(service.handle_get("missing"), (404, {"error": "not found"}))

if __name__ == "__main__":
    unittest.main()
