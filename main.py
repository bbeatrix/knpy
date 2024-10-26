from knpy import *
import random
import heapq
import time
import matplotlib.pyplot as plt
import tqdm

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
        for j in range(10): braid = gen_random_relation2(braid)()
    for j in range(100): braid = gen_random_collapse(braid)()
    return braid

def minimal_crossing(starting_braid: Braid, execution_time: int = 200000):
    pq = []
    dist = {}
    it = 0
    start_time = get_time()
    best = starting_braid

    def get_fingerprint(braid: Braid):
        return tuple(braid.notation())

    def add_node(braid: Braid, new_depth: int):
        fingerprint = get_fingerprint(braid)
        if not fingerprint in dist:
            dist[fingerprint] = new_depth
            heapq.heappush(pq, (len(braid) + new_depth, braid))

    add_node(starting_braid, 0)
    last_time = start_time
    X = []
    Y = []
    with tqdm.tqdm(total=execution_time) as pbar:
        while len(pq) > 0 and len(best) > 12:
            it += 1
            if it % 10 == 0:
                pq = pq[:100]
                now = get_time()
                pbar.update(now - last_time)
                pbar.set_description(f"c = {len(best)}; s = {best.strand_count}")
                last_time = now
                if now - start_time > execution_time:
                    break
            x = heapq.heappop(pq)
            order_operator: int = x[0]
            braid: Braid = x[1]
            depth: int = dist[get_fingerprint(braid)]
            X.append(it)
            Y.append(len(braid))
            for mv in braid.performable_moves():
                new_braid = mv()
                if len(new_braid) < len(best):
                    best = new_braid
                add_node(new_braid, depth + 1)
    plt.plot(X, Y, '.')
    plt.show()
    return best

braid = Braid("11n_16")
print("Answer:", len(braid))
#braid.show()
braid = gen_eq_braid(braid, 300)
braid.show()
#braid.show()
print("Start:", len(braid))
best = minimal_crossing(braid)
#best.show()
print("Result:", len(best))
