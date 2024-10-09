import os
BRAID_PATH = "data_knots/prime_knots_in_braid_notation.csv"

current_dir = os.path.dirname(__file__)
file_path = os.path.join(current_dir, BRAID_PATH)

knots_in_braid_notation_dict = dict()
with open(file_path, 'r') as file:
    for i,line in enumerate(file):
        if i==0: continue
        line = line.strip()
        line_splitted = line.split(",")
        key = line_splitted[0]
        temp_braid_notations = [] #TODO Multiple braid notation might be available
        for lsp in line_splitted[1].split("};{"):
            temp_braid_notations.append(list(map(int, lsp.strip('{}').split(';'))))
        knots_in_braid_notation_dict[key] = temp_braid_notations