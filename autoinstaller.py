import subprocess
import sys

def install(package):
    subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)

libraries = ["pygame", "loguru", "colorama", "httpx", "faker"]

for lib in libraries:
    try:
        install(lib)
    except subprocess.CalledProcessError:
        print(f"Failed to install {lib}")