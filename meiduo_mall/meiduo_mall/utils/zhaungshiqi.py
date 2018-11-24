from functools import wraps

import time


def time_timer(func):

    @wraps(func)
    def warapper(*args,**kwargs):
        print( '[Function: {name} start...]'.format(name = func.__name__))
        t0 = time.time()
        result = func(*args, **kwargs)
        t1 = time.time()
        print('[Function: {name} finished, spent time: {time:.2f}s]'.format(name = func.__name__,time = t1 - t0))
        return result
    return warapper()