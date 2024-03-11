import customtkinter
from model import Model
from view import View
from controller import Controller

if __name__ == "__main__":
    root = customtkinter.CTk()
    model = Model()   
    controller = Controller(model)
    view = View(root, controller)
    root.mainloop()
