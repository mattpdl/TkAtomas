# Event handling classes (e.g. gameplay, each mode, mousepress, keypress, time)
from core_graphics import *
import gamescreens, random

class Game(object):
    def __init__(self, data, difficult, nMin=1, nMax=3, score=0):
        """
        Creates a template for a given game mode of Atomas.

        data: Struct
        difficult: bool
        nMin: int
        nMax: int
        score: int
        """
        self.difficult, self.nMin, self.nMax = difficult, nMin, nMax
        self.gameOver = False
        self.score = score
        self.board = Gameboard()
        self.board.center = self.spawnPiece(data)
        for i in range(1, 7):
            self.board.addElem(i, self.spawnAtom(data, i))

    def spawnAtom(self, data, loc):
        """
        Creates an atom of a random element.

        data: Struct
        loc: int
        """
        n = random.randint(self.nMin, self.nMax)
        return Atom(data, self.board, loc, n)

    def spawnPiece(self, data):
        """
        Places a random piece at the center of the gameboard. The type of piece
        depends on the game mode.

        data: Struct
        """
        pieceType = random.randint(1, 60)
        if not self.difficult:
            isNeutrino = pieceType == 60 if self.score >= 750 else False
            if isNeutrino: return Neutrino(data, self.board, 0)
            elif 1 <= pieceType <= 12 and type(self) == Geneva:
                return Luxon(data, self.board, 0)
            elif 1 <= pieceType <= 12:
                return Proton(data, self.board, 0)
            elif 13 <= pieceType <= 17:
                return Electron(data, self.board, 0)
            # Zen mode probability of spawning proton on last move before 
            # end of game is half
            elif type(self) == Zen and len(self.board.elems) == 18 \
                and 18 <= pieceType <= 35:
                return Proton(data, self.board, 0)
            else: return self.spawnAtom(data, 0)
        else: pass # implement difficult mode

    def selectSpace(self, event, data):
        """
        Places the center element between two elements on the gameboard based 
        upon the user's mouseclick.

        event: obj
        data: Struct
        """
        clicked = None
        dx, dy, q = event.x - data.cx, data.cy - event.y, None
        if math.hypot(dx, dy) <= data.cirR or math.hypot(dx, dy) >= data.r:
            if self.board.center.prevElectron:
                self.board.center = Proton(data, self.board, 0)
                self.board.center.prevElectron = False
            return
        if dx > 0 and dy > 0: q = 0
        elif dx < 0 and dy > 0: q = 1
        elif dx < 0 and dy < 0: q = 2
        else: q = 3
        if q == 0 or q == 2:
            clicked = (q * math.pi/2 + math.atan(abs(dy)/abs(dx))) \
                // self.board.dAngle
        else:
            clicked = (q * math.pi/2 + math.pi / 2 - \
                math.atan(abs(dy)/abs(dx))) // self.board.dAngle
        self.board.center.move(data, int(clicked + 1))

    def selectAtom(self, event, data):
        """
        Determines which element on the gameboard has been clicked.

        event: obj
        data: Struct
        """
        clicked = None
        for elem in self.board.elems:
            dx, dy = event.x - elem.cx, event.y - elem.cy
            if math.hypot(dx, dy) <= data.cirR:
                clicked = elem
        return clicked

    def copyAtom(self, event, data):
        """
        Copies a given element on the gameboard and places it at the center.

        event: obj
        data: Struct
        """
        if clicked != None:
            self.board.center = self.selectAtom(event, data)

    def mousePressed(self, event, data):
        """
        Checks whether any element or position on the gameboard has been 
        clicked and determines which elements should be manipulated afterward.

        event: obj
        data: Struct
        """
        if type(self.board.center) == Neutrino:
            self.copyAtom(event, data)
        elif type(self.board.center) == Electron:
            clicked = self.selectAtom(event, data)
            if clicked != None: clicked.move(data, 0)
        elif type(self.board.center) == Luxon:
            clicked = self.selectAtom(event, data)
            if clicked != None:
                clicked.prevAtom = self
                clicked = Proton(data, self.board, self.board.index(clicked))
        else:
            self.selectSpace(event, data)

    def keyPressed(self, event, data):
        """
        Allows the user to quit the current game.

        event: obj
        data: Struct
        """
        if event.keysym == 'q':
            data.screen = gamescreens.ModeSelect()
    
    def checkForFusion(self, data):
        """
        Checks if atoms of the same element are spaced symmetrically on the 
        left and right sides of a proton, fusing them together if so.

        data: Struct
        """
        fuseCount, i, left, right = 0, None, None, None
        for elem in self.board.elems:
            if isinstance(elem, Proton):
                fuseCount, i = 0, self.board.elems.index(elem)
                left = (i - 1) % len(self.board.elems)
                right = (i + 1) % len(self.board.elems)
                if left == right: continue
                while self.board.elems[left] == self.board.elems[right]:
                    fuseCount += 1
                    left = (left - 1) % len(self.board.elems)
                    right = (right + 1) % len(self.board.elems)
        if fuseCount > 0:
            self.board.fuse(data, i, fuseCount)
            self.score += 10 * fuseCount
        return fuseCount

    def checkGameOver(self):
        """
        Checks if the gameboard contains more than 18 elements, upon which the 
        game ends.
        """
        if len(self.board.elems) > 18: self.gameOver = True

    def timerFired(self, data):
        """
        Updates the gameboard if any atoms need to be fused together and checks
        whether the game is over.

        data: Struct
        """
        self.checkForFusion(data)
        self.board.updateElems(data)
        self.checkGameOver()
        if self.gameOver:
            data.screen = gamescreens.GameOver(self.score, type(self), self.difficult)

    def draw(self, canvas, data):
        """
        Draws the current gameboard on the canvas.

        canvas: tkinter Canvas
        data: Struct
        """
        self.board.draw(canvas, data)

class Classic(Game):
    def __init__(self, data, difficult, nMin=1, nMax=3, score=0):
        """
        Creates a game in Classic mode.

        data: Struct
        difficult: bool
        nMin: int
        nMax: int
        score: int
        """
        super().__init__(data, difficult, nMin, nMax, score)

class TimeAttack(Game):
    def __init__(self, data, difficult, nMin=1, nMax=3, score=0):
        """
        Creates a game in Time Attack mode, where the user must fuse atoms at 
        least once every 20 seconds to continue the game.

        data: Struct
        difficult: bool
        nMin: int
        nMax: int
        score: int
        """
        super().__init__(data, difficult, nMin, nMax, score)
        self.time = 150

    def checkForFusion(self, data):
        """
        Checks if any atoms on the gameboard should be fused together and 
        increments the timer accordingly.

        data: Struct
        """
        fuseCount = super().checkForFusion(data)
        if fuseCount == 2: self.time += 20
        elif fuseCount > 2: self.time += 30

    def timerFired(self, data):
        """
        Decrements the timer and checks if the game is over.

        data: Struct
        """
        self.time -= 1
        super().timerFired(data)
        if self.time == 0: self.gameOver = True

    def draw(self, canvas, data):
        """
        Draws the current gameboard, including text showing the time remaining.

        canvas: tkinter Canvas
        data: Struct
        """
        super().draw(canvas, data)
        x, y = data.r, 3*data.height/24
        canvas.create_text(x, y, text='%d sec remaining' % (self.time//10), 
            font=('Verdana', 16), fill='#fff')

class Geneva(Game):
    def __init__(self, data, difficult, nMin=1, nMax=3, score=0):
        """
        Creates an Atomas game in Geneva mode, in which luxons are spawned 
        instead of protons.

        data: Struct
        difficult: bool
        nMin: int
        nMax: int
        score: int
        """
        super().__init__(data, difficult, nMin, nMax, score)

class Zen(Game):
    def __init__(self, data, difficult, nMin=1, nMax=3, score=0):
        """
        Creates an Atomas game in Zen mode, where the chance of spawning a 
        proton upon the last move before the game ends is one-half.

        data: Struct
        difficult: bool
        nMin: int
        nMax: int
        score: int
        """
        super().__init__(data, difficult, nMin, nMax, score)