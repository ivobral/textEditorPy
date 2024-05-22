import tkinter
from Location import Location
from textEditorModel import TextEditorModel
from Observers import CursorObserver, CursorObserverHelper

import os
import importlib
from Plugins.PluginInterface import PluginInterface


class TextEditor(tkinter.Canvas, CursorObserver):
    def __init__(self, model: TextEditorModel, master=None, **kwargs):
        #2.2
        super().__init__(master, **kwargs)
        self.model = model
        self.focus_set()
    
        #2.4
        self.model.addCursorObserver(self)
        self.cursor_visible = True
        #self.blink_cursor()
        self.cursorObserverHelper = CursorObserverHelper(self)
        self.model.addCursorObserver(self.cursorObserverHelper)

        #2.5
        self.model.addTextObserver(self)
        """

        self.plugins = self.loadPlugin()
        self.menu()
        self.statusBar = tkinter.Label(master, text="Line: 1, Column: 1", bd=1, relief=tkinter.SUNKEN, anchor=tkinter.W)
        
        
        """
        #close the window using Alt+F4
        self.bind("<Alt-F4>", lambda e: self.closeWindow())

        #2.4
        self.bind("<Left>", lambda e: self.model.moveCursorLeft())
        self.bind("<Right>", lambda e: self.model.moveCursorRight())
        self.bind("<Up>", lambda e: self.model.moveCursorUp())
        self.bind("<Down>", lambda e: self.model.moveCursorDown())

        #2.5
        self.bind("<BackSpace>", lambda e: self.model.deleteBefore())
        self.bind("<Delete>", lambda e: self.model.deleteAfter())

        self.bind('<Shift-Left>', lambda e: self.model.selectionRangeLeft())
        self.bind('<Shift-Right>', lambda e: self.model.selectionRangeRight())
        self.bind('<Shift-Up>', lambda e: self.model.selectionRangeUp())
        self.bind('<Shift-Down>', lambda e: self.model.selectionRangeDown())

        #2.6
        self.bind('<Key>', lambda e: self.keyPressed(e.char))
        """
        self.bind('<Control-c>', lambda e: self.copySelection())
        self.bind('<Control-x>', lambda e: self.cutSelection())
        self.bind('<Control-v>', lambda e: self.paste())
        self.bind('<Control-Shift-V>', lambda e: self.pasteAndRemove())

        self.bind('<Control-z>', lambda e: self.undo())
        self.bind('<Control-y>', lambda e: self.redo())

    #method for loading plugins
    def loadPlugin(self):
        plugins = []
        for file in os.listdir("Plugins"):
            if file.endswith(".py"):
                plugin_name = file[:-3]
                spec = importlib.util.spec_from_file_location(plugin_name, os.path.join("Plugins", file))
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                for name, obj in module.__dict__.items():
                    if isinstance(obj, type) and issubclass(obj, PluginInterface) and obj is not PluginInterface:
                        plugins.append(obj())
        return plugins
    
    def menu(self):
        self.menu = tkinter.Menu(self.master)
        self.master.config(menu=self.menu)

        file_menu = tkinter.Menu(self.menu, tearoff=0)
        file_menu.add_command(label="Open", command=self.openFile)
        file_menu.add_command(label="Save", command=self.save)
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

        # Plugins menu
        plugins_menu = tkinter.Menu(self.menu, tearoff=0)
        for plugin in self.plugins:
            plugins_menu.add_command(label=plugin.getName(), command=lambda plugin=plugin: plugin.execute(self.model, None))
        self.menu.add_cascade(label="Plugins", menu=plugins_menu)

    def openFile(self):
        with open("text.txt", "r") as file:
            self.model.setText(file.read())

    def save(self):
        with open("text.txt", "w") as file:
            file.write(self.model.getText())

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
    """
    def cursorToEnd(self):
        self.model.cursorLocation = Location(len(self.model.lines[-1]), len(self.model.lines) - 1)
        self.model.selectionRange = None
        self.drawCursor(self.model.cursorLocation)
        self.show()
    """
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
    """
    #2.6
    def keyPressed(self, char):
        if char:
            if char.isalnum() or char in ".,;:?!-()[]{} ":
                self.model.insert(char)
            elif char == "\r" or char == "\n":
                self.model.insert("\n")
        else:
            pass

    #2.5
    def updateText(self):
        self.delete("all")
        self.show()

    #2.4
    def updateCursorLocation(self, loc):
        self.drawCursor(loc)
        #2.10
        #self.statusBar.config(text=f"Ln: {loc.y + 1}, Col: {loc.x + 1}, Number of lines: {len(self.model.lines)}")

    def drawCursor(self, location):
        self.delete("cursor")

        x = 10 + location.x * 12    #width of a character
        y = 10 + location.y * 20    #height of a character

        self.create_rectangle(x, y, x+1, y+20, fill="black", tag="cursor")
    
    def blink_cursor(self):
        self.cursor_visible = not self.cursor_visible
        self.drawCursor(self.model.cursorLocation) if self.cursor_visible else self.delete("cursor")
        self.after(500, self.blink_cursor)
    
    #2.2, 2.3, 2.4, 2.5
    def show(self):
        #2.2
        y_offset = 10
        for line in self.model.allLines():
            self.create_text(10, y_offset, text=line, anchor="nw", font=("Courier", 15), tag="text")
            y_offset += 20

        #2.5
        if self.model.selectionRange:
            start = self.model.getSelectionRange().start
            end = self.model.getSelectionRange().end

            # Normalize the selection range so that start is before end
            if end.y < start.y or (end.y == start.y and end.x < start.x):
                start, end = end, start

            # If the selection is on a single line draw a single rectangle
            if start.y == end.y:
                self.create_rectangle(start.x * 12 + 10, start.y * 20 + 10, end.x * 12 + 10, (end.y + 1) * 20 + 10, fill="grey", outline="", stipple="gray50")
            else: # If the selection spans multiple lines draw multiple rectangles
                # First line
                self.create_rectangle(start.x * 12 + 10, start.y * 20 + 10, len(self.model.lines[start.y]) * 12 + 10, (start.y + 1) * 20 + 10, fill="grey", outline="", stipple="gray50")
                # Middle lines
                for curr_row in range(start.y + 1, end.y):
                    self.create_rectangle(10, curr_row * 20 + 10, len(self.model.lines[curr_row]) * 12 + 10, (curr_row + 1) * 20 + 10, fill="grey", outline="", stipple="gray50")
                # Last line
    
                self.create_rectangle(10, end.y * 20 + 10, end.x * 12 + 10, (end.y + 1) * 20 + 10, fill="grey", outline="", stipple="gray50")
        #2.4
        #self.updateCursorLocation(self.model.cursorLocation)

        #2.10
        #self.statusBar.pack(side=tkinter.BOTTOM, fill=tkinter.X)

        #2.2
        self.pack()