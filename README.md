# Prj2-CampusEvacuation
## CX4230 - Computer Simulation - Project 2B/C - Campus Evacuation

### By: Derrick Williams and Tilak Patel

#### Date: March 14, 2016

### Campus Evacuation Task:
Our task is to design a conceptual model and implement a simulator that could be used to study traffic management plans for evacuating the Georgia Tech campus.

###Conceptual Model:
This campus evacuation model can be abstracted as a queueing network conceptual model. A lane loading cars are regarded as a queue where each car is an element of the queue. When a car crosses an intersection, it will enter a new downstream queue and leave the old one. Traffic will eventually leave the model via the nearest main exit routes (North Avenue (733,270), Fifth Street (760,555), and Tenth Street (723,32)).

1. We will build the network by creating nodes that represent the intersections.  These nodes will contain queues for all downstream roads from that node and capacities of those road segments.

2. The queues for the roads will have a capacity for each determined based on the length between the two end points of the road.  There will be a global variable of what size the car will be (set as 15' for this project) that will determine how many cars can fit in each queue based on the length of the road divided by the car length and rounded down.

3. Parking lots will contain the cars needed for the evacuation simulation.  We will have a global variable to stipulate what percent we want the parking lots full.  Each parking lot will have a queue of these cars based on a random number generator (exponiental) timestamping each car in a parking lot for exiting.  

4. The provided dataset for the roads and intersections (world2.csv) will be used to build the network of nodes, parking lots, and queues.  For our model, a capacity of 1 means 1 lane each way, while a capacity of 2 means 2 lanes each way.

5. Travel time was originally considered constant at 5 seconds, but that caused the cars to travel in waves stepping through the network like there is no difference between each intersection.  With the final version, travel time is considered based on how much capacity is left in each road segment, taking the car size, and an average speed that cars would travel through the network, a travel time is calculated for everytime a car comes into a new road segment and added to the timestamp for event queuing.  (Global speed assumed at 20 mph)

6. If a car has to wait because all downstream feasible options are at capacity, the car will get put back into the process queue for another 2 seconds before given another chance to move downstream.  A wait time (global of 2 seconds) will be considered before a car has a chance again to move through an intersection to the next downstream queue.

7. We will have three scenarios that we will study for the evacuation plan: 
- **Police direction condition**:Police direction condition: In this case, cars will be allowed to travel only in the direction that the police allow them to. The police will never allow the cars to travel westward. Furthermore, the police will make all the cars go to the three main exit routes (North Avenue, Fifth Street, and Tenth Street). Police will never allow cars to go pick another exit route even if the queue for one exit route is filled. The cars will simply have to wait in the parking lot or current road segment.  The police path is determined by looking at all downstream options at the current intersection the car is waiting at and seeing which option gets you the closest to one of the three exit locations.  Whatever is the closest option, that route is chosen for that one segment.  The process is repeated until the car exits.  In real life, the police will have a designated path that all cars must follow for proper evaluation, so this simulates that.

- **No westward option**: In this case, cars are not allowed to move westward outside of a fudge factor.  As we are simulating a disaster, most people in a real situation will not go back toward the direction of the disaster and police won't be able to set up in time. This will also help flush out the cars from the simulation in a more realistic fashion toward the east.  

- **Flashing red condition**: In this case, cars will be allowed to travel in any direction at the intersections.  The allowed direction will be randomly picked.  Note that cars could potentially run forever in our simulation and not mimic the reality of the true evacuation, hence why we have the no westward option to simulate with.  

###Software Implementation:
Also, since the simulation must be stochastic, i.e., use random numbers to model unpredictable elements of the system. We will be using an existing random number generator library (numpy.random import exponiental) and then validating the random number generator using a suitable statistical test.  We will be using one global heapsort to manage all events.  We will also have a global dictionary noting what the current capacity is in each segment of road.

### Simplifications:
Some simplifications are made for our campus evacuation model. Since It is both unnecessary and difficult to take some details into consideration in our model, we make the following simplifications:
- We are making all the cars the same size (15') for the model.
- Mean parking lot leave parameter of 15 seconds per car to be used in the exponiental random generator.
- Mean wait time for a downstream segment to open up is 5 seconds.
- Police are at each intersection guiding traffic.
- Average travel speed is 25 mph to simulate somewhat real movement of the car
 
### Assumptions:
Some data about our simulation is hard to collect. So we need to make some assumptions to process our model.
- There is no record for drivers’ behaviors. Thus, we treat all drivers as unaggressive drivers, and then we induce no one will pass the cars before.
- Entering time for each car, entering intersection for each car and exiting intersection for each car all obey uniform distribution.
- The world1.csv was editted by taking out some a few of the deadends in the graph as they were causing some cars to get stuck in some simulations because we weren't allowing cars to do a u-turn.  The final csv file is named world2.csv.

### Experiments:
The following are different scenarios we will experiment with:
- Change the capacity of the parking lot - from 10% full to 100% full and compare the time steps and average time for the car to exit the system among the three scenarios (police directing condition, no westard movement condition, and flashing red light condition).
- Change the car size (vary it to make it from small to big in order to resemble all motorcycles or small cars for the small size and trucks or SUVs for the big size) and compare the times for both the scenarios with the baseline model.  

#####NOTE: Some of these scenarios will neglect the simplifications and assumptions made for the baseline model. 

### How to Run evacSim.py:
- The basic format if you are running from a command line prompt is "python evalSim.py world2.csv ['police', 'noWest', 'random'] ['0.005'-'1.00'] ['capacity','path',or 'both'] [# of simulations]".  
- If running in say pycharm, set edit configuration to "world2.csv ['police', 'noWest', 'random'] ['0.005'-'1.00'] ['capacity','path',or 'both'] [# of simulations]".

### How to Run chiSquareTest.py:
- The basic format if you are running from a command line prompt is "python chiSquare.py".
- If running in say pycharm, select the file (chiSquare.py) in the left hand side or the orginization window pane and right click and select "Run 'chiSquare'" or just click the green run button. 
- After you run the file, the analysis is also included in the console output.



