from Plugins.PluginInterface import PluginInterface
from tkinter import messagebox

class UppercasePlugin(PluginInterface):
    def getName(self):
        return "Uppercase"
    
    def getDescriptions(self):
        return "This plugin converts all first letters of words to uppercase."
    
    def execute(self, model, clipboardStack):
        #convert all first letters of words to uppercase
        text = model.getText()
        text = text.title()
        model.setText(text)

        messagebox.showinfo("Uppercase", "All first letters of words are converted to uppercase.")
    
        
