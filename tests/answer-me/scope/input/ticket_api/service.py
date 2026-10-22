class NotFound(Exception):
    pass

class FakeRepo:
    def __init__(self, rows):
        self.rows = rows
        self.reads = 0

    def find(self, ticket_id):
        self.reads += 1
        return self.rows.get(ticket_id)

class TicketService:
    def __init__(self, repo):
        self.repo = repo
        self.cache = {}

    def get_ticket(self, ticket_id):
        if ticket_id in self.cache:
            return self.cache[ticket_id]
        row = self.repo.find(ticket_id)
        if row is None:
            raise NotFound(ticket_id)
        self.cache[ticket_id] = dict(row)
        return self.cache[ticket_id]

    def handle_get(self, ticket_id):
        try:
            return 200, self.get_ticket(ticket_id)
        except NotFound:
            return 404, {"error": "not found"}
