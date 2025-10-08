import json

import redis


class RedisQueue:
    def __init__(self, name="queue"):
        self.name = name
        self.redis = redis.Redis(host="localhost", port=6379, db=0)

    def publish(self, msg: dict) -> None:
        self.redis.rpush(self.name, json.dumps(msg))

    def consume(self) -> dict | None:
        msg = self.redis.lpop(self.name)
        if msg is None:
            return None
        return json.loads(msg)


if __name__ == "__main__":
    q = RedisQueue()
    q.publish({"a": 1})
    q.publish({"b": 2})
    q.publish({"c": 3})

    assert q.consume() == {"a": 1}
    assert q.consume() == {"b": 2}
    assert q.consume() == {"c": 3}
