# You do not train the GGUF, you train the model behind it

*The spoken edition of The Working Copy for 2026-11-23. Narrated by Uncle Burt.*

There is a sentence you will hear around local AI, and it is usually wrong: train your GGUF. You cannot train a GGUF. A GGUF is the packed file that llama.cpp and Ollama run. It is the finish line, not the starting block. Both of the published walkthroughs this edition draws on put the GGUF at the end: train the model, merge the adapter, convert the merged model, quantize it, and only then serve it.

That order explains why the tutorials spend so long on steps that feel like cleanup. The merge and the conversion are not housekeeping. They are where the model you trained becomes a model you can run. Do them in the wrong order, or skip them, and the adapter stays a sidecar that most local runners never see.

So what is actually being trained? A low-rank adapter, usually called LoRA. Instead of rewriting every weight in the base model, you train a small set of extra weights that sit beside the frozen model and steer its behavior. QLoRA is the same idea with one more economy: the frozen base model is loaded in a compressed four-bit form, which is what lets a modest graphics card hold a model that would not otherwise fit. You train the adapter against that compressed model, and later you merge it into a full-precision copy.

Start with a small base model. The beginner guide uses a small instruct model under four billion parameters, which loads in four-bit form in about six gigabytes of graphics memory. That is small enough for a free cloud notebook. The same guide puts seven- and eight-billion-parameter models at roughly twelve gigabytes, and a nine-billion model at about fourteen. The pipeline does not change with size. The small model just fails faster and costs less to fix, which is exactly what a first run should do.

Now the part that decides whether any of this works: your data.

Fine-tuning is not a way to pour facts into a model. The beginner guide lists fine-tuning to add facts as a common mistake, and points to retrieval instead: search your own documents, hand the useful passages to the model, and let it answer from them. What fine-tuning is good at is behavior. The shape of an answer. A house style. A strict output format. A consistent way of classifying a request.

The file is usually JSON Lines, which sounds technical and is simple: one example per line, and each example is a short conversation. A system instruction, a user message, and the assistant's reply. The twelve-step walkthrough uses prompt and completion objects instead, and it notes that the training loss is computed only on the completion, meaning the assistant's answer is the part being taught. Either format works. What matters is that each line is valid, every example has an assistant turn, and the assistant turn is last.

When you write those examples by hand, keep one voice and one format. The walkthrough's support-ticket task gives every example the same four output keys, and the labels follow fixed rules. That uniformity is the point. You are teaching a pattern, not a pile of trivia, and the model learns the pattern from the shape of your examples whether or not you meant to teach it.

The beginner guide's advice on size is several hundred to a few thousand well-curated examples. More junk does not help. It teaches junk. And you hold some examples back. The twelve-step walkthrough starts with eight hundred training rows and one hundred test rows, and those hundred never enter training. They are how you find out whether the model learned the task or memorized the answers.

Before the expensive part, check the file. A small script that reads your JSON Lines file reports malformed lines, missing assistant turns, and the shortest and longest example. A file where one example is three words and another is three thousand is a file with a sizing problem. The check is not a quality judge. It cannot tell you that a label is wrong or that your test rows leaked into training. It makes the cheap, mechanical failures fail loudly, which is the hour you most want to save.

Then you train, merge, convert and run.

The twelve-step walkthrough's settings are a reasonable default: rank sixteen, alpha thirty-two, a small dropout, all linear layers, a learning rate of two times ten to the minus four, two epochs, and an eight-bit paged optimizer. Do not raise the learning rate for luck. The walkthrough warns that pushing it higher invites the loss to explode into not-a-number, and a run that goes to not-a-number is a run you repeat from scratch.

When training finishes, merge the adapter into a full-precision copy of the base model, on the processor, and never into the compressed four-bit weights. The walkthrough is explicit about this. Merging into the compressed weights re-quantizes the model and discards much of what the adapter learned. Merge in full precision, save the merged model, and convert that.

The conversion produces a full-precision GGUF, the packed file that llama.cpp and Ollama understand. Then quantize it, commonly to a four-bit format. Quantization shrinks the file and speeds it up at a small cost in quality. Keep the full-precision file until the quantized one passes your test, then delete it. On the walkthrough's larger example, the practical disk requirement is a hundred and fifty gigabytes, and the full-precision file is the first thing to remove. That number is not a typo. A model big enough to be interesting is also big enough to fill a laptop.

The last piece is the Modelfile, the recipe Ollama uses to create a runnable model. The walkthrough recommends starting from the base model's own Modelfile, which already contains the right chat template and stop tokens, and changing only the line that names the source file. The chat template is the format the model expects for a conversation: where the system prompt goes, how the user's turn is marked, how the assistant's turn begins. The beginner guide calls a template mismatch one of the hardest problems to diagnose, and the walkthrough warns that missing end-of-sequence handling causes endless generation. A good model with the wrong template will babble, repeat itself, or never stop.

Finally, evaluate. Send the held-out examples to the model with temperature at zero, so the answers are as repeatable as possible, and score them. Keep the same held-out rows for every run; if you change the test set between attempts, you cannot tell which change helped. If the output is supposed to be strict JSON with four keys, count a parse failure as a miss on every metric. The walkthrough requires all four keys and scores both structure and label accuracy, and it compares the fine-tuned model against the base model on the same rows. If the fine-tune is not better, you learned something for the price of a few hours, which is a bargain compared with shipping it and finding out later.

There is one more rule that sounds legal and is actually practical. Check the base model's license before you plan to share the result. The walkthrough lists it among the pitfalls for a reason. A fine-tune inherits the terms of the model it was built from.

So the honest summary is this. You cannot train a GGUF. You train a small model with an adapter. You merge the adapter in full precision. You convert the merged model to GGUF, quantize it, and serve it with Ollama. Your data decides whether the result is useful, and the chat template decides whether it works at all.

Your next step is small and concrete. Pick one narrow task you actually care about. Write twenty or thirty examples by hand. Run a small structural check on the file. If it is clean, you have the smallest possible first training run, and a real reason to make space on the disk. If it is not, you just saved yourself an afternoon of graphics memory.
