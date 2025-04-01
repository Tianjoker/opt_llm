import logging
import pickle
import client
import select
from tools import split_layers, Ability, Worker, HeapTriple
import math
import heapq
from queue import Queue

class Task(object):
    def __init__(self,config):
        self.config = config

    # Set up server
    def boot(self):
        logging.info('Booting {} server...'.format(self.config.task.name))

        total_clients = self.config.clients.total

        # Set up simulated server设置模拟任务服务器
        self.load_task()

        # with open('clients.pickle','rb') as f:
        # 	cli_list=pickle.load(f)
        # 	self.clients=cli_list

        # 加载可用客户端，配置其本地数据 配置等信息
        self.make_clients(total_clients)

        # # 序列化对象方便读取使用
        # with open('clients.pickle', 'wb') as f:
        #     pickle.dump([cli for cli in self.clients], f)


    def load_task(self):
        # Extract config for loaders#提取加载程序的配置
        config = self.config
        # Set up task
        self.task = {
            'gpt3': config.task.size["gpt3"],
            'llama2': config.task.size["llama2"],
            'deepseekv3': config.task.size["deepseekv3"]
        }[config.task.name]
        logging.info('Model name: {}, Blocks nums: {}, Size: {}, Buget'.format(
            config.task.name, self.task["transformer_num"], self.task["size"], self.task["tol_buget"]))

        self.blocks, self.lengths , self.block_size = split_layers(self.task["transformer_num"], config.task.block_num, config.task.seed)

    def make_clients(self, num_clients):

        # Extract config for loaders#提取加载程序的配置
        config = self.config

        # Make simulated clients制作模拟客户端
        # 每个客户端在创建时配置相应的硬件信息
        clients = []
        for client_id in range(num_clients):
            # Create new client
            new_client = client.Client(client_id,config)
            #初始化参数
            new_client.set_config()
            #初始化能力配置
            new_client.set_task_capability(self.blocks, self.lengths , self.block_size,self.task)
            clients.append(new_client)
        logging.info('Total clients: {}'.format(len(clients)))
        self.clients = clients

    def run(self):
        self.task_budget=self.task["tol_buget"]
        # 初始化最大堆
        heap = []  # 已选择的客户端集合（HBsFS），未考虑的客户端集合（HNCB），以及当前解的上界（U）。
        HNCB = set()  # 存未考虑的客户端
        HBsFS = set()
        CBFS = set()  # 当前最佳解集合

        for client in self.clients:
            ability = Ability(client.task_cap,client.proficiency)
            worker = Worker(ability, client.getEnergy())
            HNCB.add(worker)
        heapq.heappush(heap, HeapTriple(HBsFS.copy(), HNCB.copy(), float('inf')))
        HNCB.clear()

        select_method=select.Select(self.config,heap,HNCB,HBsFS,CBFS,self.task_budget)
        CBFS=select_method.ICOA()
        print(CBFS)














