import tkinter
from textEditorModel import TextEditorModel
from textEditor import TextEditor

def main():
    root = tkinter.Tk()
    root.title("Text Editor")

    model = TextEditorModel("Ab ovo.\nAd astra.\nCarpe diem!\nDictum, factum.\nHomo homini lupus est.\nAlea iacta est!\nPro domo!")
    editor = TextEditor(model, root, width=400, height=400, bg="#e6fffa")

    editor.show()

    root.mainloop()

if __name__ == "__main__":
    main()