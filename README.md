# First_Fuzzer
This fuzzer is HEAVILY based on gamozolabs' 
fuzzer from the first day of "Fuzz Week 2020":
https://www.youtube.com/watch?v=2xXt_q3Fex8

@gamozolabs https://twitter.com/gamozolabs

@gamozolabs https://github.com/gamozolabs

@gamozolabs https://twitch.tv/gamozolabs

@gamozolabs https://www.youtube.com/channel/UC17ewSS9f2EnkCyMztCdoKA

If you don't want to waste loads of writes on a HDD/SSD, 
then I suggest running this on a ramdisk, although that
probably won't improve performance due to bottlenecking on 
kernel calls anyway.


# Setup
1.  clone the repo `git clone https://github.com/KipHamiltons/First_Fuzzer.git`
2.  change into the repo's root directory `cd First_Fuzzer`
3.  create the necessary directories `mkdir crashed temp corpus`
4.  Copy the fuzzer inputs (binaries) into the corpus directory
5.  If you are happy using your standard objdump binary, skip to step 10
6.  clone binutils-gdb `git clone git clone git://sourceware.org/git/binutils-gdb.git`
7.  change into the binutils directory `cd binutils-gdb`
8.  Build the binutils `./configure && make`
9.  Change to the parent directory `cd ..`
10. Change `BIN_UTIL_PATH` in `hello_world.py` to be the path of the binary you wish to fuzz

# Usage
Run `python3 hello_world.py`

# Expectations
Nil. Binutils at the current time deal very well with corrupted data.
This might be more instructive if an older version of the binutil is fuzzed.
