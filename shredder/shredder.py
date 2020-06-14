import os
import argparse
import time
import random
import string
import sys
import shutil

dir_char = "/"
if(os.name == "nt"):
    dir_char = '\\'

def usage():
    print("[*] Usage")
    print("python3 shredder.py <arguments>")
    print("-d (--directories):  specify directories to shred")
    print("-f (--files):        specify files to shred")
    print("-p (--passes):       specify the amount of passes")
    print("-m (--max-filename)  specify the max filename length")

def shred_file(path : str, passes : int, max_filename : int):
    print(f"[*] Current file: {path}")
    valid_chars = string.ascii_letters + string.digits
    valid_bytes = [chr(c) for c in range(0xFF+1)]
    raw_byte_encode = "latin1"
    filesize = os.path.getsize(path)
    if(os.path.isfile(path) == True and filesize > 0):
        for temp in range(passes):
            #Overwrite file with random raw bytes
            for i in range(filesize):
                fd = os.open(path, os.O_WRONLY|os.O_NOCTTY)
                os.pwrite(fd, random.choice(valid_bytes).encode(raw_byte_encode), i)
                os.close(fd)

            #Rename File
            new_name = "".join(random.choices(valid_chars, k=random.choice(range(1, max_filename + 1))))
            new_path = f"{dir_char}".join(path.split(f"{dir_char}")[0:-1]) + f"{dir_char}{new_name}"
            if(len(path.split(f"{dir_char}")) == 1):
                new_path = new_name
            os.rename(path, new_path)
            path = new_path
        
        #Remove file after completing all passes
        os.remove(path)
            

def shredder(files : list, dirs : list, passes : int, max_filename : int):
    delay = 0.75
    separate_str = "--------------------"

    print("<< shredder.py by rdbo >>")
    time.sleep(delay)
    if(len(files) > 0):
        print(f"[i] Files to shred: {[str(file) for file in files]}")
        time.sleep(delay)

    if(len(dirs) > 0):
        print(f"[i] Directories to shred: {[str(d) for d in dirs]}")
        time.sleep(delay)

    print(f"[i] Amount of passes: {passes}")
    time.sleep(delay)
    print(f"[i] Max filename length: {max_filename}")
    time.sleep(delay)

    bcontinue = input("[#] You might not be able to ever recover the selected files. Continue? (y/n): ")
    if((bcontinue == 'n' or bcontinue == 'N') or (bcontinue != 'n' and bcontinue != 'N' and bcontinue != 'y' and bcontinue != 'Y')):
        print("[*] Exiting...")
        return 0

    print(separate_str)
    time.sleep(delay)

    dir_list = []
    file_list = []

    global dir_char
    #Identify all valid directories and subdirectories
    print("[*] Validating directories...")
    for d in dirs:
        if(os.path.isdir(d) == True):
            if(d not in dir_list):
                dir_list.append(d)
            
            for sd in next(os.walk(d))[1]:
                dirs.append(f"{d}{dir_char}{sd}") #Loop through subdirectories
        else:
            print(f"[!] The directory \"{d}\" is not valid")
    print("[+] Directories validated")
    print(separate_str)

    #Identify all valid files
    print("[*] Validating files...")
    for d in dir_list:
        file_list += [f"{d}{dir_char}{file}" for file in os.listdir(d) if os.path.isfile(f"{d}{dir_char}{file}")]
    
    for file in files:
        if(os.path.isfile(file)):
            file_list.append(file)
        else:
            print(f"[!] The file \"{file}\" is not valid")
    print("[+] Files validated")
    print(separate_str)

    #Shred all valid files
    if(len(file_list) > 0):
        print("[*] Shredding files...")
        for file in file_list:
            try:
                shred_file(file, passes, max_filename)
            except:
                print(f"[!] Exception raised while shredding file \"{file}\"")
                print(f"[i] Exception info: {sys.exc_info()[0]}")
        print("[+] Files shredded")

        if(len(dir_list) > 0):
            print("[*] Removing directories...")
            for d in dir_list:
                shutil.rmtree(d, ignore_errors=True)
            print("[+] Directories removed")
    else:
        print("[!] No files to shred")

if(__name__ == "__main__"):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-d", "--directories", type=str, nargs="+", action="store", dest="directories", default="")
    parser.add_argument("-f", "--files", type=str, nargs="+", action="store", dest="files", default="")
    parser.add_argument("-p" "--passes", type=int, action="store", dest="passes", default="4")
    parser.add_argument("-m", "--max-filename", type=int, action="store", dest="max_filename", default="10")
    args = parser.parse_args()
    try:
        file_list = args.files
        dir_list = args.directories
        passes = args.passes
        max_len = args.max_filename
        if(passes <= 0 or (len(dir_list) == 0 and len(file_list) == 0) or max_len < 1):
            usage()
            exit(0)
    except SystemExit:
        exit(0)
    except:
        print("[!] Unable to parse arguments!")
        usage()
        exit(0)
    try:
        shredder(file_list, dir_list, passes, max_len)
    except KeyboardInterrupt:
        print("[!] Interrupted, exiting...")
        exit(0)
    except:
        print("[!] Exception raised, exiting...")
        exit(0)