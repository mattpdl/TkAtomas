# Core graphics classes (e.g. protons, electrons, atoms, gameboard)
import math

class Cir(object):
    def __init__(self, data, board, loc):
        """
        Creates a circle centered at (cx, cy) on the canvas.

        cx: num
        cy: num
        """
        self.angle = loc * 2*math.pi / 6 if loc > 0 else None
        if loc == 0: self.cx, self.cy = data.cx, data.cy
        else:
            self.cx = data.cx + (data.r - data.cirR) * math.cos(self.angle)
            self.cy = data.cy - (data.r - data.cirR) * math.sin(self.angle)
        self.r = data.cirR
        self.dAngle = 2*math.pi / (len(board.elems) + 1)
        self.prevElectron = False
        self.prevLuxon = False

    def __eq__(self, other):
        """
        Determines whether two circles are both atoms of the same element.

        other: Cir
        """
        if isinstance(self, Atom) and isinstance(other, Atom):
            return self.n == other.n
        return False

    def setCenter(self, data):
        """
        Sets a circle's center point on the canvas depending on its 
        specified position on the gameboard.

        data: Struct
        """
        self.cx = data.cx + (data.r - data.cirR) * math.cos(self.angle)
        self.cy = data.cy - (data.r - data.cirR) * math.sin(self.angle)

    def move(self, data, loc=None):
        """
        Moves a circle to a specified position on the gameboard.

        data: Struct
        loc: int
        """
        if loc == 0: # move to center
            self.angle = None
            self.cx, self.cy = data.cx, data.cy
            data.screen.board.center = self
            data.screen.board.center.prevElectron = True
            data.removal.append(self)
        elif self.angle == None: # move from center
            data.screen.board.addElem(loc, self)
            data.screen.board.updateElems(data)
            data.screen.board.center = data.screen.spawnPiece(data)
        else:
            loc = data.screen.board.elems.index(self)
            self.angle = loc * 2*math.pi / len(data.screen.board.elems)
            self.setCenter(data)
    
    def draw(self, canvas):
        """
        Draws a circle of its given color on the canvas at its given center 
        point.

        canvas: tkinter Canvas
        """
        x0, x1 = self.cx - self.r, self.cx + self.r
        y0, y1 = self.cy - self.r, self.cy + self.r
        canvas.create_oval(x0, y0, x1, y1, fill=self.color)
        canvas.create_text(self.cx, self.cy, text=self.text, font=('Verdana', 20), 
            fill='#fff')

class Electron(Cir):
    def __init__(self, data, board, loc):
        """
        Creates an electron, which when clicking on an atom from the board, 
        can move an atom to a different index or turn it into a proton
        by clicking on the atom again when it moves to the center.

        data: Struct
        board: Gameboard
        loc: pos int
        """
        super().__init__(data, board, loc)
        self.color = '#00a'
        self.text = '-'

class Proton(Cir):
    def __init__(self, data, board, loc):
        """
        Creates a proton to be placed at a given location on the gameboard.

        data: Struct
        board: Gameboard
        loc: int
        """
        super().__init__(data, board, loc)
        self.color = '#a00'
        self.text = '+'

class Atom(Cir):
    def __init__(self, data, board, loc, n):
        """
        Creates an atom to be placed at a given location on the gameboard.

        data: Struct
        board: Gameboard
        loc: int
        n: int
        """
        super().__init__(data, board, loc)
        self.color = data.pTableColor[n - 1]
        self.element = data.pTable[n - 1]
        self.text = self.element
        self.n = n
        self.prevElectron = False
        self.prevLuxon = False

class Neutrino(Cir):
    def __init__(self, data, board, loc):
        """
        Creates a neutrino to be placed at a given location on the gameboard.

        data: Struct
        board: Gameboard
        loc: int
        """
        super().__init__(data, loc)
        self.color, self.text = '#fff', ''

class Luxon(Cir):
    def __init__(self, data, board, loc):
        """
        Creates a luxon to be placed at a given location on the gameboard.

        data: Struct
        board: Gameboard
        loc: int
        """
        super().__init__(data, loc)
        self.color, self.text = 'green', '*'

class Gameboard(object):
    def __init__(self):
        """
        Creates an empty gameboard.
        """
        self.center = None
        self.elems = []
        self.dAngle = None

    def addElem(self, loc, elem):
        """
        Adds the given element to the board at the specified index, starting at
        1.

        loc: pos int
        elem: Cir
        """
        self.elems.insert(loc - 1, elem)

    def updateElems(self, data):
        """
        Recalculates the angle between each element on the board such that each
        angle is equal.

        data: Struct
        """
        for i in range(len(self.elems)):
            self.elems[i].angle = (i+1) * 2*math.pi / len(self.elems)
            self.elems[i].setCenter(data)
        self.dAngle = 2*math.pi / len(self.elems)

    def fuse(self, data, protonIndex, count):
        """
        Combines count number of atoms of the same element spaced symmetrically
        around a proton into an atom of a higher element.

        data: Struct
        protonIndex: int
        count: pos int
        """
        iMin = (protonIndex - count) % len(self.elems)
        iMax = (protonIndex + count) % len(self.elems)
        if iMin > iMax: elemsToFuse = self.elems[iMin:] + self.elems[:iMax+1]
        else: elemsToFuse  = self.elems[iMin:iMax+1]
        if count == 1: n = self.elems[iMin].n + 1
        else:
            n = max([elem.n for elem in elemsToFuse if type(elem) == Atom]) \
                + count
        fusedAtom = Atom(data, self, protonIndex + 1, n)
        self.elems.insert(iMin, fusedAtom)
        for elem in elemsToFuse:
            self.elems.remove(elem)

    def draw(self, canvas, data):
        """
        Draws the gameboard on the canvas given the current game state.

        canvas: tkinter Canvas
        data: Struct
        """
        x, y = data.r, data.height/12
        canvas.create_text(x, y, text=str(data.screen.score), font=('Verdana', 30), 
            fill='#fff')
        x0, x1 = 0, data.width
        y0, y1 = (1/6)*data.height, (5/6)*data.height
        canvas.create_oval(x0, y0, x1, y1, fill=data.bgColor, outline='#fff')
        self.center.draw(canvas)
        for elem in self.elems: elem.draw(canvas)

        y = 11*data.height/12
        canvas.create_text(x, y, text='Quit [q]', font=('Verdana', 24), 
            fill='#fff')