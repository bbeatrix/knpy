import os

def load_csv(BRAID_PATH):
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, BRAID_PATH)

    res = {}
    with open(file_path, "r") as file:
        for i, line in enumerate(file):
            if i == 0:
                continue
            line = line.strip()
            line_splitted = line.split(",")
            key = line_splitted[0]
            temp_braid_notations = []  # TODO Multiple braid notation might be available
            for lsp in line_splitted[1].split("};{"):
                temp_braid_notations.append(list(map(int, lsp.strip("{}").split(";"))))
            res[key] = temp_braid_notations
    return res

knots_in_braid_notation_dict = load_csv("data_knots/prime_knots_in_braid_notation.csv")
benchmark_braids = load_csv("data_knots/benchmark.csv")
