import customtkinter
from Model import Model
from View import View
from Controller import Controller

if __name__ == "__main__":
    root = customtkinter.CTk()
    model = Model()   
    controller = Controller(model)
    view = View(root, controller)
    root.mainloop()
