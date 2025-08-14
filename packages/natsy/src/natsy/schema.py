import json
from functools import lru_cache
from pathlib import Path

from loguru import logger
from nats.js import JetStreamContext
from nats.js.errors import KeyNotFoundError

from najs.settings import SCHEMA_REGISTRY_BUCKET


@lru_cache
async def fetch_schema(
    js: JetStreamContext,
    name: str,
    fallback_path: Path | None = None,
) -> dict:
    """Fetch schema from schema registry key_value bucket

    Optionally use schema from file if not existing in the registry, which is useful
    for automatic initialization of schema.
    """
    registry = await js.key_value(SCHEMA_REGISTRY_BUCKET)
    try:
        schema = (await registry.get(name)).value
    except KeyNotFoundError:
        logger.error(f"Schema {name} not found in registry {SCHEMA_REGISTRY_BUCKET}")
        if fallback_path:
            logger.info(f"Trying to upload schema from {fallback_path}")
            schema = fallback_path.read_bytes()
            await registry.put(name, schema)
            logger.info(f"Successfully registered schema {name} from {fallback_path}")

        else:
            raise

    return json.loads(schema)
