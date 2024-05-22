from Plugins.PluginInterface import PluginInterface
from tkinter import messagebox
from Clipboard import ClipboardStack

class StatisticsPlugin(PluginInterface):
    def getName(self):
        return "Statistics"
    
    def getDescriptions(self):
        return "This plugin calculates number of lines, words and characters in the text."
    
    def execute(self, model, clipboardStack: ClipboardStack): 
        text = model.getText()
        lines = len(text.split("\n"))
        words = len(text.split())
        characters = len(text)
        messagebox.showinfo("Statistics", "Number of lines: " + str(lines) + "\nNumber of words: " + str(words) + "\nNumber of characters: " + str(characters))
