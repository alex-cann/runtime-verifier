#file to contain the code for TODO 10
#tags any values that are directly derived from the input size
#allowing for tracking of wether range actually takes O(n) time for example

def tag(x):
    #create a taggable copy
    #things can get weird if this isn't checked
    if not is_tagged(x):
        output = MetaTaggable(type(x))(x)
        #tag it
        output.tagged=True
    else:
        output = x
    return output

def is_tagged(x):
    return hasattr(x,"tagged") and x.tagged == True

#create a function that tags values
def tag_applier(func):
    def wrap(*args, **kwargs):
        tag_output = False
        for y in args:
            if is_tagged(y):
                tag_output=True
        for y in kwargs.values():
            if is_tagged(y):
                tag_output=True
        x = func(*args,**kwargs)
        return tag(x) if tag_output else x
    return wrap


target_funcs = ["__add__","__div__","__mult__"]


def decorate_from(decorator,ops):
    def decorate(target,cls):
        for attr in cls.__dict__:
            if callable(getattr(cls, attr)):
                #decorate a set of operations
                if attr in ops:
                    setattr(target, attr, decorator(getattr(cls, attr)))
                else:
                    #stop being tagged
                    setattr(target, attr, getattr(cls, attr))
        return target
    return decorate

ops = ["__add__","__radd__","__sub__","__rsub__","__mul__","__rmul__","__pow__","__rpow__","__neg__","__pos__","__abs__","__invert__",
 "__int__","__float__","__floordiv__","__rfloordiv__","__truediv__","__rtruediv__","__index__","conjugate","bit_length",
 "to_bytes","from_bytes","as_integer_ratio","__trunc__","__floor__","__ceil__","__round__","__sizeof__", "__reversed__", "__copy__", "__sort__","__iter__","__len__"]

#singleton to create wrapper classes
class MetaTaggable(type):
    _instances = {}
    def __new__(cls, target):
        if target not in MetaTaggable._instances:
            x = super().__new__(cls, target.__name__ + "tag", (target,),{})
            MetaTaggable._instances[target] = decorate_from(tag_applier, ops)(x, target)
        return MetaTaggable._instances[target]









