from transformers import pipeline
import threading

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
