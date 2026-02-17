import sys
print("Executable:", sys.executable)
print("Path:", sys.path)
try:
    import google
    print("google imported:", google.__file__)
except ImportError as e:
    print("google import failed:", e)

try:
    from google import genai
    print("google.genai imported")
except ImportError as e:
    print("google.genai import failed:", e)
