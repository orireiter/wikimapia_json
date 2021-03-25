import datetime
from inspect import isclass


def recursive_executer(
        recursive_function: callable,
        callback_function: callable,
        layers: int = 0,
        *args,
        **kwargs):
    '''
        Usage: calling for a function multiple times, 
        without hardcoding it with for loops.\n
        This function takes another function and excutes it 
        with the args sent.
        It then according to the layer, will execute it again with args before
        and the result of the last execution.
        When the deepest layer is reached, the callback function 
        will be executed with additional kwargs.
    '''
    results = recursive_function(*args)
    if layers != 0:
        if type(results) == type([]):
            for result in results:
                # when reaching an inner layer, the layer is reduced
                # other than that, everything elser is sent to the function.
                recursive_executer(recursive_function,
                                   callback_function, layers-1, *args, result, **kwargs)
        else:
            print(f'{datetime.datetime.now()} -> ERROR: couldn\'t return '
                  f'values with function {recursive_function.__name__}'
                  f' and parameters {args}')
    else:
        callback_function(results, **kwargs)


def iterate_function(urls: list, callback: callable, **kwargs):
    '''
        This function is used to take a function 
        and execute it over a list.
        It is used to allow functions to recgonize only 
        one object and not only use a list.
        Allows writing cleaner functions.
        The kwargs are used to sent extra parameters to the callback function.
    '''
    if not isclass(callback) and type(urls) == type([]):
        for url in urls:
            callback(url, **kwargs)
    elif type(urls) == type([]):
        # if a class was sent, it is first instanciated
        # and then called. the next call executes the
        # __call__ method.
        for url in urls:
            try:
                # print(kwargs)
                call = callback(url, **kwargs)
                call(**kwargs)
            except:
                print(
                    f'{datetime.datetime.now()} -> ERROR: couldn\'t iterate with {url}')
    else:
        print(
            f'{datetime.datetime.now()} -> ERROR: couldn\'t execute {callback.__name__}')


def dictionary_key_repacker(dictionary: dict,
                            originialKey_n_wantedKey_list: list):
    '''
        This function takes a dictionary and repacks it with new keys.
        The second argument is list containing original 
        key paired with a new key (or without it to keep the same name).
        It will return a new dictionary discarded of not given keys.
        \n
        before_dictionary = {'name': 'ori', 'age': 21, 'address': 'tlv'}\n
        renew_keys = [['name', 'full_name'], ['age']]\n
        print(dictionary_key_repacker(before_dictionary, renew_keys))\n
        -> {'full_name': 'ori', 'age': 21}
    '''
    return {key[-1]: dictionary[key[0]]
            for key in originialKey_n_wantedKey_list}
