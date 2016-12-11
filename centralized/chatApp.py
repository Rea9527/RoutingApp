#coding:utf-8
from Tkinter import *
from ttk import *
import socket
import thread
import json
import RoutingAlgorithm as RA

# topo
# TOPO = { "A": [ "B", "E" ] ,
#          "B": [ "A", "C", "D" ] ,
#          "C": [ "D", "E" ] ,
#          "D": [ "B", "C", "E" ] ,
#          "E": [ "A", "C", "D" ] }

_EMPTY_ = 0
_BUSY_ = 1

_ON_ = 1
_DOWN_ = 0

_MESSAGE_ = "MESSAGE"
_BROADCAST_ = "BROADCAST"
_DESTINATION_ = "DES"

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

  
  def initUI(self):
    self.root.title("Routing")
    ScreenSizeX = self.root.winfo_screenwidth()
    ScreenSizeY = self.root.winfo_screenheight()
    self.FrameSizeX  = 900
    self.FrameSizeY  = 600
    FramePosX   = (ScreenSizeX - self.FrameSizeX)/2
    FramePosY   = (ScreenSizeY - self.FrameSizeY)/2
    self.root.geometry("%sx%s+%s+%s" % (self.FrameSizeX,self.FrameSizeY,FramePosX,FramePosY))
    self.root.resizable(width=False, height=False)
    
    padX = 10
    padY = 10
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
    self.nameVar = StringVar()
    self.nameVar.set("SDH")
    nameField = Entry(ipGroup, width=10, textvariable=self.nameVar)
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
    nameField.grid(row=0, column=1)
    serverIPField.grid(row=0, column=2)
    serverPortField.grid(row=0, column=3)
    serverSetButton.grid(row=0, column=4, padx=5)
    addClientLabel.grid(row=0, column=5)
    clientIPField.grid(row=0, column=6)
    clientPortField.grid(row=0, column=7)
    clientSetButton.grid(row=0, column=8, padx=5)
    
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

    centerGroup.grid(row=0, column=0)
    ipGroup.grid(row=1, column=0)
    readChatGroup.grid(row=2, column=0)
    sendMsgGroup.grid(row=3, column=0)
    writeChatGroup.grid(row=4, column=0, pady=10)
    self.statusLabel.grid(row=5, column=0)


  def handleSetCenter(self):
    if self.adminSoc != None:
      self.admin = False;
      self.adminSoc.close()

    adminaddr = (self.serverIPVar.get().replace(' ',''), int(self.serverPortVar.get().replace(' ','')))
    try:
      self.adminSoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.adminSoc.connect(adminaddr)
      self.setStatus("Connect to controller %s:%s" % adminaddr)
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
      self.name = self.nameVar.get().replace(' ','')
      if self.name == '':
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
      self.setStatus("Set server address first")
      return
    clientaddr = (self.clientIPVar.get().replace(' ',''), int(self.clientPortVar.get().replace(' ','')))
    if clientaddr == self.addr:
      print "You cannot connect to yourself!"
    else:
      # try:
        clientsoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print "clientsoc:", clientsoc.getsockname()
        # clientsoc.bind(self.addr)
        clientsoc.connect(clientaddr)
        # print clientsoc.getsockname(), " ", clientsoc.getpeername()
        self.setStatus("Connected to client on %s:%s" % clientaddr)
        self.addClient(clientsoc, clientaddr)
        thread.start_new_thread(self.handleClientMessages, (clientsoc, clientaddr))
      # except:
      #   self.setStatus("Error connecting to client")

    
  def listenClients(self):
    while 1:
      [clientsoc, clientaddr] = self.serverSoc.accept()
      # print "soc:", clientsoc.getpeername()
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
        print "data:", data
        if data["tag"] == _MESSAGE_:
          self.addChat("%s:%s" % clientaddr, data["msg"])
        elif data["tag"] == _DESTINATION_:
          datagram = {}
          datagram["tag"] = _MESSAGE_
          datagram["sender"] = str(self.addr)
          datagram["mgs"] = self.msg
          port = data["port"]
          addr = self.ports[port]
          soc = self.clientSocs[addr]
          soc.send(json.dumps(datagram))
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
    datagram["sender"] = str(self.addr)
    datagram["ports"] = str(self.ports)
    datagram["desAddr"] = str(self.sendaddr)
    self.adminSoc.send(json.dumps(datagram))

  
  def addChat(self, client, msg):
    self.msg = msg
    self.receivedChats.config(state=NORMAL)
    self.receivedChats.insert("end",client+": "+msg+"\n")
    self.receivedChats.config(state=DISABLED)
  
  def addClient(self, clientsoc, clientaddr):
    self.clientSocs[clientaddr] = clientsoc
    self.counter += 1
    self.friends.insert(self.counter,"%s:%s" % clientaddr)

    _port = self.allocatePort()
    if _port:
      print "port:", _port
      self.ports[_port] = clientaddr
    else:
      print "Ports has been full!"

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