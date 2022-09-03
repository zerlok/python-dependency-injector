import typing as t

from mypy.nodes import ArgKind, Argument, ClassDef, TypeInfo, Var
from mypy.plugin import FunctionContext, Plugin
from mypy.subtypes import is_callable_compatible, is_subtype
from mypy.types import CallableType, Instance, Type


def strip_margin(s: str, margin: str = "|") -> str:
    return "\n".join(l.strip(f" {margin}") for l in s.split("\n"))


class DependencyInjectorPlugin(Plugin):

    def get_function_hook(self, fullname: str) -> t.Optional[t.Callable[[FunctionContext], Type]]:
        if "dependency_injector" in fullname:
            def handle(context: FunctionContext):
                tf, tf_args, tf_kwargs = context.arg_types  # type: t.Sequence[CallableType], t.Sequence[Instance], t.Sequence[Instance]

                base_func_type = tf[0]
                pos_args = [
                    (typ, kind, name)
                    for typs, kinds in zip(
                        context.arg_types[1:],
                        context.arg_kinds[1:],
                    )
                    for typ, kind, name in zip(typs, kinds, base_func_type.arg_names)
                    if kind == ArgKind.ARG_POS
                ]

                # TODO: build partial callables using positional and named arguments
                partial_func_type_from_base1 = base_func_type.copy_modified(
                    arg_types=base_func_type.arg_types[:len(pos_args)],
                    arg_kinds=base_func_type.arg_kinds[:len(pos_args)],
                    arg_names=base_func_type.arg_names[:len(pos_args)],
                )
                partial_func_type_from_base2 = base_func_type.copy_modified(
                    arg_types=base_func_type.arg_types[len(pos_args):],
                    arg_kinds=base_func_type.arg_kinds[len(pos_args):],
                    arg_names=base_func_type.arg_names[len(pos_args):],
                )

                provider_callable_type = base_func_type.copy_modified(
                    arg_types=[typ for typ, _, _ in pos_args],
                    arg_kinds=[kind for _, kind, _ in pos_args],
                    arg_names=[name for _, _, name in pos_args],
                    ret_type=partial_func_type_from_base2,
                )

                if not is_callable_compatible(
                        provider_callable_type,
                        partial_func_type_from_base1,
                        is_compat=is_subtype,
                        check_args_covariantly=True,
                        ignore_return=True,
                ):
                    # TODO: better error message
                    context.api.msg.fail(
                        msg=strip_margin(f"""
                        | base_func_type: {base_func_type}
                        | pos_args: {pos_args}
                        | partial_func_type_from_base1: {partial_func_type_from_base1}
                        | partial_func_type_from_base2: {partial_func_type_from_base2}
                        | provider_callable_type: {provider_callable_type}
                        | """),
                        context=context.context,
                    )

                    # context.api.msg.could_not_infer_type_arguments(base_func_type, 1, context)
                    return context.default_return_type

                if isinstance(context.default_return_type, Instance):
                    i: Instance = context.default_return_type
                    ti: TypeInfo = i.type
                    c: ClassDef = ti.defn

                    provider_cls = ClassDef(
                        name=ti.name + "Partial",
                        defs=c.defs,
                        type_vars=c.type_vars,
                    )
                    meth_args = [Argument(Var(name), typ, None, kind) for typ, kind, name in
                                 zip(partial_func_type_from_base2.arg_types, partial_func_type_from_base2.arg_kinds,
                                     partial_func_type_from_base2.arg_names, )]

                    # FIXME: strange error
                    #  add_method_to_class(
                    #  File "mypy/plugins/common.py", line 119, in add_method_to_class
                    #  AttributeError: attribute 'TypeInfo' of 'names' undefined
                    # add_method_to_class(
                    #     context.api,
                    #     provider_cls,
                    #     "__call__",
                    #     meth_args,
                    #     partial_func_type_from_base2.ret_type,
                    # )
                    #
                    # return Instance(provider_cls, [])

                return context.default_return_type

            return handle

    # def get_method_hook(self, fullname: str) -> Optional[Callable[[MethodContext], Type]]:
    #     if "dependency_injector" in fullname:
    #         def handle(context: MethodContext):
    #             print(context, id(context.type))
    #             return context.default_return_type
    #
    #         return handle


def plugin(version: str) -> t.Type[DependencyInjectorPlugin]:
    # ignore version argument if the plugin works with all mypy versions.
    return DependencyInjectorPlugin
