import re
from enum import Enum
from math import log2,log

#represent runtime as a dictionary


# features:
# Should be able to determine what is happening if function is called a lot
# Should be easy to specify runtime
# give an input generator -> generate from hints

# specify runtime at this level/ total runtime of top level call / input size
#
#defaults to try for suggesting alternatives

default_runtimes = {
                        "1":lambda x: 1,
                       "log(n)": log2,
                       "sqrt(n)":lambda x:x**(1/2),
                       "nlog(n)": lambda x:x*log2(x),
                       "n^2": lambda x:x**2,
                       "2^n": lambda x: 2**x,
                       "3^n": lambda x: 3**x
}


def get_random_input(generator,size):
    return [generator() for x in range(size)]


def test_runtime(sizes,func):
    expected = map(f,sizes)

    return list(expected)

def test_runtimes(r_tree):
    sizes=[5,10,20]
    #store the differences for all the tests
    diffs = {x:[0,0,0] for x,y in default_runtimes}
    diffs[r_tree.get_condensed_runtime()] = test_runtimes(sizes,r_tree.test_runtime)
    for time,func in diffs:
        test_runtimes(sizes,func)

#master theorem for recursion
def master_theorem(a,b,c=0,k=0):
    c_crit = log(a, b)
    if c < c_crit:
        return "n^" + str(c_crit)
    elif c==c_crit:
        return "n^" + str(c_crit) + "(log(n))" + str(k+1)
    elif c > c_crit:
        output =  "n^" + str(c)
        if k > 0:
            output+= "(log(n))^" + str(k)
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
    #calculates the theoretical runtime
    def get_t_runtime(self):
        #handle the recursive part
        if self.recursive:
            recursed_childs = list(filter(lambda x: x.f_name == self.f_name,self.children))
            #no splitting
            if len(recursed_childs) == 1:
                a = self.get_max_depth()
                if recursed_childs[0].a_value == self.a_value - 1:
                    return "n" + self.t_value
                else:
                    return self.t_value + "log(n)"
            else:
                a = len(recursed_childs)
                b = self._get_max_child_ratio()
                k = re.search("log\(n\)\^[1-9],",self.t_value)
                if k is None:
                    k=0
                else:
                    k=int(k.string[-1])
                c = re.search("n\^[1-9]",self.t_value)
                c_2 = re.search("sqrt\(n\)",self.t_value)
                if c is None:
                    if c_2 is not None:
                        c=1/2
                    else:
                        c=0
                else:
                    c=int(c.string[-1])
                return master_theorem(a, b, c, k)
        else:
            if(len(self.children) > 0):
                return self.t_value + "(" + "+".join(map(RuntimeTree.get_t_runtime, self.children)) + ")"
            else:
                return self.t_value

    def get_a_runtime(self):
        if len(self.children) > 0:
            children_runtimes = map(RuntimeTree.get_a_runtime, self.children)
            return default_runtimes[self.t_value](self.a_value) + sum(children_runtimes)
        else:
            return default_runtimes[self.t_value](self.a_value)

    def _get_max_child_ratio(self):
        ratio = lambda x: self.a_value / x.a_value
        if len(self.children) == 0:
            return 1
        else:
            return max(map(ratio,self.children))

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

def runtime(expected,recursive=False):
    def count_runtime(func):
            def wrapper(*args,**kwargs):
                #adds in the gubbins to the tree
                global TIME_COUNTER
                input_value = args[0]
                TIME_COUNTER = TIME_COUNTER.push(expected,input_value,func.__name__,recursive)
                x = func(*args,**kwargs)
                TIME_COUNTER = TIME_COUNTER.pop()
                return x
            return wrapper
    return count_runtime


@runtime("1",recursive=True)
def sum_list(inpt=None):
    x = len(inpt)
    if(len(inpt) == 1):
        return inpt[0]
    else:
        return sum_list(inpt[len(inpt)//2:]) + sum_list(inpt[:len(inpt)//2])




sum_list([1,2,3,4,5,6])
print(TIME_COUNTER.get_t_runtime())
print(TIME_COUNTER.get_a_runtime())