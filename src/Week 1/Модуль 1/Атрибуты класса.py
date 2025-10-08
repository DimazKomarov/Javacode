import datetime
import time


class TimestampMeta(type):
    def __new__(cls, name, bases, attrs):
        attrs["created_at"] = datetime.datetime.now()
        return super().__new__(cls, name, bases, attrs)


class FirstClass(metaclass=TimestampMeta):
    pass


time.sleep(2)


class SecondClass(metaclass=TimestampMeta):
    pass


if __name__ == "__main__":
    print(FirstClass.created_at)
    print(SecondClass.created_at)
