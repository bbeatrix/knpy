from knpy import *
from knpy.data_utils import benchmark_braids
import random
import heapq
import time
import matplotlib.pyplot as plt
import tqdm
import torch
import network

def get_time() -> int:
    return int(round(time.time() * 1000))

def gen_random_move(braid: Braid) -> Braid:
    moves = braid.performable_moves()
    return random.choice(moves)

def gen_random_relation2(braid: Braid) -> Braid:
    moves = braid.performable_rel2()
    return random.choice(moves)

def gen_random_collapse(braid: Braid) -> Braid:
    moves = braid.performable_collapse()
    return random.choice(moves)
    
def gen_eq_braid(braid: Braid, depth: int) -> Braid:
    for i in tqdm.tqdm(range(depth)):
        mv = gen_random_move(braid)
        braid = mv()
        for j in range(100): braid = gen_random_relation2(braid)()
    for j in range(100): braid = gen_random_collapse(braid)()
    return braid

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

def minimal_crossing(starting_braid: Braid, execution_time: int, model):
    pq = []
    dist = {}
    it = 0
    start_time = get_time()
    best = starting_braid

    def get_fingerprint(braid: Braid):
        x = braid.notation(False)
        x.flags.writeable = False
        return hash(x.tobytes())
    
    # def calculate_heuristic(braid: Braid):
    #     res = len(braid)
    #     x = braid.notation(False)
    #     for i in range(len(x)):
    #         for j in range(min(10, i)):
    #             res += abs(x[i-j]) > abs(x[i])
    #     return res

    queue = []

    def calc_queue(model):
        nonlocal queue
        tensor = torch.zeros((len(queue), 100))
        for idx, (depth, arr) in enumerate(queue):
            b = Braid(arr)
            while len(b) < 100:
                b = b.stabilization(0, on_top=False)
            tensor[idx] = b.to_torch()
        values = model(tensor)
        print(values)
        for idx in range(len(queue)):
            heapq.heappush(pq, (values[idx] * 5 + depth, Braid(queue[idx][1])))
        queue = []
    
    def add_node(braid: Braid, new_depth: int):
        nonlocal queue
        fingerprint = get_fingerprint(braid)
        if not fingerprint in dist:
            dist[fingerprint] = new_depth
            if len(pq) <= 100:
                heapq.heappush(pq, (braid.calculate_heuristic() * 5 + new_depth, braid))
            else:
                queue.append((new_depth, braid.notation(False)))

    add_node(starting_braid, 0)
    while len(best) > 12:
        if len(pq) == 0 or len(queue) > 1024:
            calc_queue(model)
            continue
        it += 1
        if it % 100 == 0:
            pq = pq[:10000]
            now = get_time()
            if now - start_time > execution_time:
                break
        x = heapq.heappop(pq)
        order_operator: int = x[0]
        braid: Braid = x[1]
        depth: int = dist[get_fingerprint(braid)]
        for mv in braid.performable_moves():
            new_braid = mv()
            if len(new_braid) < len(best):
                best = new_braid
            add_node(new_braid, depth + 1)
    return best

# score = 0
# max_score = 0
# braids = []
# for i in range(20):
#     x = gen_eq_braid(Braid("11n_16"), random.randint(40, 100))
#     braids.append(x)
#     braid = minimal_crossing(x, 5000)
#     print(len(braid))
#     max_score += len(x)-12
#     score += len(braid)-12

model = network.NetworkV1()
model.load_state_dict(torch.load("model.pt"))
model.eval()
with torch.no_grad():
    score = 0
    max_score = 0
    X = []
    Y = []
    Z = []
    for i in tqdm.tqdm(list(benchmark_braids.keys())[:10]):
        x = Braid(benchmark_braids[i][0])
        braid = minimal_crossing(x, 10000, model)
        max_score += len(x)-12
        score += len(braid)-12
        X.append(len(x))
        Y.append(len(braid))
        Z.append("orange" if int(i.split("_")[0]) >= 20  else "green")
    print("Score =", 1-score/max_score)
    plt.vlines(12, 0, 100, colors='red', linestyles='dashed', label='True crossing number')
    plt.title("Crossing number prediction of 11n_16 equivalent knots")
    plt.scatter(Y, X, c=Z)
    plt.xlim(0, 100)
    plt.ylim(0, 100)
    plt.xlabel("Predicted crossing number")
    plt.ylabel("Input crossing number")
    plt.legend()
    plt.show()