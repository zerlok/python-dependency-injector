# mypy plugin should provide a type for dependency injector provider instances similar to a class below
# import abc
# import typing as t
# class TripleMultiplierProvider(t.Protocol):
#     @abc.abstractmethod
#     def __call__(self, y: float) -> "TripleMultiplier":
#         raise NotImplementedError

from dependency_injector import providers


class TripleMultiplier:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def perform(self, z: float) -> float:
        return self.x * self.y * z


invalid_x_provider: providers.Provider[TripleMultiplier] = providers.Factory(TripleMultiplier, "invalid")
valid_x_provider: providers.Provider[TripleMultiplier] = providers.Factory(TripleMultiplier, 2.0)

invalid_y_instance1: TripleMultiplier = valid_x_provider("invalid")
invalid_y_instance2: TripleMultiplier = valid_x_provider(x=3.0)
valid_y_instance1: TripleMultiplier = valid_x_provider(4.0)
valid_y_instance2: TripleMultiplier = valid_x_provider(y=5.0)

invalid_result1: float = valid_y_instance1.perform("invalid")
valid_result1: float = valid_y_instance1.perform(6.0)
