# Solving Constraint Satisfaction Problems in Python

An implementation of a solution to a Constraint Satisfaction Problem in Python.

Attempts to achieve an optimal series of assignments using a series of hueristics that trade off between run-time and minimum cost in a search space of 1250P25 possible assignment permutations (207,889,198,850,066,441,757,915,286,543,749,608,006,884,481,814,379,450,166,991,776,789,299,200,000,000 or ~2.0789*10^46) 

We achieve an average run time of ~120ms, with costs averaging ~4.5% above optimal. 

To see the algorithm in action, run the scheduler with `python3 runScheduler.py`. Change the problem set in `runScheduler` to solve a different example problem. 
