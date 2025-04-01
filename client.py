import random
import logging
import math
random.seed(123)


class Client(object):
	"""Simulated client."""

	def __init__(self, client_id,config):
		self.client_id = client_id
		#判断设备的活跃状态
		self.alive=True
		self.config=config
		#定义各个设备的成本
		self.reward={}
		self.category=''
		self.proficiency=None
		"""计算单位训练成本"""
		#cpu频率  (2-2.5)GHz
		self.fn=0
		#CPU/GPU周期 20-30/bit
		self.Cyn=0

		"""计算香农公式"""
		# 传输带宽  0.5-1MHz
		self.B = (0.005 * random.randint(100, 170)) * (10 ** 6)
		# 传输功率   0.3-0.5W
		self.Pn = 0.01 * random.randint(50, 70) - 0.2
		# 信道增益 -40dBm
		self.hn = -0.04
		# 噪声 2*10(-8)
		self.N0 = 10**(-8)
		#定义函数计算rn
		self.rn=0
		self.temp_battery_num=0
		#读取客户端比例信息
		self.ratio=config.clients.ratio


	def set_config(self):
		total_ratio = sum(self.ratio)
		high_ratio = self.ratio[0] / total_ratio
		medium_ratio = self.ratio[1] / total_ratio
		low_ratio = self.ratio[2] / total_ratio

		# 根据比例分配客户端数量
		high_count = int(self.config.clients.total * high_ratio)
		medium_count = int(self.config.clients.total * medium_ratio)
		low_count = self.config.clients.total - high_count - medium_count  # 剩余的分配给低性能客户端

		# 创建客户端编号
		temp = list(range(self.config.clients.total))
		# 分配到各个类别
		if self.client_id in temp[:high_count]:
			self.category=="H"
			self.ene_cost_rate=0.0001* random.randint(11000, 13000)
			self.fn = 0.01 * random.randint(260, 270) * (10 ** 9)
			self.Cyn = 0.1 * random.randint(140, 160)  # 105.33
		elif self.client_id in temp[high_count:high_count + medium_count]:
			self.category=="M"
			self.ene_cost_rate = 0.0001 * random.randint(12000, 14000)
			self.fn = 0.01 * random.randint(240, 250) * (10 ** 9)
			self.Cyn = 0.1 * random.randint(190, 210)    #120
		elif self.client_id in temp[high_count+medium_count:]:
			self.category=="L"
			self.ene_cost_rate = 0.0001 * random.randint(13000, 15000)
			self.fn = 0.01 * random.randint(220, 230) * (10 ** 9)
			self.Cyn = 0.1 * random.randint(240, 260)    #126.56

	#初始化客户端完成任务的能力和熟练度
	def set_task_capability(self, blocks, lengths, block_size,task):
		self.task=task
		self.task_cap=random.sample(list(range(len(blocks))),self.config.clients.task["task_num"])
		self.lengths = sum(lengths[i] for i in self.task_cap)
		self.size= sum(block_size[i] for i in self.task_cap)
		self.proficiency = [int(random.uniform(self.config.clients.task["proficiency_rage"][0],self.config.clients.task["proficiency_rage"][1])) for _ in range(self.config.clients.task["task_num"])]

	#获取总的成本, 能耗*（能耗成本比)
	def getEnergy(self):
		self.tol_energy_consumption = self.getEcomp(self.task["act_size"],self.lengths) + self.getEcomm(self.task["act_size"])
		self.cost=self.tol_energy_consumption*self.ene_cost_rate
		return self.cost
	#计算能耗
	def getEcomp(self,data_size,block_length):
		return self.getUnit_Cost(data_size)*block_length
	#通信能耗
	def getEcomm(self,data_size):
		rates = self.getRates()
		#print("通信能耗{}".format(2 * model_size * self.Pn / rates))
		return 2 * data_size * self.Pn / rates
	def getRates(self):
		# 香农公式及其参数  得到传输速率
		self.rn = self.B * math.log((1 + self.Pn * self.hn) / self.N0, math.e)
		return self.rn

	def getUnit_Cost(self,data_size):
		#此处得到训练成本
		# the effective capacitance parameter of computing chipset for worker
		effective_cap =10**(-28)
		return effective_cap * self.Cyn * (self.fn ** 2) * data_size

	# Server interactions
	def download(self, argv):
		# Download from the server.
		try:
			return argv.copy()
		except:
			return argv

	def upload(self, argv):
		# Upload to the server
		try:
			return argv.copy()
		except:
			return argv


	def run(self):
		# Perform task
		return {
			"train": self.train()
		}[self.task]

	def get_report(self):
		# Report results to server.
		return self.upload(self.report)

	# Machine learning tasks
	def train(self):

		# Perform model training
		trainloader = fl_model.get_trainloader(self.trainset, self.batch_size)
		#print("当前客户端：{}的训练集大小{}".format(self.client_id,len(self.trainset)))
		#print("当前客户端：{}的epochge{}".format(self.client_id,self.epochs))
		fl_model.train(self.model, trainloader,self.get_glo_model(),
					   self.optimizer, self.epochs)

		# Extract model weights and biases
		weights = fl_model.extract_weights(self.model)

		# Generate report for server
		self.report = Report(self)
		self.report.weights = weights

		# Perform model testing if applicable
		if self.do_test:
			testloader = fl_model.get_testloader(self.testset, 1000)
			self.report.accuracy = fl_model.test(self.model, testloader)
			#print("客户端{}的准确率为：{}".format(self.client_id,self.report.accuracy))
			# self.report.model_acc[self.report.client_id] = self.report.accuracy
		return (self.client_id, self.report)
