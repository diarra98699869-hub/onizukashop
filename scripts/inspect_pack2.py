import os
import sys

downloads = r"C:\Users\a\Downloads"

print("Matches in Downloads:")
for item in os.listdir(downloads):
    full_path = os.path.join(downloads, item)
    if "clim" in item.lower() or "pack" in item.lower():
        print(f"[{'DIR' if os.path.isdir(full_path) else 'FILE'}] {item}")

# Look specifically for exact or partial 2pack clim
for item in os.listdir(downloads):
    if "2pack" in item.lower() or "pack 2" in item.lower() or ("2" in item and "clim" in item.lower()):
        target = os.path.join(downloads, item)
        print(f"\n--- Checking candidate target: {target} ---")
        if os.path.isdir(target):
            files = os.listdir(target)
            print(f"Found {len(files)} items:")
            for f in files:
                fpath = os.path.join(target, f)
                print(f"  - {f} ({os.path.getsize(fpath)} bytes)")
        else:
            print(f"File size: {os.path.getsize(target)} bytes")
