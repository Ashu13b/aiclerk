import os
import subprocess
import sys
import time
from pathlib import Path

REINGEST_DIR = Path(__file__).parent / "tmp_reingest"

files = sorted(list(REINGEST_DIR.glob("*.pdf")))

def run_ingest(file_path):
    print(f"\n>>> Processing {file_path.name}")
    cmd = ["aiclerk", "ingest", str(file_path)]
    
    # Pre-defined answers based on filename or known patterns
    answers = []
    
    # List detection logic (from user knowledge)
    if "p9-s167" in file_path.name:
        # 1. Track them? (Maybe not if Ashish is known, but if it asks)
        # 2. Is list? (Yes)
        # 3. Page 9
        # 4. S.No 167
        # 5. Ashish Yadav
        pass # We'll handle this dynamically in the loop
    
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    output = ""
    try:
        while True:
            line = proc.stdout.readline()
            if not line and proc.poll() is not None:
                break
            if line:
                print(line, end="")
                output += line
                
                # Check for prompts
                if "Track them? [y/N]:" in line:
                    if "rashi" in line.lower() or "ras" in line.lower():
                        proc.stdin.write("y\n")
                    elif "ashish" in line.lower() or "jitendra" in line.lower() or "sanjeev" in line.lower():
                        # Should already be known, but if not
                        proc.stdin.write("y\n")
                    else:
                        proc.stdin.write("n\n")
                    proc.stdin.flush()
                
                elif "Canonical name" in line:
                    if "rashi" in output.lower():
                        proc.stdin.write("Rashi\n")
                    elif "ashish" in output.lower():
                        proc.stdin.write("Ashish Yadav\n")
                    elif "jitendra" in output.lower():
                        proc.stdin.write("Jitendra Patawat\n")
                    else:
                        # Use default
                        proc.stdin.write("\n")
                    proc.stdin.flush()
                
                elif "Short prefix" in line:
                    if "rashi" in output.lower():
                        proc.stdin.write("ras\n")
                    elif "ashish" in output.lower():
                        proc.stdin.write("ash\n")
                    elif "jitendra" in output.lower():
                        proc.stdin.write("jit\n")
                    else:
                        # Use default
                        proc.stdin.write("\n")
                    proc.stdin.flush()
                
                elif "This looks like a list. Do you want to index a specific entry?" in line:
                    if "p9-s167" in file_path.name or "p9-s157" in file_path.name:
                        proc.stdin.write("y\n")
                    else:
                        # Maybe the AI found it's a list but we don't have instructions?
                        # Let's say 'n' unless we know
                        proc.stdin.write("n\n")
                    proc.stdin.flush()
                
                elif "Page Number" in line:
                    proc.stdin.write("9\n")
                    proc.stdin.flush()
                
                elif "S.No / Index" in line:
                    if "p9-s167" in file_path.name:
                        proc.stdin.write("167\n")
                    elif "p9-s157" in file_path.name:
                        proc.stdin.write("157\n")
                    else:
                        proc.stdin.write("0\n")
                    proc.stdin.flush()
                
                elif "Person Name" in line:
                    if "ash" in file_path.name or "p9-s167" in file_path.name:
                        proc.stdin.write("Ashish Yadav\n")
                    elif "jit" in file_path.name or "p9-s157" in file_path.name:
                        proc.stdin.write("Jitendra Patawat\n")
                    else:
                        proc.stdin.write("General\n")
                    proc.stdin.flush()

    except Exception as e:
        print(f"Error: {e}")
        proc.kill()
    
    proc.wait()
    return output

for f in files:
    run_ingest(f)
