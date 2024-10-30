import knpy
from knpy import Braid
import knpy.data_utils as du
import heapq
import tqdm
import torch
import random

N = 20000
ITER_COUNT = 400
PADDING_SIZE = 100

def gen_random_move(braid: Braid) -> Braid:
    moves = braid.performable_moves()
    return random.choice(moves)

def gen_random_relation2(braid: Braid) -> Braid:
    moves = braid.performable_rel2()
    return random.choice(moves)

def gen_random_relation(braid: Braid) -> Braid:
    moves = braid.performable_rel2() + braid.performable_rel1() * 10
    return random.choice(moves)

def gen_random_collapse(braid: Braid) -> Braid:
    moves = braid.performable_collapse()
    return random.choice(moves)

def gen_eq_braid_hard(braid: Braid, depth: int) -> Braid:
    for i in range(depth):
        mv = gen_random_move(braid)
        braid = mv()
        for j in range(50): braid = gen_random_relation(braid)()
        for j in range(len(braid) // 13):
            braid = gen_random_collapse(braid)()
    for j in range(100): braid = gen_random_collapse(braid)()
    return braid

def calculate_value(starting_braid, iterations):
    pq = []
    dist = {}
    best_value = starting_braid.calculate_heuristic()

    def get_fingerprint(braid):
        x = braid.notation(False)
        x.flags.writeable = False
        return hash(x.tobytes())

    def add_node(braid, new_depth):
        fingerprint = get_fingerprint(braid)
        nonlocal best_value
        if not fingerprint in dist:
            dist[fingerprint] = new_depth
            val = braid.calculate_heuristic()
            best_value = min(best_value, val)
            heapq.heappush(pq, (val * 5 + new_depth, braid))

    add_node(starting_braid, 0)
    for it in range(iterations):
        x = heapq.heappop(pq)
        braid = x[1]
        depth = dist[get_fingerprint(braid)]
        for mv in braid.performable_moves():
            new_braid = mv()
            add_node(new_braid, depth + 1)
    return best_value

import torch
import tqdm
from multiprocessing import Pool, cpu_count

X = torch.zeros((N, PADDING_SIZE))
Y = torch.zeros((N))

def process_braid(idx):
    braid = gen_eq_braid_hard(Braid("11n_16"), 200)
    while len(braid) > PADDING_SIZE:
        braid = gen_eq_braid_hard(Braid("11n_16"), 200)

    value = calculate_value(braid, 500)
    print(value, braid.calculate_heuristic())

    while len(braid) < PADDING_SIZE:
        braid = braid.stabilization(0, on_top=False)

    tensor = braid.to_torch()
    assert torch.max(torch.abs(tensor)) < PADDING_SIZE
    return idx, tensor, value

if __name__ == '__main__':
    with Pool(processes=4) as pool:
        results = list(tqdm.tqdm(pool.imap(process_braid, range(N)), total=N))
        
    for idx, tensor, value in results:
        X[idx] = tensor
        Y[idx] = value
    
    data = {"X": X, "Y": Y}
    torch.save(data, "dataset200.pt")