print("Starting minimal test...")

try:
    print("Testing numpy...")
    import numpy
    print("numpy imported successfully")
except Exception as e:
    print(f"numpy failed: {e}")

try:
    print("Testing pandas...")
    import pandas
    print("pandas imported successfully")
except Exception as e:
    print(f"pandas failed: {e}")

print("Minimal test completed.") 