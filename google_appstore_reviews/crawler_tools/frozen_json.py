from collections import abc
import keyword


class FrozenJson:

    def __new__(cls, arg):
        if isinstance(arg, abc.Mapping):
            return super().__new__(cls)

        elif isinstance(arg, abc.MutableSequence):
            return [cls(item) for item in arg]

        else:
            return arg

    def __init__(self, mapping):
        self.__data = {}
        for key, val in mapping.items():
            if keyword.iskeyword(key):
                key += '_'
            self.__data[key] = val

    def __getattr__(self, name):
        if hasattr(self.__data, name):
            return getattr(self.__data, name)
        else:
            if name not in self.__data:
                msg = "'{}' object has no attribute '{}'"
                raise AttributeError(msg.format(self.__class__.__name__, name))
            else:
                return FrozenJson(self.__data[name])

