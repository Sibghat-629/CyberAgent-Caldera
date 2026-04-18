import autogen
import pkgutil
import os

def find_module(package, target):
    for loader, name, is_pkg in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
        if target in name:
            print(f"Found match: {name}")

try:
    import autogen
    print(f"AutoGen version: {autogen.__version__}")
    for loader, name, is_pkg in pkgutil.walk_packages(autogen.__path__, autogen.__name__ + "."):
        if "context_handling" in name or "token" in name:
            print(f"Candidate: {name}")
except Exception as e:
    print(f"Error: {e}")
