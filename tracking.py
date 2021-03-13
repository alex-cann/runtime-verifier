#file to contain the code for TODO 10
#tags any values that are directly derived from the input size
#eventually this will replace the rudimentary mechanism of comparing the input size to the children's input size
#value that is O(n)

def tag(x):
    x.tagged=True

def is_tagged(x):
    return hasattr(x,'tagged') and x.tagged

class TrackedInt(int):

    def __init__(self, value):
        super().__init__(value)
