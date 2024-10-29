# MagiCoder
 
This is just a toy project for seeing how easy it was to get started with hugging face models running locally in python.

My main takeaway is that quantized models [(link to model)](https://huggingface.co/TheBloke/Magicoder-S-DS-6.7B-GGUF) run just fine with useable results, without quantization the speed of the code generation, at least with [MagiCoder](https://huggingface.co/ise-uiuc/Magicoder-S-DS-6.7B) is shockingly slow to an unusable degree.

The model was nice and straight forward to get running off the ground. Benchmarking was interesting to see where bottlenecks lied but I didn't do a thorough analysis because it would have taken days to run the original model against the quantized one, and I'm only on my laptop at the moment. I'll leverage my desktop machine in the near future to add more to this readme to make it actually interesting for analytics.
