import torch
from torchvision.models.resnet import Bottleneck
from torch import nn
from torch.nn import functional as F
from toolz.functoolz import curry


def make_residual_layer(block, inplanes, planes, blocks, stride=1):
    """Create a layer with a number of residual blocks.

    This function was modified from torchvision.models.resnet.ResNet._make_layers for convenience.
    """
    downsample = None
    if stride != 1 or inplanes != planes * block.expansion:
        downsample = nn.Sequential(
            nn.Conv2d(inplanes, planes * block.expansion, 1, stride),
            nn.BatchNorm2d(planes * block.expansion),
        )

    layers = [block(inplanes, planes, stride, downsample)]
    inplanes = planes * block.expansion
    for _ in range(1, blocks):
        layers.append(block(inplanes, planes))

    return nn.Sequential(*layers)


class SoftMask(nn.Module):
    def __init__(self, inplanes, planes, r, residual_block=Bottleneck):
        super().__init__()
        self.inplanes = inplanes
        self.planes = planes
        self.outplanes = self.planes * residual_block.expansion

        self.maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)
        interpolate = curry(F.interpolate)
        self.interpolation = interpolate(mode='bilinear', align_corners=True)

        self.preprocessing = make_residual_layer(residual_block, inplanes, planes, r)
        self.horizontal_connection = make_residual_layer(residual_block, self.outplanes, planes, 1)
        self.core = make_residual_layer(residual_block, self.outplanes, planes, 2*r)
        self.postprocessing = make_residual_layer(residual_block, self.outplanes, planes, r)
        self.conv1x1block = nn.Sequential(
            *[nn.Conv2d(self.outplanes, self.outplanes, 1, 1) for _ in range(2)]
        )

    def forward(self, input):
        x = self.maxpool(input)
        x = self.preprocessing(x)
        residue = self.horizontal_connection(x)
        x = self.maxpool(x)
        x = self.core(x)
        x = self.interpolation(x, size=residue.shape[-2:])
        x = x + residue

        x = self.postprocessing(x)
        x = self.interpolation(x, size=input.shape[-2:])
        x = self.conv1x1block(x)

        return torch.sigmoid(x)


class AttentionModule(nn.Module):
    def __init__(self, inplanes, planes, p, t, r, residual_block=Bottleneck):
        super().__init__()
        self.inplanes = inplanes
        self.planes = planes
        self.outplanes = planes * residual_block.expansion
        self.residual_block = residual_block

        self.preprocessing = make_residual_layer(residual_block, inplanes, planes, p)
        self.mask_branch = SoftMask(self.outplanes, planes, r, residual_block)
        self.trunk_branch = make_residual_layer(residual_block, self.outplanes, planes, t)
        self.postprocessing = make_residual_layer(residual_block, self.outplanes, planes, p)

    def forward(self, input):
        x = self.preprocessing(input)
        mask = self.mask_branch(x)
        x = self.trunk_branch(x)
        x = (1 + mask) * x
        x = self.postprocessing(x)

        return x
