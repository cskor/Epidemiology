from matplotlib import pyplot as plt
import networkx as nx
import random

NUMBER_OF_NODES = 50
NUMBER_OF_INTERACTIONS = 20
CHANCE_OF_INFECTION = 0.4
PATIENT_ZERO = 0

def createInteractions(graph):
    """ This function randomly selects numInteraction nodes for each node to 
        interact with within the graph """
    nodeInteractions = {}
        
    #For each node, randomly select numIteraction nodes for them to interact with
    for node in range(graph.number_of_nodes()):
        #Create a random list of nodes that the graph interacts with
        iteractions = random.sample(range(graph.number_of_nodes()), NUMBER_OF_INTERACTIONS)
        
        #Keep randomly creating lists if the node is in its connections
        while(node in iteractions):
            iteractions = random.sample(range(graph.number_of_nodes()), NUMBER_OF_INTERACTIONS)
        
        #Add node to nodeIteractions
        nodeInteractions[node] = iteractions
    
    return nodeInteractions

def runInfection(graph, infectedNode, index, nodeInteractions, listOfInfected, nodeInfectedCount):
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
                if index < indexInfectedOn:
                    #Remove the old edge
                    graph.remove_edge(alreadyInfectedNode, node)
                    
                    #Remove the infected count
                    nodeInfectedCount[alreadyInfectedNode] -= 1
                    
                    #Add the new edge
                    graph.add_edge(infectedNode, node)
                    
                    #Save info to listOfInfected
                    listOfInfected[node] = [infectedNode, interactions.index(node) + index + 1]
                    
                    #Add to the infected count of the node
                    nodeInfectedCount[infectedNode] += 1
            else:
            #This node has not already been infected
                #Add the new edge
                graph.add_edge(infectedNode, node)
                    
                #Save info to listOfInfected
                listOfInfected[node] = [infectedNode, interactions.index(node) + index + 1]
                
                #Add to the infected count of the node
                nodeInfectedCount[infectedNode] += 1
            
            #Call function again on this newly infected node
            runInfection(graph, node, interactions.index(node) + index + 1, nodeInteractions, listOfInfected, nodeInfectedCount)
    
def drawGraph(graph, nodeColor):
    cmap = plt.cm.YlOrRd
    vmin=0
    vmax = max(nodeColor)
    #Draw the nodes and edges
    nx.draw_networkx(graph, pos=nx.spring_layout(graph, k=0.3), with_labels=False, node_size=75, node_color=nodeColor, cmap=cmap, vmin=vmin, vmax=vmax)
    
    #Add a colorbar
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=vmin, vmax=vmax))
    sm.set_array([])
    cbar = plt.colorbar(sm, orientation='horizontal', pad=0.2)
    cbar.set_label('Round Node was Infected')
    
    #add a title
    plt.title("Number of Nodes: {0}\nNumber of Interactions: {1}\nChance of Infection: {2}".format(NUMBER_OF_NODES, NUMBER_OF_INTERACTIONS, CHANCE_OF_INFECTION))
    plt.axis('off')
    plt.show()
            
if __name__ == "__main__":
    #Create the initial graph with NUMBER_OF_NODES
    graph = nx.empty_graph(NUMBER_OF_NODES)
    
    #Determine who the nodes interact with
    nodeInteractions = createInteractions(graph)
    
    #Create a dict of nodes infected so the same node doesnt get infected twice
    infectedNodes = {}
    
    #Key: Node, Value:[Who infected them, which round]
    infectedNodes[PATIENT_ZERO] = [PATIENT_ZERO, 0]
    
    #Create a list telling how many nodes each node infected
    nodeInfectedCount = [1] * NUMBER_OF_NODES
    
    #Run the experiment
    runInfection(graph, PATIENT_ZERO, 0, nodeInteractions, infectedNodes, nodeInfectedCount)
    
    #Determine which round the nodes were infected
    roundInfected = [0] * NUMBER_OF_NODES
    for key, value in infectedNodes.items():
        roundInfected[key] = value[1]
            
    #Draw the graph
    drawGraph(graph, roundInfected)
