import customtkinter
import tkinter as tk
from transformers import pipeline
import threading
import os
import configparser

MAGICODER_PROMPT = """You are an exceptionally intelligent coding assistant that consistently delivers accurate and reliable responses to user instructions.

@@ Instruction
{instruction}

@@ Response
"""

generator = None
generator_lock = threading.Lock()

class LoadingSpinner(tk.Toplevel):
    def __init__(self, parent, *args, **kwargs):
        tk.Toplevel.__init__(self, parent, *args, **kwargs)
        self.overrideredirect(True)
        self.geometry("+%d+%d" % (parent.winfo_rootx() + parent.winfo_reqwidth() // 2,
                                  parent.winfo_rooty() + parent.winfo_reqheight() // 2))
        self.spinner = tk.PhotoImage(file="./images/loading.gif")
        self.image_item = tk.Label(self, image=self.spinner)
        self.image_item.pack()

class TestManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Test Manager")

        self.config = configparser.ConfigParser()
        self.config_file = "config.ini"
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
            width = int(self.config.get("Window", "width", fallback=root.winfo_screenwidth()))
            height = int(self.config.get("Window", "height", fallback=root.winfo_screenheight()))
            x_position = int(self.config.get("Window", "x_position", fallback=0))
            y_position = int(self.config.get("Window", "y_position", fallback=0))
        else:
            width, height = root.winfo_screenwidth(), root.winfo_screenheight()
            x_position, y_position = 0, 0

        self.root.geometry(f"{width}x{height}+{x_position}+{y_position}")

        self.title = customtkinter.CTkLabel(self.root, height=10, width=50, text="MagiCoder")
        self.title.pack(pady=10, fill="x")

        self.loading_spinner = LoadingSpinner(self.root)
        self.loading_spinner.withdraw()

        text_frame = tk.Frame(self.root)
        text_frame.pack(expand=True, fill="both", padx=10, pady=0)

        self.input_textbox = tk.Text(text_frame, wrap="word", height=5, width=50)
        self.input_textbox.grid(row=0, column=0, sticky="nsew")

        self.output_textbox = tk.Text(text_frame, wrap="word", height=5, width=50, state="disabled")
        self.output_textbox.grid(row=1, column=0, sticky="nsew")

        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_rowconfigure(1, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)

        self.submit_button = customtkinter.CTkButton(self.root, text="Submit", command=self.submit)
        self.submit_button.pack(pady=5)

        generator_thread = threading.Thread(target=self.construct_generator)
        generator_thread.start()

        self.splash_screen = tk.Toplevel(root)
        self.splash_screen.title("Loading...")
        tk.Label(self.splash_screen, text="MagiCoder is initializing. Please wait...").pack(padx=20, pady=20)

        self.root.bind('<Return>', self.enter_pressed)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def construct_generator(self):
        global generator
        self.root.withdraw()
        try:
            with generator_lock:
                generator = pipeline(
                    model=".\models\Magicoder-S-DS-6.7B-GPTQ",
                    task="text-generation",
                    device_map="auto"
                )
        finally:
            self.root.deiconify()
            self.loading_spinner.withdraw()
            self.root.after(0, self.splash_screen.destroy)

    def submit(self):
        self.loading_spinner.deiconify()
        input_text = self.input_textbox.get("1.0", "end-1c")
        prompt = MAGICODER_PROMPT.format(instruction=input_text)

        with generator_lock:
            if generator is not None:
                result = generator(prompt, max_length=1024, num_return_sequences=1, temperature=0.0)
                generated_text = result[0]["generated_text"]
                
                print(generated_text)

                if generated_text.startswith(prompt):
                    generated_text = generated_text[len(prompt):].strip()

                self.output_textbox.configure(state="normal")
                self.output_textbox.delete("1.0", "end")
                self.output_textbox.insert("1.0", generated_text)
                self.output_textbox.configure(state="disabled")
                self.output_textbox.see("end")

                self.loading_spinner.withdraw()

    def enter_pressed(self, event):
        if not event.state & (1 << 0):
            self.submit()

    def on_close(self):
        self.config["Window"] = {
            "width": self.root.winfo_width(),
            "height": self.root.winfo_height(),
            "x_position": self.root.winfo_x(),
            "y_position": self.root.winfo_y()
        }

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.config["Window"]["width"] = str(min(int(self.config["Window"]["width"]), screen_width))
        self.config["Window"]["height"] = str(min(int(self.config["Window"]["height"]), screen_height))

        if (self.root.winfo_x() + self.root.winfo_width() > screen_width or
                self.root.winfo_y() + self.root.winfo_height() > screen_height):
            self.config["Window"]["x_position"] = "0"
            self.config["Window"]["y_position"] = "0"

        with open(self.config_file, "w") as configfile:
            self.config.write(configfile)
        self.root.destroy()


if __name__ == "__main__":
    root = customtkinter.CTk()
    app = TestManagerApp(root)
    root.mainloop()
