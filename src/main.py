from transformers import pipeline
import torch
import json

PROFILER = torch.autograd.profiler.profile(enabled=True, use_cuda=True, use_cpu=True, profile_memory=True)
MAGICODER_PROMPT = """You are an exceptionally intelligent coding assistant that consistently delivers accurate and reliable responses to user instructions.

@@ Instruction
{instruction}

@@ Response
"""

with open("instructions.json", "r") as file:
    instructions = json.load(file)

generator = pipeline(
    model="..\models\Magicoder-S-DS-6.7B-GPTQ",
    task="text-generation",
    torch_dtype=torch.bfloat16,
    device_map="auto",
    use_fast=True
)

inference_lambda = lambda prompt: generator(prompt, max_length=1024, num_return_sequences=1, temperature=0.0)

with PROFILER:
    for instruction in instructions:
        prompt = MAGICODER_PROMPT.format(instruction=instruction["instruction"])
        result = inference_lambda(prompt)
        print(result[0]["generated_text"])

print(PROFILER.key_averages().table(sort_by='self_cpu_time_total'))
PROFILER.export_chrome_trace("../benchmarking/trace.json")
