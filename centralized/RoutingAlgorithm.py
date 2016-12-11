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
	if desaddr not in TOPO.keys():
		return ""
	D = {(srcaddr): [0, srcaddr]}
	N = {(srcaddr):0}
	for key in TOPO:
		if key in TOPO[srcaddr]:
			D.update({(key):[1,srcaddr]})
		else:
			D.update({(key):[2147483647,srcaddr]})
			pass
	print "D:", D
	D.update({(srcaddr):[0, srcaddr]})
	F = sorted(D.items(), key=lambda D: D[1])[:]
	while hasnot_keys(TOPO,N):
		for e in F:
			if (e[0] not in N):
				if (e[1][0] != 2147483647):
					N.update({(e[0]):0})
					for elment in TOPO[e[0]]:
						if (elment not in N):
							if ( D[elment][0] < (D[e[0]][0]+1)):
							 	pass
							else:
							 	D[elment][0] = D[e[0]][0]+1
							 	D[elment][1] = e[0]
								F = sorted(D.items(), key=lambda D: D[1])[:]
						else:
							pass
				break
			else:
				pass
	while D[desaddr][1] != srcaddr:
		desaddr = D[desaddr][1]
		pass
	for key in ports:
		if ports[key]:
			if tuple(ports[key]) == desaddr:
				return key
	return ""

def hasnot_keys(TOPO, N):
	for key in TOPO:
		if key not in N:
			return True
	return False


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


