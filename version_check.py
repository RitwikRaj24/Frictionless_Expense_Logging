import sys
import flet as ft

print("--- DIAGNOSTIC REPORT ---")
print(f"PYTHON EXECUTABLE: {sys.executable}")
print(f"PYTHON VERSION: {sys.version}")

try:
    print(f"FLET VERSION: {ft.version.version}")
except AttributeError:
    try:
        # Fallback for very old versions
        print(f"FLET VERSION: {ft.__version__}")
    except:
        print("FLET VERSION: Unknown (Very Old)")

print("-------------------------")