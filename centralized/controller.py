#coding:utf-8
from Tkinter import *
from ttk import *
import socket
import thread
import json
import RoutingAlgorithm as RA


_DESTINATION_ = "DES"
_PORT_ = "PORT"
_TOPO_ = "TOPO"
_FROM_CONTROLLER_ = "FROM CONTROLLER"

class Controller(Frame):

	def __init__(self, root):
		Frame.__init__(self, root)
		self.root = root
		self.initUI()
		self.buffsize = 1024
		self.clientSocs = {}
		self.counter = 0
		self.admin = False;
		self.adminSoc = None;
		self.TOPO = {}

	def initUI(self):
		self.root.title("Routing")
		ScreenSizeX = self.root.winfo_screenwidth()
		ScreenSizeY = self.root.winfo_screenheight()
		self.FrameSizeX  = 700
		self.FrameSizeY  = 550
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

		readChatGroup = Frame(parentFrame)
		self.receivedChats = Text(readChatGroup, bg="white", width=60, height=26, state=DISABLED)
		self.friends = Listbox(readChatGroup, bg="white", width=30, height=26)
		self.receivedChats.grid(row=0, column=0, sticky=W+N+S, padx = (0,10))
		self.friends.grid(row=0, column=1, sticky=E+N+S)

		self.statusLabel = Label(parentFrame)

		centerGroup.grid(row=0, column=0)
		readChatGroup.grid(row=1, column=0)
		self.statusLabel.grid(row=2, column=0)

	def handleSetCenter(self):
		if self.adminSoc != None:
		  self.admin = False;
		  self.adminSoc.close()

		adminAddr = (self.centerIPVar.get().replace(' ',''), int(self.centerPortVar.get().replace(' ','')))
		try:
		  self.adminSoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		  self.adminSoc.bind(adminAddr)
		  self.adminSoc.listen(5)
		  self.setStatus("Controller listening on %s:%s" % adminAddr)
		  thread.start_new_thread(self.listenClients, ())
		  self.addr = adminAddr
		except:
			self.setStatus("Error setting controller!")

	def listenClients(self):
		while 1:
		  clientSoc, clientAddr = self.adminSoc.accept()
		  print clientSoc
		  while 1:
				buf = clientSoc.recv(self.buffsize)
				print buf
				clientAddr = tuple(json.loads(buf))
				break
		  print "clientSoc: %s, clientAddr: %s", clientSoc, clientAddr
		  self.setStatus("Client connected from %s:%s" % clientAddr)
		  self.addClient(clientSoc, clientAddr)
		  thread.start_new_thread(self.handleClientMessages, (clientSoc, clientAddr))
		self.adminSoc.close()

	def handleClientMessages(self, clientSoc, clientAddr):
		while 1:
			try:
				data = clientSoc.recv(self.buffsize)
				if not data:
					break
				data = str(data)
				data = json.loads(data)
				print "data:", data
				if data["tag"] == _TOPO_:
					desAddr = data["desAddr"]
					self.TOPO[clientAddr].append(tuple(desAddr))
					# print self.TOPO
				else:
					[sendAddr, ports, desAddr] = tuple(data["sender"]), data["ports"], tuple(data["desAddr"])
					port = RA.LS(self.TOPO, ports, sendAddr, desAddr)
					# port = "1"
					datagram = {}
					datagram["tag"] = _FROM_CONTROLLER_
					datagram["desAddr"] = desAddr
					datagram["srcAddr"] = data["srcAddr"]
					datagram["msg"] = data["msg"]
					datagram["port"] = port
					clientSoc.send(json.dumps(datagram))
			except:
				break
		self.removeClient(clientSoc, clientAddr)
		clientSoc.close()
		self.setStatus("Client disconnected from %s:%s" % clientAddr)

	def addClient(self, clientSoc, clientAddr):
		self.clientSocs[clientAddr] = clientSoc
		self.counter += 1
		self.TOPO[clientAddr] = []

	def removeClient(self, clientSoc, clientAddr):
		pass

	def setStatus(self, msg):
		self.receivedChats.config(state=NORMAL)
		self.receivedChats.insert("end",msg+"\n")
		self.receivedChats.config(state=DISABLED)
		self.statusLabel.config(text=msg)
		print msg

# main 
def main():  
  root = Tk()
  app = Controller(root)
  root.mainloop()  

if __name__ == '__main__':
  main()  
