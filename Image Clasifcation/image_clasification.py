from sklearn.datasets import fetch_openml
import numpy as np
from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset
from torch.utils.data import DataLoader
from torch import nn
import torch.nn.functional as F
from torch import Tensor
import torch
from torch import optim
from collections import Counter
import matplotlib.pyplot as plt

mnist = fetch_openml("mnist_784", parser='auto')

data = mnist.data.to_numpy()
targets = np.vectorize(lambda x: int(x))(mnist.target.to_numpy()) # changing a string to an int

print(data.shape)
print(targets.shape)
print(len(set(targets)))

# Data split
train_data, test_data, train_targets, test_targets = train_test_split(data, targets, train_size=0.8, stratify=targets)

# Data Set
class DigitsDataset(Dataset):
    def __init__(self, data, targets):
        self.data = data
        self.targets = targets

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        x = self.data[idx] / 255
        y = self.targets[idx]

        return x, torch.tensor(y, dtype=torch.long)


train_dataset = DigitsDataset(train_data, train_targets)
test_dataset = DigitsDataset(test_data, test_targets)


# print(train_dataset[0][0])
# print(test_dataset[0][1])

# DataLoader
train_dataloader = DataLoader(train_dataset, batch_size=32, shuffle=True)
test_dataloader = DataLoader(test_dataset, batch_size=32, shuffle=False)

# Neural Network

class Model(nn.Module):
    def __init__(self, input_size, num_classes):
        super(Model, self).__init__()
        self.fc1 = nn.Linear(input_size, 200)
        self.fc2 = nn.Linear(200, 100)
        self.fc3 = nn.Linear(100, num_classes)

    def forward(self, x):
        out = self.fc1(x)
        out = F.relu(out)
        out = self.fc2(out)
        out = F.relu(out)
        out = self.fc3(out)

        if not self.training:
            out = F.softmax(out, dim=1)
        return out


# Training
model = Model(784, 10)
loss_function = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters())

train_losses = []
test_losses = []

for epoch in range(10):
    epoch_train_loss = 0.0
    epoch_test_loss = 0.0

    for data in train_dataloader:
        inputs, labels = data

        optimizer.zero_grad()
        inputs = inputs.float()
        outputs = model(inputs)
        loss = loss_function(outputs, labels)
        loss.backward()
        optimizer.step()

        epoch_train_loss += loss.item()

    with torch.no_grad():
        for test_data in test_dataloader:
            inputs, labels = test_data

            inputs = inputs.float()
            outputs = model(inputs)
            loss = loss_function(outputs, labels)

            epoch_test_loss += loss.item()

    epoch_train_loss /= len(train_dataloader)
    epoch_test_loss /= len(test_dataloader)

    train_losses.append(epoch_train_loss)
    test_losses.append(epoch_test_loss)

    print(f"Epoch {epoch} - Train Loss: {epoch_train_loss:.4f}, Test Loss: {epoch_test_loss:.4f}")


plt.plot(list(range(40)),train_losses)
plt.plot(list(range(40)),test_losses)