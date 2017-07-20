# coding: utf-8
import operator
from functools import partial


def handle_error_func(func):
    def wrap(*args, **kwargs):
        try:
            res, error = func(*args, **kwargs), None
        except Exception as e:
            res, error = None, e.message or e.__class__.__name__
        return res, error

    return wrap


def error_chain(*steps):
    funcs = steps[::-1]

    def wrap(*args, **kwargs):
        res, error = funcs[0](*args, **kwargs)
        if error:
            return res, error

        for func in funcs[1:]:
            res, error = func(res)
            if error:
                res = None
                break
        return res, error

    return wrap


def get_item(data, *keys):
    res, error = data, None
    key, keys = keys[:1], keys[1:]
    if key:
        res, error = error_chain(handle_error_func(operator.methodcaller("__getitem__", key[0])))(data)
        if not error:
            return get_item(res, *keys)
    return res, error


def parse_data(row_data, params):
    data = {}

    for key, attrs in params.items():
        data_value = row_data.get(key, None)

        if isinstance(data_value, list):

            for value in data_value:
                value_item = partial(operator.getitem, value)

                if isinstance(attrs, dict):
                    _filter = attrs.get("_filter", None)
                    _take = attrs.get("_take", lambda: None)

                    if _filter and _take:
                        first_filtered, _ = get_item(filter(_filter, data_value), 0)
                        taked_data = _take(first_filtered)
                        data[key] = taked_data
                        continue

                if not isinstance(attrs, list):
                    data[key] = value.get(attrs)
                    break

                attrs_value = map(value_item, attrs)
                v = data.setdefault(key, [])
                v.extend(attrs_value)

        elif isinstance(attrs, dict):

            for subkey, subvalue in attrs.items():
                data_value = data_value.get(subkey, None)
                v = data.setdefault(key, [])
                for value in data_value:
                    value_item = partial(operator.getitem, value)

                    attrs_value = map(value_item, subvalue)
                    v.extend(attrs_value)
        else:
            data[key] = data_value

    return data
