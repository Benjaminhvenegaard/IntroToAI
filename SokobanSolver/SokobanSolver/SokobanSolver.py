print("Begin program")

# ----- Classes -------------------------------------------------------------------------

class Node:
    def __init__(self, name):
        self.name = name

# ----- Variables -----------------------------------------------------------------------

sokobanMap = []



# ----- Functions -------------------------------------------------------------------------

def readMap(nameOfFile): #Reads the map and outputs the layout to a list of strings and to the terminal. 
    print("Reading the map")

    testMapObject = open(nameOfFile+(".txt"))
    tempList = []
    for line in testMapObject:
        tempList = []
        for elem in range(len(line)-1):
            tempList.append(line[elem])
        sokobanMap.append(tempList)    
        print (line,end = "") 

def visualizeMap():
    for i in range(len(sokobanMap)):
        for j in range(len(sokobanMap[i])):
            print(sokobanMap[i][j],end="")
        print("\n",end="")
    print("\n")





# ----- Program ------------------------------------------------------------------------


readMap("testMap")
print("\n")
print(len(sokobanMap[1]))

visualizeMap()


print(".",sokobanMap[0][1],".")
        




