from Location import Location
from LocationRange import LocationRange
from Iterators import AllLines, LinesRange
from TextObserver import TextObserver
from CursorObserver import CursorObserver
from copy import deepcopy
from Clipboard import ClipboardStack

class TextEditorModel:
    def __init__(self, text):
        #2.2
        self.lines = text.split("\n")
        self.cursorLocation = Location(0, 0)
        self.selectionRange = None

        self.cursor_observers = []
        self.text_observers = []
        self.clipboard = ClipboardStack()

    def setText(self, text):
        self.lines = text.split("\n")
        self.cursorLocation = Location(0, 0)
        self.selectionRange = None
        self.notifyTextObservers()
        self.notifyCursorObservers()

    def getText(self):
        return "\n".join(self.lines)

    def clear(self):
        self.lines = [""]
        self.cursorLocation = Location(0, 0)
        self.selectionRange = None
        self.notifyTextObservers()
        self.notifyCursorObservers()

    def copySelection(self):
        if self.selectionRange is not None:
            text = self.get_text_from_range(self.selectionRange)
            self.clipboard.push(text)
    
    def cutSelection(self):
        if self.selectionRange is not None:
            text = self.get_text_from_range(self.selectionRange)
            self.clipboard.push(text)
            self.deleteRange(self.selectionRange)
            self.selectionRange = None

    def paste(self):
        text = self.clipboard.peek()
        if text is not None:
            self.insert(text)

    def pasteAndRemove(self):
        #print("pasteAndRemove")
        text = self.clipboard.pop()
        if text is not None:
            self.insert(text)

    def get_text_from_range(self, selected):
        if selected:
            start = selected.start
            end = selected.end
            if end.y < start.y or (end.y == start.y and end.x < start.x):
                start, end = end, start
            if start.y == end.y:
                return self.lines[start.y][start.x:end.x]
            else:
                selectedText = [self.lines[start.y][start.x:]]
                for i in range(start.y + 1, end.y):
                    selectedText.append(self.lines[i])
                selectedText.append(self.lines[end.y][:end.x])
                return "\n".join(selectedText)

    #method to insert a character at the cursor location and update the cursor location
    def insert(self, c):
        if self.selectionRange is not None:
            self.deleteRange(self.selectionRange)
            self.selectionRange = None

        #if the character is a newline character then split the line at the cursor location
        if c == "\n" or c == "\r":
            self.lines.insert(self.cursorLocation.y + 1, self.lines[self.cursorLocation.y][self.cursorLocation.x:])
            self.lines[self.cursorLocation.y] = self.lines[self.cursorLocation.y][:self.cursorLocation.x]
            self.cursorLocation.y += 1
            self.cursorLocation.x = 0
        else:
            y = self.cursorLocation.y
            x = self.cursorLocation.x

            self.lines[y] = self.lines[y][:x] + c + self.lines[y][x:]
            self.cursorLocation.x += 1
        
        self.notifyTextObservers()
        self.notifyCursorObservers()

    #method to insert a string at the cursor location and update the cursor location
    def insertText(self, text):
        if self.selectionRange is not None:
            self.deleteRange(self.selectionRange)
            self.selectionRange = None

        lines = text.split("\n")
        self.lines[self.cursorLocation.y] = self.lines[self.cursorLocation.y][:self.cursorLocation.x] + lines[0]
        self.cursorLocation.x += len(lines[0])
        self.lines[self.cursorLocation.y] += lines.pop(0)

        for line in lines:
            self.lines.insert(self.cursorLocation.y + 1, line)
            self.cursorLocation.y += 1
            self.cursorLocation.x = len(line)

        self.notifyTextObservers()
        self.notifyCursorObservers()

    #2.5
    def addTextObserver(self, observer: TextObserver):
        self.text_observers.append(observer)

    def removeTextObserver(self, observer: TextObserver):
        self.text_observers.remove(observer)

    def notifyTextObservers(self):
        for observer in self.text_observers:
            observer.updateText()

    def deleteBefore(self):
        if self.selectionRange is not None:
            self.deleteRange(self.selectionRange)
            self.selectionRange = None
            self.notifyTextObservers()
            return
        if self.cursorLocation.x > 0:
            self.lines[self.cursorLocation.y] = self.lines[self.cursorLocation.y][:self.cursorLocation.x-1] + self.lines[self.cursorLocation.y][self.cursorLocation.x:]
            self.cursorLocation.x -= 1
            self.notifyTextObservers()
            #self.notifyCursorObservers()
        elif self.cursorLocation.y > 0:
            self.cursorLocation.y -= 1
            self.cursorLocation.x = len(self.lines[self.cursorLocation.y])
            self.lines[self.cursorLocation.y] += self.lines.pop(self.cursorLocation.y+1)
            self.notifyTextObservers()
            #self.notifyCursorObservers()
            
    def deleteAfter(self):
        if self.selectionRange is not None:
            self.deleteRange(self.selectionRange)
            self.selectionRange = None
            self.notifyTextObservers()
            return
        if self.cursorLocation.x < len(self.lines[self.cursorLocation.y]):
            self.lines[self.cursorLocation.y] = self.lines[self.cursorLocation.y][:self.cursorLocation.x] + self.lines[self.cursorLocation.y][self.cursorLocation.x+1:]
            self.notifyTextObservers()
            #self.notifyCursorObservers()
        elif self.cursorLocation.y < len(self.lines) - 1:
            self.lines[self.cursorLocation.y] += self.lines.pop(self.cursorLocation.y+1)
            self.notifyTextObservers()
            #self.notifyCursorObservers()

    def deleteRange(self, r: LocationRange):
        # Ensure start is before end
        start, end = (r.start, r.end) if (r.start.y < r.end.y or (r.start.y == r.end.y and r.start.x <= r.end.x)) else (r.end, r.start)

        if start.y == end.y:
            # Same line
            self.lines[start.y] = self.lines[start.y][:start.x] + self.lines[end.y][end.x:]
        else:
            # Different lines
            self.lines[start.y] = self.lines[start.y][:start.x] + self.lines[end.y][end.x:]
            del self.lines[start.y + 1:end.y + 1]

        self.cursorLocation = deepcopy(start)
        self.selectionRange = None
        self.notifyTextObservers()
        self.notifyCursorObservers()

    def getSelectionRange(self):
        return self.selectionRange

    def setSelectionRange(self, r: LocationRange):
        self.selectionRange = r
        self.notifyTextObservers()

    def update_selection_range_left(self):
        #this is the case when the cursor is at the beginning of the first line
        if self.cursorLocation.x <= 0 and self.cursorLocation.y == 0:
            self.notifyTextObservers()
            return
        
        #this is the case when the selection range is None
        if self.selectionRange is None:
            self.selectionRange = LocationRange(deepcopy(self.cursorLocation), deepcopy(self.cursorLocation))
        
        #this is the case when the cursor is not at the beginning of the line
        if self.cursorLocation.x > 0:
            self.cursorLocation.x -= 1
        else:   #this is the case when the cursor is at the beginning of the line
            if self.cursorLocation.y > 0:
                self.cursorLocation.y -= 1
                self.cursorLocation.x = len(self.lines[self.cursorLocation.y])

        #this is the case when the cursor is at the beginning of the first line
        self.selectionRange.end = deepcopy(self.cursorLocation)
        self.notifyCursorObservers()
        self.notifyTextObservers()

    def update_selection_range_right(self):
        #this is the case when the cursor is at the end of the last line
        if self.cursorLocation.x >= len(self.lines[self.cursorLocation.y]) and self.cursorLocation.y == len(self.lines) - 1:
            self.notifyTextObservers()
            return

        #this is the case when the selection range is None
        if self.selectionRange is None:
            self.selectionRange = LocationRange(deepcopy(self.cursorLocation), deepcopy(self.cursorLocation))

        #this is the case when the cursor is not at the end of the line
        if self.cursorLocation.x < len(self.lines[self.cursorLocation.y]):
            self.cursorLocation.x += 1
        else:   #this is the case when the cursor is at the end of the line
            if self.cursorLocation.y < len(self.lines) - 1:
                self.cursorLocation.y += 1
                self.cursorLocation.x = 0

        #this is the case when the cursor is at the end of the last line
        self.selectionRange.end = deepcopy(self.cursorLocation)
        self.notifyCursorObservers()
        self.notifyTextObservers()

    def update_selection_range_up(self):
        if self.selectionRange is None:
            self.selectionRange = LocationRange(deepcopy(self.cursorLocation), deepcopy(self.cursorLocation))

        if self.cursorLocation.y > 0:
            self.cursorLocation.y -= 1
            self.cursorLocation.x = min(self.cursorLocation.x, len(self.lines[self.cursorLocation.y]))

        self.selectionRange.end = deepcopy(self.cursorLocation)
        self.notifyCursorObservers()
        self.notifyTextObservers()

    def update_selection_range_down(self):
        if self.selectionRange is None:
            self.selectionRange = LocationRange(deepcopy(self.cursorLocation), deepcopy(self.cursorLocation))

        if self.cursorLocation.y < len(self.lines) - 1:
            self.cursorLocation.y += 1
            self.cursorLocation.x = min(self.cursorLocation.x, len(self.lines[self.cursorLocation.y]))

        self.selectionRange.end = deepcopy(self.cursorLocation)
        self.notifyCursorObservers()
        self.notifyTextObservers()

    #2.4
    def addCursorObserver(self, observer: CursorObserver):
        self.cursor_observers.append(observer)

    def removeCursorObserver(self, observer: CursorObserver):
        self.cursor_observers.remove(observer)

    def notifyCursorObservers(self):
        for observer in self.cursor_observers:
            observer.updateCursorLocation(self.cursorLocation)

    def moveCursorLeft(self):
        if self.cursorLocation.x > 0:
            self.cursorLocation.x -= 1
            self.selectionRange = None
            self.notifyTextObservers()
            self.notifyCursorObservers()
        else:
            if self.cursorLocation.y > 0:
                self.cursorLocation.y -= 1
                self.cursorLocation.x = len(self.lines[self.cursorLocation.y])
                self.selectionRange = None
                self.notifyTextObservers()
                self.notifyCursorObservers()

    def moveCursorRight(self):
        if self.cursorLocation.x < len(self.lines[self.cursorLocation.y]):
            self.cursorLocation.x += 1
            self.selectionRange = None
            self.notifyTextObservers()
            self.notifyCursorObservers()
        elif self.cursorLocation.y == len(self.lines) - 1:
            pass
        else:
            self.cursorLocation.x = 0
            self.cursorLocation.y += 1
            self.selectionRange = None
            self.notifyTextObservers()
            self.notifyCursorObservers()

    def moveCursorUp(self):
        if self.cursorLocation.y > 0:
            self.cursorLocation.y -= 1
            self.cursorLocation.x = min(self.cursorLocation.x, len(self.lines[self.cursorLocation.y]))
            self.selectionRange = None
            self.notifyTextObservers()
            self.notifyCursorObservers()

    def moveCursorDown(self):
        self.selectionRange = None
        if self.cursorLocation.y < len(self.lines) - 1:
            self.cursorLocation.y += 1
            self.cursorLocation.x = min(self.cursorLocation.x, len(self.lines[self.cursorLocation.y]))
            self.selectionRange = None
            self.notifyTextObservers()
            self.notifyCursorObservers()

    #2.3
    def allLines(self):
        return AllLines(self.lines)
    
    def linesRange(self, index1, index2):
        return LinesRange(self.lines, index1, index2)