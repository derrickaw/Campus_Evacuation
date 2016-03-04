import sys
import simpy
import numpy

def readFileAndSetUp(fileName):
    worldFile = open(fileName,'r')
    worldFile.readline() # Throw Away top line


    nodes_graph = {}

    for line in worldFile:
        array = line.split(',')
        typeNode = array[0]
        nodeFrom = (int(array[1]),int(array[2]))
        nodeTo = (int(array[3]),int(array[4]))
        capacity = int(array[5])

        if typeNode == 'Street' and capacity == 1:
            if nodeTo not in nodes_graph:
                nodes_graph[nodeTo] = []
                nodes_graph[nodeTo].append((typeNode,nodeFrom))
            else:
                nodes_graph[nodeTo].append((typeNode,nodeFrom))

        elif typeNode == 'Street' and capacity == 2:
            if nodeTo not in nodes_graph:
                nodes_graph[nodeTo] = []
                nodes_graph[nodeTo].append((typeNode,nodeFrom))
            else:
                nodes_graph[nodeTo].append((typeNode,nodeFrom))
            if nodeFrom not in nodes_graph:
                nodes_graph[nodeFrom] = []
                nodes_graph[nodeFrom].append((typeNode,nodeTo))
            else:
                nodes_graph[nodeFrom].append((typeNode,nodeTo))

        elif typeNode == 'Parking':
            if nodeTo not in nodes_graph:
                nodes_graph[nodeTo] = []
                nodes_graph[nodeTo].append((typeNode,nodeFrom))
            else:
                nodes_graph[nodeTo].append((typeNode,nodeFrom))

    worldFile.close()

    #for item in sorted(nodes_graph):
    #    print (item, nodes_graph[item])

    return nodes_graph

def main():
    args = sys.argv

    graph = readFileAndSetUp(args[1])
    print (graph)


if __name__=='__main__':
	main()