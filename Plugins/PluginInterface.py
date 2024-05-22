import abc
from Clipboard import ClipboardStack

class PluginInterface(abc.ABC):

    @abc.abstractmethod
    def getName(self):
        pass

    @abc.abstractmethod
    def getDescriptions(self):
        pass

    @abc.abstractmethod
    def execute(self, model, ClipboardStack: ClipboardStack):
        pass