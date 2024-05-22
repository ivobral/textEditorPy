from Location import Location

#2.4
class CursorObserver:
    def updateCursorLocation(self, loc: Location):
        pass

class CursorObserverHelper(CursorObserver):
    def __init__(self, textEditor):
        self.textEditor = textEditor

    def updateCursorLocation(self, loc: Location):
        self.textEditor.updateCursorLocation(loc)

#2.5
class TextObserver:
    def updateText(self):
        pass