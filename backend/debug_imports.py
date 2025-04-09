import sys
import os
import importlib.util

print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print("\nPython path:")
for path in sys.path:
    print(f"  - {path}")

def check_module(module_name):
    print(f"\nChecking module: {module_name}")
    try:
        spec = importlib.util.find_spec(module_name)
        if spec is None:
            print(f"  - Module {module_name} not found in sys.path")
            # Check if the module exists with a different name format (dash vs underscore)
            alt_name = module_name.replace("_", "-")
            alt_spec = importlib.util.find_spec(alt_name)
            if alt_spec:
                print(f"  - But found as {alt_name} at {alt_spec.origin}")
            else:
                print(f"  - Also not found as {alt_name}")
        else:
            print(f"  - Found at {spec.origin}")
            try:
                module = importlib.import_module(module_name)
                print(f"  - Successfully imported")
                return True
            except ImportError as e:
                print(f"  - Import error: {str(e)}")
                return False
    except Exception as e:
        print(f"  - Error checking module: {str(e)}")
        return False

# Check problematic modules
modules_to_check = [
    "aiofiles",
    "PyPDF2",
    "pdfplumber", 
    "docx",
    "langchain_community",
    "langchain_community.embeddings",
    "langchain_google_genai",
    "bs4"
]

for module in modules_to_check:
    check_module(module)

# Try to import and use one of the modules
print("\nTrying to use PyPDF2:")
try:
    from PyPDF2 import PdfReader
    print("  - Successfully imported PdfReader from PyPDF2")
except ImportError as e:
    print(f"  - Failed to import PdfReader: {str(e)}")

print("\nTrying to use langchain_community:")
try:
    from langchain_community.embeddings import HuggingFaceEmbeddings
    print("  - Successfully imported HuggingFaceEmbeddings from langchain_community.embeddings")
except ImportError as e:
    print(f"  - Failed to import HuggingFaceEmbeddings: {str(e)}")
