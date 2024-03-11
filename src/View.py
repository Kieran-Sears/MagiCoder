import customtkinter
import tkinter as tk
import threading

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
            result = self.controller.submit(input_text)
            self.print_generated_text(result)
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