from Observers import ClipboardObserver

#2.7
class ClipboardStack:
    def __init__(self):
        self.texts = []
        self.observers = []

    def push(self, text: str):
        self.texts.append(text)
        self.notifyObservers()

    def pop(self):
        if self.texts:
            text = self.texts.pop()
            self.notifyObservers()
            return text
        return None

    def peek(self):
        if self.texts:
            return self.texts[-1]
        return None

    def isEmpty(self):
        return len(self.texts) == 0

    def clear(self):
        self.texts.clear()
        self.notifyObservers()

    def addObserver(self, observer: ClipboardObserver):
        self.observers.append(observer)

    def removeObserver(self, observer: ClipboardObserver):
        self.observers.remove(observer)

    def notifyObservers(self):
        for observer in self.observers:
            observer.updateClipboard()