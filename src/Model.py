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