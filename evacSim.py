import sys
import simpy
import numpy
import math
import queue
from numpy.random import exponential
from numpy import mean
from heapq import heappush, heappop, heapify

# Globals
X_MEAN = 5.0
PARKING_CAP = .10
SCALE = 70/500
CAR_SIZE = 15 * SCALE


"""
Method to read from the world file and create a basic graph dictionary to pull
from for creating intersection and parking lot nodes.  There are no one lane
roads in this model except from exiting a parking lot.
fileName - name of file to read from
Return - return intersection dictionary of nodes and incoming queues to node
with capacities for each queue (number of lanes) and
parking lots dictionary of nodes with capacties of each.
Intersection Format -  (89, 81): [((86, 129),1), ((50, 87),2)]
Parking Lot Format  -  (86, 149): (1200, (83, 43))
"""
def readFileAndSetUp(fileName):
    worldFile = open(fileName,'r')
    worldFile.readline() # Throw Away top line

    intersections_graph = {}
    parking_nodes = {}

    for line in worldFile:
        array = line.split(',')
        typeNode = array[0]
        nodeFrom = (int(array[1]),int(array[2]))
        nodeTo = (int(array[3]),int(array[4]))
        capacity = int(array[5])

        # Street Nodes; lets process these
        if typeNode == 'Street':
            # Add queue for NodeFrom to NodeTo
            if nodeTo not in intersections_graph:
                intersections_graph[nodeTo] = []
                intersections_graph[nodeTo].append((nodeFrom,capacity))
            else:
                intersections_graph[nodeTo].append((nodeFrom,capacity))
            # Add queue for NodeTo to NodeFrom
            if nodeFrom not in intersections_graph:
                intersections_graph[nodeFrom] = []
                intersections_graph[nodeFrom].append((nodeTo,capacity))
            else:
                intersections_graph[nodeFrom].append((nodeTo,capacity))

        # Parking Nodes; lets process these; never allowing a queue to enter
        # parking lot
        elif typeNode == 'Parking':
            if nodeTo not in intersections_graph:
                intersections_graph[nodeTo] = []
                intersections_graph[nodeTo].append(nodeFrom)
            # Shouldn't ever happen, since there is only one parking lot per
            # coordinate, but let's check anyways
            else:
                intersections_graph[nodeTo].append(nodeFrom)

            parking_nodes[nodeFrom] = (capacity, nodeTo)

    worldFile.close()

    #for item in sorted(intersections_graph):
    #    print (item, intersections_graph[item])

    return intersections_graph, parking_nodes



def createQueuingCapacityDict(intersections):
    currentRoadCapacities = {}


globalTimeList = []
def globalQueue(parkingDicts):

    for key,value in parkingDicts:
        X_COUNT = value[0]
        x_values = exponential (X_MEAN, X_COUNT)
        print ("X ~ Exp(%g):" % X_MEAN)
        for (i, x_i) in enumerate (x_values):
            print ("  X_%d = %g" % (i, x_i))
        listOfTimeStamps = list(x_values)
        for time in listOfTimeStamps:
            carTuple = (time, key, value[1], key)
            globalTimeList.append(carTuple)

    heapify(globalTimeList)




    pass



"""
Method to calculate the capacity for a road between two nodes based on two
end points and number of lanes of road between those two nodes.
firstNode  - firstNode to pull from
secondNode - secondNode to pull from
numLanes   - number of lanes between firstNode and secondNode
Return - return capacity of road between the firstNode and secondNode
"""
def calculateRoadCapacity(firstNode, secondNode, numLanes):
    # Use Euclid distance
    distance = ((firstNode[0] - secondNode[0])**2 +
                (firstNode[1] - secondNode[1])**2)**(0.5)
    numCarsCapacity = distance * numLanes // CAR_SIZE

    return numCarsCapacity





def main():
    args = sys.argv

    intersections, parkingLots = readFileAndSetUp(args[1])

    #print (intersections)
    #print (parkingLots)
    #print (calculateRoadCapacity((0,0), (10,0), 1))

if __name__=='__main__':
	main()






# class ParkingLot(object):
#     def __init__(self, value, percent):
#         self.total = math.ceil(value * percent)
#
#     def cars(self):
#         X_COUNT = self.total
#         x_values = exponential (X_MEAN, X_COUNT)
#         # print ("X ~ Exp(%g):" % X_MEAN)
#         # for (i, x_i) in enumerate (x_values):
#         #     print ("  X_%d = %g" % (i, x_i))
#
#
#
# class Intersection:
#         def __init__(self, key, value, carSize):
#             self.carsPQ = []
#             for x in range (len(value)):
#                 pq = queue.PriorityQueue(maxsize = (math.sqrt((key[0]-value[x][0])**2 + (key[1]-value[x][1])**2) // CAR_SIZE))
#                 self.carsPQ.append(pq)
#
# parkingDict = {}
# intersectionDict = {}
# for key, value in parkingDict:
#     ParkingLot(value, PARKING_CAP)
#
# for key, value in intersectionDict:
#     Intersection(key, value, CAR_SIZE)
