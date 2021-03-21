# Overview
A Decorator method to compute/test the runtime of a function or functions. Works like finite differences but for runtimes
instead of distances

#How to Use
- Decorate the function you want to use by doing @runtime() (see usage below) as well as any helper functions
- Call the function you would like to track
- Call RUNTIME_TREE.get_t_runtime() to see the predicted theoretical runtime is
- Call RUNTIME_TREE.get_a_runtime() to see a rough number of operations executed
- Or call test_runtimes(func,gen) where func is the function you want to test and gen is a generator that returns a random value
(for a list of int gen yields ints)


#TODO
1) use runtimes from children(not the recursive ones) when calculating recursive runtime
2) Build testing aparatus (compare a_runtime to t_runtime)
3) Allow for more complicated runtimes
4) Smarter output calculation(n(n) -> n^2)
5) Make defaults more general (x^n instead of 2^n and 3^n only)
6) Make the output prettier
7) Override range so the cost of for loops is automagically included
