import os
import re
from pathlib import Path

def replace_in_file(path):
    try:
        content = path.read_text(encoding="utf-8")
    except Exception:
        return
        
    original = content
    
    # Replace Dark-Brain07 -> Dark-Brain07
    content = content.replace("Dark-Brain07", "Dark-Brain07")
    content = content.replace("Dark-Brain07", "Dark-Brain07")
    
    # Replace spacly variants
    content = content.replace("SPACLY", "SPACLY")
    content = content.replace("Spacly", "Spacly")
    content = content.replace("spacly", "spacly")
    
    if content != original:
        path.write_text(content, encoding="utf-8")
        print(f"Updated content in: {path}")

def rename_path(path):
    name = path.name
    if "spacly" in name or "Spacly" in name or "SPACLY" in name:
        new_name = name.replace("SPACLY", "SPACLY").replace("Spacly", "Spacly").replace("spacly", "spacly")
        new_path = path.with_name(new_name)
        path.rename(new_path)
        print(f"Renamed: {path} -> {new_path}")
        return new_path
    return path

def process_dir(root):
    skip = {".git", "node_modules", ".next", "dist", ".vercel"}
    
    # Bottom-up for renaming safety
    for dirpath, dirnames, filenames in os.walk(root, topdown=False):
        dp = Path(dirpath)
        if any(p in dp.parts for p in skip):
            continue
            
        for f in filenames:
            if f == "package-lock.json": continue
            fpath = dp / f
            # first replace content
            replace_in_file(fpath)
            # then rename file
            rename_path(fpath)
            
        # rename dir if needed
        rename_path(dp)

if __name__ == "__main__":
    process_dir(".")
    print("Done!")
