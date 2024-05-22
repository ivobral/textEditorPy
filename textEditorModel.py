from Location import Location
from LocationRange import LocationRange
from Iterators import AllLines, LinesRange
from Observers import CursorObserver, TextObserver

from copy import deepcopy
from Clipboard import ClipboardStack

class TextEditorModel:
    def __init__(self, text):
        #2.2
        self.lines = text.split("\n")
        self.cursorLocation = Location(0, 0)
        self.selectionRange = None

        #2.4
        self.cursorObservers = []
        
        #2.5
        self.textObservers = []

        #2.7
        self.clipboard = ClipboardStack()

        #2.9
        self.selectionObservers = []

    #2.9
    def addSelectionObserver(self, observer):
        self.selectionObservers.append(observer)

    def removeSelectionObserver(self, observer):
        self.selectionObservers.remove(observer)

    def notifySelectionObservers(self):
        for observer in self.selectionObservers:
            observer.selectionChanged()

    def setText(self, text):
        self.lines = text.split("\n")
        self.setSelectionRange(None)
        self.notifyTextObservers()

    def getText(self):
        return "\n".join(self.lines)

    def clear(self):
        self.lines = [""]
        self.cursorLocation = Location(0, 0)
        self.setSelectionRange(None)
        self.notifyTextObservers()
        self.notifyCursorObservers()
    
    #2.7
    def copySelection(self):
        selected = self.getSelectionRange()
        if selected:
            text = self.getTextFromRange(selected)
            self.clipboard.push(text)

    def cutSelection(self):
        selected = self.getSelectionRange()
        if selected:
            text = self.getTextFromRange(selected)
            self.clipboard.push(text)
            self.deleteRange(selected)
            self.setSelectionRange(None)
        self.notifyCursorObservers()

    def paste(self):
        text = self.clipboard.peek()
        if text is not None:
            self.insert(text)
            
            self.notifyCursorObservers()
            self.notifySelectionObservers()

    def pasteAndRemove(self):
        text = self.clipboard.pop()
        if text is not None:
            self.insert(text)
            
            self.notifyCursorObservers()
            self.notifySelectionObservers()

    def getTextFromRange(self, selected):
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

    #2.6
    def insert(self, c):

        if self.getSelectionRange() is not None:
            self.deleteRange(self.getSelectionRange())
            self.setSelectionRange(None)
        if len(c) == 1:
            #if the character is a newline character then split the line at the cursor location
            if c == "\n" or c == "\r":
                self.lines.insert(self.cursorLocation.y + 1, self.lines[self.cursorLocation.y][self.cursorLocation.x:])
                self.lines[self.cursorLocation.y] = self.lines[self.cursorLocation.y][:self.cursorLocation.x]
                self.cursorLocation.y += 1
                self.cursorLocation.x = 0
            else:  #if the character is not a newline character then insert the character at the cursor location
                y = self.cursorLocation.y
                x = self.cursorLocation.x

                self.lines[y] = self.lines[y][:x] + c + self.lines[y][x:]
                self.cursorLocation.x += 1
        else:
            self.insertText(c)
        
        self.notifyTextObservers()
        self.notifyCursorObservers()
    

    def insertText(self, text):
        if self.selectionRange is not None:
            self.deleteRange(self.selectionRange)
            self.selectionRange = None

        # Split the text by newline characters
        lines = text.split("\n")

        # Get the current line at the cursor location
        current_line = self.lines[self.cursorLocation.y]
        before_cursor = current_line[:self.cursorLocation.x]
        after_cursor = current_line[self.cursorLocation.x:]

        # Insert the first line at the cursor location
        self.lines[self.cursorLocation.y] = before_cursor + lines[0]

        # If there's more than one line to insert
        if len(lines) > 1:
            # Insert all middle lines directly
            for i in range(1, len(lines) - 1):
                self.cursorLocation.y += 1
                self.lines.insert(self.cursorLocation.y, lines[i])
            
            # Insert the last line and attach the after_cursor part of the original line
            self.cursorLocation.y += 1
            self.lines.insert(self.cursorLocation.y, lines[-1] + after_cursor)
            self.cursorLocation.x = len(lines[-1])
        else:
            # If there's only one line, reattach the after_cursor part
            self.lines[self.cursorLocation.y] += after_cursor
            self.cursorLocation.x += len(lines[0])

        self.notifyTextObservers()

    
    #2.5
    def addTextObserver(self, observer: TextObserver):
        self.textObservers.append(observer)

    def removeTextObserver(self, observer: TextObserver):
        self.textObservers.remove(observer)

    def notifyTextObservers(self):
        for observer in self.textObservers:
            observer.updateText()

    def deleteBefore(self):
        if self.selectionRange is not None:                 #if there is a selection range then delete the selected text
            self.deleteRange(self.getSelectionRange())
            self.selectionRange = None
            self.notifyTextObservers()
            self.notifyCursorObservers()
            self.notifySelectionObservers()
            return
        
        if self.cursorLocation.x > 0:                       #if the cursor is not at the beginning of the line
            self.lines[self.cursorLocation.y] = self.lines[self.cursorLocation.y][:self.cursorLocation.x-1] + self.lines[self.cursorLocation.y][self.cursorLocation.x:]
            self.cursorLocation.x -= 1

            self.notifyTextObservers()
            self.notifyCursorObservers()
            self.notifySelectionObservers()
        elif self.cursorLocation.y > 0:                     #if the cursor is at the beginning of the line
            self.cursorLocation.y -= 1
            self.cursorLocation.x = len(self.lines[self.cursorLocation.y])
            self.lines[self.cursorLocation.y] += self.lines.pop(self.cursorLocation.y+1)
            
            self.notifyTextObservers()
            self.notifyCursorObservers()
            self.notifySelectionObservers()
            
    def deleteAfter(self):
        if self.selectionRange is not None:
            self.deleteRange(self.getSelectionRange())
            self.selectionRange = None
            self.notifyTextObservers()
            self.notifyCursorObservers()
            self.notifySelectionObservers()
            return
        
        if self.cursorLocation.x < len(self.lines[self.cursorLocation.y]):              #if the cursor is not at the end of the line
            self.lines[self.cursorLocation.y] = self.lines[self.cursorLocation.y][:self.cursorLocation.x] + self.lines[self.cursorLocation.y][self.cursorLocation.x+1:]
            
            self.notifyTextObservers()
            self.notifyCursorObservers()
            self.notifySelectionObservers()
        elif self.cursorLocation.y < len(self.lines) - 1:                               #if the cursor is at the end of the line
            self.lines[self.cursorLocation.y] += self.lines.pop(self.cursorLocation.y+1)
            
            self.notifyTextObservers()
            self.notifyCursorObservers()
            self.notifySelectionObservers()

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
        self.setSelectionRange(None)
        self.notifyCursorObservers()
        self.notifySelectionObservers()

    def getSelectionRange(self):
        return self.selectionRange

    def setSelectionRange(self, r: LocationRange):
        self.selectionRange = r
        self.notifyTextObservers()
        self.notifySelectionObservers()

    def selectionRangeLeft(self):
        #this is the case when the cursor is at the beginning of the first line
        if self.cursorLocation.x <= 0 and self.cursorLocation.y == 0:
            return
        
        #this is the case when the selection range is None
        if self.getSelectionRange() is None:
            self.setSelectionRange(LocationRange(deepcopy(self.cursorLocation), deepcopy(self.cursorLocation)))
        
        #this is the case when the cursor is not at the beginning of the line
        if self.cursorLocation.x > 0:
            self.cursorLocation.x -= 1
        else:   #this is the case when the cursor is at the beginning of the line
            if self.cursorLocation.y > 0:
                self.cursorLocation.y -= 1
                self.cursorLocation.x = len(self.lines[self.cursorLocation.y])

        self.getSelectionRange().end= deepcopy(self.cursorLocation)
        self.notifyTextObservers()
        self.notifyCursorObservers()
        self.notifySelectionObservers()

    def selectionRangeRight(self):
        #this is the case when the cursor is at the end of the last line
        if self.cursorLocation.x >= len(self.lines[self.cursorLocation.y]) and self.cursorLocation.y == len(self.lines) - 1:
            return

        #this is the case when the selection range is None
        if self.getSelectionRange() is None:
            self.setSelectionRange(LocationRange(deepcopy(self.cursorLocation), deepcopy(self.cursorLocation)))

        #this is the case when the cursor is not at the end of the line
        if self.cursorLocation.x < len(self.lines[self.cursorLocation.y]):
            self.cursorLocation.x += 1
        else:   #this is the case when the cursor is at the end of the line
            if self.cursorLocation.y < len(self.lines) - 1:
                self.cursorLocation.y += 1
                self.cursorLocation.x = 0

        #this is the case when the cursor is at the end of the last line
        self.getSelectionRange().end = deepcopy(self.cursorLocation)
        self.notifyTextObservers()
        self.notifyCursorObservers()
        self.notifySelectionObservers()

    def selectionRangeUp(self):
        if self.getSelectionRange() is None:
            self.setSelectionRange(LocationRange(deepcopy(self.cursorLocation), deepcopy(self.cursorLocation)))

        if self.cursorLocation.y > 0:
            self.cursorLocation.y -= 1
            self.cursorLocation.x = min(self.cursorLocation.x, len(self.lines[self.cursorLocation.y]))

        self.getSelectionRange().end = deepcopy(self.cursorLocation)
        self.notifyTextObservers()
        self.notifyCursorObservers()
        self.notifySelectionObservers()

    def selectionRangeDown(self):
        if self.getSelectionRange() is None:
            self.setSelectionRange(LocationRange(deepcopy(self.cursorLocation), deepcopy(self.cursorLocation)))

        if self.cursorLocation.y < len(self.lines) - 1:
            self.cursorLocation.y += 1
            self.cursorLocation.x = min(self.cursorLocation.x, len(self.lines[self.cursorLocation.y]))

        self.getSelectionRange().end = deepcopy(self.cursorLocation)
        self.notifyTextObservers()
        self.notifyCursorObservers()
        self.notifySelectionObservers()

    #2.4
    def addCursorObserver(self, observer: CursorObserver):
        self.cursorObservers.append(observer)

    def removeCursorObserver(self, observer: CursorObserver):
        self.cursorObservers.remove(observer)

    def notifyCursorObservers(self):
        for observer in self.cursorObservers:
            #print(observer.__class__.__name__)
            observer.updateCursorLocation(self.cursorLocation)

    def moveCursorLeft(self):
        if self.cursorLocation.x > 0:           #if the cursor is not at the beginning of the line
            self.cursorLocation.x -= 1

            self.setSelectionRange(None)
            self.notifyCursorObservers()
            
        else:                                   #if the cursor is at the beginning of the line
            if self.cursorLocation.y > 0:       #if the cursor is not at the beginning of the first line
                self.cursorLocation.y -= 1
                self.cursorLocation.x = len(self.lines[self.cursorLocation.y])

                self.setSelectionRange(None)
                self.notifyCursorObservers()

    def moveCursorRight(self):
        if self.cursorLocation.x < len(self.lines[self.cursorLocation.y]):    #if the cursor is not at the end of the line
            self.cursorLocation.x += 1

            self.setSelectionRange(None)
            self.notifyCursorObservers()
        elif self.cursorLocation.y == len(self.lines) - 1:                      #if the cursor is at the end of the last line
            pass
        else:                                                                   #if the cursor is at the end of the line
            self.cursorLocation.x = 0
            self.cursorLocation.y += 1

            self.setSelectionRange(None)
            self.notifyCursorObservers()

    def moveCursorUp(self):
        if self.cursorLocation.y > 0:
            self.cursorLocation.y -= 1
            self.cursorLocation.x = min(self.cursorLocation.x, len(self.lines[self.cursorLocation.y]))

            self.setSelectionRange(None)
            self.notifyCursorObservers()

    def moveCursorDown(self):
        if self.cursorLocation.y < len(self.lines) - 1:
            self.cursorLocation.y += 1
            self.cursorLocation.x = min(self.cursorLocation.x, len(self.lines[self.cursorLocation.y]))

            self.setSelectionRange(None)
            self.notifyCursorObservers()

    #2.3
    def allLines(self):
        return AllLines(self.lines)
    
    def linesRange(self, index1, index2):
        return LinesRange(self.lines, index1, index2)