# Overview
A Decorator method to compute/test the runtime of a function or functions. Works like finite differences but for runtimes
instead of distances



#TODO
1) use runtimes from children(not the recursive ones) when calculating recursive runtime
2) Build testing aparatus (compare a_runtime to t_runtime)
3) Allow for more complicated runtimes
4) Smarter output calculation(n(n) -> n^2)
5) Make defaults more general (x^n instead of 2^n and 3^n only)
6) Make the output prettier
7) Override range so the cost of for loops is automagically included
