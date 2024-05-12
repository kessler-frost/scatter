from scatter.earth.cache import cache


STRUCT_CLASS_PREFIX = "Function"
CALLABLE_PREFIX = "callable"
SEPARATOR = "/"


# -------------------------- From function name helpers --------------------------

@cache.memoize()
def func_name_to_struct_name(func_name: str) -> str:
    """
    my_func -> "Function/my_func"
    """

    return SEPARATOR.join([STRUCT_CLASS_PREFIX, func_name])


@cache.memoize()
def func_name_to_struct_key(func_name: str, version: int) -> str:
    """
    my_func -> "Function/my_func/1"
    """

    return SEPARATOR.join([func_name_to_struct_name(func_name), version])


@cache.memoize()
def func_name_to_callable_key(func_name: str, version: int) -> str:
    """
    my_func -> "callable/my_func/1"
    """

    return SEPARATOR.join([CALLABLE_PREFIX, func_name, version])


# -------------------------- From struct name helpers --------------------------

@cache.memoize()
def struct_name_to_func_name(struct_name: str) -> str:
    """
    Function/my_func -> my_func
    """

    return struct_name.split(SEPARATOR)[1]


@cache.memoize()
def struct_name_to_struct_key(struct_name: str, version: int) -> str:
    """
    Function/my_func -> Function/my_func/1
    """

    return SEPARATOR.join([struct_name, version])


@cache.memoize()
def struct_name_to_callable_key(struct_name: str, version: int) -> str:
    """
    Function/my_func -> callable/my_func/1
    """

    return SEPARATOR.join([CALLABLE_PREFIX, struct_name_to_func_name(struct_name), version])


# -------------------------- From struct key helpers --------------------------

@cache.memoize()
def struct_key_to_struct_name(struct_key: str) -> str:
    """
    Function/my_func/1 -> Function/my_func
    """

    return SEPARATOR.join(struct_key.split(SEPARATOR)[:-1])


@cache.memoize()
def struct_key_to_func_name(struct_key: str) -> str:
    """
    Function/my_func/1 -> my_func
    """

    return struct_key.split(SEPARATOR)[1]


@cache.memoize()
def struct_key_to_callable_key(struct_key: str) -> str:
    """
    Function/my_func/1 -> callable/my_func/1
    """

    return SEPARATOR.join([CALLABLE_PREFIX, struct_key.split(SEPARATOR)[1], struct_key.split(SEPARATOR)[2]])
