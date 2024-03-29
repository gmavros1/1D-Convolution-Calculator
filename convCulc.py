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
# To handle .wav files
from scipy.io.wavfile import read
import scipy.io.wavfile as wavOut

"""Convolution function """

def MyConvolve(A, B):
 
  # Desmeush xwrou sthn gpu
  a_cuda = cuda.mem_alloc(A.nbytes)
  b_cuda = cuda.mem_alloc(B.nbytes)
  c_cuda = cuda.mem_alloc(A.nbytes)

  # dhmiourgia kainou array gia thn apo8hkeush tou apotelesmatos
  C = np.empty_like(A)

  # antigrafh dedomenwn apo thn cpu (host) ston xwro pou desmeusame sthn gpu (device) 
  cuda.memcpy_htod(a_cuda, A)
  cuda.memcpy_htod(b_cuda, B)
  cuda.memcpy_htod(c_cuda, C)


  # ulopoihsh sunarthshs upologismou sunelixis se cuda c
  convCudaScript = SourceModule("""
  __global__ void conv1d(float *A, float *B, int lenA, int lenB, float *C){

    // upologismos 8esis thread
    int tIndex = blockIdx.x * blockDim.x + threadIdx.x;

    //  upologismos stoixeiwn aristera kai deksia toy meseou arithmou tou B array
    int r = int(lenA/2);

    // o arithmos tou thread pou jekinane ta epimerous athrismata tis sunelixis
    int strt =  tIndex - r;

    // edo apo8hkeuetai to apotelesma kathe stoixeiou tou telikou array
    float sumOfMults = 0.f;

    // h exwterikh epanalypsh trehei ena ena ta stoixeia toy B array (mask)
    for (int i = 0; i < lenB; i++) {
      // sthn sunelixh twn arxikwn stoixeiwn kai twn telikwn, tuxainei kapoia 
      // stoixeia na "kremane". Theoroume pws auta ta stoixeia poll/zontai me to 0
      // opote den ta lambanoume upopsin sto a8roisma
      if ((strt + i >= 0) && (strt + i < lenA)) {
      sumOfMults += (A[strt + i] * B[i]);
      }
    }

    C[tIndex] = sumOfMults;
  } 
  """)


  # upologismos blocks
  threads = 256;
  lenA = len(A)
  lenB = len(B)
  blocks = int((len(A) + threads - 1) / threads)
  kernelFunction = convCudaScript.get_function("conv1d")
  # klhsh cuda sunarthshs
  kernelFunction(a_cuda, b_cuda, np.int32(lenA), np.int32(lenB), c_cuda, block=(blocks, 1, 1), grid=(1, 1, 1))

  
  cuda.memcpy_dtoh(C, c_cuda)

  return C

"""PART A"""

# Kataskeuh tuxaias list A me N float stoixeia
a = []
N = int(input("N : "))

for i in range(N):
  a.append(random.uniform(0.0, 500.0))

# metatroph list se 32 bit float array
A = np.array(a)
A = A.astype(np.float32)

# omoia gia to B
b = [1/5, 1/5, 1/5, 1/5, 1/5]
B = np.array(b)
B = B.astype(np.float32)

C = MyConvolve(A, B)

print(C)

"""PART B"""

# Pink noise

# Anagnosh wav arxeiwn
SampleAudio = read("/content/drive/MyDrive/signal - systems/sample_audio.wav")
PinkNoise = read("/content/drive/MyDrive/signal - systems/pink_noise.wav")

# metatroph se arrays
# e.x. To SampleAudior[0] afora to mhkos enw to SampleAudior[0] to shma auto kathe auto
SampleAudioAr = np.array(SampleAudio[1],dtype=float)
PinkNoiseAr = np.array(PinkNoise[1],dtype=float)

# h cuda xeirizetai 32 bir floats opote kanoume thn anagkaia metatroph
SampleAudioAr = SampleAudioAr.astype(np.float32)
PinkNoiseAr = PinkNoiseAr.astype(np.float32)

# klhsh sunarthshs
rarray = MyConvolve(SampleAudioAr, PinkNoiseAr)

#eggrafh apotelesmatos se wav arxeio
result = "/content/drive/MyDrive/signal - systems/pinkNoise_sampleAudio3.wav"
wavOut.write(result, SampleAudio[0], rarray)

# dhmiourgeia leukou thorybou
WhiteNoise =  np.random.random_sample((132300,))

# antistoixa gia to arxeio tou leukoy thorubou
WhiteNoise = WhiteNoise.astype(np.float32)

rarray2 = MyConvolve(SampleAudioAr, WhiteNoise)

result2 = "/content/drive/MyDrive/signal - systems/whiteNoise_sampleAudio1.wav"

wavOut.write(result2, SampleAudio[0], rarray2)
