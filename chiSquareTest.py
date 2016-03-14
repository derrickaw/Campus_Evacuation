from math import sqrt
from collections import Counter
from numpy.random import exponential

def is_random(random_nums, r: int):
    """Calculates the chi-square value for n positive integers less than r

    Arguments:
    - random_nums: list of uniformly-randomly generated integers
    - r: int, upper bound for the random range

    Source: "Algorithms in C" - Robert Sedgewick - pp. 517

    NB: Sedgewick recommends:

        ...to be sure, the test should be tried a few times, since it could be
        wrong in about one out of ten times.

    """
    # Calculate the number of samples - n
    n = len(random_nums)

    # According to Sedgewick:
    # This is valid if n is greater than about 10r
    if n <= 10 * r:
        return False

    n_r = n / r

    # PART A: Get frequency of randoms
    ht = Counter(random_nums)

    # PART B: Calculate chi-square - this approach is in Sedgewick
    chi_square = sum((v - n_r)**2 for v in ht.values()) / n_r

    # PART C: According to Sedgewick:
    # The statistic should be within 2(r)^1/2 of r
    # This is valid if N is greater than about 10r
    return abs(chi_square - r) <= 2 * sqrt(r)



def main():
    x_values = exponential (10, 1000)
    print("EXPONENTIAL:", is_random(x_values, 100000))
    import os
    r = 256
    sample = os.urandom(r * 11)
    print("EXAMPLE:", is_random(sample, r))

    import numpy as np
    from numpy import random
    import matplotlib.pyplot as plt
    points = exponential(10, 1000)
    ax = plt.subplot(111,aspect='equal')
    ax.scatter(points)
    plt.show()


if __name__ == '__main__':
    main()

