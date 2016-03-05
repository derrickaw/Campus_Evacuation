import math

from numpy.random import exponential
from numpy import mean
import queue


X_MEAN = 5.0
PARKING_CAP = .10
SCALE = 70/500
CAR_SIZE = 15 * SCALE

class ParkingLot(object):
    def __init__(self, value, percent):
        self.total = math.ceil(value * percent)

    def cars(self):
        X_COUNT = self.total
        x_values = exponential (X_MEAN, X_COUNT)
        # print ("X ~ Exp(%g):" % X_MEAN)
        # for (i, x_i) in enumerate (x_values):
        #     print ("  X_%d = %g" % (i, x_i))



class Intersection:
        def __init__(self, key, value, carSize):
            self.carsPQ = []
            for x in range (len(value)):
                pq = queue.PriorityQueue(maxsize = (math.sqrt((key[0]-value[x][0])**2 + (key[1]-value[x][1])**2) // CAR_SIZE))
                self.carsPQ.append(pq)

parkingDict = {}
intersectionDict = {}
for key, value in parkingDict:
    ParkingLot(value, PARKING_CAP)

for key, value in intersectionDict:
    Intersection(key, value, CAR_SIZE)


    # def cars(self, car):
    #     X_COUNT = ParkingLot.total
    #     x_values = exponential (X_MEAN, X_COUNT)
    #     print ("X ~ Exp(%g):" % X_MEAN)
    #     for (i, x_i) in enumerate (x_values):
    #         print ("  X_%d = %g" % (i, x_i))


