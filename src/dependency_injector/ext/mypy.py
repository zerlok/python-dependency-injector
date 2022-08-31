import typing as t

from mypy.plugin import FunctionContext, Plugin
from mypy.types import Type


class DependencyInjectorPlugin(Plugin):

    def get_function_hook(self, fullname: str) -> t.Optional[t.Callable[[FunctionContext], Type]]:
        if "dependency_injector" in fullname:
            def handle(context: FunctionContext):
                print(context)
                # context.api.named_generic_type()
                return context.default_return_type

            return handle

    # def get_function_hook(self, fullname: str) -> Optional[Callable[[FunctionContext], Type]]:
    #     if "dependency_injector" in fullname:
    #         def handle(context: FunctionContext):
    #             return context
    #
    #         return handle


def plugin(version: str) -> t.Type[DependencyInjectorPlugin]:
    # ignore version argument if the plugin works with all mypy versions.
    return DependencyInjectorPlugin
