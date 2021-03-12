import re
from math import log2,log
import random
#represent runtime as a dictionary


#TODO
# 1) use runtimes from children(not the recursive ones) when calculating recursive runtime
# 2) Build testing aparatus (compare a_runtime to t_runtime)
# 3) Allow for more complicated runtimes
# 4) Smarter output calculation(n(n) -> n^2)
# 5) Make defaults more general (x^n instead of 2^n and 3^n only)
# 6) Make the output prettier
# 7) Make how the input size is selected smarter




#defaults to try for suggesting alternatives

default_runtimes = {
                        "1":lambda x: 1,
                       "log(n)": log2,
                       "sqrt(n)":lambda x:x**(1/2),
                       "nlog(n)": lambda x:x*log2(x),
                        "n": lambda x:x,
                       "n^2": lambda x:x**2,
                       "2^n": lambda x: 2**x,
                       "3^n": lambda x: 3**x
}

#take in a function that generates inputs and create an input for testing
def get_random_input(generator,size):
    return [generator() for x in range(size)]


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
            recursed_childs = list(filter(lambda x: x.f_name == self.f_name, self.children))
            other_childs = list(filter(lambda x: not x.f_name == self.f_name, self.children))
            #TODO make this a function and less jank
            tester = lambda x: default_runtimes[x.t_value](20)
            #uses the largest runtime between this and the children as the per level runtime
            total_t = max(other_childs, key=tester)
            total_t = max(total_t, self, key=tester).t_value
            #no splitting
            if len(recursed_childs) == 1:
                a = self.get_max_depth()
                if recursed_childs[0].a_value == self.a_value - 1:
                    #TODO this might be incorrect now
                    return "n(" + total_t + ")"
                else:
                    return total_t + "(log(n))"
            else:
                a = len(recursed_childs)
                b = self._get_max_child_ratio()
                k = re.search("log\(n\)\^[1-9],", total_t)
                if k is None:
                    k=0
                else:
                    k=int(k.string[-1])
                c = re.search("n\^[1-9]", total_t)
                c_2 = re.search("sqrt\(n\)", total_t)
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

#TODO setup tests to compare predicted runtime to actual runtime
def test_runtime(sizes,func):
    expected = map(f,sizes)
    return list(expected)

def test_runtimes(func,gen):
    sizes=[5,10,20]
    global TIME_COUNTER
    outcomes = []
    #store the differences for all the tests
    for size in sizes:
        TIME_COUNTER=RuntimeTree()
        func(get_random_input(gen,size))
        outcomes.append(TIME_COUNTER.get_a_runtime() / size)
        #TODO compare the outcomes to the result of interpreting the theoretical value
    print(outcomes)




@runtime("n")
def merge(left, right):
    result=[]
    while not left == [] and not right == []:
        if left[0] < right[0]:
            result.append(left.pop(0))
        else:
            result.append(right.pop(0))
    # one of these must be empty so it's safe to add
    return result + left + right

@runtime("1",recursive=True)
def merge_sort(arr):
    if len(arr) == 1:
        return arr
    mid = len(arr)//2
    left = arr[:mid]
    right = arr[mid:]
    left = merge_sort(left)
    right = merge_sort(right)
    return merge(left, right)


gen = lambda : random.randint(1, 100)
test_runtimes(merge_sort,gen)