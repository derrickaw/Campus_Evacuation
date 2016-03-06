import sys
import simpy
import numpy


"""
Method to read from the world file and create a basic graph dictionary to pull
from for creating intersection and parking lot nodes.
Intersection Format -  (89, 81): [(86, 129), (50, 87)]
Parking Lot Format  -  (86, 149): 1200
fileName - name of file to read from
Return - return intersection dictionary of nodes and incoming queues to node and
parking lots dictionary of nodes with capacties of each
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

        elif typeNode == 'Parking':
            # Never allowing a queue to enter parking lot
            if nodeTo not in intersections_graph:
                intersections_graph[nodeTo] = []
                intersections_graph[nodeTo].append(nodeFrom)
            else:
                intersections_graph[nodeTo].append(nodeFrom)

            parking_nodes[nodeFrom] = capacity

    worldFile.close()

    #for item in sorted(intersections_graph):
    #    print (item, intersections_graph[item])

    return intersections_graph, parking_nodes



def main():
    args = sys.argv

    intersections, parkingLots = readFileAndSetUp(args[1])
    print (intersections, parkingLots)


if __name__=='__main__':
	main()