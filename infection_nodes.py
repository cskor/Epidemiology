from matplotlib import pyplot as plt
import networkx as nx
import numpy as np
import random

NUMBER_OF_NODES = 100
NUMBER_OF_INTERACTIONS = 15
CHANCE_OF_INFECTION = 0.75
NUMBER_OF_ROUNDS = 30
PATIENT_ZERO = 0
DRAW_FINAL_GRAPH = False
DRAW_GRAPH_EACH_STEP = False

def createInteractions():
    """ This function randomly selects numInteraction nodes for each node to 
        interact with within the graph """
    nodeInteractions = {}
        
    #For each node, randomly select numIteraction nodes for them to interact with
    for node in range(NUMBER_OF_NODES):
        #Create a random list of nodes that the graph interacts with
        iteractions = random.sample(range(NUMBER_OF_NODES), NUMBER_OF_INTERACTIONS)
        
        #Keep randomly creating lists if the node is in its connections
        while(node in iteractions):
            iteractions = random.sample(range(NUMBER_OF_NODES), NUMBER_OF_INTERACTIONS)
        
        #Add node to nodeIteractions
        nodeInteractions[node] = iteractions
    
    return nodeInteractions

def runInfection(graph, infectedNode, index, nodeInteractions, listOfInfected, nodeInfectedCount):
    """ This function goes thru the list of interactions for PATIENT ZERO and using the CHANCE OF 
        INFECTION determines if the node it came into contact with also gets infected. If a new
        node is infected then we recursively go through that nodes future interactions to see if 
        they also infect anyone. """
    #BASE CASE: if there are no more interactions for a node to make, return
    if index + 1 == NUMBER_OF_INTERACTIONS:
        return
    
    #Get the list of interactions of the currently infected node
    interactions = nodeInteractions[infectedNode]
    
    #Only care about the interactions after the node is infected
    interactions = interactions[index:]
        
    #for the remaining interactions, try to infect them
    for node in interactions:
        #Randomly choose a number from [0,1]
        infectedChance = random.uniform(0,1)
        
        #If your random chance is withing [0, chanceOfInfection] you are now infected
        if infectedChance <= CHANCE_OF_INFECTION:
            if node in listOfInfected:
                #This node has already been infected, check the round to see if this
                #interaction could have occurred before the recorded interaction
                alreadyInfectedNode, indexInfectedOn = listOfInfected.get(node)
                
                #This interact would have occurred first
                if interactions.index(node) + index < indexInfectedOn:
                    #Remove the old edge
                    graph.remove_edge(alreadyInfectedNode, node)
                    
                    #Remove the infected count
                    nodeInfectedCount[alreadyInfectedNode] -= 1
                    
                    #Add the new edge
                    graph.add_edge(infectedNode, node)
                    
                    #Save info to listOfInfected
                    listOfInfected[node] = [infectedNode, interactions.index(node) + index]
                    
                    #Add to the infected count of the node
                    nodeInfectedCount[infectedNode] += 1
            else:
            #This node has not already been infected
                #Add the new edge
                graph.add_edge(infectedNode, node)
                    
                #Save info to listOfInfected
                listOfInfected[node] = [infectedNode, interactions.index(node) + index]
                
                #Add to the infected count of the node
                nodeInfectedCount[infectedNode] += 1
            
            #Call function again on this newly infected node
            runInfection(graph, node, interactions.index(node) + index + 1, nodeInteractions, listOfInfected, nodeInfectedCount)
    
def drawGraph(graph, roundInfected, infectedNode):
    """ This function draws a graph where each node represents a person and if there is an edge
        connecting the two nodes then one node infected the other. The color scale represents at 
        what round did the node become infected. This function has the ability to draw the graph
        at each round and at the conclusion of the infection rounds."""
    cmap = plt.cm.YlOrRd
    vmin=0
    vmax = max(roundInfected)
    
    
    if DRAW_GRAPH_EACH_STEP:
        #Create the initial graph with NUMBER_OF_NODES
        roundGraph = nx.empty_graph(NUMBER_OF_NODES)
        
        for round in range(1, NUMBER_OF_INTERACTIONS):
            #determine which nodes were infected that round
            indices = [i for i, x in enumerate(roundInfected) if x == round]
    
            #make an edge from the node that infected them to the node
            for index in indices:
                roundGraph.add_edge(infectedNode[index][0], index)
    
            #Create the subplot
            nx.draw_networkx(roundGraph, pos=nx.spring_layout(roundGraph, k=0.3), with_labels=False, node_size=75, node_color='black')
            
            #Plot graph
            plt.title("Round #{0}".format(round))
            plt.axis('off')
            plt.figure("Round #{0}".format(round))
        
    #Draw the nodes and
    nx.draw_networkx(graph, pos=nx.spring_layout(graph, k=0.3), with_labels=False, node_size=75, node_color=roundInfected, cmap=cmap, vmin=vmin, vmax=vmax)
    
    #Add a colorbar
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=vmin, vmax=vmax))
    sm.set_array([])
    cbar = plt.colorbar(sm, orientation='horizontal')
    cbar.set_label('Round Node was Infected')
    
    #add a title
    plt.title("Number of Nodes: {0}\nNumber of Interactions: {1}\nChance of Infection: {2}".format(NUMBER_OF_NODES, NUMBER_OF_INTERACTIONS, CHANCE_OF_INFECTION))
    plt.axis('off')
    plt.show()
    
def sumUpRoundsInfected(infectedNodes):
    """This function takes information about when all the nodes were infected and returns a dict
        telling how many infections occured in each round. """
    #Determine which round the nodes were infected
    roundInfected = np.zeros(NUMBER_OF_NODES,)
    for key, value in infectedNodes.items():
        roundInfected[key] = value[1]
        
                
    #Create a dict that holds the total number of sums of infected per round
    unique, counts = np.unique(roundInfected, return_counts=True)
    return dict(zip(unique, counts)), roundInfected

    
def iterations(resultsFromIterations):
    """ This function run the entire experiment however many times you tell it to run. """
    for i in range(NUMBER_OF_ROUNDS):
        print("Round {}".format(i))
        #Create the initial graph with NUMBER_OF_NODES
        graph = nx.empty_graph(NUMBER_OF_NODES)
    
        #Determine who the nodes interact with
        nodeInteractions = createInteractions()
        
        #Create a dict of nodes infected so the same node doesnt get infected twice
        infectedNodes = {}
            
        #Key: Node, Value:[Who infected them, which round]
        infectedNodes[PATIENT_ZERO] = [PATIENT_ZERO, 0]
        
        #Create a list telling how many nodes each node infected
        nodeInfectedCount = [1 for _ in range(NUMBER_OF_NODES)] 
    
        #Run the experiment
        runInfection(graph, PATIENT_ZERO, 0, nodeInteractions, infectedNodes, nodeInfectedCount)
        
        #Sum up the number of infections per round
        roundInfo, roundInfected = sumUpRoundsInfected(infectedNodes)
        
        #Save the num infected per round 
        saveToResults(resultsFromIterations, roundInfo)
        
        #Draw the graph
        if DRAW_FINAL_GRAPH:
            drawGraph(graph, roundInfected, infectedNodes)
    
def saveToResults(resultsFromIterations, roundInfo):
    """ This function takes the infection information from each round and adds the number of
        infections in a specific round to a dict that holds infection information about every
        previous iteration. """
    for k,v in roundInfo.items():
        resultsFromIterations[k].append(v)
    
def collectionStats(resultsFromIterations):
    """ This function computes the mean and standard deviation of the number of new infections
        each round. """
    #Populate empty columns with 0 in sumOfRounds
    for k, v in resultsFromIterations.items():
        if not v:
            resultsFromIterations[k].append(0)
            
    mean = [np.mean(v) for k, v in resultsFromIterations.items()]
    sd = [np.std(v) for k, v in resultsFromIterations.items()]
    
    return mean, sd
        

def graphResults(mean, sd):
    """ This function plots two graphs. One of the graphs plots the number of people who have
        become infected with the disease and the number of people who are susceptible to the 
        disease. The other graph plots the mean number of new infections at each round with its 
        standard deviation."""
    rounds = list(range(NUMBER_OF_INTERACTIONS))
    numberInfected = [0 for _ in range(NUMBER_OF_INTERACTIONS - 1)]
    numberSafe = [NUMBER_OF_NODES for _ in range(NUMBER_OF_INTERACTIONS - 1)]
    
    numberSafe = np.array(numberSafe) - np.cumsum(np.array(mean))
    numberInfected = np.array(numberInfected) + np.cumsum(np.array(mean))

    plt.plot(rounds[1:], numberSafe, label="Susceptible")
    plt.plot(rounds[1:], numberInfected, label="Infected")
    plt.ylabel("People")
    plt.xlabel("Number of Interactions")
    plt.title("How Long Does It Take For The Whole Population To Become Infected?")
    plt.legend()
    plt.show()

    plt.errorbar(rounds[1:], mean, sd, linestyle='None', marker='^')
    plt.xlabel("Number of Interactions")
    plt.ylabel("Number of People Infected")
    plt.title("Average Number of New Infections per Round with Standard Deviation")
    plt.show()
        
if __name__ == "__main__":
    #Create a dict that holds the number of infected per each round for all iterations
    resultsFromIterations = dict(zip(range(NUMBER_OF_INTERACTIONS), [[] for _ in range(NUMBER_OF_INTERACTIONS)]))

    #Run number of iterations and save the sum of each infected in each round
    iterations(resultsFromIterations)
    
    #Collection the mean and variance for results of number infected per round
    mean, var = collectionStats(resultsFromIterations)
    
    #Graph the number of infected and the number clean for each round
    graphResults(mean[1:], var[1:]) 
