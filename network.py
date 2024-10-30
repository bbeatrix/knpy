import torch.nn as nn

class NetworkV1(nn.Module):
    def __init__(self):
        super(NetworkV1, self).__init__()
        self.embedding_layer = nn.Embedding(num_embeddings=200, embedding_dim=5)
        self.relu = nn.ReLU()
        self.fc1 = nn.Linear(100 * 5, 256)
        self.fc2 = nn.Linear(256, 1)

    def forward(self, x):
        x = (x + 100).int()
        x = self.embedding_layer(x)
        x = x.view(x.shape[0], x.shape[1] * x.shape[2])
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return x
