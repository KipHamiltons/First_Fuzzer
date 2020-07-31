# print("hello fuzzing world")
# (This is my first fuzzer)

import os, random, hashlib, time
from multiprocessing import Process
import subprocess

"""
This fuzzer is HEAVILY based on gamozolabs' 
fuzzer from the first day of "Fuzz Week 2020":
https://www.youtube.com/watch?v=2xXt_q3Fex8

@gamozolabs https://twitter.com/gamozolabs
@gamozolabs https://github.com/gamozolabs
@gamozolabs https://twitch.tv/gamozolabs
@gamozolabs https://www.youtube.com/channel/UC17ewSS9f2EnkCyMztCdoKA

If you don't want to waste loads of writes on a HDD/SSD, 
then I suggest running this on a ramdisk, although that
probably won't improve performance, due to bottlenecking on 
kernel calls anyway.

"""

# This number will need individual tuning for a given system, 
#    although a linux kernel will probably bottleneck this if it can go any higher.
NUM_PROCESSES = 5

# Change this path to control which binutil binary you use
# (Doesn't have to be objdump, or even a binutil, it just has to take a file as command line input)
BIN_UTIL_PATH = "./binutils-gdb/binutils/objdump"

CORPUS_PATH = "./corpus/"
TEMP_PATH = "./temp/"
CRASHED_PATH = "./crashed/"

# Corrupts the passed in binary data, then saves the corrupted data
#   and runs objdump on it, returning an indicator of if it crashed.
def fuzz(file_selection_data, thr_id):

    # Corrupt the file
    # 200 is just some number - it can be as few as 1-8 bytes corrupted to get a crash on a buggy program.
    for r in range(200):
        file_selection_data[random.randint(0, len(file_selection_data) -1)] = random.randint(0,255)

    # hash the file and save that string as a filename
    hashed_path = hashlib.sha1(file_selection_data).hexdigest()

    # save the file as $PWD/temp/hash
    with open(TEMP_PATH + hashed_path, 'wb') as f:
        f.write(file_selection_data)

    # run objdump (or some other binutil)
    # return_code is the exit status. 0 => no error. +- 11 => SIGSEGV
    return_code = subprocess.run([BIN_UTIL_PATH,
                                    '-xd', # flags -> -x does all headers, and -d disassembles the code
                                    TEMP_PATH + hashed_path], 
                                    stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL
                                    ).returncode # The actual linux shell command exit code, as would be assigned to $?

    # delete the temp file $PWD/temp/hash
    subprocess.run(['rm', TEMP_PATH + hashed_path])

    # depending on the exit status, save the file in $PWD/crashed/hash
    # Bad header happens a lot, because if there is a corrupted byte in there, and 
    #     the binutil is working as intended, it will just nope out of there instead of crashing.
    if return_code not in [0, 1]: # SIGSEGV is +-11, bad header is 1, 0 is no error
        with open(CRASHED_PATH + hashed_path, 'wb') as f:
            f.write(file_selection_data)
        return 1
    else:
        return 0

# Main workhorse function
# One instance of this function per process or thread.
# This function will never stop running fuzz cases without an 
#    external signal such as `ctrl + c`
def worker(thr_id):

    # These variables are used for stats, and making them global
    #    for all of the processes allows global statistics tracking
    global start, corpus, cases, crashes

    # Keep fuzzing indefinitely
    while True:

        # Make a random file selection and call fuzz
        # The fuzz method will corrupt the data, then
        # it will return 1 if the program crashes, or zero if it doesn't
        crashes += fuzz(bytearray(random.choice(corpus)), thr_id)

        cases += 1
        
        # Track how much time has passed, so that the fuzz cases per second can be calc'd
        elapsed = time.time() - start

        fcps = float(cases) / elapsed

        # Only print if it's the first process, so that we don't bottleneck on
        #    spamming stdout with stats.
        if thr_id == 0:
            print(f"{elapsed:10.3f}s  -- {cases:7} cases -- {crashes:4} crashes -- {fcps:10.3f} fuzz cases per second")



# Keep the binaries in memory to improve perf
corpus = []
for f in os.listdir(CORPUS_PATH):
    corpus.append(open(CORPUS_PATH + f, 'rb').read())

# intialise the global stats variables
start = time.time()
cases = 0
crashes = 0

for thr_id in range(NUM_PROCESSES):
    Process(target=worker, args=(thr_id,)).start()
while True:
    time.sleep(0.1)

# Unthreaded option (won't run without commenting out above loops)
# Approximately the same perf as NUM_PROCESSES == 1, using the above loops instead.
worker(0)