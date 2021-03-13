from runtime_counter import *

#abs,
#all,
#any,
#ascii,
#hash,
#range,
#reversed,
#sum,
#len,
#filter,
#dict,
#min,
#slice,


def range_size(*args):
    if len(args) >=2:
        size = abs(args[0] - args[1])
    else:
        size = abs(args[0])
    pass



dec = runtime("n",inputs=(0,),recursive=False)
__builtins__.range = dec(range)

