# coding:utf-8

# LS
# TOPO: 拓扑图, dict类型, key为当前主机, tuple类型; value为所有的直连主机,数组类型
# 如: {("192.168.1.1", 8090): [("192.168.1.2", 8095), ("192.168.1.3", 8092)], 
#     ("192.168.1.2", 8095): [("192.168.1.1", 8090), ("192.168.1.4", 8090), ("192.168.1.5", 8090)]}

# ports: 源主机端口与其它主机地址的映射(即数据报要去到哪个地址，就应该从哪个端口出去), dict类型
# 如: {"0": ("192.168.1.2"， 8095)}

# srcaddr: 源主机, tuple类型, 如("192.168.1.1", 8090), tuple中第一个为host(字符串类型), 第二个参数为port(整数类型)
# desaddr: 目的主机, 同上.

# 返回值: 端口号(计算出最短路径后, 数据报应从源主机的哪个端口出去), string类型, 如"0", "1"; 若无法到达, 回空字符串""
def LS(TOPO, ports, srcaddr, desaddr):
	pass


# DV
# addr, 主机地址，tuple类型，如("192.168.1.1", 8090)

# selfRoutingTable, clientRoutingTable分别为主机和客户机的路由表，dist类型
# 如 selfRoutingTable = {("192.168.1.2", 8090): {"port": "0", "state": 1},
# 						("192.168.1.3", 8090): {"port": "1", "state": 1},
#						("192.168.1.4", 8091): {"port": "0", "state": 1} }
# 表示到这三个IP，应该从哪个端口（port）出去

# 返回值，数组类型，[更新后的主机路由表, 是否有更新（0或1）]
def DV(addr, selfRoutingTable, clientRoutingTable):
	return [selfRoutingTable, 1]


