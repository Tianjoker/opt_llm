import random
from functools import total_ordering
import math
from queue import Queue
@total_ordering
class Ability:
    #能力
    def __init__(self, task_cap, proficiency):
        self.task_cap = task_cap  # 当前客户端可完成的区块列表，假设为列表
        self.proficiency = proficiency  # 当前客户端可完成的区块对应的熟练度，假设为列表
        self.loc = (tuple(task_cap), tuple(proficiency))  # 转换为 tuple

    def __eq__(self, other):
        # 对比时， 转换为 tuple
        return tuple(self.task_cap) == tuple(other.task_cap) and tuple(self.proficiency) == tuple(other.proficiency)

    def __lt__(self, other):
        # 对比时， 转换为 tuple
        return (tuple(self.task_cap), tuple(self.proficiency)) < (tuple(other.task_cap), tuple(other.proficiency))

    def __hash__(self):
        # 对 hash 使用 tuple 类型
        return hash((tuple(self.task_cap), tuple(self.proficiency)))

@total_ordering
class Worker:
    def __init__(self, loc, w):
        self.loc = loc  # 能力tuple
        self.w = w  # 成本

    def __eq__(self, other):
        return self.loc == other.loc and self.w == other.w

    def __lt__(self, other):
        return (self.w, self.loc.task_cap, self.loc.proficiency) < (other.w, other.loc.task_cap, other.loc.proficiency)

    def __hash__(self):
        return hash((self.loc, self.w))

@total_ordering
class HeapTriple:
    def __init__(self, HBsFS, HNCB, U):
        self.HBsFS = HBsFS.copy()  # 已选客户端集合
        self.HNCB = HNCB.copy()  # 未考虑客户端集合
        self.U = U  # 上界值

    def __lt__(self, other):
        return self.U < other.U

    def __eq__(self, other):
        return self.U == other.U



def split_layers(N, M, size, seed=None):
    if seed is not None:
        random.seed(seed)  # 设置随机种子，保证结果可复现

    layers = list(range(N))  # Transformer 层的编号 [0, 1, ..., N-1]
    # random.shuffle(layers)  # 随机打乱层的顺序

    # 生成 M 份，每份的大小随机
    noise_scale=50
    split_sizes = sorted(random.sample(range(1, N), M - 1))  # 生成 M-1 个分割点
    split = []
    split_lengths = []  # 存储每一份的层数
    split_size = []  # 存储每一份的总大小
    start = 0
    for s in split_sizes:
        split.append(layers[start:s])
        split_lengths.append(len(layers[start:s]))
        split_size.append(len(layers[start:s]) * size+int(random.uniform(0, noise_scale)))
        start = s
    split.append(layers[start:])  # 添加最后一部分
    split_lengths.append(len(layers[start:]))
    split_size.append(len(layers[start:]) * size+int(random.uniform(0, noise_scale)))

    return split, split_lengths, split_size



if __name__ == "__main__":
    # 示例：N=12 层 Transformer，随机分成 M=3 份，每层大小为 256，固定种子
    N = 108
    M = 20
    size = 90
    seed = 42
    splits, split_lengths, split_size = split_layers(N, M, size, seed)
    for i, (s, l, sz) in enumerate(zip(splits, split_lengths, split_size)):
        print(f"Group {i + 1} (layers count {l}, total size {sz}): {s}")
