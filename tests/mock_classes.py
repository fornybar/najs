class FakeMsg:
    def __init__(self, ack_error=None):
        self.ack_count = 0
        self.ack_error = ack_error

    async def ack(self):
        if self.ack_error is not None:
            raise self.ack_error
        self.ack_count += 1


class FakeConsumerConfig:
    def __init__(self, ack_policy):
        self.ack_policy = ack_policy


class FakeConsumerInfo:
    def __init__(self, ack_policy):
        self.config = FakeConsumerConfig(ack_policy)


class FakeSubscription:
    def __init__(self, outcomes, ack_policy=None):
        self.outcomes = list(outcomes)
        self.fetch_calls = []
        self.unsubscribe_count = 0
        self.ack_policy = ack_policy

    async def fetch(self, *, batch, timeout, heartbeat):
        self.fetch_calls.append(
            {
                "batch": batch,
                "timeout": timeout,
                "heartbeat": heartbeat,
            },
        )
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome

    async def consumer_info(self):
        return FakeConsumerInfo(self.ack_policy)

    async def unsubscribe(self):
        self.unsubscribe_count += 1


class FakeJetstream:
    def __init__(self, sub):
        self.sub = sub
        self.subjects = []

    async def pull_subscribe(self, *, subject):
        self.subjects.append(subject)
        return self.sub


class FailingJetstream:
    def __init__(self, error):
        self.error = error
        self.subjects = []

    async def pull_subscribe(self, *, subject):
        self.subjects.append(subject)
        raise self.error


class FakeClient:
    def __init__(self, js):
        self.js = js

    def jetstream(self):
        return self.js
