###################################################################################################
# MemeNet dataloader
# Marco Giordano
# Center for Project Based Learning
# 2022 - ETH Zurich
###################################################################################################
"""
MemeNet dataset
"""
from torch.utils.data import Dataset
from torch.utils.data import DataLoader

import torchvision
from torchvision import transforms
from torchvision.io import read_image

import ai8x

import os
import pandas as pd

import matplotlib.pyplot as plt

"""
Custom image dataset class
"""
class MemesDataset(Dataset):
    def __init__(self, img_dir, transform=None):
        self.img_labels = pd.read_csv(os.path.join(img_dir, "labels.txt"))
        self.img_dir = img_dir
        self.transform = transform

    def __len__(self):
        return len(self.img_labels)

    def __getitem__(self, idx):
        img_path = os.path.join(self.img_dir, self.img_labels.iloc[idx, 0])
        image = read_image(img_path)
        label = self.img_labels.iloc[idx, 1]
        if self.transform:
            image = self.transform(image)
        return image, label

"""
Dataloader function
"""
def memes_get_datasets(data, load_train=False, load_test=False):
   
    (data_dir, args) = data
    # data_dir = data

    if load_train:
        train_transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.RandomAffine(degrees=30, translate=(0.5, 0.5), scale=(0.5,1.5), fill=0),
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0),
            # transforms.GaussianBlur(kernel_size=3),
            # transforms.RandomGrayscale(p=0.1),
            transforms.Resize((64,64)),
            transforms.ToTensor(),
            ai8x.normalize(args=args)
        ])

        train_dataset = MemesDataset(img_dir=os.path.join(data_dir, "memes", "train"), transform=train_transform)
    else:
        train_dataset = None

    if load_test:
        test_transform = transforms.Compose([
            transforms.ToPILImage(),
            # 960 and 720 are not random, but dimension of input test img
            transforms.CenterCrop((960,720)),
            transforms.Resize((64,64)),
            transforms.ToTensor(),
            ai8x.normalize(args=args)
        ])

        test_dataset = MemesDataset(img_dir=os.path.join(data_dir, "memes", "test"), transform=test_transform)

        # if args.truncate_testset:
        #     test_dataset.data = test_dataset.data[:1]
    else:
        test_dataset = None

    return train_dataset, test_dataset


"""
Dataset description
"""
datasets = [
    {
        'name': 'memes',
        'input': (3, 64, 64),
        'output': list(map(str, range(4))),
        'loader': memes_get_datasets,
    }
]
