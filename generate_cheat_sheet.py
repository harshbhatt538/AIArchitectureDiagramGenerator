import inspect
import pkgutil
import diagrams.azure

print("Scanning local diagrams package for exact Azure imports...")

with open("azure_imports.txt", "w") as f:
    f.write("EXACT AZURE IMPORTS AVAILABLE ON THIS MACHINE:\n")
    
    # Loop through all submodules in diagrams.azure
    for _, modname, _ in pkgutil.iter_modules(diagrams.azure.__path__):
        full_module_name = f"diagrams.azure.{modname}"
        try:
            # Import the module
            module = __import__(full_module_name, fromlist=["*"])
            
            # Find all classes defined inside it
            classes = [name for name, obj in inspect.getmembers(module, inspect.isclass) 
                       if obj.__module__ == full_module_name]
            
            if classes:
                f.write(f"\n[{full_module_name}]\n")
                for c in classes:
                    f.write(f"from {full_module_name} import {c}\n")
        except Exception:
            pass

print("Done! 'azure_imports.txt' has been generated.")