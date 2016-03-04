# Prj2-CampusEvacuation
## CX4230 - Computer Simulation - Project 2B/C - Campus Evacuation

### By: Derrick Williams and Tilak Patel

#### Date: March 4, 2016

### Campus Evacuation Task:
Our task is to design a conceptual model and implement a simulator that could be used to study traffic management plans for evacuating the Georgia Tech campus.

###Conceptual Model:
This campus evacuation model can be abstracted as a queueing network conceptual model. A lane loading cars are regarded as a queue where each car is an element of the queue. When a car crosses an intersection, it will enter a new queue and leave the old one. If there is a police directing the traffic, the police will direct all cars to the nearest main exit routes (North Avenue, Fifth Street, and Tenth Street). The police will never allow the cars to travel westward. If there is a red light directing the traffic, the cars will be allowed to go anywhere except westward. 
We will build the network by creating nodes that represent the intersections.  These nodes will contain queues for all incoming roads to that node and information on downstream nodes.

1. The queues for the roads will have a capacity for each determined based on the length between the two end points of the road.There will be a global variable of what size the car will be that will determine how many cars can fit in each queue based on the length of the road divided by the car length.

2. Parking lots will contain the cars needed for the evacuation simulation.  We will have a global variable to stipulate what percent we want the parking lots full.  Each parking lot will have a queue of these cars based on a random number generator timestamping each car in a parking lot for exiting.

3. The provided dataset for the roads and intersections (world.csv) will be used to build the network of nodes, parking lots, and queues.  For our model, we will assume the direction from x1,y1 to x2,y2 is the direction that cars can travel on the road if the capacity of the road is 1, simulating a one-way street.  If the capacity of the road is 2, then the road will be bi-directional.

4. Travel time will not be considered in the model from traveling from one node to the next as the time is really not too significant for such short distances and adds additional complexity that is not needed at this stage.  If time permits, we may add this feature.

5. We will have two scenarios that we will study for the evacuation plan: 
  - **Flashing red condition**: In this case, cars will be allowed to travel in any direction at the intersections long as the direction is equal to or progressively eastward from the current location.  As we are simulating a disaster, most people in a real situation will not go back toward the direction of the disaster.  This will also help flush out the cars from the simulation in a more realistic fashion toward the east.  If we did allow cars to possibly go westward, cars could potentially run forever in our simulation and not mimic the reality of the true evacuation.  If time permits, we may look at allowing cars to go westward to see what happens.
  - **Police direction condition**: In the case, cars will be allowed to travel only in the direction that the police allow them to. The police will never allow the cars to travel westward. Furthermore, the police will make all the cars go to the three main exit routes (North Avenue, Fifth Street, and Tenth Street). Police will never allow cars to go pick another exit route even if the queue for one exit route is filled. The cars will simply have to wait in the parking lot.


###Software Implementation:
We will use SimPy to handle the simulation portion of the project.  SimPy will handle the events and resources used in the simulation based on timestamps.
Also, since the simulation must be stochastic, i.e., use random numbers to model unpredictable elements of the system. We will be using an existing random number generator library and then validating the random number generator using a suitable statistical test.


### Simplifications:
Some simplifications are made for our campus evacuation model. Since It is both unnecessary and difficult to take some details into consideration in our model, we make the following simplifications:
- We are not including the time it takes for a car to evacuate. Instead we are going to measure the total time it will take take for all the cars to evacuate from the beginning of the simulation.
- We are making all the cars the same size for the model. This will allow for a uniform number of cars for each of the lanes (queues). 
 
### Assumptions:
Some data about our simulation is hard to collect. So we need to make some assumptions to process our model.
- There is no record for drivers’ behaviors. Thus, we treat all drivers as unaggressive drivers, and then we induce no one will pass the cars before.
- Entering time for each car, entering intersection for each car and exiting intersection for each car all obey uniform distribution.
- All cars will always travel eastward - towards the exit. They will never travel westward - towards the disaster.


### Experiments:
The following are different scenarios we will experiment with:
- Change the capacity of the parking lot - from 10% full to 100% full and compare the times between the two scenarios (flashing red light and police directing condition).
- Change the car size (vary it to make it from small to big in order to resemble all motorcycles or small cars for the small size and trucks or SUVs for the big size) and compare the times for both the scenarios with the baseline model.  
- Possibly allow the cars to travel westward (towards the disaster) for the flashing red light scenario.

#####NOTE: Some of these scenarios will neglect the simplifications and assumptions made for the baseline model. 
