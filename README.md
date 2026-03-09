# AI Architecture Diagram Generator

This tool uses **Azure OpenAI (GPT-4o)** to automatically generate cloud architecture diagrams from plain text descriptions.

It produces:

- Standard **PNG images**
- Raw **Graphviz DOT files**
- Editable **Draw.io files**

---

# 1. Prerequisites & Dependencies

Before running the script, you must install the following **system and Python dependencies**.

---

## System-Level Dependencies

The **diagrams** library requires **Graphviz** to render the images.  
Installing `graphviz` via `pip` is **not enough** — you must install the **system package**.

### Ubuntu / Debian

```bash
sudo apt-get install graphviz
```

### macOS

```bash
brew install graphviz
```

### Windows

Download from the **Graphviz website** and add it to your **PATH**.

---

### Draw.io Conversion Tool

You also need the tool that converts the diagram to an **editable Draw.io format**.

Install:

```bash
pip install graphviz2drawio
```

or (depending on your environment)

```bash
npm install graphviz2drawio
```

---

## Python Packages

Install the required Python libraries:

```bash
pip install openai diagrams
```

---

# 2. Configuration (Azure OpenAI)

This project uses **environment variables** to securely store Azure OpenAI credentials.

Instead of hardcoding keys in the script, credentials are loaded from a `.env` file using **python-dotenv**.


## Install Additional Dependency

Install `python-dotenv`:

```bash
pip install python-dotenv
```

---

## Create a `.env` File

Create a file named `.env` in the same directory as `main_script.py`.

Example:

```
AZURE_OPENAI_ENDPOINT=https://your-resource-name.cognitiveservices.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_API_KEY=your_api_key_here
```

---

## Environment Variables Explained

| Variable | Description |
|------|------|
| `AZURE_OPENAI_ENDPOINT` | Your Azure OpenAI resource endpoint |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | Your model deployment name in Azure |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key |

---

## Example `.env`

```
AZURE_OPENAI_ENDPOINT=https://my-openai-resource.cognitiveservices.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## How the Script Loads These Variables

The script automatically loads the `.env` file:

```python
from dotenv import load_dotenv
import os

load_dotenv()

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
```

This approach is **more secure and production-friendly** than hardcoding credentials.

---

**Important**

Never commit your `.env` file to GitHub.

Add it to `.gitignore`:

```
.env
```

---

#  3. File Structure

To run this tool, you need **three files in the same directory**:

```
project-folder/
│
├── main_script.py
├── architecture.txt
└── azure_imports.txt
```

### File Descriptions

**main_script.py**

The main program that:

- Calls Azure OpenAI
- Generates Python diagram code
- Executes the code to generate architecture diagrams

---

**architecture.txt**

Contains your **plain text architecture description**.

Example:

```
Users connect to an Azure Application Gateway.
The gateway routes traffic to an AKS cluster.
AKS connects to Azure SQL Database and Azure Storage.
```

---

**azure_imports.txt**

A **cheat sheet of valid diagrams module paths**.

This prevents the AI from **hallucinating incorrect resource names**.

---

# 4. Generating the Azure Import Cheat Sheet

The file `azure_imports.txt` contains all valid **Azure node classes from the diagrams library**.  
This helps prevent the AI from **hallucinating incorrect import paths**.

Instead of writing this file manually, you can automatically generate it using a helper script.

---

## Create the Script

Create a file named:

```
generate_cheat_sheet.py
```

Add the following code:

```python
import pkgutil
import diagrams.azure as azure

def generate():
    with open("azure_imports.txt", "w") as f:
        # Walk through the azure submodules (compute, network, storage, etc.)
        for loader, module_name, is_pkg in pkgutil.walk_packages(azure.__path__, azure.__name__ + "."):
            try:
                # Import the module dynamically
                module = loader.find_module(module_name).load_module(module_name)

                # Find all classes inside that module
                for attribute_name in dir(module):
                    attribute = getattr(module, attribute_name)

                    if isinstance(attribute, type):
                        f.write(f"{module_name}.{attribute_name}\n")

            except Exception as e:
                print(f"Error processing {module_name}: {e}")

if __name__ == "__main__":
    generate()
    print("Success: azure_imports.txt has been generated!")
```

---

## Run the Script

Make sure the `diagrams` library is installed:

```bash
pip install diagrams
```

Then run:

```bash
python3 generate_cheat_sheet.py
```

---

## Output

A new file will be created:

```
azure_imports.txt
```

Example contents:

```
diagrams.azure.compute.VM
diagrams.azure.network.LoadBalancers
diagrams.azure.database.SQLDatabases
diagrams.azure.storage.StorageAccounts
```

This file acts as a **cheat sheet** that tells the AI exactly which Azure components are valid in the `diagrams` library.

---

**Note**

You only need to generate this file **once**, unless you upgrade the `diagrams` library and want to refresh the available Azure resources.

---

#  5. How to Run

The script accepts **command-line arguments**.

You must provide the **architecture description file**.


## Standard Run

```bash
python3 main_script.py architecture.txt
```



## Custom Imports File Run

If you want to use a **different cheat sheet** instead of the default `azure_imports.txt`:

```bash
python3 main_script.py architecture.txt custom_imports.txt
```
---

#  6. Outputs

If the script runs successfully, it will generate **three files** in the current directory.

---

### ai_diagram.png

High-resolution architecture image.

---

### ai_diagram.dot

Raw **Graphviz DOT source code**.

---

### ai_diagram.drawio

Editable **Draw.io diagram**.

You can open this file in:

https://app.diagrams.net/



#  Result

You can now generate **production-quality cloud architecture diagrams automatically from plain English descriptions**.

# 7. Model Compatibility (Azure OpenAI / Other Models)

The provided script is **not strictly limited to a single model**, but it is currently configured to use an **Azure OpenAI GPT deployment**.

Example from the script:

```python
deployment_name = "gpt-4o"
```

This value refers to the **deployment name you created inside Azure OpenAI**, not necessarily the exact model name.

---

# Default Model

The script was tested with:

```
gpt-4o
```

This model works well because:

- It produces **consistent Python code**
- It follows **strict instructions**
- It works reliably with **large prompts**
- It performs well in **agentic retry loops**

---

# Using a Different Azure OpenAI Model

If you deployed another model in **Azure OpenAI**, you only need to change this line:

```python
deployment_name = "gpt-4o"
```

Examples:

### GPT-4.1

```python
deployment_name = "gpt-4.1"
```

### GPT-4 Turbo

```python
deployment_name = "gpt-4-turbo"
```

 **Important:**  
The value must match your **Azure deployment name**, not just the model name.

You can find it in:

```
Azure Portal
→ Azure OpenAI Resource
→ Model Deployments
→ Deployment Name
```

---

# Using OpenAI API (Non-Azure)

If you want to use **OpenAI directly instead of Azure**, modify the client initialization.

### Replace this

```python
from openai import AzureOpenAI

client = AzureOpenAI(
    api_version="2024-12-01-preview",
    azure_endpoint=endpoint,
    api_key=api_key,
)
```

### With this

```python
from openai import OpenAI

client = OpenAI(api_key="YOUR_OPENAI_KEY")
```

Then keep the model call like this:

```python
response = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    temperature=0.1
)
```

---

# Using Other AI Models (Claude, Gemini, Ollama)

The current implementation is designed for **Azure OpenAI models** using the `AzureOpenAI` client.

Because of this, the script **cannot directly work** with models like:

- Claude (Anthropic)
- Gemini (Google)
- Local models (Ollama / Llama)
- Other providers

However, the tool **can still work with them** if you replace the **API client and request format**.

---

## 1. Using Anthropic (Claude 3.5 Sonnet)

Install the Anthropic SDK:

```bash
pip install anthropic
```

Example implementation:

```python
import anthropic

client = anthropic.Anthropic(
    api_key="YOUR_ANTHROPIC_KEY"
)

response = client.messages.create(
    model="claude-3-5-sonnet-20240620",
    max_tokens=4000,
    messages=messages
)

ai_code = response.content[0].text
```

Important differences:

- Claude uses the **messages API**
- Output is accessed using:

```
response.content[0].text
```

---

## 2. Using Google Gemini

Install the Gemini SDK:

```bash
pip install google-generativeai
```

Example usage:

```python
import google.generativeai as genai

genai.configure(api_key="YOUR_GEMINI_KEY")

model = genai.GenerativeModel("gemini-1.5-pro")

response = model.generate_content(system_prompt + architecture_text)

ai_code = response.text
```

---

## 3. Using Local Models (Ollama / Llama)

You can run the tool **fully locally** using Ollama.

Install Ollama:

```
https://ollama.com
```

Pull a model:

```bash
ollama pull llama3
```

Example Python integration:

```python
import requests

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "llama3",
        "prompt": system_prompt + architecture_text,
        "stream": False
    }
)

ai_code = response.json()["response"]
```

---

## Model Requirements

For this tool to work properly, the model must support:

- **Chat completions**
- **Long context prompts**
- **Structured code generation**

Small models may:

- hallucinate imports
- generate invalid Python
- break the diagram script


---

# Summary

| Feature | Requirement |
|------|------|
| Default model | GPT-4o |
| Compatible models | GPT-4-class or equivalent |
| Azure OpenAI | Supported by default |
| OpenAI API | Supported with small change |
| Claude / Gemini / Ollama | Supported with API modifications |

