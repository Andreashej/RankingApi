import re, shlex
from sqlalchemy.ext.hybrid import hybrid_property

_missing = object()   # sentinel object for missing values


class cached_hybrid_property(hybrid_property):
    def __get__(self, instance, owner):
        if instance is None:
            # getting the property for the class
            return self.expr(owner)
        else:
            # getting the property for an instance
            name = self.fget.__name__
            value = instance.__dict__.get(name, _missing)
            if value is _missing:
                value = self.fget(instance)
                instance.__dict__[name] = value
            return value

camel_expr = re.compile('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')

def snake_to_camel(snake_str):
    if isinstance(snake_str, list):
        return [snake_to_camel(name) for name in snake_str]

    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])

def camel_to_snake(camel_str):
    if isinstance(camel_str, list):
        return [camel_to_snake(name) for name in camel_str]

    return camel_expr.sub(r'_\1', camel_str).lower()

def split(string, maxsplit=-1):
    """ Split a string with shlex when possible, and add support for maxsplit. """
    if maxsplit == -1:
        try:
            split_object = shlex.shlex(string, posix=True)
            split_object.quotes = '"`'
            split_object.whitespace_split = True
            split_object.commenters = ""
            return list(split_object)
        except ValueError:
            return string.split(" ", maxsplit)

    split_object = shlex.shlex(string, posix=True)
    split_object.quotes = '"`'
    split_object.whitespace_split = True
    split_object.commenters = ""
    maxsplit_object = []
    splits = 0

    while splits < maxsplit:
        maxsplit_object.append(next(split_object))

        splits += 1

    maxsplit_object.append(split_object.instream.read())

    return maxsplit_object