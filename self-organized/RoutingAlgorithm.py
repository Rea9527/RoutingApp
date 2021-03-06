# coding:utf-8

_EMPTY_ = 0
# DV
# addr_self, 主机地址，tuple类型，如("192.168.1.1", 8090)
# addr_sender, 发来DV的相邻主机的地址，同上

# dv_self 主机的距离向量，dict类型
# 如 dv_self = {("192.168.1.2", 8090) : 3, ...}, 3为到该客户机的最小路径开销

# dv_received, sender发来的距离向量                                                }

# routing_table, 主机的路由表，dict类型
# 如 routing_table = {("192.168.1.2", 8090): {"port": "0", "state": 1},
# 						("192.168.1.3", 8090): {"port": "1", "state": 1},
#						("192.168.1.4", 8091): {"port": "0", "state": 1} }
# port表示到该主机，应该从哪个端口出去

# ports, 相邻主机与端口的映射，如{"0": ("192.168.1.2"， 8095)}

# 返回值，布尔型，主机的距离向量有没有更新，即是否需要向所有邻居发送本机距离向量
# dv_self, dv_neighbors, routing_table参数传引用，均在此函数内更新
def DV(addr_self, addr_sender, dv_self, dv_received, routing_table, ports):
    # 本机DV是否改变
    dv_changed = False

    # 将接收到的DV中，所有未记录在本机DV的主机信息更新到本机DV
    for addr in dv_received.keys():
        if dv_self.has_key(addr) and dv_self[addr] > (dv_received[addr] + 1):
            dv_self[addr] = dv_received[addr] + 1
            for port in ports:
                if ports[port] == addr_sender:
					# print "routing_table:", routing_table
					routing_table[addr]["port"] = port
					break
            dv_changed = True
        if (not dv_self.has_key(addr)) and addr_self != addr:
            dv_self[addr] = dv_received[addr] + 1
            _port = routing_table[addr_sender]["port"]
            routing_table[addr] = {}
            routing_table[addr]["port"] = _port
            routing_table[addr]["state"] = 1
            dv_changed = True

    return [dv_changed, dv_self, routing_table, ports]




