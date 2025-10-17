print("Test 1: Basic print")

import sys
print(f"Test 2: Python version: {sys.version}")

print("Test 3: Importing gradio...")
import gradio as gr
print("Test 4: Gradio imported successfully")

print("Test 5: Creating simple UI...")
def greet(name):
    return f"Hello {name}!"

iface = gr.Interface(fn=greet, inputs="text", outputs="text")
print("Test 6: UI created, launching on port 7863...")

iface.launch(server_port=7863, share=False, quiet=False)
