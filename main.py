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
    braid = minimal_crossing(x, 1000)
    return len(x), len(braid), key

if __name__ == "__main__":
    score = 0
    max_score = 0
    X = []
    Y = []
    Z = []
    labels = []
    prime_to_color = {"unknot": "blue", "6_2": "red", "9_27": "pink", "12n_8": "green"}

    with ProcessPoolExecutor(max_workers=2) as executor:
        futures = {executor.submit(compute_braid, key): key for key in benchmark_braids}

        for future in tqdm.tqdm(as_completed(futures), total=len(benchmark_braids)):
            x_len, braid_len, key = future.result()
            max_score += x_len - 1
            score += braid_len - 1
            prime = key.split(":")[0]
            X.append(x_len)
            Y.append(braid_len)
            Z.append(prime_to_color[prime])
            labels.append(prime)

    print("Score =", 1 - score / max_score)

    plt.title("Crossing number prediction of knots")
    plt.vlines(1, 0, 100, colors='blue', linestyles='dashed')
    plt.vlines(6, 0, 100, colors='red', linestyles='dashed')
    plt.vlines(9, 0, 100, colors='pink', linestyles='dashed')
    plt.vlines(12, 0, 100, colors='green', linestyles='dashed')

    plt.vlines(-100, -100, -200, colors='black', linestyles='dashed', label="True crossing number")
    plt.vlines(-100, -100, -200, colors='blue', linestyles='solid', label="unknot")
    plt.vlines(-100, -100, -200, colors='red', linestyles='solid', label="6_2")
    plt.vlines(-100, -100, -200, colors='pink', linestyles='solid', label="9_27")
    plt.vlines(-100, -100, -200, colors='green', linestyles='solid', label="12n_8")

    plt.scatter(Y, X, c=Z)
    plt.xlim(-5, 90)
    plt.ylim(-5, 90)
    plt.xlabel("Predicted crossing number")
    plt.ylabel("Input crossing number")
    plt.legend(loc="lower right")
    plt.show()
