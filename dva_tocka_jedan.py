import tkinter

class graphicalComponent(tkinter.Canvas):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        
        self.create_line(100, 200, 300, 200, fill="red", width=1)
        self.create_line(200, 100, 200, 300, fill="red", width=1)

        self.create_text(150, 150, text="Prvi tekst")
        self.create_text(150, 250, text="Drugi tekst")

        self.bind("<Return>", lambda e: self.master.destroy())

        self.focus_set()
    

def main():
    root = tkinter.Tk()
    root.title("2.1")

    component = graphicalComponent(root, width=400, height=400)
    component.pack()

    root.mainloop()

if __name__ == '__main__':
    main()

"""Prvi dio tvog pitanja govori o oblikovnom obrascu "Okvirna metoda" (Template Method). 
Ovaj obrazac omogućava definiranje okvira algoritma u nadrazredu, ali omogućava podrazredima da implementiraju konkretne korake tog algoritma. 
U ovom slučaju, nadrazred (u tvojem primjeru, tkinter.Canvas) definira okvir za crtanje komponenti, 
ali ostavlja konkretne detalje crtanja podrazredima (u tvom slučaju, graphicalComponent).

Drugi dio tvog pitanja odnosi se na oblikovni obrazac "Promatrač" (Observer). 
U tvojem kodu, self.bind("<Return>", lambda e: self.master.destroy()) omogućava grafičkoj 
komponenti da "promatra" događaj pritiska na tipku <Return> i reagira na njega. 
Opservator omogućava objektima da se pretplate na promjene u drugom objektu i automatski reagiraju na te promjene. 
U ovom slučaju, grafička komponenta pretplaćuje se na događaj pritiska na tipku <Return> i reagira uništavanjem glavnog prozora."""