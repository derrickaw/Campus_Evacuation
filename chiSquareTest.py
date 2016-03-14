from math import sqrt
from collections import Counter
from numpy.random import exponential
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import chisquare


# NOTE: the code below is not being used. The following is a program to calculate the chi-square value for N positive integers less than r.
# It is taken from https://en.wikibooks.org/wiki/Algorithm_Implementation/Pseudorandom_Numbers/Chi-Square_Test
# IT IS JUST BEING USED FOR TESTING PURPOSES AND HAS NOT BEEN USED TO TEST FOR TESTING THE NUMPY'S EXPONENTIAL GENERATOR.

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



#
#
# def calc_chisquare_statistic (counts, probs):
#     """
#     Given a target distribution and empirically observed counts, compute the
#     chi-square statistic of the observations relative to the target.
#
#     The input `counts[v] = y_v` is the dictionary of observations and
#     `probs[v] = p_v` is the probability of observing `v`.
#     """
#     n = sum (counts)
#     chi_sq = 0.0
#     # @YOUSE:
#     #assert False
#     for v in range(0, len(counts)):
#         y_v = counts[v]
#         x_v = float (n) * probs[v]
#         chi_sq += (y_v - x_v)**2 / x_v
#         if y_v < 5: print ("*** Warning: Only", y_v, "< 5 samples of item", v, "***")
#     return chi_sq




def main():
    bin = 50
    s = 1000
    #x_values = np.random.randn(s)
    x_values = exponential(.25,s)
    #print(x_values)
    y,x = np.histogram(x_values, bins=bin)
    y_norm = y/s
    #print("Y", y)
    n = len(x) - 1
    # x_prime is for getting the middle point of the histogram to avoid skewednees
    x_prime = [0] * bin
    for i in range(0, n):
        x_prime[i] = x[i] + ((x[i+1] - x[i])/2)
    #print (x_prime)
    #print(len(x_prime))
    print ("CHI_SQUARE TEST:", chisquare (y_norm,f_exp=x_prime))
    chiResult = chisquare(y_norm,f_exp=x_prime)
    print()
    print("According to the result of the Chi-Square test, we fail to reject the null hypothesis ")
    print("that numpy’s random number generator generates exponential random numbers ")
    print("with only 5% confidence. Since the p-value of", chiResult[1], "for the chi-square is greater than an alpha of ")
    print(".05, we fail to reject the null hypothesis and prove that numpy's random number generator is random!")
    print()
    print("Please take a look at the graphs and notice how, when plotting the random exponential values (which is what we used),")
    print("we notice that the distribution follows the exponential distributions. Thus, proving that numpy's random")
    print("number generator for exponential values is random.")
    plt.hist(x_values, bins = bin)
    plt.show()
    plt.plot(x_prime, y)
    plt.show()
    #q = calc_chisquare_statistic(y, y_norm)
    import os
    r = 256
    sample = os.urandom(r * 11)
    #print("SAMPLE", sample)
    print("EXAMPLE:", is_random(sample, r))


if __name__ == '__main__':
    main()

