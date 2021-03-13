import re
from math import log2,log
import random
from tracking import *
#represent runtime as a dictionary


#TODO
# 4) Smarter output calculation(n(n) -> n^2) (Done except for cleaner)
# 7) Make the random input generator smarter
# 8) Add runtimes to builtin functions (just need to do the rest by hand now)
# 9) Track what transformations have been applied to the input to figure out when something of size O(n) is being used
# 10) Add some fancy number crunchers once 9 is done (1 + 1/2 + 1/4 + ... =2) for example
# 11) Fix bug where if params are not passed it loses it's mind

#defaults to try for suggesting alternatives
#leaf equations
#x is to be left until the very end
base_equations = {
    "([0-9]+)": lambda x,y: int(y),
    "n": lambda x: x,
}
#binary/unary functions
r_time_functions = {
                       "log\((.+)\)": lambda x,y : log2(y(x)),
                       "sqrt\((.+)\)": lambda x,y: y(x) ** (1/2),
                       "([^tg(]+)\((.+)\)": lambda x,y,z: y(x) * z(x),
                       "(.+)\^(.+)": lambda x,y,z: y(x) ** z(x),
                       "(.+)\+(.+)": lambda x,y,z: y(x) + z(x)
}


#think about converting this to a full blown tokenizer... maybe?
def parse_runtime(r_str):
    # test if this is a leaf
    for x,func in base_equations.items():
        test = re.fullmatch(x,r_str)
        if not test:
            continue
        arg_count = func.__code__.co_argcount
        if arg_count > 1:
            #these are concrete values
            args = test.group(*list(range(1, arg_count)))
            return lambda x: func(x, *args)
        else:
            return lambda x: func(x)

    for x, func in r_time_functions.items():
        test = re.fullmatch(x, r_str)
        # skip nonmatching value
        if not test:
            continue
        arg_count = func.__code__.co_argcount
        #on the other hand these are all going to be functions
        args = list(map(parse_runtime, test.group(*list(range(1, arg_count)))))
        return lambda x: func(x, *args)


#take in a function that generates inputs and create an input for testing
def get_random_input(generator,size):
    return list(generator() for x in range(size))

#makes things more presentable
#TODO make this less silly
def cleanup(formula):
    #replace x^0 with 1
    x=re.sub("n\^0","1",formula)
    x = re.sub("\(log\(n\)\)\^0","1",x)
    # replace x^1 with x
    x = re.sub("[+\^]+1", "", x)
    #get rid of any 1's
    x = re.sub("1", "", x)
    #remove any brackets on the outside
    while len(x) > 0 and x[0] == "(":
        x = re.sub("^\(", "", x)
        x = re.sub("\)$", "", x)
    x = re.sub("^[+]", "", x)
    return x if x else "1"

#master theorem for recursion
def master_theorem(a,b,c=0,k=0):
    #print(a, b, c, k)
    c_crit = log(a, b)
    if int(c_crit) == c_crit:
        c_crit = int(c_crit)
    if c < c_crit:
        return "n^" + str(c_crit)
    elif c==c_crit:
        return "n^" + str(c_crit) + "(log(n)^" + str(k+1) + ")"
    elif c > c_crit:
        output = "n^" + str(c)
        if k > 0:
            output+= "(log(n)^" + str(k) + ")"
        return output

def a_master_theorem(n,a,b,c=0,k=0):
    c_crit = log(a, b)
    if c < c_crit:
        return n ** c_crit
    elif c == c_crit:
        return n**c_crit + log2(n) ** (k + 1)
    elif c > c_crit:
        return n**c + log2(n)**k


class RuntimeTree:

    def __init__(self, children = None, t_value = "1", a_value = 1, parent=None,f_name = "root", recursive=False):
        if children is None:
            self.children = []
        else:
            self.children = children
        self.a_value = a_value
        self.t_value = t_value
        self.parent=parent
        self.f_name = f_name
        self.recursive = recursive

    def test_runtime(self):
        '''
        compare the theoretical runtime vs the number of steps the program actually took
        :return:
        '''

    def get_shrinkage(self):
        recursed_childs = list(filter(lambda x: x.f_name == self.f_name, self.children))
        if len(recursed_childs) > 0:
            return self.a_value - recursed_childs[0].a_value
        else:
            #default to true for tiny inputs
            return self.parent.a_value - self.a_value

    #calculates the theoretical runtime
    def get_t_runtime(self):
        #handle the recursive part
        if self.recursive:
            recursed_childs = list(filter(lambda x: x.f_name == self.f_name, self.children))
            other_childs = list(filter(lambda x: not x.f_name == self.f_name, self.children))
            #TODO make this less aproximate and more smart
            tester = lambda x: parse_runtime(x.t_value)(20)
            #uses the largest runtime between this and the children as the per level runtime
            if len(other_childs) > 0:
                total_t = max(other_childs, key=tester)
                total_t = max(total_t, self, key=tester).t_value
            else:
                total_t = self.t_value
            #no splitting
            if len(recursed_childs) == 1:
                #check if the decrease is linear
                #TODO make it so that this works for trees as well a.k.a shrinkage uses tree size etc
                if self.get_shrinkage() == recursed_childs[0].get_shrinkage:
                    return "n(" + total_t + ")"
                else:
                    #TODO make this better than just assuming (log(n))
                    return total_t + "(log(n))"
            else:
                a = len(recursed_childs)
                b = self._get_max_child_ratio()
                k = re.search("log\(n\)\^[1-9]", total_t)
                if k is None:
                    k=0
                else:
                    k=int(k.string[-1])
                #Remove any logs from the string
                total_t = re.sub("log\(n\)\^[1-9]","",total_t)
                c_str = re.search("sqrt\(n\)", total_t)
                total_t = re.sub("sqrt\(n\)", "", total_t)
                if c_str is None:
                    c_str = re.search("n\^[1-9]", total_t) or re.search("n", total_t)
                    if c_str is None:
                        c=0
                    elif c_str.string == "n":
                        c=1
                    else:
                        #TODO make this less jank
                        c=int(c_str.string[-1])
                else:
                    c = 1/2
                return master_theorem(a, b, c, k)
        else:
            if len(self.children) > 1:
                return self.t_value + "(" + "+".join(map(RuntimeTree.get_t_runtime, self.children)) + ")"
            elif len(self.children) == 1:
                return self.t_value + "(" + self.children[0].get_t_runtime() + ")"
            else:
                return self.t_value


    def get_a_runtime(self):
        if len(self.children) > 0:
            children_runtimes = map(RuntimeTree.get_a_runtime, self.children)
            return parse_runtime(self.t_value)(self.a_value) + sum(children_runtimes)
        else:
            return parse_runtime(self.t_value)(self.a_value)

    def _get_max_child_ratio(self):
        #TODO make sure it's okay to round down here
        ratio = lambda x: self.a_value // x.a_value
        if len(self.children) == 0:
            return 1
        else:
            return max(map(ratio, self.children))

    def get_max_depth(self,depth=0):
        m_depth = 0
        get_depth = lambda x: x.get_max_depth(m_depth+1)
        if len(self.children) > 0:
            return max(map(get_depth,self.children))
        else:
            return depth

    def push(self, t_run, input, f_name, recursive=False):
        if hasattr(input,'__len__'):
            a_run = len(input)
        else:
            a_run = input
        x = RuntimeTree(t_value=t_run, a_value=a_run,parent=self, f_name=f_name, recursive=recursive)
        self.children.append(x)
        return x

    def pop(self):
        return self.parent


TIME_COUNTER = RuntimeTree()


def runtime(expected="1", recursive=False, inputs=None, leaf=False):
    def count_runtime(func):
        def wrapper(*args,**kwargs):
            nonlocal expected
            args = list(args)
            #adds in the gubbins to the tree
            global TIME_COUNTER
            #just add up all the inputs
            if inputs == "ALL":
                input_value = args[0]
                for x in args[1:]:
                    input_value = input_value + x
                for x in args:
                    x = tag(x)
            #O(whatever) if supplied O(1) otherwise
            elif inputs == "TAGGED":
                tagged_inputs = list(filter(is_tagged, args))
                if len(tagged_inputs) > 0:
                    input_value=tagged_inputs[0]
                    for input in tagged_inputs[1:]:
                        input_value+=input
                else:
                    expected="1"
                    input_value=1
            #a list of values to use was supplied
            elif hasattr(inputs, "__iter__"):
                input_value = args[inputs[0]]
                args[inputs[0]] = tag(args[inputs[0]])
                for index in inputs[1:]:
                    input_value += args[index]
                    args[index] = tag(args[index])
            #a function was supplied should be taggable
            elif callable(inputs):
                input_value = inputs(*args)
            else:
                args[0] = tag(args[0])
                input_value = args[0]
            TIME_COUNTER = TIME_COUNTER.push(expected, input_value, func.__name__, recursive)
            if not leaf:
                x = tag_applier(func)(*args, **kwargs)
            else:
                x = func(*args, **kwargs)
            TIME_COUNTER = TIME_COUNTER.pop()
            return x
        return wrapper
    return count_runtime

def test_runtimes(func, gen):
    sizes = [5, 10, 15, 200]
    global TIME_COUNTER
    outcomes = []
    #store the differences for all the tests
    for size in sizes:
        #Disabled because it's pretty clean as is
        #print("--------SIZE " + str(size) + "--------")
        TIME_COUNTER = RuntimeTree()
        func(get_random_input(gen, size))
        #TODO make this not break if the input isn't one of the default runtimes
        r_time = cleanup(TIME_COUNTER.get_t_runtime())
        f = parse_runtime(TIME_COUNTER.get_t_runtime())
        outcomes.append(TIME_COUNTER.get_a_runtime() / f(size))
        #TODO compare the actual runtime to the one received from counting values
        
    #TODO graphs or something
    print("labeled runtime: O(" + cleanup(TIME_COUNTER.get_t_runtime()) + ")")
    print("Ratios: " +str(outcomes))

