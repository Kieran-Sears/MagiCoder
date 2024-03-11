import customtkinter
import tkinter as tk
from transformers import pipeline
import threading
import os
import configparser

class Model:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config_file = "config.ini"
        self.default_prompt = """
        You are an exceptionally intelligent coding assistant that consistently delivers accurate and reliable responses to user instructions.
        @@ Instruction
        {instruction}
        @@ Response
        """

    def load_model(self):
        return {"model": ".\models\Magicoder-S-DS-6.7B-GPTQ", "task": "text-generation", "device_map": "auto"}
                

    def load_display_properties(self, width, height, x_position, y_position):
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
            width = int(self.config.get("Window", "width", fallback=width))
            height = int(self.config.get("Window", "height", fallback=height))
            x_position = int(self.config.get("Window", "x_position", fallback=x_position))
            y_position = int(self.config.get("Window", "y_position", fallback=y_position))
        return width, height, x_position, y_position

    def load_prompt(self, instruction):
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
            prompt = self.config.get("Model", "prompt", fallback=self.default_prompt)
            return prompt.format(instruction=instruction)
        else:
            return self.default_prompt.format(instruction=instruction)

class Controller:
    def __init__(self, model):
        self.model = model
        self.generator_lock = threading.Lock()
        self.generator = None

    def initialise_generator(self):
        model_config = self.model.load_model()
        self.generator = pipeline(model=model_config["model"], task=model_config["task"], device_map=model_config["device_map"])

    def submit(self, user_input):
        with self.generator_lock:
            if self.generator is not None:
                prompt = self.model.load_prompt(user_input) 
                result = self.generator(prompt, max_length=1024, num_return_sequences=1, temperature=0.0)
                generated_text = result[0]["generated_text"][len(prompt):].strip()
                print(generated_text)
                view.print_generated_text(generated_text)

class View:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller

        self.splash_screen = tk.Toplevel(root)
        self.splash_screen.title("Loading...")
        tk.Label(self.splash_screen, text="MagiCoder is initializing. Please wait...").pack(padx=20, pady=20)

        self.root.title("Test Manager")
        self.set_window_geometry(*self.controller.model.load_display_properties(self.root.winfo_screenwidth(), self.root.winfo_screenheight(), 0, 0))

        self.title = customtkinter.CTkLabel(self.root, height=10, width=50, text="MagiCoder")
        self.title.pack(pady=10, fill="x")

        self.loading_spinner = None

        text_frame = tk.Frame(self.root)
        text_frame.pack(expand=True, fill="both", padx=10, pady=0)

        self.input_textbox = tk.Text(text_frame, wrap="word", height=5, width=50)
        self.input_textbox.grid(row=0, column=0, sticky="nsew")

        self.output_textbox = tk.Text(text_frame, wrap="word", height=5, width=50, state="disabled")
        self.output_textbox.grid(row=1, column=0, sticky="nsew")

        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_rowconfigure(1, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)

        self.submit_button = customtkinter.CTkButton(self.root, text="Submit", command=self.handle_submit)
        self.submit_button.pack(pady=5)

        self.root.bind('<Return>', self.handle_submit)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.generator = None
        self.generator_lock = threading.Lock()

        generator_thread = threading.Thread(target=self.construct_generator)
        generator_thread.start()

    def construct_generator(self):
        self.root.withdraw()
        try:
            with self.generator_lock:
                self.generator = self.controller.initialise_generator()
        finally:
            self.root.deiconify()
            self.root.after(0, self.splash_screen.destroy)

    def handle_submit(self, event=None):
        if not event.state & (1 << 0) or event is None:
            self.loading_spinner = self.show_loading_spinner()
            input_text = self.input_textbox.get("1.0", "end-1c")
            self.controller.submit(input_text)
            if self.loading_spinner:
                    self.loading_spinner.withdraw()

    def set_window_geometry(self, width, height, x_position, y_position):
        self.root.geometry(f"{width}x{height}+{x_position}+{y_position}")

    def show_loading_spinner(self):
        loading_spinner = tk.Toplevel(self.root)
        loading_spinner.overrideredirect(True)
        loading_spinner.geometry("+%d+%d" % (self.root.winfo_rootx() + self.root.winfo_reqwidth() // 2,
                                            self.root.winfo_rooty() + self.root.winfo_reqheight() // 2))
        spinner = tk.PhotoImage(file="./images/loading.gif")
        image_item = tk.Label(loading_spinner, image=spinner)
        image_item.pack()
        return loading_spinner

    def print_generated_text(self, generated_text):
        self.output_textbox.configure(state="normal")
        self.output_textbox.delete("1.0", "end")
        self.output_textbox.insert("1.0", generated_text)
        self.output_textbox.configure(state="disabled")
        self.output_textbox.see("end")
    
    def on_close(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.controller.model.config["Window"]["width"] = str(min(int(self.controller.model.config["Window"]["width"]), screen_width))
        self.controller.model.config["Window"]["height"] = str(min(int(self.controller.model.config["Window"]["height"]), screen_height))

        if (self.root.winfo_x() + self.root.winfo_width() > screen_width or
                self.root.winfo_y() + self.root.winfo_height() > screen_height):
            self.controller.model.config["Window"]["x_position"] = "0"
            self.controller.model.config["Window"]["y_position"] = "0"

        with open(self.controller.model.config_file, "w") as configfile:
            self.controller.model.config.write(configfile)
        self.root.destroy()


if __name__ == "__main__":
    root = customtkinter.CTk()
    model = Model()   
    controller = Controller(model)
    view = View(root, controller)
    root.mainloop()
