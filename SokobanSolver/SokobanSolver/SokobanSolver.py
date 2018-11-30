print("Begin program")

from timeit import default_timer as timer

import copy

# ----- Variables and lists -----------------------------------------------------------------------

Openlist=[]
ClosedList = []
GoalList = []
BoxList = []

initMap = []
sokobanMap = []
noBoxList = []

manCoord = [0,0]
iterator = 1

resultString = ''

WALL = 'X'
GOAL = 'G'
PLAYER = 'M'
DIAMOND = 'J'
FLOOR = '.'
NOTHING = ' '

UP  = 'u'
LEFT = 'l'
DOWN = 'd'
RIGHT = 'r'

DEAD = 0

GOALREACHED = False
GOALID = 0

X = 1
Y = 0
VERTICAL = False
HORIZONTAL = True

hashTable = {} # Hashtable for holding the sorted positions of boxes


# ----- Classes -------------------------------------------------------------------------

class Node:
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

    def isRoot(self):
        if self.parent == None:
            return not self.parent
        else:
            return False

    def isLeaf(self):
        return not ( self.left or self.right or self.down or self.up)

    def hasAllChildren(self):
        return (self.left and self.right and self.down and self.up)

    def getName(self):
        return self.name

    def getCoord(self):
        return self.coord

    def getboxList(self):
        return self.boxCoord


    def createChildren(self):
        global GOALREACHED
        global GOALID
        global resultString

        if self.isLeaf():
            for i in range(0,4):
                if i == 0:
                    ddx = 0
                    ddy = -1
                    direc = LEFT
                elif i == 1:
                    ddx = +1
                    ddy = 0
                    direc = DOWN
                elif i == 2:
                    ddx = 0
                    ddy = +1
                    direc = RIGHT
                elif i == 3:
                    ddx = -1
                    ddy = 0
                    direc = UP
                temp = Node(getNameForNode(),direc,[None,None],[None],self.nGoal,self)

                tempBoxCoordinate = list(self.getboxList().copy())
                tempBoxCoordinate = [x[:] for x in self.getboxList()]
                
                illegal,isGoal,boxPush = isIllegalMove(self.coord,direc,self.boxCoord)
                if not illegal:
                    tempCoordList = list(self.getCoord().copy())
                    temp.coord[0] = tempCoordList[0] + ddx
                    temp.coord[1] = tempCoordList[1] + ddy
                    temp.boxCoord = tempBoxCoordinate[:]
                    if isGoal:    
                        temp.nGoal +=1
                    if boxPush:
                        if temp.coord in tempBoxCoordinate:
                            indexOfBox = tempBoxCoordinate.index(temp.coord)
                            temp.boxCoord[indexOfBox][0] = temp.boxCoord[indexOfBox][0] + ddx
                            temp.boxCoord[indexOfBox][1] = temp.boxCoord[indexOfBox][1] + ddy
                        if sokobanMap[temp.coord[0]][temp.coord[1]] == GOAL:
                            temp.nGoal -= 1
                    
                    if i == 0:
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
                    if inserted:
                        Openlist.append(temp)
                        print(tempListState)
                    if temp.nGoal == len(BoxList):
                        GOALREACHED = True
                        GOALID = temp.name
                        outputListOfMoves(temp)
                
                else:
                    if i == 0:
                        self.left = DEAD
                    elif i == 1:
                        self.down = DEAD
                    elif i == 2:
                        self.right = DEAD
                    elif i == 3:
                        self.up = DEAD


class Tree:
     def __init__(self):
         self.root = None
         self.size = 0

     def length(self):
         return self.size

     def insert(self, direction):
         return 0


# ----- Hash functions -------------------------------------------------------------------------

def hashing(listoflist):
    hashval = 0
    for i in listoflist:
        for j in i:
            hashval = hashval * 191 + j

    return hashval

def insertInHashtable(hashtable, listoflists, key):
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



def visualizeMap(aMap):
    for i in range(len(aMap)):
        for j in range(len(aMap[i])):
            print(aMap[i][j],end="")
        print("\n",end="")
    print("\n")


def visualizeMap2(aMap):
    for i in aMap:
        print(i)

def copyCleanMap(outputMap):
    mCoord=[]
    for i in range(len(outputMap)):
        for j in range(len(outputMap[i])):
            if outputMap[i][j] == GOAL:
                GoalList.append([i,j])
            elif outputMap[i][j] == PLAYER:
                print(i,j)
                mCoord = [i,j]
                outputMap[i][j] = FLOOR
            elif outputMap[i][j] == DIAMOND:
                BoxList.append([i,j])
                outputMap[i][j] = FLOOR
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
    counter = 0
    if map[coord[0]][coord[1]-1] == WALL:
            counter += 1
    if map[coord[0]+1][coord[1]] == WALL:
            counter += 1
    if map[coord[0]][coord[1]+1] == WALL:
            counter += 1
    if map[coord[0]-1][coord[1]] == WALL:
            counter += 1
    return counter

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

    # Go through the map
    retList =[]
    for x in range(1,len(Map)-1):
        for y in range(1,len(Map[x])-1):
            nWallsInNeighbourhood = getNeighbouringWalls(Map,[x , y])
            if checkCorners(Map,[x , y]) and Map[x][y] != GOAL:
                retList.append([x,y])
            
            
            

            







        #    if Map[y][x] is not WALL and Map[y][x] is not NOTHING:
        #        # If the current coord is not the player
        #        # If the current coord is a deadlock pos (DEADLOCK = DL)
        #        nCont = getNeighboursContent(Map, [y,x])
        #        count = 0
        #        for i in nCont:
        #            if i is WALL:
        #                count += 1

                    
        #        # If goal append to list - All goal are eligable
        #        if Map[y][x] is GOAL:
        #            retList.append([y,x])

        #        else:
        #            # DL check 1 : endWall with goal
        #            print(count, y,x)
        #            if count < 2:
        #                if y is len(Map)-2 or y is 1:
        #                    if goalMoveCheck(Map,[y,x], HORIZONTAL):
        #                        retList.append([y,x])

        #                elif x is len(Map[y])-2 or x is 1: # -1 would be a wall
        #                    if goalMoveCheck(Map,[y,x], VERTICAL):
        #                        retList.append([y,x])

        #                else:
        #                    retList.append([y,x])

    return retList

# ----- Random functions ----------------------------------------------------------------------
def li():
    print('--------------------------------------------------------')

def outputListOfMoves(self):
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


def getNameForNode():
    global iterator
    iterator+=1
    return iterator-1


def isIllegalMove(coord, dir, boxList): # Returns two variables: first being illegal move, Second being whether the diamond is placed on a goal
    # This function takes the current map as a reference for box positions but this should be changed to the list with box coordinates
    # The third being if a DIAMOND has been moved
    x = coord[0]
    y = coord[1]

    dx = 0
    dy = 0

    if dir == LEFT:
        dy = -1
    elif dir == RIGHT:
        dy = 1
    elif dir == UP:
        dx = -1
    elif dir == DOWN:
        dx = 1
    someCoordinate = [[x + dx,y + dy]]
    if ([x + dx,y + dy]) in boxList:
        if ([x + (2 * dx) , y + (2 * dy)]) not in noBoxList:
            if ([x + (2 * dx) , y + (2 * dy)]) in boxList:
                return True, None, None
            elif sokobanMap[x + (2 * dx)][y + (2 * dy)] == GOAL:
                return False, True, True               #Returns legal 
            elif sokobanMap[x + (2 * dx)][y + (2 * dy)] == FLOOR:# and sokobanMap[x + (2 * dx)][y + (2 * dy)] in eligibleCoordList:
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
readMap("CompetitionMap")
#readMap("testMap3")   # Read the competition map
print("\n")

sokobanMap = initMap[:][:]
print('initMap')
visualizeMap2(initMap)
print('sokobanMap')
visualizeMap2(sokobanMap)
sokobanMap,manCoord = copyCleanMap(sokobanMap)
            
li()   # todo : fix initMap
print('initMap')
visualizeMap2(initMap)
print('sokobanMap')
visualizeMap2(sokobanMap)
li()
# For manual input:
#BoxList = []
#BoxList = [[2,2],[2,3]]
#GoalList = []
#GoalList = [[2,1],[2,3]]
#manCoord = []
#manCoord = [1,1]
# For automatic
print('initial coordinates')
print(GoalList)
print(BoxList)
print(manCoord)



li()
print('check eligible Coords')
noBoxList = makeNoBoxList(sokobanMap)

print(noBoxList)
li()
print('test of first node in tree')
#rootBoxList = BoxList.copy()
root = Node(getNameForNode(),'init',manCoord,BoxList,0)

tempListStateRoot = [root.coord]+BoxList


li()
print("Hashing root")
insertInHashtable(hashTable,root.name,hashing(tempListStateRoot))
insertInHashtable(hashTable,root.name,hashing(tempListStateRoot))


print(root.name, root.hasAllChildren(),root.direction,root.isLeaf(),root.left, root.isRoot())


mytree = Tree()

mytree = root
Openlist.append(root)
#
#li()
#print('test the tree structure')
#print(root.isLeaf())

#print(isIllegalMove(root.coord,LEFT))

#print('open list ', Openlist)

#root.createChildren()

#print('length of open list', len(Openlist))

#for i in Openlist:
#    print(i.coord)
  
#print(hashTable)
li()
print('begin solving')
start = timer()
while len(Openlist):
    print(Openlist[0].name, len(Openlist))
    Openlist[0].createChildren()
    if GOALREACHED:
        print('Done - GOAL REACHED')
        print('path')
        #while:
        break
    else:
        print('Goal not reached')
    Openlist.pop(0)
end = timer()
    
# ...

    
li()
print('done solving hashTable:')
print(len(hashTable))


li()

print('output string - number of moves:',len(resultString),'  ' , resultString[::-1])
li()
print('Time elapsed: ', end - start) # Time in seconds, e.g. 5.38091952400282





