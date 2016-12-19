#coding:utf-8
from Tkinter import *
from ttk import *
import socket
import thread
import json
import RoutingAlgorithm as RA


_EMPTY_ = 0
_BUSY_ = 1


_MESSAGE_ = "MESSAGE"
_DESTINATION_ = "DES"
_TO_CONTROLLER_ = "TO CONTROLLER"
_FROM_CONTROLLER_ = "FROM CONTROLLER"
_PORT_ = "PORT"
_TOPO_ = "TOPO"

class ChatClient(Frame):
  
  def __init__(self, root):
    Frame.__init__(self, root)
    self.root = root
    self.initUI()
    self.serverSoc = None
    self.serverStatus = 0
    self.buffsize = 1024
    self.clientSocs = {}
    self.ports = {"0": _EMPTY_, "1": _EMPTY_, "2": _EMPTY_, "3": _EMPTY_, "4": _EMPTY_}
    self.counter = 0
    self.admin = False;
    self.adminSoc = None;
    self.name = ''

  
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
    
    padX = 5
    padY = 5
    parentFrame = Frame(self.root)
    parentFrame.grid(padx=padX, pady=padY, stick=E+W+N+S)

    centerGroup = Frame(parentFrame)
    self.centerIPVar = StringVar()
    self.centerIPVar.set("127.0.0.1")
    centerIPField = Entry(centerGroup, width=15, textvariable=self.centerIPVar)
    self.centerPortVar = StringVar()
    self.centerPortVar.set("8090")
    centerPortField = Entry(centerGroup, width=5, textvariable=self.centerPortVar)
    centerSetButton = Button(centerGroup, text="SetCenter", width=12, command=self.handleSetCenter)
    centerIPField.grid(row=0, column=0)
    centerPortField.grid(row=0, column=1)
    centerSetButton.grid(row=0, column=2)

    ipGroup = Frame(parentFrame)
    serverLabel = Label(ipGroup, text="Set: ")
    self.serverIPVar = StringVar()
    self.serverIPVar.set("127.0.0.1")
    serverIPField = Entry(ipGroup, width=15, textvariable=self.serverIPVar)
    self.serverPortVar = StringVar()
    self.serverPortVar.set("8091")
    serverPortField = Entry(ipGroup, width=5, textvariable=self.serverPortVar)
    serverSetButton = Button(ipGroup, text="Set", width=10, command=self.handleSetServer)
    addClientLabel = Label(ipGroup, text="Set Conn: ")
    self.clientIPVar = StringVar()
    self.clientIPVar.set("127.0.0.1")
    clientIPField = Entry(ipGroup, width=15, textvariable=self.clientIPVar)
    self.clientPortVar = StringVar()
    self.clientPortVar.set("8092")
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
    self.receivedChats = Text(readChatGroup, bg="white", width=60, height=26, state=DISABLED)
    self.friends = Listbox(readChatGroup, bg="white", width=30, height=26)
    self.receivedChats.grid(row=0, column=0, sticky=W+N+S, padx = (0,10))
    self.friends.grid(row=0, column=1, sticky=E+N+S)

    sendMsgGroup = Frame(parentFrame)
    sendLabel = Label(sendMsgGroup, text="Send To: ")
    self.sendIPVar = StringVar()
    self.sendIPVar.set("127.0.0.1")
    sendIPField = Entry(sendMsgGroup, width=15, textvariable=self.sendIPVar)
    self.sendPortVar = StringVar()
    self.sendPortVar.set("8092")
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
    centerGroup.grid(row=1, column=0)
    ipGroup.grid(row=2, column=0)
    readChatGroup.grid(row=3, column=0)
    sendMsgGroup.grid(row=4, column=0)
    writeChatGroup.grid(row=5, column=0, pady=10)

    # self.friends.insert(0,"当前直连路由:")


  def handleSetCenter(self):
    if self.adminSoc != None:
      self.admin = False;
      self.adminSoc.close()
    if self.serverStatus == 0:
      self.setStatus("Error, set server address first")
      return

    adminAddr = (self.centerIPVar.get().replace(' ',''), int(self.centerPortVar.get().replace(' ','')))
    try:
      self.adminSoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.adminSoc.connect(adminAddr)
      self.adminSoc.send(json.dumps(self.addr))
      self.setStatus("Connect to controller %s:%s" % adminAddr)
      self.admin = True
      thread.start_new_thread(self.handleClientMessages, (self.adminSoc, adminAddr))
    except:
      self.setStatus("Controller addr error!")

    
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
    except:
      self.setStatus("Error setting up server")

  def handleSendIP(self):
    sendaddr = (self.sendIPVar.get().replace(' ',''), int(self.sendPortVar.get().replace(' ','')))
    self.sendaddr = sendaddr
    self.setStatus("Set client %s:%s to send" % sendaddr)

  
  def handleSetConn(self):
    if self.serverStatus == 0:
      self.setStatus("Error, set server address first")
      return
    else:
      if self.admin == False:
        self.setStatus("Error, please connect to controller first")
        return
    clientaddr = (self.clientIPVar.get().replace(' ',''), int(self.clientPortVar.get().replace(' ','')))
    if clientaddr == self.addr:
      print "You cannot connect to yourself!"
    else:
      try:
        clientsoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # print "clientsoc:", clientsoc.getsockname()
        clientsoc.connect(clientaddr)
        clientsoc.send(json.dumps(self.addr))
        # print clientsoc.getsockname(), " ", clientsoc.getpeername()
        self.setStatus("Connected to client on %s:%s" % clientaddr)
        self.addClient(clientsoc, clientaddr)
        thread.start_new_thread(self.handleClientMessages, (clientsoc, clientaddr))
      except:
        self.setStatus("Error connecting to client")

    
  def listenClients(self):
    while 1:
      [clientsoc, clientaddr] = self.serverSoc.accept()
      while 1:
        buf = clientsoc.recv(self.buffsize)
        clientaddr = tuple(json.loads(buf))
        break

      print "clientsoc: %s, clientaddr: %s", clientsoc, clientaddr
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
          print("msg")
          addr = tuple(data["srcAddr"])
          self.addChat("%s:%s" % addr, data["msg"])

        elif data["tag"] == _FROM_CONTROLLER_:
          # print _FROM_CONTROLLER_
          port = str(data["port"])
          if port == "":
            self.setStatus("Address is not exist!")
          else:
            addr = self.ports[port]
            datagram = {}
            datagram["sender"] = str(self.addr)
            datagram["msg"] = data["msg"]
            datagram["desAddr"] = data["desAddr"]
            datagram["srcAddr"] = data["srcAddr"]
            # print "addr&desAddr:", addr, tuple(datagram["desAddr"])
            if addr == tuple(datagram["desAddr"]):
              datagram["tag"] = _MESSAGE_
            else:
              datagram["tag"] = _TO_CONTROLLER_
            soc = self.clientSocs[addr]
            soc.send(json.dumps(datagram))

        elif data["tag"] == _TO_CONTROLLER_:
          datagram = {}
          datagram["tag"] = _TO_CONTROLLER_
          datagram["sender"] = self.addr
          datagram["ports"] = self.ports
          datagram["msg"] = data["msg"]
          datagram["srcAddr"] = data["srcAddr"]
          datagram["desAddr"] = data["desAddr"]
          self.adminSoc.send(json.dumps(datagram))
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
    msg = self.chatVar.get().replace(' ','')
    if msg == '':
        return
    self.addChat("me", msg)

    datagram = {}
    datagram["tag"] = _TO_CONTROLLER_
    datagram["sender"] = self.addr
    datagram["msg"] = self.msg
    datagram["ports"] = self.ports
    datagram["srcAddr"] = self.addr
    datagram["desAddr"] = self.sendaddr
    self.adminSoc.send(json.dumps(datagram))

  
  def addChat(self, client, msg):
    self.msg = msg
    self.receivedChats.config(state=NORMAL)
    self.receivedChats.insert("end",client+": "+msg+"\n")
    self.receivedChats.config(state=DISABLED)
  
  def addClient(self, clientsoc, clientaddr):
    self.clientSocs[tuple(clientaddr)] = clientsoc
    self.counter += 1
    self.friends.insert(self.counter + 1,"%s:%s" % clientaddr)

    _port = self.allocatePort()
    if _port:
      self.ports[_port] = tuple(clientaddr)
    else:
      print "Ports has been full!"

    datagram = {}
    datagram["tag"] = _TOPO_
    datagram["desAddr"] = tuple(clientaddr)
    self.adminSoc.send(json.dumps(datagram))

  def removeClient(self, clientsoc, clientaddr):
    pass

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