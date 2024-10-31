from knpy import *
from knpy.data_utils import benchmark_braids
import random
import heapq
import time
import matplotlib.pyplot as plt
import tqdm
import numpy as np

def get_time() -> int:
    return int(round(time.time() * 1000))

def hard(n):
    return Braid([i for i in range(1, 2*n+1)] + [-i for i in range(1, 2*n+1)])

def convert_to_csv(braids):
    csv_lines = ["Name,Braid Notation"]
    
    for i, b in enumerate(braids):
        array_str = '{' + ';'.join(map(str, b.notation())) + '}'
        csv_lines.append(f"{i}_{len(b)},{array_str}")
    
    csv_output = '\n'.join(csv_lines)
    f = open("braids.csv", "w")
    f.write(csv_output)
    f.close()

def minimal_crossing(starting_braid: Braid, execution_time: int):
    pq = []
    dist = {}
    it = 0
    start_time = get_time()
    best = starting_braid

    def get_fingerprint(braid: Braid):
        x = braid.notation(False)
        x.flags.writeable = False
        return hash(x.tobytes())

    def add_node(braid: Braid, new_depth: int):
        fingerprint = get_fingerprint(braid)
        if not fingerprint in dist:
            dist[fingerprint] = new_depth
            heapq.heappush(pq, (braid.calculate_heuristic() * 5 + new_depth, braid))

    add_node(starting_braid, 0)
    while len(pq) > 0 and len(best) > 1:
        it += 1
        if it % 100 == 0:
            now = get_time()
            if now - start_time > execution_time:
                break
        x = heapq.heappop(pq)
        braid: Braid = x[1]
        depth: int = dist[get_fingerprint(braid)]
        for mv in braid.performable_moves():
            new_braid = mv()
            if len(new_braid) < len(best):
                best = new_braid
            add_node(new_braid, depth + 1)
    return best

from concurrent.futures import ProcessPoolExecutor, as_completed
import tqdm
import matplotlib.pyplot as plt

def compute_braid(key):
    x = Braid(benchmark_braids[key][0])
    braid = minimal_crossing(x, 200000)
    return len(x), len(braid)

if __name__ == "__main__":
    score = 0
    max_score = 0
    X = []
    Y = []
    Z = []

    with ProcessPoolExecutor(max_workers=2) as executor:
        futures = {executor.submit(compute_braid, key): key for key in benchmark_braids}

        for future in tqdm.tqdm(as_completed(futures), total=len(benchmark_braids)):
            x_len, braid_len = future.result()
            max_score += x_len - 1
            score += braid_len - 1
            X.append(x_len)
            Y.append(braid_len)
            Z.append("blue")

    print("Score =", 1 - score / max_score)

    plt.title("Crossing number prediction of 11n_16 equivalent knots")
    plt.scatter(Y, X, c=Z)
    plt.xlim(0, 100)
    plt.ylim(0, 100)
    plt.xlabel("Predicted crossing number")
    plt.ylabel("Input crossing number")
    plt.legend()
    plt.show()
