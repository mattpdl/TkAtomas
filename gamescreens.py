# Gamescreen classes (e.g. selecting mode, pause menu, game over)
from event_handling import Classic, TimeAttack, Geneva, Zen

class Gamescreen(object):
    def __init__(self): pass
    
    def mousePressed(self, event, data): pass

    def keyPressed(self, event, data): pass
    
    def timerFired(self, data): pass

class ModeSelect(Gamescreen):
    def __init__(self): pass

    def keyPressed(self, event, data):
        """
        Checks whether the user has pressed a key to start the game in a given
        mode.

        event: obj
        data: Struct
        """
        if event.keysym == 'c':
            data.screen = Classic(data, False)
        elif event.keysym == 't':
            data.screen = TimeAttack(data, False)
        elif event.keysym == 'g':
            data.screen = Geneva(data, False)
        elif event.keysym == 'z':
            data.screen = Zen(data, False)

    def draw(self, canvas, data):
        """
        Displays the homescreen UI, containing mode selection, on the canvas.

        canvas: tkinter Canvas
        data: Struct
        """
        x = data.r
        y = 3*data.height/12
        canvas.create_text(x, y, text='Atomas', font=('Verdana', 48), 
            fill='#fff')
        y = 7*data.height/12
        canvas.create_text(x, y, text='Classic [c]', font=('Verdana', 24), 
            fill='#fff')
        y = 8*data.height/12
        canvas.create_text(x, y, text='Time Attack [t]', font=('Verdana', 24), 
            fill='#fff')
        y = 9*data.height/12
        canvas.create_text(x, y, text='Geneva [g]', font=('Verdana', 24), 
            fill='#fff')
        y = 10*data.height/12
        canvas.create_text(x, y, text='Zen [z]', font=('Verdana', 24), 
            fill='#fff')

class GameOver(Gamescreen):
    def __init__(self, score, mode, difficult):
        """
        Creates a gamescreen to be displayed when a game ends.

        score: int
        mode: Game (Classic, TimeAttack, Geneva, Zen)
        difficult: bool
        """
        self.score = score
        self.mode = mode
        self.difficult = difficult

    def keyPressed(self, event, data):
        """
        Checks if the user wishes to restart the game or go to the homescreen.

        event: obj
        data: Struct
        """
        if event.keysym == 'r':
            data.screen = self.mode(data, self.difficult)
        elif event.keysym == 'q':
            data.screen = ModeSelect()

    def draw(self, canvas, data):
        """
        Displays a "Game Over!" message and the final score for a given game.

        canvas: tkinter Canvas
        data: Struct
        """
        canvas.create_text(data.cx, data.cy, text='Game Over!', 
            font=('Verdana', 48), fill='#fff')
        x, y = data.r, 7*data.height/12
        canvas.create_text(x, y, text='Score: %d' % self.score, 
            font=('Verdana', 24), fill='#fff')
        x, y = data.r, 9*data.height/12
        canvas.create_text(x, y, text='Restart [r]', 
            font=('Verdana', 20), fill='#fff')
        x, y = data.r, 10*data.height/12
        canvas.create_text(x, y, text='Quit [q]', 
            font=('Verdana', 20), fill='#fff')