print("Begin program")

# ----- Classes -------------------------------------------------------------------------

class Node:
    def __init__(self, name, direction, coord, nBox, nGoal):
        self.name = name
        self.direction = direction
        self.coord = coord
        self.nBox = nBox
        self.nGoal = nGoal
        self.up = None
        self.left = None
        self.down = None
        self.right = None




# ----- Variables and lists -----------------------------------------------------------------------

Openlist=[]
ClosedList = []

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


def isIllegalMove(x , y,dir):
    if dir == 'u':

    elif dir == 'l':

    elif dir == 'd':

    elif dir == 'r':

def insert(self,data):
    if self.data:




    # Insert method to create nodes
    def insert(self, data):

        if self.data:
            if data < self.data:
                if self.left is None:
                    self.left = Node(data)
                else:
                    self.left.insert(data)
            elif data > self.data:
                if self.right is None:
                    self.right = Node(data)
                else:
                    self.right.insert(data)
        else:
            self.data = data
# findval method to compare the value with nodes
    def findval(self, lkpval):
        if lkpval < self.data:
            if self.left is None:
                return str(lkpval)+" Not Found"
            return self.left.findval(lkpval)
        elif lkpval > self.data:
            if self.right is None:
                return str(lkpval)+" Not Found"
            return self.right.findval(lkpval)
        else:
            print(str(self.data) + ' is found')
# Print the tree
    def PrintTree(self):
        if self.left:
            self.left.PrintTree()
        print( self.data),
        if self.right:
            self.right.PrintTree()









#def move(direction):
    #if direction == "u" or direction == "U":
        



# ----- Program ------------------------------------------------------------------------


readMap("testMap")
print("\n")
print(len(sokobanMap[0]))
print(len(sokobanMap[1]))
print(len(sokobanMap[4]))
visualizeMap()


print(".",sokobanMap[0][1],".")
        

print(sokobanMap[4][0],sokobanMap[4][1],sokobanMap[4][2],end="")

print(sokobanMap[4][3])

root = Node(0,'init',[0,1],1,0)

if root.left == None:
    temp = Node(root.name+1,'l',)
    Openlist.append(Node(root.name+1,'l',))












