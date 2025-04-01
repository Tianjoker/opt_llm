import math
import heapq
from queue import Queue
from functools import total_ordering
from tools import HeapTriple


class ComputeBoundResult:
    def __init__(self, Sc, L, U):
        self.Sc = Sc.copy()  # 候选集
        self.L = L  # 下界影响
        self.U = U  # 上界影响

class Select:
    def __init__(self,config,heap,HNCB,HBsFS,CBFS,task_budget):
        self.config=config
        self.heap=heap
        self.HNCB=HNCB
        self.HBsFS=HBsFS
        self.CBFS=CBFS
        self.task_budget=task_budget
        self.layers=list(range(self.config.task.block_num))

    def ICOA(self):

        self.alpha = self.config.server.alpha
        self.beta = self.config.server.beta

        LG = 0.0  # 全局下界
        UG = float('inf')  # 全局上界

        while LG < UG and self.heap:
            current = heapq.heappop(self.heap)  # 当前处理的分支
            print(f"\n处理分支：HBsFS={current.HBsFS}, HNCB={current.HNCB}, U={current.U:.6f}")

            # 创建两个分支：包含和不包含当前客户端
            for cli in current.HNCB.copy():  # 遍历未考虑的客户端
                # 计算已选客户端的总成本
                current_cost = self.get_cost(current.HBsFS)
                print(current_cost)
                # 判断添加当前客户端后是否超过预算
                if current_cost + cli.w > self.task_budget:
                    continue  # 超出预算，跳过

                # 分支一：包含该客户端
                Sa = current.HBsFS.copy()
                Sa.add(cli)
                SB_HNCB = current.HNCB - {cli}  # 未考虑的客户端

                # 输出分支一信息，显示客户端能力和成本
                print(f"\n分支一：包含客户端，能力=({cli.loc.task_cap}, {cli.loc.proficiency}), 成本={cli.w}")
                print("Sa:", [b.w for b in Sa])
                print("HNCB:", [b.w for b in SB_HNCB])

                # 计算边界
                cb_a = self.compute_bound(Sa, SB_HNCB)
                if cb_a.L > LG:
                    LG = cb_a.L
                    self.CBFS = cb_a.Sc
                    print(f"更新LG为 {LG:.6f}")
                if cb_a.U > LG:
                    heapq.heappush(self.heap, HeapTriple(Sa.copy(), SB_HNCB.copy(), cb_a.U))
                    print(f"将分支一 (U={cb_a.U:.6f}) 插入堆")

                # 分支二：不包含该客户端
                Sb = current.HBsFS.copy()
                SB_HNCB = current.HNCB - {cli}

                # 输出分支二信息，显示端位置和成本
                print(f"\n分支二：不包含客户端，能力=({cli.loc.task_cap}, {cli.loc.proficiency}), 成本={cli.w}")
                print("Sb:", [b.w for b in Sb])
                print("HNCB:", [b.w for b in SB_HNCB])

                cb_b = self.compute_bound(Sb, SB_HNCB)
                if cb_b.L > LG:
                    LG = cb_b.L
                    self.CBFS = cb_b.Sc
                    print(f"更新LG为 {LG:.6f}")
                if cb_b.U > LG:
                    heapq.heappush(self.heap, HeapTriple(Sb.copy(), SB_HNCB.copy(), cb_b.U))
                    print(f"将分支二 (U={cb_b.U:.6f}) 插入堆")

        print("\n最优解集合：")
        for b in self.CBFS:
            # 输出最优客户端的能力和成本
            print(f"客户端能力({b.loc.task_cap}, {b.loc.proficiency}), 成本{b.w}")
        return self.CBFS

    def compute_bound(self, Sa, S_, verbose=True):
        """分支定界核心计算函数"""
        Sd = set()  # S*
        new_Sa = Sa.copy()

        while self.get_cost(Sa) + self.get_cost(S_) <= self.task_budget and len(S_) > 0:
            # 简化实现，假设选择S_中第一个符合条件的客户端
            #需要按照原文----
            for cli in S_:
                if self.get_cost(Sa) + cli.w <= self.task_budget:
                    Sd.add(cli)
                    S_.remove(cli)
                    break  # 模拟选择第一个符合条件的                   客户端

        new_Sc = Sa | Sd
        L = self.IS(new_Sc)
        U = self.ISUpper(new_Sc)  # 使用上界函数

        if verbose:
            print(f"候选集 Sc: {[cli.w for cli in new_Sc]}")
            print(f"下界 L: {L:.6f}")
            print(f"上界 U: {U:.6f}")
            print("-------------------------")

        return ComputeBoundResult(new_Sc, L, U)

    def get_cost(self,S):
        """计算客户端集合总成本"""
        return sum(cli.w for cli in S)

    def IS(self,S):
        """
        计算客户端集合对区块集合的有效影响
        :param S: 客户端集合
        :param t_list: 区块列表
        :return: 影响值
        """

        score=[0.0] * len(self.layers)
        block_weights=[1] * len(self.layers)
        index=0
        for block in self.layers:
            for s in S:
                print(s.loc.loc[0])
                if block in s.loc.loc[0]:
                    score[index]+=s.loc.loc[1][s.loc.loc[0].index(block)]
            index+=1

        return sum([(1 / (1 + math.exp(self.alpha - self.beta * x))) * y for y,x in zip(block_weights, score)])

    def ISUpper(self,S):
        """计算客户端集合的上界影响力"""
        # 这里需要实现ISUpper的功能，但由于实现复杂，暂时简化为IS的1.2倍
        data = self.IS(S)
        #按照原文
        return data * 1.2