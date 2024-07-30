import sys
import os
import subprocess

def main():
    file_path = sys.argv[1]
    file_size = os.path.getsize(file_path)
    print(f"FileSize = {file_size}")

    command = f"sudo dd if={file_path} of={sys.argv[2]} status=progress 2>&1 | cat"
    print(command)

    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    n_bytes = 0
    line = ""

    while True:
        c = process.stdout.read(1).decode()
        if not c:
            break
        if c == '\r':
            print(line)
            pos = line.find(" bytes")
            if pos != -1:
                n_bytes = int(line[:pos].strip())
                percent = n_bytes * 100 // file_size
                print(f"{percent}%")
                with open(sys.argv[3], 'w') as of:
                    of.write(f"{percent}\n")
            line = ""
        else:
            line += c

    process.stdout.close()
    with open(sys.argv[3], 'w') as of:
        of.write("100\n")
    
    print("DONE")

if __name__ == "__main__":
    main()

