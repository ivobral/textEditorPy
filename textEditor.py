import tkinter
from textEditorModel import TextEditorModel
from CursorObserver import CursorObserver
from Location import Location


class TextEditor(CursorObserver, tkinter.Canvas):
    def __init__(self, model: TextEditorModel, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.model = model
        self.model.addCursorObserver(self)
        self.model.addTextObserver(self)
        self.cursor_visible = True
        #self.blink_cursor()
        self.menu()
        self.focus_set()

        #2.4
        self.bind("<Left>", lambda e: self.model.moveCursorLeft())
        self.bind("<Right>", lambda e: self.model.moveCursorRight())
        self.bind("<Up>", lambda e: self.model.moveCursorUp())
        self.bind("<Down>", lambda e: self.model.moveCursorDown())

        #2.5
        self.bind("<BackSpace>", lambda e: self.model.deleteBefore())
        self.bind("<Delete>", lambda e: self.model.deleteAfter())

        self.bind('<Shift-Left>', self.shift_left)
        self.bind('<Shift-Right>', self.shift_right)
        self.bind('<Shift-Up>', self.shift_up)
        self.bind('<Shift-Down>', self.shift_down)
        
        self.bind('<Key>', lambda e: self.keyPressed(e.char))

        self.bind('<Control-c>', lambda e: self.copySelection())
        self.bind('<Control-x>', lambda e: self.cutSelection())
        self.bind('<Control-v>', lambda e: self.paste())
        self.bind('<Control-Shift-V>', lambda e: self.pasteAndRemove())

        self.bind('<Control-z>', lambda e: self.undo())
        self.bind('<Control-y>', lambda e: self.redo())

    def menu(self):
        self.menu = tkinter.Menu(self.master)
        self.master.config(menu=self.menu)

        file_menu = tkinter.Menu(self.menu, tearoff=0)
        file_menu.add_command(label="Open", command="")
        file_menu.add_command(label="Save", command="")
        file_menu.add_command(label="Exit", command=self.closeWindow)
        self.menu.add_cascade(label="File", menu=file_menu)

        # Edit menu
        edit_menu = tkinter.Menu(self.menu, tearoff=0)
        edit_menu.add_command(label="Undo", command="")
        edit_menu.add_command(label="Redo", command="")
        edit_menu.add_command(label="Cut", command=self.cutSelection)
        edit_menu.add_command(label="Copy", command=self.copySelection)
        edit_menu.add_command(label="Paste", command=self.paste)
        edit_menu.add_command(label="Paste and Take", command=self.pasteAndRemove)
        edit_menu.add_command(label="Delete selection", command=self.deleteSelection)
        edit_menu.add_command(label="Clear document", command=self.clearDocument)
        self.menu.add_cascade(label="Edit", menu=edit_menu)

        # Move menu
        move_menu = tkinter.Menu(self.menu, tearoff=0)
        move_menu.add_command(label="Cursor to document start", command=self.cursorToStart)
        move_menu.add_command(label="Cursor to document end", command=self.cursorToEnd)
        self.menu.add_cascade(label="Move", menu=move_menu)

    def clearDocument(self):
        self.model.clear()

    def deleteSelection(self):
        self.model.deleteRange(self.model.getSelectionRange())

    def closeWindow(self):
        self.master.destroy()

    def cursorToStart(self):
        self.model.cursorLocation = Location(0, 0)
        self.model.selectionRange = None
        self.show()

    def cursorToEnd(self):
        self.model.cursorLocation = Location(len(self.model.lines[-1]), len(self.model.lines) - 1)
        self.model.selectionRange = None
        self.show()


    def copySelection(self):
        selected = self.model.getSelectionRange()
        if selected:
            self.model.copySelection()

    def cutSelection(self):
        selected = self.model.getSelectionRange()
        if selected:
            self.model.cutSelection()

    def paste(self):
        self.model.paste()

    def pasteAndRemove(self):
        self.model.pasteAndRemove()

    def undo(self):
        pass

    def redo(self):
        pass


    def keyPressed(self, char):
        if char.isalnum() or char.isspace():
            self.model.insert(char)
        elif char == "\r":
            self.model.insert("\n")
        
    #2.5
    def updateText(self):
        self.delete("all")
        self.show()

    def shift_left(self, event):
        self.model.update_selection_range_left()

    def shift_right(self, event):
        self.model.update_selection_range_right()

    def shift_up(self, event):
        self.model.update_selection_range_up()

    def shift_down(self, event):
        self.model.update_selection_range_down()

    #2.4
    def updateCursorLocation(self, loc):
        self.drawCursor(loc)

    def drawCursor(self, location):
        self.delete("cursor")

        x = 10 + location.x * 12
        y = 10 + location.y * 20

        self.create_rectangle(x, y, x+1, y+20, fill="black", tag="cursor")

    def blink_cursor(self):
        self.cursor_visible = not self.cursor_visible
        self.drawCursor(self.model.cursorLocation) if self.cursor_visible else self.delete("cursor")
        self.after(500, self.blink_cursor)

    def show(self):
        y_offset = 10
        for line in self.model.allLines():
            self.create_text(10, y_offset, text=line, anchor="nw", font=("Courier", 15))
            y_offset += 20

        if self.model.selectionRange:
            start = self.model.selectionRange.start
            end = self.model.selectionRange.end
            if end.y < start.y or (end.y == start.y and end.x < start.x):
                start, end = end, start

            if start.y == end.y:
                #print("1")
                self.create_rectangle(start.x * 12 + 10, start.y * 20 + 10, end.x * 12 + 10, (end.y + 1) * 20 + 10, fill="grey", outline="", stipple="gray50")
            else:
                # First line
                #print("2")
                self.create_rectangle(start.x * 12 + 10, start.y * 20 + 10, len(self.model.lines[start.y]) * 12 + 10, (start.y + 1) * 20 + 10, fill="grey", outline="", stipple="gray50")
                # Middle lines
                for curr_row in range(start.y + 1, end.y):
                    self.create_rectangle(10, curr_row * 20 + 10, len(self.model.lines[curr_row]) * 12 + 10, (curr_row + 1) * 20 + 10, fill="grey", outline="", stipple="gray50")
                # Last line
                #print("3")
                self.create_rectangle(10, end.y * 20 + 10, end.x * 12 + 10, (end.y + 1) * 20 + 10, fill="grey", outline="", stipple="gray50")


        self.updateCursorLocation(self.model.cursorLocation)
        self.pack()