import typing
from scatter.earth.structure import create_struct


class MyClass:
    x: int


if __name__ == "__main__":

    def my_func(a: list[list[int]], b: int, c: MyClass) -> typing.Tuple[int, int, MyClass]:
        return a, b, c

    func_struct = create_struct(my_func)

    # print(func_struct)

    # custom_type = list

    # type_ = msgspec.inspect.type_info(custom_type)

    # print(type_.__class__)
