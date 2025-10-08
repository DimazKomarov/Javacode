import random
import time

import redis


class RateLimitExceed(Exception):
    pass


class RateLimiter:
    def __init__(
        self, max_requests=5, window_seconds=3, redis_host="localhost", redis_port=6379
    ):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.redis = redis.Redis(host=redis_host, port=redis_port, db=0)
        self.key = "rate_limiter"

    def test(self) -> bool:
        now = time.time()

        pipeline = self.redis.pipeline()

        pipeline.zremrangebyscore(self.key, "-inf", now - self.window_seconds)

        pipeline.zcard(self.key)
        result = pipeline.execute()

        current_count = result[1]

        if current_count >= self.max_requests:
            return False

        self.redis.zadd(self.key, {str(now): now})
        self.redis.expire(self.key, self.window_seconds + 1)

        return True


def make_api_request(rate_limiter: RateLimiter) -> None:
    if not rate_limiter.test():
        raise RateLimitExceed
    else:
        print("Request allowed")


if __name__ == "__main__":
    rate_limiter = RateLimiter()

    for _ in range(50):
        time.sleep(random.randint(1, 2))

        try:
            make_api_request(rate_limiter)
        except RateLimitExceed:
            print("Rate limit exceed!")
        else:
            print("All good")
