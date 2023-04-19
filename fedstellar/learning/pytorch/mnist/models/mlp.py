from typing import List, Dict
import lightning as pl
import torch
import torchmetrics
from torch.nn import functional as F
from torchmetrics import Accuracy

EPOCH_OUTPUT = List[Dict[str, torch.Tensor]]

###############################
#    Multilayer Perceptron    #
###############################


class MLP(pl.LightningModule):
    """
    Multilayer Perceptron (MLP) to solve MNIST with PyTorch Lightning.
    """

    def __init__(
            self, metric=Accuracy, out_channels=10, lr_rate=0.001, seed=None
    ):  # low lr to avoid overfitting

        # Set seed for reproducibility iniciialization
        if seed is not None:
            torch.manual_seed(seed)
            torch.cuda.manual_seed_all(seed)

        super().__init__()
        self.example_input_array = torch.zeros(1, 1, 28, 28)
        self.lr_rate = lr_rate
        self.metric = metric(num_classes=10, task="multiclass")

        self.l1 = torch.nn.Linear(28 * 28, 256)
        self.l2 = torch.nn.Linear(256, 128)
        self.l3 = torch.nn.Linear(128, out_channels)

    def forward(self, x):
        """ """
        batch_size, channels, width, height = x.size()

        # (b, 1, 28, 28) -> (b, 1*28*28)
        x = x.view(batch_size, -1)
        x = self.l1(x)
        x = torch.relu(x)
        x = self.l2(x)
        x = torch.relu(x)
        x = self.l3(x)
        x = torch.log_softmax(x, dim=1)
        return x

    def configure_optimizers(self):
        """ """
        return torch.optim.Adam(self.parameters(), lr=self.lr_rate)

    def training_step(self, batch, batch_id):
        """ """
        x, y = batch
        loss = F.cross_entropy(self(x), y)
        self.log("Train/Loss", loss, prog_bar=True)
        return loss

    def validation_step(self, batch, batch_idx):
        """ """
        x, y = batch
        logits = self(x)
        loss = F.cross_entropy(self(x), y)
        out = torch.argmax(logits, dim=1)
        metric = self.metric(out, y)
        self.log("Validation/Loss", loss, prog_bar=True)
        self.log("Validation/Accuracy", metric, prog_bar=True)
        return loss

    def test_step(self, batch, batch_idx):
        """ """
        x, y = batch
        logits = self(x)
        loss = F.cross_entropy(self(x), y)
        out = torch.argmax(logits, dim=1)
        metric = self.metric(out, y)
        self.log("Test/Loss", loss, prog_bar=True)
        self.log("Test/Accuracy", metric, prog_bar=True)
        return loss
