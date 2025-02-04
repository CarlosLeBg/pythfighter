# Installe les librairies nécessaires au projet si elles ne sont pas déjà installées

import subprocess
import sys
import importlib.util

def is_installed(package):
    return importlib.util.find_spec(package) is not None

def install(package):
    subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)

libraries = ["pygame", "loguru", "colorama", "httpx"]

for lib in libraries:
    if not is_installed(lib):
        try:
            install(lib)
        except subprocess.CalledProcessError:
            print(f"Failed to install {lib}")
    else:
        print(f"{lib} is already installed")