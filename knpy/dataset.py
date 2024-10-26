import torch
from torch.utils.data import Dataset, DataLoader
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
        performable_moves = braid.performable_moves()
        print(performable_moves)
        for move in performable_moves:
            if move == partial(braid.conjugation, index=-1) or partial(braid.conjugation, index=1):
                print('---conjugation')
                move = partial(braid.conjugation, random.randint(1, braid._n - 1), random.randint(0, braid._n + 1))
            braid = move()
            print(move, " performed: ", braid._braid)


        '''
        for i in range(num_moves):
                performable_moves = braid.performable_moves()
                #move = random.choice(performable_moves)
                if move == braid.conjugation:
                     move = partial(move, random.randint(1, braid._n - 1), random.randint(0, braid._n + 1))
                braid = move()
        '''
        return braid

    def __getitem__(self, id):
        num_moves = random.randint(0, self.max_transform)
        orig_braid = Braid(self.data.iloc[id][0])
        print(orig_braid._braid)
        if random.randint(0,9) >= 5:
            return ((self.transform(orig_braid, num_moves), self.transform(orig_braid, num_moves)), 1)
        
        else:
            dist_id = random.randint(0, self.__len__())
            while dist_id == id:
                 dist_id = random.randint(0, self.__len__())
            distinct_braid = self.data.iloc[dist_id]

            return ((self.transform(orig_braid, num_moves), self.transform(distinct_braid, num_moves)), 0)
            

dataset = KnotData("./data_knots/prime_knots_in_braid_notation.csv")

test = dataset[32]
print(test)
print(test[0][0]._braid, test[0][1]._braid)