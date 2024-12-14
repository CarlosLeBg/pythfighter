import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Liste des bibliothèques à installer
libraries = ["pygame","loguru"]

for lib in libraries:
    install(lib)
