# Синглтон через метакласс
class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class MyClass(metaclass=SingletonMeta):
    pass


a = MyClass()
b = MyClass()

print(a is b)  # True


# Синглтон через __new__
class MySingleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


a = MySingleton()
b = MySingleton()

print(a is b)  # True


# Синглтон через механизм импортов
from singleton_module import singleton

a = singleton
b = singleton

print(a is b)  # True
