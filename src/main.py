from transformers import pipeline
from pathlib import Path
import torch
import json

MAGICODER_PROMPT = """You are an exceptionally intelligent coding assistant that consistently delivers accurate and reliable responses to user instructions.

@@ Instruction
{instruction}

@@ Response
"""

with open("./src/instructions.json", "r") as file:
    instructions = json.load(file)

generator = pipeline(
    model=".\models\Magicoder-S-DS-6.7B-GPTQ",
    task="text-generation",
    device_map="auto"
)

inference_lambda = lambda prompt: generator(prompt, max_length=1024, num_return_sequences=1, temperature=0.0)

def trace_handler(p):
    output = p.key_averages().table(sort_by="self_cuda_time_total", row_limit=10)
    print(output)
    tracefile = "./benchmarking/trace_" + str(p.step_num) + ".json"
    Path(tracefile).touch()
    p.export_chrome_trace(tracefile)

with torch.profiler.profile(
    activities=[torch.profiler.ProfilerActivity.CPU, torch.profiler.ProfilerActivity.CUDA],
    schedule=torch.profiler.schedule(
        wait=1,
        warmup=1,
        active=2),
    on_trace_ready=trace_handler
) as p:
    for instruction in instructions:
        prompt = MAGICODER_PROMPT.format(instruction=instruction["instruction"])
        result = inference_lambda(prompt)
        print(result[0]["generated_text"])
        p.step()