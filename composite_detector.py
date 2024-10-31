import knpy as kn
import numpy as np
import pandas as pd

def detect_composite(braid: kn.Braid):
    n = braid.notation().size
    stacked_array = np.abs(np.tile(braid.notation(), 2))
    minmax = np.zeros((stacked_array.size, 2), dtype=int)
    stack=[]
    for i in range(stacked_array.size):
        while stack and stacked_array[i] > stacked_array[stack[-1]]:
            stack.pop()
        if stack:
            minmax[i, 0] = stack[-1]
        else:
            minmax[i, 0] = -1
        stack.append(i)
    stack=[]
    for i in range(stacked_array.size - 1, -1, -1):
        while stack and stacked_array[i] < stacked_array[stack[-1]]:
            stack.pop()
        if stack:
            minmax[i, 1] = stack[-1]
        else:
            minmax[i, 1] = stacked_array.size
        stack.append(i)
    for i in range(stacked_array.size):
        if minmax[i, 1] - minmax[i, 0] >= n+1:
            return True    
    return False

def combine_braids(braid1, braid2):
    braid1 = braid1.notation()
    braid2 = braid2.notation()
    max1 = np.max(np.abs(braid1))

    combined_notation = np.zeros(len(braid1)+len(braid2)+1, dtype=int)
    combined_notation[:len(braid1)] = braid1
    combined_notation[len(braid1)]=max1+1
    combined_notation[len(braid1)+1:] = [x + max1 + 1 if x > 0 else x - (max1 + 1) for x in braid2]

    return kn.Braid(combined_notation)

def circular_shift(braid, shift):
    shift %= len(braid.notation())
    return kn.Braid(np.concatenate((braid.notation()[shift:], braid.notation()[:shift])))
