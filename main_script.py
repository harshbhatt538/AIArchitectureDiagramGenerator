import sys
import os
import subprocess
from dotenv import load_dotenv
from openai import AzureOpenAI

# --- 0. Set up Command Line Arguments using sys ---
# sys.argv[0] is always the name of the script itself (e.g., main_script.py)
# sys.argv[1] will be your architecture text file
# sys.argv[2] will be your imports file (optional)

if len(sys.argv) < 2:
    print(" Error: You must provide the architecture text file.")
    print(" Usage: python3 main_script.py <architecture_file> [imports_file]")
    sys.exit(1)

architecture_file = sys.argv[1]

# If they provided a second argument, use it as the imports file. 
# Otherwise, default to "azure_imports.txt"
if len(sys.argv) >= 3:
    imports_file = sys.argv[2]
else:
    imports_file = "azure_imports.txt"

load_dotenv()
# 1. Retrieve the variables safely
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
api_key = os.getenv("AZURE_OPENAI_API_KEY")

client = AzureOpenAI(
    api_version="2024-12-01-preview",
    azure_endpoint=endpoint,
    api_key=api_key,
)

# --- NEW: Read the Cheat Sheet ---
try:
    with open(imports_file, "r") as file:
        cheat_sheet = file.read()
except FileNotFoundError:
    print(f" Error: Could not find '{imports_file}'. Please check the path!")
    sys.exit(1)

# --- 2. The System Instructions ---
system_prompt = f"""
You are an expert Cloud Architect and Python Developer. Your job is to read a plain text description of a cloud architecture and convert it into a fully functional Python script using the 'diagrams' library (by mingrammer).

You must output ONLY raw, valid Python code. Do not include markdown formatting (like ```python) and do not include explanations.

CRITICAL RULES FOR AZURE IMPORTS:
You must strictly follow these import paths. NEVER invent or guess module paths.
Don't assume edges of they are not specified   

IMPORT FORMATTING RULE:
You MUST put every single import on its own separate line. 
DO NOT group imports with commas.
BAD: `from diagrams.azure.network import VirtualNetworks, Subnets`
GOOD: 
`from diagrams.azure.network import VirtualNetworks`
`from diagrams.azure.network import Subnets`

{cheat_sheet}

Your Python script must:
1. Import Diagram, Cluster, and Edge from 'diagrams'.
2. ANTI-HALLUCINATION FALLBACK RULE: Check the cheat sheet above for the correct specific resource nodes. If the requested Azure service is NOT explicitly listed in the cheat sheet, do NOT attempt to guess its path. You MUST use a generic node to represent it: `from diagrams.azure.general import AllResources` (Rename the AllResources node to the name of the missing service).
3. Initialize the Diagram exactly like this, using graph_attr to force spacing and layout:
    graph_attr = {{
        "nodesep": "1.0", 
        "ranksep": "2.0", 
        "splines": "ortho", 
        "compound": "true"
    }}
    with Diagram("Enterprise Architecture", filename="ai_diagram", show=False, outformat="png", direction="LR", graph_attr=graph_attr) as diag:
4. Create Clusters for logical groupings.
5. Define the nodes and their connections using the >> and << operators.
6. INSIDE the 'with Diagram(...)' block at the very end, write the dot source to a file:
    with open("ai_diagram.dot", "w", encoding="utf-8") as f:
        f.write(diag.dot.source)
7. OUTSIDE the 'with Diagram(...)' block, run the conversion:
    import subprocess
    subprocess.run(["graphviz2drawio", "ai_diagram.dot", "-o", "ai_diagram.drawio"])
"""

# --- 3. Read your text description ---
try:
    with open(architecture_file, "r") as file:
        architecture_text = file.read()
except FileNotFoundError:
    print(f" Error: Could not find '{architecture_file}'. Please check the path!")
    sys.exit(1)

print(f" Reading architecture from '{architecture_file}'...")
print(f" Using imports cheat sheet from '{imports_file}'...")
print(" Asking AI to design the architecture and write the code... Please wait.")

# --- 4. Initialize the Conversation History ---
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": f"Generate the diagrams Python script for this architecture:\n\n{architecture_text}"}
]

max_retries = 10 

# --- 5. The Agentic Loop ---
for attempt in range(max_retries):
    print(f"\n--- Attempt {attempt + 1} of {max_retries} ---")
    
    # Call the AI
    response = client.chat.completions.create(
        model=deployment_name,
        messages=messages,
        temperature=0.1
    )

    # Extract the AI's code
    ai_code = response.choices[0].message.content

    # Append the AI's response to the history so it remembers what it wrote!
    messages.append({"role": "assistant", "content": ai_code})

    # Clean up markdown
    if ai_code.startswith("```python"):
        ai_code = ai_code.replace("```python\n", "").replace("```", "")
    elif ai_code.startswith("```"):
        ai_code = ai_code.replace("```\n", "").replace("```", "")

    # Save the code
    with open("generated_diagram_script.py", "w") as f:
        f.write(ai_code)

    print(" Executing the generated script...")

    # Run the script and CAPTURE the output and errors
    result = subprocess.run(
        ["python3", "generated_diagram_script.py"], 
        capture_output=True, 
        text=True
    )

    # Check if the script succeeded
    if result.returncode == 0:
        print(" Success! The script ran without errors.")
        print(" Check your folder for ai_diagram.png, ai_diagram.dot, and ai_diagram.drawio.")
        break # Exit the loop, we are done!
        
    else:
        # The script failed. Grab the error traceback.
        error_output = result.stderr
        print(f" The script had an error:\n{error_output}")
        
        if attempt < max_retries - 1:
            print(" Feeding the error back to the AI for correction...")
            
            # Formulate the feedback message
            feedback = f"""When I ran that code, it failed with this exact error:
{error_output}

CRITICAL INSTRUCTIONS TO FIX THIS:
1. If the error says 'Did you mean: <Name>?', you MUST use exactly that name.
2. Put EVERY import on its own separate line. Do NOT use commas to group them. 
3. Do NOT change the names of other imports that were not mentioned in the error.
4. If a class completely fails to import (like Bastion or VPNGateways) and has no 'Did you mean' suggestion, you MUST replace it with `from diagrams.azure.general import AllResources`. Do not guess another path.
Please provide the completely corrected, full Python script."""

            # Append the error feedback to the conversation history
            messages.append({"role": "user", "content": feedback})
        else:
            print(" Reached maximum retries. The AI could not fix the script.")