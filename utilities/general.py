import datetime


def recursive_executer(recursive_function: callable, callback_function: callable, layers: int = 0, *args, **kwargs):
    results = recursive_function(*args)
    if layers != 0:
        if results != None:
            for result in results:
                recursive_executer(recursive_function,
                                   callback_function, layers-1, *args, result, **kwargs)
        else:
            print(f'{datetime.datetime.now()} -> ERROR: couldn\'t return '
                  f'values with function {recursive_function.__name__}'
                  f' and parameters {args}')
    else:
        callback_function(results, **kwargs)
