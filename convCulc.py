# -*- coding: utf-8 -*-
"""System_and_Signals.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ES0eymV4JD3DAUfr_DfmfDu7AsfdfUP2

Cuda Pacakges installation
"""

!pip install pycuda
!curl https://colab.chainer.org/install | sh -
!sudo apt-get install nvidia-modprobe

"""Import cuda stuff for python"""

import pycuda.driver as cuda 
import pycuda.autoinit
from pycuda.compiler import SourceModule
# Import numpy and random in order to handle arrays
import numpy as np
import random

"""Convolution function """

def MyConvolve(A, B):
 
  # Allocate space for the arrays on the GPU
  a_cuda = cuda.mem_alloc(A.nbytes)
  b_cuda = cuda.mem_alloc(B.nbytes)
  c_cuda = cuda.mem_alloc(A.nbytes)

  c = []
  for i in range(len(A)):
    c.append(0.0)
  C = np.array(c)
  C = C.astype(np.float32)

  # copy data from cpu (host) to gpu (device) allocated space
  cuda.memcpy_htod(a_cuda, A)
  cuda.memcpy_htod(b_cuda, B)
  cuda.memcpy_htod(c_cuda, C)


  # GPU kenrel code - convolution implementation
  convCudaScript = SourceModule("""
  __global__ void conv1d(float *A, float *B, int lenA, int lenB, float *C){

    // thread index
    int tIndex = blockIdx.x * blockDim.x + threadIdx.x;

    //  number of elements left or right of the middle element of B array (mask)
    int r = int(lenA/2);

    // begin from
    int strt =  tIndex - r;

    float sumOfMults = 0;

    // loop over the elements of array B
    for (int i = 0; i < lenB; i++) {
      // throw outrange elements
      if ((strt + i >= 0) && (strt + i < lenA)) {
      sumOfMults = sumOfMults + (A[strt + i] * B[i]);
      }
    }

    C[tIndex] = sumOfMults;
  } 
  """)

  # calculate blocks 
  threads = 256;
  lenA = len(A)
  lenB = len(B)
  blocks = int((len(A) + threads - 1) / threads)
  kernelFunction = convCudaScript.get_function("conv1d")
  kernelFunction(a_cuda, b_cuda, np.int32(lenA), np.int32(lenB), c_cuda, block=(blocks, 1, 1), grid=(1, 1, 1))

  
  cuda.memcpy_dtoh(C, c_cuda)

  return C

"""PART A"""

# array A with N random 32 bit floats
a = []
# N = int(input("N : "))
N = 36

for i in range(N):
  a.append(random.uniform(0.0, 234.5))

A = np.array(a)
A = A.astype(np.float32)

b = [1/5, 1/5, 1/5, 1/5, 1/5]
B = np.array(b)
B = B.astype(np.float32)

C = MyConvolve(A, B)

print(C)

"""PART B"""

