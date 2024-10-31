from knpy import *
import numpy as np
import tqdm
import random

def random_markov_move(braid):
    mx = 1 if len(braid) == 0 else np.max(np.abs(braid.notation(False)))
    if random.choice([True, False]):
        inverse = random.choice([+1, -1])
        value = random.randint(1, mx)
        return braid.conjugation(index = len(braid) + 1, value = inverse * value)
    else:
        inverse = random.choice([True, False])
        return braid.stabilization(len(braid), on_top=False, inverse=inverse)

def smart_collapse(braid):
    while True:
        indices1 = braid.remove_sigma_inverse_pair_performable_indices()
        indices2 = []
        for i in range(len(braid)):
            if braid.is_destabilization_performable(i):
                indices2.append(i)
        
        if len(indices1) > 0:
            braid = braid.remove_sigma_inverse_pair(random.choice(indices1))
        elif len(indices2) > 0:
            braid = braid.destabilization(random.choice(indices2))
        else:
            break

    return braid
            
    
def gen_knot(braid, n, m, use_smart_collapse):
    starting_braid = braid.notation(True)
    while len(braid) != n:
        if len(braid) > n:
            braid = Braid(starting_braid)
        for k in range(m):
            braid = random_markov_move(braid)

            rel1_indices = braid.braid_relation1_performable_indices()
            if len(rel1_indices) > 0:
                braid = braid.braid_relation1(random.choice(rel1_indices))
        
        if use_smart_collapse:
            braid = smart_collapse(braid)
    return braid

def convert_to_csv(braids, id):
    # csv_lines = ["Name,Braid Notation"]
    csv_lines = []
    
    for i, b in enumerate(braids):
        array_str = '{' + ';'.join(map(str, b.notation())) + '}'
        csv_lines.append(f"{id}:{len(b)}-{i},{array_str}")
    
    return csv_lines

def write_to_csv(csv_lines):
    csv_output = '\n'.join(csv_lines)
    f = open("braids.csv", "w")
    f.write(csv_output)
    f.close()


def gen_knots(cnt, prime_knot_id, min_n, max_n, m, use_smart_collapse):
    if prime_knot_id is None:
        prime_knot_id = "unknot"
        braid = Braid([])
    else:
        braid = Braid(prime_knot_id)
    
    braids = []
    for i in tqdm.tqdm(range(cnt)):
        b = Braid(braid.notation(False))
        braids.append(gen_knot(b, random.randint(min_n, max_n), m, use_smart_collapse))

    return convert_to_csv(braids, f"{prime_knot_id}:{use_smart_collapse}:{m}")

def datagen():
    csv_lines = ["Name,Braid Notation"]
    csv_lines += gen_knots(10, None, 30, 80, 10, True)
    csv_lines += gen_knots(10, None, 30, 80, 10, False)
    csv_lines += gen_knots(10, "6_2", 30, 80, 10, True)
    csv_lines += gen_knots(10, "6_2", 30, 80, 10, False)
    csv_lines += gen_knots(10, "9_27", 30, 80, 10, True)
    csv_lines += gen_knots(10, "9_27", 30, 80, 10, False)
    csv_lines += gen_knots(10, "12n_8", 30, 80, 10, True)
    csv_lines += gen_knots(10, "12n_8", 30, 80, 10, False)


    write_to_csv(csv_lines)

if __name__ == "__main__":
    datagen()