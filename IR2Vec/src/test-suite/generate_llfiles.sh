# Copyright (c) 2021, S. VenkataKeerthy, Rohit Aggarwal
# Department of Computer Science and Engineering, IIT Hyderabad

# This software is available under the BSD 4-Clause License. Please see LICENSE
# file in the top-level directory for more details.
#
SRC_WD="/home/Kiprey/Desktop/dg/Juliet/testcases/**/*.c"
DEST_FOLDER="/home/Kiprey/Desktop/dg/Juliet/testcases/CWE122_Heap_Based_Buffer_Overflow/s03_ll"
INCLUDE="/home/Kiprey/Desktop/dg/Juliet/testcasesupport/"

mkdir -p ${DEST_FOLDER}

# Update the BUILD to use
LLVM_BUILD=/usr/lib/llvm-13

if [ -z ${LLVM_BUILD} ]; then
	echo "Enter the llvm build path.."
	exit
fi

for d in ${SRC_WD}/*.c ${SRC_WD}/*.cpp ${SRC_WD}/*.cc; do
	name=$(basename ${d}) && oname=${name%.*} && ${LLVM_BUILD}/bin/clang -S -g -I ${INCLUDE} -emit-llvm -Xclang -disable-O0-optnone ${d} -o ${DEST_FOLDER}/${oname}.ll &
    sleep 0.1
done
wait
