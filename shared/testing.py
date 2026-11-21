from shared.events import EventPublisher


class FakeEventPublisher(EventPublisher):
    def __init__(self):
        self.published: list[tuple[str, dict, str]] = []

    def publish(self, event_type: str, payload: dict, correlation_id: str) -> None:
        self.published.append((event_type, payload, correlation_id))

class FakeOrderClient:
    def __init__(self):
        self.requests: list[tuple[str, dict, str]] = []

    def post_order(self, url: str, payload: dict, correlation_id: str) -> int:
        self.requests.append((url, payload, correlation_id))
        return 201