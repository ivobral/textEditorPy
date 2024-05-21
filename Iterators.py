#2.3
class AllLines:
    def __init__(self, lines):
        self.lines = lines
        self.index = 0
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.index < len(self.lines):
            line = self.lines[self.index]
            self.index += 1
            return line
        else:
            raise StopIteration
        
class LinesRange:
    def __init__(self, lines, start, end):
        self.lines = lines
        self.index = start
        self.end = end
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.index < self.end:
            line = self.lines[self.index]
            self.index += 1
            return line
        else:
            raise StopIteration