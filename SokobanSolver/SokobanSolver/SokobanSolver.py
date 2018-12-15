print("Begin program")

# ----- Imports ----------------------------------------------------------------------
from timeit import default_timer as timer

import copy

# ----- Variables and lists -----------------------------------------------------------------------

Openlist = []           # A list containing the notes which hasn't yet been searched. They all don't have children.
GoalList = []           # List containg the coordinates of all goals found in the map.
BoxList = []            # List with the box-coordinates found on the map.
BoxOnGoal = []          # List containing the coordinates on the map where a box is on a goal at start-time.

initMap = []            # The first list the sokobanmap from a txt file is read to. (Most to get it into the program properly).
sokobanMap = []         # Resulting map where boxes and the man has been removed. This map is then used for reference through the solving of the map.
noBoxList = []          # A list containing the coordinates in a map where a box is not allowed to be spushed to. Much like a no flight list but for coordinates.

manCoord = [0,0]        # Man-coordinates can be set here for manually inputting the map (No longer necessary)
iterator = 1            # Iterator for naming nodes.

resultString = ''       # The resulting string which is output as a stream of characters corresponding to the movements needed to solve the map.

WALL = 'X'              # Below is the different characters for naming the structure of a map in the txt file. This can be altered
GOAL = 'G'              # to better fit individual needs.
PLAYER = 'M'
DIAMOND = 'J'
FLOOR = '.'
NOTHING = ' '
BOXANDGOAL = 'O'

LEFT = 'l'              # Directions for the outputstring as the different characters. Further below is the capitals for box-moves so it can be differentiatet
DOWN = 'd'              # between when the man or robot is pushing a box or not.
RIGHT = 'r'
UP  = 'u'

LEFTCAPITAL = 'L'
DOWNCAPITAL = 'D'
RIGHTCAPITAL = 'R'
UPCAPITAL = 'U'

DEAD = 0                # Name for child-notes which are repetitions of earlier states

GOALREACHED = False     # A variable which is set to True when all boxes are moved to a goal which signifies the goal state.
GOALID = 0

X = 1                   # Variables which aren't used.
Y = 0
VERTICAL = False
HORIZONTAL = True

hashTable = {} # Hashtable for holding the sorted positions of boxes


# ----- Classes -------------------------------------------------------------------------

class Node:             # The node class for storage of the state of the map with the corresponding direction and relatio to parent and children (if any).
    def __init__(self, name, direction, coord, boxCoord, nGoal, parent = None):
        self.name = name
        self.direction = direction
        self.coord = coord
        self.boxCoord = boxCoord
        self.nGoal = nGoal
        self.up = None
        self.left = None
        self.down = None
        self.right = None
        self.parent = parent

    def isRoot(self):       # Function to test if a node is the root node.
        if self.parent == None:
            return not self.parent
        else:
            return False

    def isLeaf(self):       # Function to test whether a note has children or not. If it has children it is therefore not a leaf.
        return not ( self.left or self.right or self.down or self.up)

    def hasAllChildren(self): # Function very much like isLeaf().
        return (self.left and self.right and self.down and self.up)

    def getName(self):      # Function to get the name of the node.
        return self.name

    def getCoord(self):         # Function to get the coordinates of said note.
        return self.coord

    def getboxList(self):       # Function to get the boxcoordinates for the node.
        return self.boxCoord


    def createChildren(self):       # Function to make the children of a given node. This function makes children in the order: 
                                    # Left -> Down -> Right -> Up and checks if it is a viable child. If not the node "Dies".
        global GOALREACHED          # The global is used to make the variable or list with a global property so the resultsring 
                                    # is not initialized here but the global list used.
        global GOALID
        global resultString

        if self.isLeaf():           # Check the node whether it is a leaf. Only leafs should be created children from since it makes all directions at the same time
            for i in range(0,4):    # For loop to go through the four directions and make the functionality more streamlined by not having a block for each direction 
                if i == 0:          # but rather have one single block with different variables each time it runs.
                    direc = LEFT
                    ddx = 0
                    ddy = -1
                elif i == 1:
                    direc = DOWN
                    ddx = +1
                    ddy = 0
                elif i == 2:
                    direc = RIGHT
                    ddx = 0
                    ddy = +1
                elif i == 3:
                    direc = UP
                    ddx = -1
                    ddy = 0
                temp = Node(getNameForNode(),direc,[None,None],[None],self.nGoal,self)  # Make a temporary child node.

                tempBoxCoordinate = list(self.getboxList().copy())      # Deep copy the list instead of just pointing to the same place in memory.
                tempBoxCoordinate = [x[:] for x in self.getboxList()]   # make sure to make a deep copy
                
                illegal,isGoal,boxPush = isIllegalMove(self.coord,direc,self.boxCoord)  # Check isIllegalMove
                if illegal:                                                             # Kill children which are illegal fast to save time
                    if i == 0:
                        self.left = DEAD
                    elif i == 1:
                        self.down = DEAD
                    elif i == 2:
                        self.right = DEAD
                    elif i == 3:
                        self.up = DEAD
                elif not boxPush and isOppositeMove(self.direction,temp.direction) and not illegal: # Kill child-moves which are opposite of their parent and don't move a box
                    if i == 0:                                                                      # since this doesn't change the state of the map.
                        self.left = DEAD
                    elif i == 1:
                        self.down = DEAD
                    elif i == 2:
                        self.right = DEAD
                    elif i == 3:
                        self.up = DEAD
                elif not illegal:       # if legal give the nodes man- and box coordinates corresponding to the parent and the move.
                    tempCoordList = list(self.getCoord().copy())
                    temp.coord[0] = tempCoordList[0] + ddx
                    temp.coord[1] = tempCoordList[1] + ddy
                    temp.boxCoord = tempBoxCoordinate[:]
                    if isGoal:    
                        temp.nGoal +=1
                    if boxPush:         # if a box is pushed update the coordinate of that box in the given direction
                        if temp.coord in tempBoxCoordinate:
                            indexOfBox = tempBoxCoordinate.index(temp.coord)
                            temp.boxCoord[indexOfBox][0] = temp.boxCoord[indexOfBox][0] + ddx
                            temp.boxCoord[indexOfBox][1] = temp.boxCoord[indexOfBox][1] + ddy
                        if sokobanMap[temp.coord[0]][temp.coord[1]] == GOAL: # If a box is moved away from a goal decrement the amount of goals reached in that node.
                            temp.nGoal -= 1
                        if i == 0:
                            temp.direction = LEFTCAPITAL
                        elif i == 1:
                            temp.direction = DOWNCAPITAL
                        elif i == 2:
                            temp.direction = RIGHTCAPITAL
                        elif i == 3:
                            temp.direction = UPCAPITAL
                    if i == 0:              # Input the direction to the coresponding place among child-nodes
                        self.left = temp
                    elif i == 1:
                        self.down = temp
                    elif i == 2:
                        self.right = temp
                    elif i == 3:
                        self.up = temp

                    tempcoord1 = [temp.coord]
                    tempListState = tempcoord1 + temp.boxCoord
                    inserted = False
                    inserted = insertInHashtable(hashTable,temp.name,hashing(tempListState))
                    if inserted: # only insert a node on the Openlist if it is inserted in the hashtable
                        Openlist.append(temp)
                    if temp.nGoal == len(BoxList): # if the amount of boxes on goals matches the length of the goalList recognise this as the goal state.
                        GOALREACHED = True
                        GOALID = temp.name
                        outputListOfMoves(temp)
                else:                       # if every check fails the node should not be recognised as a viable option and therefore should be dead:
                    if i == 0:
                        self.left = DEAD
                    elif i == 1:
                        self.down = DEAD
                    elif i == 2:
                        self.right = DEAD
                    elif i == 3:
                        self.up = DEAD
                


class Tree:         # Tree class not implementet properly
     def __init__(self):
         self.root = None
         self.size = 0

     def length(self):
         return self.size

     def insert(self, direction):
         return 0


# ----- Hash functions -------------------------------------------------------------------------

def hashing(listoflist): # Makes the hashvalue for an input list
    hashval = 0
    for i in listoflist:
        for j in i:
            hashval = hashval * 191 + j

    return hashval

def insertInHashtable(hashtable, listoflists, key): # Inserts the given list on the key position in a hashtable. The function outputs true or false if the place is vacant or free.
    if not hashtable.get(key):
        hashtable[key] = listoflists
        return True
    else:
        #print('overwrite', listoflists, key)
        return False


# ----- Map functions -----------------------------------------------------------------------

def readMap(nameOfFile): #Reads the map and outputs the layout to a list of strings and to the terminal. 
    print("Reading the map")

    testMapObject = open(nameOfFile+(".txt"))
    tempList = []
    for line in testMapObject:
        tempList = []
        for elem in range(len(line)-1):
            tempList.append(line[elem])
        initMap.append(tempList)    
        print (line,end = "")



def visualizeMap(aMap): # Function which runs through the map and outputs it to the console
    for i in range(len(aMap)):
        for j in range(len(aMap[i])):
            print(aMap[i][j],end="")
        print("\n",end="")
    print("\n")


def visualizeMap2(aMap): # Function which runs through the map and outputs it to the console
    for i in aMap:
        print(i)

def copyCleanMap(outputMap): # Function to read to map into a format to make it a reference map.
    mCoord=[]
    for i in range(len(outputMap)):
        for j in range(len(outputMap[i])):
            if outputMap[i][j] == GOAL: # Check the tile for goals
                GoalList.append([i,j])
            elif outputMap[i][j] == PLAYER: # Check the tile for the player
                print(i,j)
                mCoord = [i,j]
                outputMap[i][j] = FLOOR
            elif outputMap[i][j] == DIAMOND: # Check the tile for Diamonds
                BoxList.append([i,j])
                outputMap[i][j] = FLOOR
            elif outputMap[i][j] == BOXANDGOAL: # Check the tile for goals with boxes on them
                BoxOnGoal.append([i,j])
                GoalList.append([i,j])
                BoxList.append([i,j])
                outputMap[i][j] = GOAL
    return outputMap, mCoord
        

def goalMoveCheck(Map,coord,VH):
    # VH should describe whether the check should be vertical or horizontal 
    #   0 = vertical
    #   1 = horizontal#
    goalSeen = False
    if VH: # HORIZONTAL
        # check in both dir if a goal is visible
        for x in range(coord[X], len(Map[coord[Y]])): # check right
            if Map[coord[Y]][x] is GOAL:
                goalSeen = True
                break
            elif Map[coord[Y]][x] is WALL:
                break

        for x in range(coord[X],0): # check left
            if Map[coord[Y]][x] is GOAL:
                goalSeen = True
                break
            elif Map[coord[Y]][x] is WALL:
                break
    elif not VH: # VERTICAL
        # check in both dir if a goal is visible
        for y in range(coord[Y], len(Map)): # check down
            if Map[y][coord[X]] is GOAL:
                goalSeen = True
                break
            elif Map[y][coord[X]] is WALL:
                break

        for y in range(coord[Y],0): # check up
            if Map[y][coord[X]] is GOAL:
                goalSeen = True
                break
            elif Map[y][coord[X]] is WALL:
                break
    return goalSeen


def getNeighbouringWalls(map, coord):
    # returns the neighbours of 4-way neighbour-check 
    # The function fails if the coordinate does not have 4 neighbors 
    # 
    # 4-way check:
    #  4
    # 1X3
    #  2
    tempList = []
    
    if map[coord[0]][coord[1]-1] == WALL:
        tempList.append('LEFT')
    if map[coord[0]+1][coord[1]] == WALL:
        tempList.append('DOWN')
    if map[coord[0]][coord[1]+1] == WALL:
        tempList.append('RIGHT')
    if map[coord[0]-1][coord[1]] == WALL:
        tempList.append('UP')
    return tempList

def checkCorners(map,coord):
    #returns true if the player tries to push a box into a corner in a four connected mannor
    # 4-way check:
    #  4
    # 1X3
    #  2
    counter1 = 0
    counter2 = 0
    counter3 = 0
    counter4 = 0
    if map[coord[0]][coord[1]-1] == WALL:
            counter1 += 1
    if map[coord[0]+1][coord[1]] == WALL:
            counter2 += 1
    if map[coord[0]][coord[1]+1] == WALL:
            counter3 += 1
    if map[coord[0]-1][coord[1]] == WALL:
            counter4 += 1
    #upper left corner:
    if counter1 and counter4:
        return True
    #Upper right
    elif counter4 and counter3:
        return True
    #Lower right
    elif counter3 and counter2:
        return True
    #Lower left
    elif counter1 and counter2:
        return True
    else:
        return False



def makeNoBoxList(Map):
    # @ Map         : The game map described in a list of lists, where every element in the inner most list contains is a single character. 
    #                       This character can be either GOAL, FLOOR, WALL or NOTHING 
    # #

    # Go through the map and find the corners which can't be put boxes into
    retList =[]
    for x in range(1,len(Map)-1):
        for y in range(1,len(Map[x])-1):
            if Map[x][y] != WALL:
                nWallsInNeighbourhood = len(getNeighbouringWalls(Map,[x , y]))
                if checkCorners(Map,[x , y]) and Map[x][y] != GOAL:
                    retList.append([x,y])

    # Find horisontal walls which do not have any goals
    commonDirection = 0
    # Search all elements in the list and find pairs of corners
    xMax = len(retList)
    yMax = len(retList)

    for x in range(0,xMax):
        for y in range(0,yMax):
            tempRetList=[]
            if retList[x][0] == retList[y][0] and x != y :
                Walls1 = getNeighbouringWalls(Map,[retList[x][0],retList[x][1]])
                Walls2 = getNeighbouringWalls(Map,[retList[y][0],retList[y][1]])
                # Try to connect the corners
                if len(Walls1) >= len(Walls2):
                    for i in range(len(Walls2)):
                        if Walls2[i] in Walls1:
                            commonDirection = Walls2[i]
                else:
                    for i in range(len(Walls1)):
                        if Walls1[i] in Walls2:
                            commonDirection = Walls1[i]
                #If they don't have a goal and share 1 wall
                #Put all points along that line on retList
                distanceBetweenCorners=0
                for i in range(1,retList[y][1]-retList[x][1]):
                    distanceBetweenCorners = retList[y][1]-retList[x][1]-1
                    walls = getNeighbouringWalls(Map,[retList[x][0],retList[x][1]+i])
                    if (commonDirection in walls) and Map[retList[x][0]][retList[x][1]+i] == FLOOR:
                        tempRetList.append([retList[x][0],retList[x][1]+i])
                if len(tempRetList) == distanceBetweenCorners:
                    retList += tempRetList


    for x in range(0,xMax):
        for y in range(0,yMax):
            tempRetList=[]
            if retList[x][1] == retList[y][1] and x != y :
                Walls1 = getNeighbouringWalls(Map,[retList[x][0],retList[x][1]])
                Walls2 = getNeighbouringWalls(Map,[retList[y][0],retList[y][1]])
                # Try to connect the corners
                if len(Walls1) >= len(Walls2):
                    for i in range(len(Walls2)):
                        if Walls2[i] in Walls1:
                            commonDirection = Walls2[i]
                else:
                    for i in range(len(Walls1)):
                        if Walls1[i] in Walls2:
                            commonDirection = Walls1[i]
                #If they don't have a goal and share 1 wall
                #Put all points along that line on retList
                for i in range(1,retList[y][0]-retList[x][0]):
                    distanceBetweenCorners = retList[y][0]-retList[x][0]-1
                    walls = getNeighbouringWalls(Map,[retList[x][0]+i,retList[x][1]])
                    if (commonDirection in walls) and Map[retList[x][0]+i][retList[x][1]] == FLOOR:
                        tempRetList.append([retList[x][0]+i,retList[x][1]])
                if len(tempRetList) == distanceBetweenCorners:
                    retList += tempRetList    #        #Do the same for vertical lines


    return retList

# ----- Random functions ----------------------------------------------------------------------
def li():
    print('--------------------------------------------------------')

def outputListOfMoves(self): # function to make the resulting string from the solver.
    # It functions by getting the node which is a goal. From there traverse through all the parents
    # to the root node and output the directions on the nodes. This gives an inversed list
    # which later has to be turned around.
    global resultString
    #resultString += self.direction
    while self.isRoot:
        print(self.getCoord())
        resultString += self.direction
        self = self.parent
        if self.direction == 'init':
            break

def getNeighboursContent(Map, coord):
    # returns the neighbours of 4-way neighbour-check 
    # The function fails if the coordinate does not have 4 neighbors 
    # 
    # 4-way check:
    #  4
    # 1X3
    #  2
    returnList = []
    returnList.append(Map[coord[0]][coord[1]-1]) # 1
    returnList.append(Map[coord[0]+1][coord[1]]) # 2
    returnList.append(Map[coord[0]][coord[1]+1]) # 3
    returnList.append(Map[coord[0]-1][coord[1]]) # 4

    return returnList



def sortCoord(listoflists): 
    #It will first sort on the y value and if that's equal then it will sort on the x value. 
    #I would also advise to not use list as a variable because it is a built-in data structure.
    temp = sorted(listoflists , key=lambda k: [k[5], k[1]])
    return temp


def getNameForNode(): # Function to name nodes in an incrementally manner.
    global iterator
    iterator+=1
    return iterator-1

def isOppositeMove(parentDir,childDir): # Checks whether the current direction is the direct opposite of the last (parent) direction.
    if parentDir == LEFT and childDir == RIGHT:
        return True
    if parentDir == DOWN and childDir == UP:
        return True
    if parentDir == RIGHT and childDir == LEFT:
        return True
    if parentDir == UP and childDir == DOWN:
        return True
    else:
        return False
     

def isIllegalMove(coord, dir, boxList): # Returns two variables: first being illegal move, Second being whether the diamond is placed on a goal
    # This function takes the current map as a reference for box positions but this should be changed to the list with box coordinates
    # The third being if a DIAMOND has been moved
    x = coord[0]
    y = coord[1]

    dx = 0
    dy = 0

    if dir == LEFT:
        dy = -1
    elif dir == DOWN:
        dx = 1
    elif dir == RIGHT:
        dy = 1
    elif dir == UP:
        dx = -1
    someCoordinate = [[x + dx,y + dy]]
    if ([x + dx,y + dy]) in boxList:
        if ([x + (2 * dx) , y + (2 * dy)]) not in noBoxList:
            if ([x + (2 * dx) , y + (2 * dy)]) in boxList:
                return True, None, None
            elif sokobanMap[x + (2 * dx)][y + (2 * dy)] == GOAL:
                return False, True, True               #Returns legal 
            elif sokobanMap[x + (2 * dx)][y + (2 * dy)] == FLOOR:
                return False, False,True
            else: 
                return True, None, None
        else:
            return True, None, None
    else:
        if sokobanMap[x + dx][y + dy] == FLOOR or sokobanMap[x + dx][y + dy] == GOAL:
            return False, False, False
        else:
            return True, None, None


# ----- Program ------------------------------------------------------------------------
li()
start1 = timer()
readMap('aMap')
#readMap("testMap12")
#readMap("testMap11")   # Read the competition map
print("\n")

sokobanMap = initMap[:][:]
print('initMap')
visualizeMap2(initMap)
print('sokobanMap')
visualizeMap2(sokobanMap)
# For manual input:
sokobanMap,manCoord = copyCleanMap(sokobanMap)

countGoals = len(BoxOnGoal)
            
li()  
print('initMap')
visualizeMap2(initMap)
print('sokobanMap')
visualizeMap2(sokobanMap)
li()
# For automatic
print('initial coordinates')
print('List of Goals: ',GoalList)
print('List of Boxes: ',BoxList)
print('Man-coordinates: ',manCoord)
print('Amount of boxes already on goal: ',countGoals)



li()
print('check noBoxList')
noBoxList = makeNoBoxList(sokobanMap)


print(noBoxList)

li()
print('test of first node in tree')

root = Node(getNameForNode(),'init',manCoord,BoxList,countGoals)
print('root name: ',root.getName())
tempListStateRoot = [root.coord]+BoxList
print('root info: ',tempListStateRoot)

li()
print("Hashing root")
insertInHashtable(hashTable,root.name,hashing(tempListStateRoot))
insertInHashtable(hashTable,root.name,hashing(tempListStateRoot))


print(root.name, root.hasAllChildren(),root.direction,root.isLeaf(),root.left, root.isRoot())


mytree = Tree()

mytree = root
Openlist.append(root)


li()
print('begin solving')
print('Name of the first element on Openlist: ', Openlist[0].name)
stop1 = timer()
start2 = timer()
counterForCounts = 0
while len(Openlist):
    counterForCounts += 1
    #for p in range(len(Openlist)):
    #    print(Openlist[p].name,end=', ')
    Openlist[0].createChildren()
    if GOALREACHED:
        print('Done - GOAL REACHED')
        print('path')
        #while:
        break
    else:
        if counterForCounts%1000==1:
            print('Length on Openlist: ',len(Openlist),'  Nodes on Openlist:  ',end='')
            print('Goal not reached')
    Openlist.pop(0)
end = timer()
    
   
li()
print('done solving hashTable:')
print(len(hashTable))


li()

print('output string - number of moves:',len(resultString),'  ' , resultString[::-1])
li()
print('Time elapsed in seconds: ', end - start1) # Time in seconds, e.g. 5.38091952400282
print('Time spent preprocessing: ',stop1- start1 )
print('Time spent solving the resulting map', end- start2)
