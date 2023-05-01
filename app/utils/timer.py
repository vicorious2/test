import time
from functools import wraps


def time_this(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        tic = time.perf_counter()
        result = f(*args, **kwargs)
        toc = time.perf_counter()

        arg1 = []
        for x in args:
            if type(x) is str and len(x) > 200:
                arg1.append(x[0:5] + "..." + x[-5:])
            else:
                arg1.append(x)
        return result

    return decorator
