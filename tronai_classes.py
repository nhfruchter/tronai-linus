import resource, math, random

class AIBase(object):
    """A base class for all Tron AIs that implements a lot of standard features.
    To create your own AI, simply implement the play() function, which returns a direction.
    Your AI's __init__ class should probably use super(), also.
    """
    def __init__(self, board):
        # Board state
        self.board = board
        self.playerPos = None
        self.opponentPos = None
        self.legal = []
        
        # Board tokens
        self.PLAYER = "@"
        self.OPPONENT = "A"
        self.EMPTY = "."
        self.FULL = "X"
        
        # Directions 
        self.LEFT = "a"
        self.RIGHT = "d"
        self.UP = "w"
        self.DOWN = "s"
        self.VECTOR_MAP = {"w":(0,-1), "a":(-1,0), "s":(0,1), "d":(1,0)}

    def vectorize(self, direction):
        """Converts a wasd direction to a vector."""
        if direction in self.VECTOR_MAP:
            return self.VECTOR_MAP[direction] 
        else:
            return False    
        
    def findToken(self, token=None):
        """Finds the x,y location of a given token on the board. Defaults to player."""
        token = token or self.PLAYER # instance methods don't like defaults
        oldPos = None
        for x in xrange(len(self.board)):
            for y in xrange(len(self.board[0])):
                if self.board[x][y] == token:
                    oldPos = (x, y)
        return oldPos    
        
    def vsum(self, a, b):
        # SO MUCH PYTHON
        return map(sum, zip(a, b)) 
        
    def findLegal(self):
        """Gets all legal moves from current state."""
        # Now, loop over all possible directions.
        possibleDirections = []
        for dirLetter, vector in self.VECTOR_MAP.iteritems():
            # Calculate your new x and y coordinates
            newx, newy = self.vsum(self.playerPos, vector) 
            # And check to see if the target square is empty.
            if self.board[newx][newy] == self.EMPTY:
                possibleDirections.append(dirLetter)
        self.legal = possibleDirections    
        
    def play(self):
        raise Exception("I didn't read the instructions.")
        

class RandomMover(AIBase):
    def __init__(self, board):
        super(RandomMover, self).__init__(board)
        
    def update(self):
        """Runs every time the game state updates and changes 
        the AI's internal state to reflect the new game state."""
        self.playerPos = self.findToken(self.PLAYER)
        self.findLegal()
        
    def play(self):
        self.update()
        if self.legal != []:
            from random import choice
            return choice(self.legal)
        else:
            return "w"   

# Here is an "AI" which just asks you which way to move every turn.

class Human(AIBase):
    def __init__(self, board):
        super(Human, self).__init__(board)
    
    def play(self):
        return raw_input("w, a, s, or d? > ")


class AIOne(AIBase):
    def __init__(self, board):
        super(AIOne, self).__init__(board)
        self.timeForRandom = random.randint(1, 5)
        
    def update(self):
        """Runs every time the game state updates and changes 
        the AI's internal state to reflect the new game state."""
        self.playerPos = self.findToken(self.PLAYER)
        self.opponentPos = self.findToken(self.OPPONENT)
        self.findLegal()

    def distance(self, a, b):
        x0, y0, x1, y1 = tuple(a) + tuple(b)
        return math.sqrt((x1-x0)**2 + (y1-y0)**2)
        
    def randomMove(self):
        if len(self.legal) != 0:
            return random.choice(self.legal)
        else:
            return "w"   
        
    def play(self):    
        self.update()
        if self.opponentPos == None and self.legal != []:
            return random.choice(self.legal)
        dists = {}
        for move in self.legal:
            d = self.distance(self.vsum(self.playerPos, self.vectorize(move)), self.opponentPos)
            dists[d] = move
            
        if dists != {}:
            maximizeDistance = dists[max(dists)]
        else:
            return "w"
                
        sysinfo = resource.getrusage(resource.RUSAGE_SELF)
        
        if sysinfo.ru_utime >= self.timeForRandom:
            return self.randomMove()
        else:    
            weight = math.floor((1 - 1/(self.timeForRandom - sysinfo.ru_utime))*100)                
            if 0 <= weight <= random.randint(0, 100):
                return self.randomMove()
            else:
                return maximizeDistance    

#############################
#
# Below lies a tangled mess of game code! Warning! Do not touch!
#
#############################

from copy import deepcopy

class Board(object):
    def __init__(self, X, Y):
        self.X = X
        self.Y = Y
        self.board = [["." for i in xrange(Y)] for j in xrange(X)]
        for x in xrange(X):
            for y in xrange(Y):
                if x in [0,X-1] or y in [0,Y-1]:
                    self.board[x][y] = "xB"
        self.players = {1:[1,1], 2:[X-2,Y-2]}

    def toString(self):
        board = deepcopy(self.board)

        for P in self.players:
            player = self.players[P]
            board[player[0]][player[1]] = P
            
        # because I screwed with X and Y
        board = zip(*board)
        
        def squareToChar(sq):
            if sq == ".": return "."
            if sq[0] == "x": return "x"
            return chr(ord("A")+sq-1)
    
        string = ""
        for row in xrange(len(board)):
            for col in xrange(len(board[0])):
                string += squareToChar(board[row][col])
            string += "\n"
        return string[:-1]

    def stringOutputForAI(self, P):
        '''string output for a non-Python program.'''
        s = self.toString()
        # Replace your own player with "@"
        s.replace(chr(ord("A")+P-1), "@")
        # Prepend your coordinates
        you = self.players[P]
        s = str(you[0])+"\n"+str(you[1])+"\n"+s
        return s

    def outputForAI(self, P):
        '''for Python programs'''
        board = deepcopy(self.board)
        for x in xrange(self.X):
            for y in xrange(self.Y):
                if board[x][y][0] == "x":
                    board[x][y] = "x"
        for p in self.players:
            player = self.players[p]
            if p == P:
                board[player[0]][player[1]] = "@"
            else:
                board[player[0]][player[1]] = "A"
        return board
        

    def movePlayer(self, P, direction):
        oldSquare = self.players[P]
        self.board[oldSquare[0]][oldSquare[1]] = "x"+str(P)
        
        if direction != "": direction = direction[0] # Allow e.g. "w \n"
        if direction not in "wasd" or direction == "":
            # Not a valid move. Kill the player?
            self.kill(P)
            return
            
        if not P in self.players:
            # Oops, you're already dead.
            return
        
        # direction is "w", "a", "s", "d"
        v = {"w":(0,-1),"a":(-1,0),"s":(0,1),"d":(1,0)}[direction]
        oldSquare = self.players[P]
        newSquare = [v[0]+oldSquare[0], v[1]+oldSquare[1]]
        self.players[P] = newSquare
        # Test for deaths after every player moves, not here.

    def killPlayers(self):
        board = self.board
        # Did anyone move off the board?
        for P in list(self.players):
            player = self.players[P]
            if not (0 <= player[0] < self.X and 0 <= player[1] < self.Y):
                # Oops, you fell off the board.
                self.kill(P)
        
        # Did anyone fall in a hole?
        for P in list(self.players):
            player = self.players[P]
            target = board[player[0]][player[1]]
            if target[0] == "x":
                # Whoops!
                self.kill(P)

        # Did anyone collide?
        # O(n^2) lol
        for P in list(self.players):
            for Q in list(self.players):
                player = self.players[P]
                qlayer = self.players[Q]
                if player == qlayer and P != Q:
                    # Whoops!
                    self.kill(P)
                    self.kill(Q)

    def kill(self, P):
        if P in self.players:
            del self.players[P]

def inputMove(B, P, AI):
    # Send new board into AI
    AI.board = B.outputForAI(P)
    # And tell AI to process it and grab move
    move = AI.play()    
    # And then move the AI's board back to the global one
    B = AI.board

    return move
    
from Tkinter import *

def makeMove():
    for P in list(B.players):
        global scores
        scores[P] += 1        
        Pmove = inputMove(B, P, AIDict[P])
        B.movePlayer(P, Pmove)

    drawBoard(B.board)

    B.killPlayers()

    if B.players:
        canvas.after(100, makeMove)
    else:
        print "Game over! Scores:"
        for i in xrange(1, len(scores)):
            print "%d: %d" % (i, scores[i])

def redrawAll(): # Not in use
    canvas.delete(ALL)
    drawBoard(board)

def drawBoard(board):
    canvas.delete(ALL)
    rows = len(board)
    cols = len(board[0])
    for row in range(rows):
        for col in range(cols):
            drawCell(board[row][col], row, col)

def drawCell(sq, row, col):
    margin = 5
    cellSize = 30
    left = margin + col * cellSize
    right = left + cellSize
    top = margin + row * cellSize
    bottom = top + cellSize

    colorDict = {".":"white", "xB":"red", "x1":"blue", "x2":"green"}
    color = colorDict[sq] if sq in colorDict else "pink"
    
    canvas.create_rectangle(top, left, bottom, right, fill=color)

    for P in B.players:
        player = B.players[P]
        if player[0] == row and player[1] == col:
            canvas.create_oval(top, left, bottom, right, fill="blue")

def init(board):
    drawBoard(board)

def playGame(B, AIDict):
    global canvas
    root = Tk()
    canvas = Canvas(root, width=B.X*30, height=B.Y*30)
    canvas.pack()
    init(B.board)
    canvas.after(2000, makeMove)
    print "hello"
    global scores
    scores = [0]*(len(B.players)+1)
    root.mainloop()

def match(AI1,AI2):
    global B
    global AIDict
    B = Board(20,21)
    B.players = {1:[9,10],2:[10,10]}
    AIDict = {1:AI1(B),2:AI2(B)} # Contains AI class instances
    playGame(B, AIDict)