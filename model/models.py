import torch
import torch.nn as nn
from modules import * 
from torchvision.models import resnet50

class SeResNext50_Unet_MultiScale(nn.Module):
    def __init__(self, pretrained='imagenet', **kwargs):
        super(SeResNext50_Unet_MultiScale, self).__init__()

        encoder_filters = [128, 256, 512, 1024, 2048]
        fuse_filter = 64

        self.down12 = DownSample(encoder_filters[0], 2)
        self.down13 = DownSample(encoder_filters[0]*2, 2)
        self.down23 = DownSample(encoder_filters[1], 2)
        self.up21 = UpSample(encoder_filters[1], 2)
        self.up31 = UpSample(encoder_filters[2]//2, 2)
        self.up32 = UpSample(encoder_filters[2], 2)

        self.conv0 = ConvRelu(encoder_filters[0]//2, encoder_filters[0])
        self.convF1 = nn.Sequential(ConvRelu(encoder_filters[0], encoder_filters[0]), SCSEModule(encoder_filters[0], reduction=4, concat=True))
        self.conv1_1 = ConvRelu(encoder_filters[0]*2, encoder_filters[0])
        self.convF2 = nn.Sequential(ConvRelu(encoder_filters[1], encoder_filters[1]), SCSEModule(encoder_filters[1], reduction=8, concat=True))
        self.conv2_1 = ConvRelu(encoder_filters[1]*2, encoder_filters[1])
        self.convF3 = nn.Sequential(ConvRelu(encoder_filters[2], encoder_filters[2]), SCSEModule(encoder_filters[2], reduction=16, concat=True))
        self.conv3_1 = ConvRelu(encoder_filters[2]*2, encoder_filters[2])

        self.conv1_2 = ConvRelu(encoder_filters[0] * 2, fuse_filter)
        self.conv2_2 = ConvRelu(encoder_filters[1] * 2, fuse_filter)
        self.conv3_2 = ConvRelu(encoder_filters[2] * 2, fuse_filter*2)
        self.up31_2 = UpSample(fuse_filter*2, 4)   #32
        self.up21_2 = UpSample(fuse_filter, 2)   #32

        self.conv4 = ConvRelu(fuse_filter * 2, fuse_filter)  # 32+32+64
        self.conv4_2 = nn.Conv2d(fuse_filter, fuse_filter, 1, stride=1, padding=0)
        self.relu = nn.ReLU(inplace=True)

        self.res = nn.Conv2d(64, 1, kernel_size=1, stride=1)

        self.classification_head = nn.Sequential(
            nn.Conv2d(fuse_filter * 2, 5, kernel_size=1)
        )

        self._initialize_weights()

        encoder = resnet50(pretrained = pretrained)

        self.conv1 = nn.Sequential(
            encoder.conv1,
            encoder.bn1,
            encoder.relu,
            encoder.maxpool
        )

        self.conv2 = nn.Sequential(
            encoder.layer1,
            nn.Conv2d(256, 256, kernel_size=3, stride=2, padding=1),  # Introduce downsampling
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
        )

        self.conv3 = nn.Sequential(
            encoder.layer2
        )



    def forward1(self, x):
        batch_size, C, H, W = x.shape
        #print(x.shape)
        enc1 = self.conv1(x)
        #print("\nenc1",enc1.shape)
        enc2 = self.conv2(enc1)
        #print("enc2",enc2.shape)
        enc3 = self.conv3(enc2)
        #print("enc3",enc3.shape)

        enc1 = self.conv0(enc1)
        #print("\nenc1",enc1.shape)
        f12 = self.down12(enc1)
        f13 = self.down13(f12)
        f23 = self.down23(enc2)
        f21 = self.up21(enc2)
        f32 = self.up32(enc3)
        f31 = self.up31(f32)

        #print("\nf12 ", f12.size(),"\nf13 ", f13.size(), "\nf23 ", f23.size(),"\nf21 ",  f21.size(),"\nf32 ",  f32.size(),"\nf31 ",  f31.size())
        fusion1 = self.convF1(enc1+f21+f31)
        fusion1 = self.conv1_1(fusion1)
        fusion2 = self.convF2(enc2+f12+f32)
        fusion2 = self.conv2_1(fusion2)
        fusion3 = self.convF3(enc3+f23+f13)
        fusion3 = self.conv3_1(fusion3)

        dec1 = self.conv1_2(torch.cat([enc1, fusion1], 1))
        dec2 = self.conv2_2(torch.cat([enc2, fusion2], 1))
        dec3 = self.conv3_2(torch.cat([enc3, fusion3], 1))

        dec2 = self.up21_2(dec2)
        dec3 = self.up31_2(dec3)
        dec4 = self.conv4(torch.cat([dec1, dec2, dec3], 1))
        dec4 = self.conv4_2(F.interpolate(dec4, scale_factor=2, mode='bilinear'))
        dec4 = self.conv4_2(F.interpolate(dec4, scale_factor=2, mode='bilinear'))
        dec4 = self.relu(dec4)
        #print("\ndec4",dec4.shape)

        return dec4

    def forward(self, x):
        dec10_0 = self.forward1(x[:, :3, :, :])
        dec10_1 = self.forward1(x[:, 3:, :, :])

        dec10 = torch.cat([dec10_0, dec10_1], 1)

        #return self.res(dec10)
        output = self.classification_head(dec10)

        return output


    def _initialize_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d) or isinstance(m, nn.ConvTranspose2d) or isinstance(m, nn.Linear):
                m.weight.data = nn.init.kaiming_normal_(m.weight.data)
                if m.bias is not None:
                    m.bias.data.zero_()
            elif isinstance(m, nn.BatchNorm2d):
                m.weight.data.fill_(1)
                m.bias.data.zero_()