# @quantlab/output: 5f13143d
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

class FinancialGAN:
    """
    简化版金融时间序列GAN

    生成器: 从噪声生成收益率序列
    判别器: 区辩真实 vs 生成的收益率序列
    """

    def __init__(self, seq_length=60, feature_dim=5, latent_dim=32):
        self.seq_length = seq_length
        self.feature_dim = feature_dim
        self.latent_dim = latent_dim

        # 生成器
        self.generator = nn.Sequential(
            nn.Linear(latent_dim, 128),
            nn.LeakyReLU(0.2),
            nn.Linear(128, 256),
            nn.LeakyReLU(0.2),
            nn.Linear(256, seq_length * feature_dim),
            nn.Tanh()  # 输出范围 [-1, 1]
        )

        # 判别器
        self.discriminator = nn.Sequential(
            nn.Linear(seq_length * feature_dim, 256),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            nn.Linear(256, 128),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            nn.Linear(128, 1),
            nn.Sigmoid()
        )

        self.g_optimizer = optim.Adam(self.generator.parameters(), lr=0.0002, betas=(0.5, 0.999))
        self.d_optimizer = optim.Adam(self.discriminator.parameters(), lr=0.0002, betas=(0.5, 0.999))
        self.criterion = nn.BCELoss()

    def train(self, real_data, n_epochs=100, batch_size=32):
        """训练GAN"""
        real_data = torch.FloatTensor(real_data)
        dataset = TensorDataset(real_data)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

        for epoch in range(n_epochs):
            for batch_idx, (real_batch,) in enumerate(dataloader):
                batch_size_actual = real_batch.size(0)

                # 真实标签为1，虚假标签为0
                real_labels = torch.ones(batch_size_actual, 1)
                fake_labels = torch.zeros(batch_size_actual, 1)

                # === 训练判别器 ===
                self.d_optimizer.zero_grad()

                # 真实数据损失
                real_output = self.discriminator(real_batch.view(batch_size_actual, -1))
                d_real_loss = self.criterion(real_output, real_labels)

                # 虚假数据损失
                noise = torch.randn(batch_size_actual, self.latent_dim)
                fake_data = self.generator(noise)
                fake_output = self.discriminator(fake_data.detach().view(batch_size_actual, -1))
                d_fake_loss = self.criterion(fake_output, fake_labels)

                d_loss = d_real_loss + d_fake_loss
                d_loss.backward()
                self.d_optimizer.step()

                # === 训练生成器 ===
                self.g_optimizer.zero_grad()

                noise = torch.randn(batch_size_actual, self.latent_dim)
                fake_data = self.generator(noise)
                fake_output = self.discriminator(fake_data.view(batch_size_actual, -1))
                g_loss = self.criterion(fake_output, real_labels)  # 生成器希望被判定为真

                g_loss.backward()
                self.g_optimizer.step()

            if epoch % 20 == 0:
                print(f"Epoch {epoch}: D_loss={d_loss.item():.4f}, G_loss={g_loss.item():.4f}")

    def generate(self, n_samples):
        """生成合成金融时间序列"""
        self.generator.eval()
        with torch.no_grad():
            noise = torch.randn(n_samples, self.latent_dim)
            synthetic = self.generator(noise)
            synthetic = synthetic.view(n_samples, self.seq_length, self.feature_dim)
            return synthetic.numpy()

# ===== 示例：使用GAN生成合成收益率数据 =====
np.random.seed(42)
n_sequences = 500
seq_len = 60
n_features = 5

# 生成真实数据（模拟多资产收益率）
real_returns = np.random.randn(n_sequences, seq_len, n_features) * 0.01
# 加入一些真实数据的统计特征：波动率聚类
for i in range(n_sequences):
    regime = np.random.choice([0.5, 1.0, 2.0], p=[0.2, 0.6, 0.2])
    real_returns[i] *= regime

# 训练GAN（概念演示）
print("金融时间序列GAN演示:")
print(f"  真实数据形状: {real_returns.shape}")
print(f"  生成器将在 {seq_len * n_features} 维空间中学习\n")

gan = FinancialGAN(seq_length=seq_len, feature_dim=n_features, latent_dim=32)

# gan.train(real_returns, n_epochs=200)  # 实际训练时取消注释
# synthetic_data = gan.generate(100)
#
# # 验证生成数据的统计特征
# print("生成数据的统计验证:")
# print(f"  真实数据均值: {real_returns.mean():.6f}")
# print(f"  合成数据均值: {synthetic_data.mean():.6f}")
# print(f"  真实数据标准差: {real_returns.std():.6f}")
# print(f"  合成数据标准差: {synthetic_data.std():.6f}")

print("GAN模型结构已创建，取消注释以运行训练")
