import unittest
from runtime_counter import *
from decorate_builtins import *
class MyTestCase(unittest.TestCase):

    def test_merge_sort(self):
        print("testing merge sort")
        test_runtimes(merge_sort, lambda : random.randint(1,100))

    def test_basic_tracking(self):
        print("testing loop")
        test_runtimes(loop, lambda : random.randint(1, 100))
    def test_negative_tracking(self):
        test_runtimes(o1_loop, lambda: random.randint(1, 100))
@runtime("n", inputs="ALL")
def merge(left, right):
    result = []
    while (not left == []) and (not right == []):
        if left[0] <= right[0]:
            result.append(left.pop(0))
        else:
            result.append(right.pop(0))
    # one of these must be empty so it's safe to add
    return result + left + right

@runtime(recursive=True)
def merge_sort(arr):
    if len(arr) == 1:
        return arr
    mid = len(arr) // 2
    left = arr[:mid]
    right = arr[mid:]
    left = merge_sort(left)
    right = merge_sort(right)
    return merge(left, right)

@runtime(recursive=True)
def binary_search(arr, k):
    i = len(arr) // 2
    if len(arr) == 0:
        return False
    elif len(arr) == 1:
        return arr[0] == k
    if arr[i] < k:
        return binary_search(arr[i + 1:], k)
    elif arr[i] == k:
        return True
    else:
        return binary_search(arr[i + 1:], k)

@runtime(recursive=True)
def lazy_search(arr, k):
    if len(arr) == 0:
        return False
    else:
        return arr[0] == k or lazy_search(arr[1:], k)


@runtime()
def loop(arr):
    tot = 0
    for x in range(len(arr)):
        tot += arr[x]
    return tot

@runtime()
def o1_loop(arr):
    tot=0
    for x in range(5):
        tot+=x
    return tot

#def len(*args):
#    dec=runtime("n", inputs="TAGGED", recursive=False)
#    return dec(len)(*args)
lf = runtime("n", inputs="TAGGED", leaf=True)
md = runtime("1", inputs="TAGGED", leaf=False)
range = lf(range)
len = md(len)

if __name__ == '__main__':
    unittest.main()

# here are some functions for testing it out
#-----------------------------------------------------------------------------------------------------------------
