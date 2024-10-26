import torch
from torch.utils.data import Dataset, DataLoader
import torch.nn.functional as F
import pandas as pd
import random
from functools import partial
from braid import Braid

class KnotData(Dataset):
    def __init__(self, data_file, max_transform=1):
        self.data = pd.read_csv(data_file)
        self.max_transform = max_transform

    def __len__(self):
        return len(self.data)
    
    def transform(self, braid, num_moves):
        for i in range(num_moves):
                performable_moves = braid.performable_moves()
                move = random.choice(performable_moves)
                braid = move()
        return braid

    def __getitem__(self, id):
        num_moves = random.randint(0, self.max_transform)
        orig_braid = Braid(self.data.iloc[id][0])
        if random.randint(0,9) >= 5:
            return ([self.transform(orig_braid, num_moves).to_torch(), self.transform(orig_braid, num_moves).to_torch()], 1)
        
        else:
            dist_id = random.randint(0, self.__len__())
            while dist_id == id:
                 dist_id = random.randint(0, self.__len__())
            distinct_braid = Braid(self.data.iloc[dist_id][0])

            return ([self.transform(orig_braid, num_moves).to_torch(), self.transform(distinct_braid, num_moves).to_torch()], 0)
            

def collate_fn(data):
    max_length = 0
    for i in range(len(data)):
         for j in [0, 1]:
              length = len(data[i][0][j])
              if length > max_length:
                   max_length = length

    for i in range(len(data)):
         for j in [0, 1]:
              data[i][0][j] = F.pad(data[i][0][j], (0, max_length - len(data[i][0][j])))

    first = torch.stack([data[i][0][0] for i in range(len(data))])
    second = torch.stack([data[i][0][1] for i in range(len(data))])
    labels = torch.tensor([data[i][1] for i in range(len(data))])

    return first, second, labels