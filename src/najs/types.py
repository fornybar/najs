from typing import NamedTuple


class StreamMsg(NamedTuple):
    """A NATS Jetstream message

    Parameters:
        stream: Stream to which the message is published.
        subject: Subject to which the message is published.
        records: List of records. Prefer to contain many records(/rows) in one message.
        headers: The headers to be published.
        schema_name : Name of an avro schema that message should be serialized with
    """

    stream: str
    subject: str
    records: list[dict]
    headers: dict | None = None
    schema_name: str | None = None
