# Adapted from Animation Starter Code at 
# http://www.cs.cmu.edu/~112n18/notes/notes-animations-part2.html

from tkinter import *
from gamescreens import *

def getElements():
    """
    Returns two lists containing the elements of the periodic table and each 
    element's corresponding color within the game.
    """
    pTable, pTableColor = [], []
    with open('pTable.csv', 'r') as f:
        for line in f.readlines():
            if line.startswith('#'): continue
            line = line.split(',')
            pTable.append(line[1].strip())
            pTableColor.append(line[3].strip())
    return pTable, pTableColor

def init(data):
    """
    Declares and stores game metadata upon launch of the game.

    data: Struct
    """
    data.bgColor = '#800000'
    data.pTable, data.pTableColor = getElements()
    data.margin = 0
    data.cx, data.cy, data.r = data.width / 2, data.height / 2, data.width / 2
    data.cirR = 30
    data.screen = ModeSelect()
    data.removal = []

def mousePressed(event, data):
    """
    Executes the mousePressed method for the current gamescreen.

    event: obj
    data: Struct
    """
    data.screen.mousePressed(event, data)

def keyPressed(event, data):
    """
    Executes the keyPressed method for the current gamescreen.

    event: obj
    data: Struct
    """
    data.screen.keyPressed(event, data)

def timerFired(data):
    """
    Removes unneeded gameboard elements and executes the timerFired method for 
    the current gamescreen.

    data: Struct
    """
    for elem in data.removal:
        data.screen.board.elems.remove(elem)
    data.removal = []
    data.screen.timerFired(data)

def redrawAll(canvas, data):
    """
    Executes the draw method for the current gamescreen.

    canvas: tkinter Canvas
    data: Struct
    """
    data.screen.draw(canvas, data)

def run(width=300, height=300):
    """
    Initializes window GUI and canvas using the Tkinter library.

    width: int
    height: int
    """
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, data.width, data.height,
                                fill=data. bgColor, width=0)
        redrawAll(canvas, data)
        canvas.update()

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 100 # milliseconds
    root = Tk()
    root.title("TkAtomas") # window title
    init(data)
    # create the root and the canvas
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.configure(bd=0, highlightthickness=0)
    canvas.pack()
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed

if __name__ == "__main__":
    run(400, 600)