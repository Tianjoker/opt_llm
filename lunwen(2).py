import math
import heapq
from queue import Queue
from functools import total_ordering

# 地球半径常量
EARTH_RADIUS = 6371.004


# -------------------------数据结构定义-------------------------
@total_ordering
class Location:
    def __init__(self, lat, lng):
        self.lat = lat  # 纬度
        self.lng = lng  # 经度
        self.loc = [lat,lng]
    # 为了能放入集合需要定义比较方法
    def __eq__(self, other):
        return self.lat == other.lat and self.lng == other.lng

    def __lt__(self, other):
        return (self.lat, self.lng) < (other.lat, other.lng)

    def __hash__(self):
        return hash((self.lat, self.lng))


class Trajectory:
    def __init__(self, *locs):
        """
        初始化轨迹对象，轨迹由多个轨迹点组成
        :param locs: 任意数量的轨迹点
        """
        self.locations = list(locs)  # 将轨迹点存储在列表中

    def add_location(self, loc):
        """添加一个新的轨迹点"""
        self.locations.append(loc)

    def __repr__(self):
        return f"Trajectory({', '.join([f'({loc.lat}, {loc.lng})' for loc in self.locations])})"


@total_ordering
class Billboard:
    def __init__(self, loc, w):
        self.loc = loc  # 位置对象
        self.w = w  # 成本

    def __eq__(self, other):
        return self.loc == other.loc and self.w == other.w

    def __lt__(self, other):
        return (self.w, self.loc.lat, self.loc.lng) < (other.w, other.loc.lat, other.loc.lng)

    def __hash__(self):
        return hash((self.loc, self.w))


@total_ordering
class SelectCandidate:
    def __init__(self, mize, billboard):
        self.mize = mize  # 影响力/成本比值
        self.billboard = billboard  # 广告牌对象

    def __lt__(self, other):
        return self.mize < other.mize

    def __eq__(self, other):
        return self.mize == other.mize


@total_ordering
class HeapTriple:
    def __init__(self, HBsFS, HNCB, U):
        self.HBsFS = HBsFS.copy()  # 已选广告牌集合
        self.HNCB = HNCB.copy()  # 未考虑广告牌集合
        self.U = U  # 上界值

    def __lt__(self, other):
        return self.U < other.U

    def __eq__(self, other):
        return self.U == other.U


class ComputeBoundResult:
    def __init__(self, Sc, L, U):
        self.Sc = Sc.copy()  # 候选集
        self.L = L  # 下界影响
        self.U = U  # 上界影响


# -------------------------全局变量-------------------------
trajectory_num = 0  # 轨迹点数
trajectory_group_num = 0  # 轨迹组数
nb = 0.0  # 距离阈值
trajectory_group = Queue()  # 轨迹队列
LG = 0.0  # 全局下界
UG = float('inf')  # 全局上界
CBFS = set()  # 当前最佳解集合
HBsFS = set()
billboard_budget = 0  # 广告牌预算
af = 0.0  # α参数
bf = 0.0  # β参数


# -------------------------工具函数-------------------------
def get_cost(S):
    """计算广告牌集合总成本"""
    return sum(b.w for b in S)


def rad(d):
    """角度转弧度"""
    return math.radians(d)


def Iot(o, t_list):
    """
    判断广告牌是否影响轨迹点
    :param o: 广告牌对象
    :param t_list: 轨迹点列表
    :return: 是否在影响范围内 (0/1)
    """
    for t in t_list:
        # 计算大圆距离
        lat1 = rad(o.loc.lat)
        lng1 = rad(o.loc.lng)
        lat2 = rad(t.loc[0])
        lng2 = rad(t.loc[1])

        dlat = lat1 - lat2
        dlng = lng1 - lng2

        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))
        distance = c * EARTH_RADIUS

        if distance <= nb:
            return 1
    return 0


def P(S, t_list):
    """
    计算广告牌集合对轨迹的有效影响
    :param S: 广告牌集合
    :param t_list: 轨迹点列表
    :return: 影响概率值
    """
    count = sum(1 for b in S if Iot(b, t_list))
    if count == 0:
        return 0.0
    return 1 / (1 + math.exp(af - bf * count))

def IS(S):
    """计算广告牌集合对轨迹的总体影响力"""
    total = 0.0

    # 遍历轨迹队列中的所有轨迹
    trajectory_group_copy = Queue()
    trajectory_group_copy.queue.extend(trajectory_group.queue)
    while not trajectory_group_copy.empty():
        traj = trajectory_group_copy.get()
        # 获取该轨迹的所有轨迹点
        t_points = traj.locations  # 轨迹点集合
        # 计算广告牌集合 S 对该轨迹的影响力
        total += P(S, t_points)

    return total

def ISUpper(S):
    """计算广告牌集合的上界影响力"""
    # 这里需要实现ISUpper的功能，但由于实现复杂，暂时简化为IS的1.2倍
    data = IS(S)
    return data * 1.2

# -------------------------核心算法函数-------------------------
def compute_bound(Sa, S_, verbose=True):
    """分支定界核心计算函数"""
    Sd = set()  # S*
    new_Sa = Sa.copy()

    while get_cost(Sa) + get_cost(S_) <= billboard_budget and len(S_) > 0:
        # 简化实现，假设选择S_中第一个符合条件的广告牌
        for bill in S_:
            if get_cost(Sa) + bill.w <= billboard_budget:
                Sd.add(bill)
                S_.remove(bill)
                break  # 模拟选择第一个符合条件的广告牌

    new_Sc = Sa | Sd
    L = IS(new_Sc)
    U = ISUpper(new_Sc)  # 使用上界函数

    if verbose:
        print(f"候选集 Sc: {[b.w for b in new_Sc]}")
        print(f"下界 L: {L:.6f}")
        print(f"上界 U: {U:.6f}")
        print("-------------------------")

    return ComputeBoundResult(new_Sc, L, U)

# -------------------------主程序-------------------------
def main():
    global af, bf, nb, billboard_budget, trajectory_num, trajectory_group_num, LG, CBFS

    print("--------定值输入--------\n")
    # af, bf = map(float, input("请输入α和β的值：").split())
    af = 1.5
    bf = 0.8
    nb = 100
    # nb = float(input("请输入规定的距离阈值："))

    print("\n------广告牌信息输入------\n")
    billboard_budget = 50
    # billboard_budget = int(input("请输入广告牌预算："))
    # group_num = int(input("请输入广告牌组数："))
    # bill_num = int(input("请输入每组广告牌数量："))
    group_num = 3
    bill_num = 4
    # 初始化最大堆
    heap = []  # 已选择的广告牌集合（HBsFS），未考虑的广告牌集合（HNCB），以及当前解的上界（U）。
    HNCB = set()  # 存未考虑的广告牌

    print("请输入每个广告牌的经度、纬度和成本：")  # 注意这个是按组把广告牌扔进去
    for i in range(group_num):
        print(f"第{i + 1}组广告牌：")
        bill_group = []
        for _ in range(bill_num):
            lat, lng, w = map(float, input().split())
            loc = Location(lat, lng)
            bill = Billboard(loc, w)
            HNCB.add(bill)
            bill_group.append(bill)
        heapq.heappush(heap, HeapTriple(HBsFS.copy(), HNCB.copy(), float('inf')))
        HNCB.clear()

    print("\n-------轨迹信息输入-------\n")
    trajectory_group_num = int(input("请输入轨迹条数："))
    trajectory_num = int(input("请输入轨迹点数："))

    print("请输入每个轨迹点的经度和纬度：")
    for i in range(trajectory_group_num):
        print(f"第{i + 1}组轨迹点：")
        points = []
        for _ in range(trajectory_num):
            lat, lng = map(float, input().split())
            points.append(Trajectory(Location(lat, lng)))
        for p in points:
            trajectory_group.put(p)


    while LG < UG and heap:
        current = heapq.heappop(heap)  # 当前处理的分支
        print(f"\n处理分支：HBsFS={current.HBsFS}, HNCB={current.HNCB}, U={current.U:.6f}")

        # 创建两个分支：包含和不包含当前广告牌
        for bill in current.HNCB.copy():  # 遍历未考虑的广告牌
            # 计算已选广告牌的总成本
            current_cost = get_cost(current.HBsFS)

            # 判断添加当前广告牌后是否超过预算
            if current_cost + bill.w > billboard_budget:
                continue  # 超出预算，跳过

            # 分支一：包含该广告牌
            Sa = current.HBsFS.copy()
            Sa.add(bill)
            SB_HNCB = current.HNCB - {bill}  # 未考虑的广告牌

            # 输出分支一信息，显示广告牌位置和成本
            print(f"\n分支一：包含广告牌，位置=({bill.loc.lat}, {bill.loc.lng}), 成本={bill.w}")
            print("Sa:", [b.w for b in Sa])
            print("HNCB:", [b.w for b in SB_HNCB])

            # 计算边界
            cb_a = compute_bound(Sa, SB_HNCB)
            if cb_a.L > LG:
                LG = cb_a.L
                CBFS = cb_a.Sc
                print(f"更新LG为 {LG:.6f}")
            if cb_a.U > LG:
                heapq.heappush(heap, HeapTriple(Sa.copy(), SB_HNCB.copy(), cb_a.U))
                print(f"将分支一 (U={cb_a.U:.6f}) 插入堆")

            # 分支二：不包含该广告牌
            Sb = current.HBsFS.copy()
            SB_HNCB = current.HNCB - {bill}

            # 输出分支二信息，显示广告牌位置和成本
            print(f"\n分支二：不包含广告牌，位置=({bill.loc.lat}, {bill.loc.lng}), 成本={bill.w}")
            print("Sb:", [b.w for b in Sb])
            print("HNCB:", [b.w for b in SB_HNCB])

            cb_b = compute_bound(Sb, SB_HNCB)
            if cb_b.L > LG:
                LG = cb_b.L
                CBFS = cb_b.Sc
                print(f"更新LG为 {LG:.6f}")
            if cb_b.U > LG:
                heapq.heappush(heap, HeapTriple(Sb.copy(), SB_HNCB.copy(), cb_b.U))
                print(f"将分支二 (U={cb_b.U:.6f}) 插入堆")

    print("\n最优解集合：")
    for b in CBFS:
        # 输出最优广告牌的完整位置和成本
        print(f"广告牌位置({b.loc.lat}, {b.loc.lng}), 成本{b.w}")


if __name__ == "__main__":
    main()
