import types

def hide_user(f):
    """Hide all globals
    except builtins

    Args:
        f (function pointer): function to hide globals within

    Returns:
        function pointer: with globals hidden
    """
    inner_globals = dict()
    inner_globals['__builtins__'] = globals().get('__builtins__')
    return types.FunctionType(f.__code__, inner_globals)

@hide_user
def exec_user(code):
    """executes code with
    globals hidden

    Args:
        code (str): string of code

    Returns:
        any: return value of eval(code)
    """
    try:
        exec(code)
    except Exception:
        raise
