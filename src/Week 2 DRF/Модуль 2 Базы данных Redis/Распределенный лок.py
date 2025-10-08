import datetime
import functools
import time
import uuid

import redis

redis_client = redis.Redis(host="localhost", port=6379, db=0)


def single(max_processing_time: datetime.timedelta):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            lock_key = f"lock: {func.__name__}"
            lock_value = str(uuid.uuid4())
            lock_ttl = int(max_processing_time.total_seconds())

            acquired = redis_client.set(lock_key, lock_value, nx=True, ex=lock_ttl)

            if not acquired:
                print(f"[LOCKED] {func.__name__} уже выполняется.")
                return None

            try:
                print(f"[LOCK ACQUIRED] Выполняем {func.__name__}.")
                return func(*args, **kwargs)
            finally:
                val = redis_client.get(lock_key)
                if val and val.decode() == lock_value:
                    redis_client.delete(lock_key)
                    print(f"[LOCK RELEASED] {func.__name__}.")

        return wrapper

    return decorator


@single(max_processing_time=datetime.timedelta(seconds=5))
def process_transaction():
    print("Старт транзакции.")
    time.sleep(3)
    print("Транзакция завершена.")


if __name__ == "__main__":
    process_transaction()
