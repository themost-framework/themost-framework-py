import inspect
import pydash
import re
from os import getcwd
from .expect import expect


def replace_slash_with_dot(path: str) -> str:
    return re.sub(r'/', '.', path)


class ExpectedStrategyTypeError(Exception):
    def __init__(self, message='Configuration strategy must be a type'):
        self.message = message
        super().__init__(self.message)


class ExpectedConfigurationStrategyError(Exception):
    def __init__(self, message='The specified object must be an instance of configuration strategy'):
        self.message = message
        super().__init__(self.message)


class ConfigurationStrategy:
    configuration = None

    def __init__(self, configuration):
        self.configuration = configuration
        pass


class ConfigurationBase:
    __strategy__ = {}
    __source__ = {}
    cwd = None

    def __init__(self, cwd=None):
        self.cwd = cwd or getcwd()

    def getstrategy(self, strategy):
        expect(inspect.isclass(strategy)).to_be_truthy(ExpectedStrategyTypeError())
        return self.__strategy__.get(type(strategy))

    def usestrategy(self, strategy, useclass=None):
        expect(inspect.isclass(useclass)).to_be_truthy(ExpectedStrategyTypeError())
        if useclass is None:
            self.__strategy__.update({
                type(strategy): strategy(self)
            })
        elif inspect.isclass(useclass):
            instance = useclass(self)
            self.__strategy__.update({
                type(strategy): instance
            })
        elif type(useclass) is ConfigurationStrategy:
            self.__strategy__.update({
                type(strategy): useclass
            })
        else:
            raise ExpectedConfigurationStrategyError()

    def hasstrategy(self, strategy):
        return type(strategy) in self.__strategy__

    def get(self, path: str):
        return pydash.get(self.__source__, replace_slash_with_dot(path))

    def has(self, path: str):
        return pydash.has(self.__source__, replace_slash_with_dot(path))

    def set(self, path: str, value):
        return pydash.update(self.__source__, replace_slash_with_dot(path), value)


