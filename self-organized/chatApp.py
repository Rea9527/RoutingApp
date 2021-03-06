#coding:utf-8
from Tkinter import *
from ttk import *
import socket
import thread
import json
import RoutingAlgorithm as RA

_EMPTY_ = 0
_BUSY_ = 1

_ON_ = 1
_DOWN_ = 0

_MESSAGE_ = "MESSAGE"
_BROADCAST_ = "BROADCAST"

def convert_to_builtin_type(obj):
  d = {}
  d.update(obj.__dict__)
  return d

class ChatClient(Frame):
  
  def __init__(self, root):
    Frame.__init__(self, root)
    self.root = root
    self.initUI()
    self.serverSoc = None
    self.serverStatus = 0
    self.buffsize = 1024
    self.clientSocs = {}
    self.ports = {"0": _EMPTY_, "1": _EMPTY_, "2": _EMPTY_, "3": _EMPTY_}
    self.counter = 0

    # routint table
    self.routingTable = {}

    # dv
    self.dv = {}
  
  def initUI(self):
    self.root.title("Routing")
    ScreenSizeX = self.root.winfo_screenwidth()
    ScreenSizeY = self.root.winfo_screenheight()
    self.FrameSizeX  = 810
    self.FrameSizeY  = 600
    FramePosX   = (ScreenSizeX - self.FrameSizeX)/2
    FramePosY   = (ScreenSizeY - self.FrameSizeY)/2
    self.root.geometry("%sx%s+%s+%s" % (self.FrameSizeX,self.FrameSizeY,FramePosX,FramePosY))
    self.root.resizable(width=False, height=False)
    
    padX = 10
    padY = 10
    parentFrame = Frame(self.root)
    parentFrame.grid(padx=padX, pady=padY, stick=E+W+N+S)
    
    ipGroup = Frame(parentFrame)
    serverLabel = Label(ipGroup, text="Set: ")
    self.serverIPVar = StringVar()
    self.serverIPVar.set("127.0.0.1")
    serverIPField = Entry(ipGroup, width=15, textvariable=self.serverIPVar)
    self.serverPortVar = StringVar()
    self.serverPortVar.set("8090")
    serverPortField = Entry(ipGroup, width=5, textvariable=self.serverPortVar)
    serverSetButton = Button(ipGroup, text="Set", width=10, command=self.handleSetServer)
    addClientLabel = Label(ipGroup, text="Set Conn: ")
    self.clientIPVar = StringVar()
    self.clientIPVar.set("127.0.0.1")
    clientIPField = Entry(ipGroup, width=15, textvariable=self.clientIPVar)
    self.clientPortVar = StringVar()
    self.clientPortVar.set("8091")
    clientPortField = Entry(ipGroup, width=5, textvariable=self.clientPortVar)
    clientSetButton = Button(ipGroup, text="Add", width=10, command=self.handleSetConn)
    serverLabel.grid(row=0, column=0)
    serverIPField.grid(row=0, column=1)
    serverPortField.grid(row=0, column=2)
    serverSetButton.grid(row=0, column=3, padx=5)
    addClientLabel.grid(row=0, column=4)
    clientIPField.grid(row=0, column=5)
    clientPortField.grid(row=0, column=6)
    clientSetButton.grid(row=0, column=7, padx=5)
    
    readChatGroup = Frame(parentFrame)
    self.receivedChats = Text(readChatGroup, bg="white", width=60, height=27, state=DISABLED)
    self.friends = Listbox(readChatGroup, bg="white", width=30, height=27)
    self.receivedChats.grid(row=0, column=0, sticky=W+N+S, padx = (0,10))
    self.friends.grid(row=0, column=1, sticky=E+N+S)

    sendMsgGroup = Frame(parentFrame)
    sendLabel = Label(sendMsgGroup, text="Send To: ")
    self.sendIPVar = StringVar()
    self.sendIPVar.set("127.0.0.1")
    sendIPField = Entry(sendMsgGroup, width=15, textvariable=self.sendIPVar)
    self.sendPortVar = StringVar()
    self.sendPortVar.set("8091")
    sendPortField = Entry(sendMsgGroup, width=5, textvariable=self.sendPortVar)
    sendSetButton = Button(sendMsgGroup, text="Set", width=10, command=self.handleSendIP)
    sendLabel.grid(row=0, column=1)
    sendIPField.grid(row=0, column=2)
    sendPortField.grid(row=0, column=3)
    sendSetButton.grid(row=0, column=4, padx=5)

    writeChatGroup = Frame(parentFrame)
    self.chatVar = StringVar()
    self.chatField = Entry(writeChatGroup, width=80, textvariable=self.chatVar)
    sendChatButton = Button(writeChatGroup, text="Send", width=10, command=self.handleSendChat)
    self.chatField.grid(row=0, column=0, sticky=W)
    sendChatButton.grid(row=0, column=1, padx=5)

    self.statusLabel = Label(parentFrame)

    self.statusLabel.grid(row=0, column=0)
    ipGroup.grid(row=1, column=0)
    readChatGroup.grid(row=2, column=0)
    sendMsgGroup.grid(row=3, column=0)
    writeChatGroup.grid(row=4, column=0, pady=10)
    

    
  def handleSetServer(self):
    if self.serverSoc != None:
      self.serverSoc.close()
      self.serverSoc = None
      self.serverStatus = 0
    serveraddr = (self.serverIPVar.get().replace(' ',''), int(self.serverPortVar.get().replace(' ','')))
    
    try:
      self.serverSoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.serverSoc.bind(serveraddr)
      self.serverSoc.listen(5)
      self.setStatus("Server listening on %s:%s" % serveraddr)
      thread.start_new_thread(self.listenClients,())
      self.serverStatus = 1
      self.name = "%s:%s" % serveraddr
      self.addr = serveraddr
      self.dv = {self.addr: 0}
    except:
      self.setStatus("Error setting up server")

  def handleSendIP(self):
    sendaddr = (self.sendIPVar.get().replace(' ',''), int(self.sendPortVar.get().replace(' ','')))
    self.sendaddr = tuple(sendaddr)
    self.setStatus("Set client %s:%s to send" % sendaddr)

  
  def handleSetConn(self):
    if self.serverStatus == 0:
      self.setStatus("Set server address first")
      return
    clientaddr = (self.clientIPVar.get().replace(' ',''), int(self.clientPortVar.get().replace(' ','')))
    if clientaddr == self.addr:
      print "You cannot connect to yourself!"
    else:
      try:
        clientsoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # print "clientsoc:", clientsoc
        clientsoc.connect(clientaddr)
        clientsoc.send(json.dumps(self.addr))
        self.setStatus("Connected to client on %s:%s" % clientaddr)
        self.addClient(clientsoc, clientaddr)
        thread.start_new_thread(self.handleClientMessages, (clientsoc, clientaddr))
      except:
        self.setStatus("Error connecting to client")


  def listenClients(self):
    while 1:
      clientsoc, clientaddr = self.serverSoc.accept()
      while 1:
        buf = clientsoc.recv(self.buffsize)
        clientaddr = tuple(json.loads(buf))
        break
      print "clientsoc: ", clientsoc, " clientaddr: ",  clientaddr
      self.setStatus("Client connected from %s:%s" % clientaddr)
      self.addClient(clientsoc, clientaddr)
      thread.start_new_thread(self.handleClientMessages, (clientsoc, clientaddr))
    self.serverSoc.close()


  def handleClientMessages(self, clientsoc, clientaddr):
    while 1:
      try:
        data = clientsoc.recv(self.buffsize)
        if not data:
          break
        data = str(data)
        data = json.loads(data)
        # print "data:", data
        if data["tag"] == _MESSAGE_:
          [data["target"], data["sender"]] = tuple(data["target"]), tuple(data["sender"])
          if data["target"] == self.addr:
            self.addChat("%s:%s" % data["sender"], data["msg"])
          else:
            # print "target:", data["target"]
            self.sendaddr = data["target"]
            for client in self.routingTable:
              target_client = self.routingTable[client]
              if target_client["state"] == _ON_ and client == self.sendaddr:
                datagram = {}
                datagram["tag"] = _MESSAGE_
                datagram["msg"] = data["msg"]
                datagram["sender"] = data["sender"]
                datagram["target"] = self.sendaddr

                _port = target_client["port"]
                addr = self.ports[_port]
                soc = self.clientSocs[addr]
                # print soc, target_client, _port
                soc.send(json.dumps(datagram, ensure_ascii=False))
                break
              else:
                pass
        elif data["tag"] == _BROADCAST_:
          [addr_sender, dv_received] = tuple(data["sender"]), eval(data["dv"])
          # print addr_sender, dv_received
          self.updateRoutingTable(addr_sender, dv_received)
      except:
        break
    self.removeClient(clientsoc, clientaddr)
    clientsoc.close()
    self.setStatus("Client disconnected from %s:%s" % clientaddr)
  
  # send message to the selected client
  def handleSendChat(self):
    if self.serverStatus == 0:
      self.setStatus("Set server address first")
      return
    self.msg = self.chatVar.get().replace(' ','')
    if self.msg == '':
      return
    self.addChat("me", self.msg)

    print "routing table:", self.routingTable
    for client in self.routingTable:
      target_client = self.routingTable[client]
      if target_client["state"] == _ON_ and client == self.sendaddr:
        datagram = {}
        datagram["tag"] = _MESSAGE_
        datagram["msg"] = self.msg
        datagram["sender"] = self.addr
        datagram["target"] = self.sendaddr

        _port = target_client["port"]
        addr = self.ports[_port]
        soc = self.clientSocs[addr]
        # print soc, target_client, _port
        soc.send(json.dumps(datagram, ensure_ascii=False))
        break
      else:
        pass

  def broadcastRoutingTable(self):
    for client in self.clientSocs:
      datagram = {}
      datagram["tag"] = _BROADCAST_
      datagram["sender"] = self.addr
      datagram["dv"] = str(self.dv)
      datagram = json.dumps(datagram, ensure_ascii=False)
      soc = self.clientSocs[client]
      soc.send(datagram)

  # update route table
  def updateRoutingTable(self, addr_sender, dv_received):

    [isChanged, self.dv, self.routingTable, self.ports] = RA.DV(self.addr,
                                                              addr_sender,
                                                              self.dv,
                                                              dv_received,
                                                              self.routingTable,
                                                              self.ports)

    if isChanged:
      self.broadcastRoutingTable()
  
  def addChat(self, client, msg):
    self.receivedChats.config(state=NORMAL)
    self.receivedChats.insert("end",client+": "+msg+"\n")
    self.receivedChats.config(state=DISABLED)
  
  def addClient(self, clientsoc, clientaddr):
    clientaddr = tuple(clientaddr)
    self.clientSocs[clientaddr] = clientsoc
    self.counter += 1
    self.friends.insert(self.counter,"%s:%s" % clientaddr)

    _port = self.allocatePort()
    if _port:
      self.routingTable[clientaddr] = {"port": _port, "state": _ON_}
      self.dv[clientaddr] = 1
      self.ports[_port] = clientaddr
    else:
      print "Ports has been full!"
    self.broadcastRoutingTable()

  def removeClient(self, clientsoc, clientaddr):
    self.routingTable[clientaddr]["state"] = _DOWN_

  def allocatePort(self):
    for port in self.ports:
      if self.ports[port] == _EMPTY_:
        return port
    return 0
  
  def setStatus(self, msg):
    self.statusLabel.config(text=msg)
    print msg


# main 
def main():  
  root = Tk()
  app = ChatClient(root)
  root.mainloop()  

if __name__ == '__main__':
  main()  