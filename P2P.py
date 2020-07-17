from datetime import datetime
import threading
import time
import schedule 
import random


ports = [20001,20002,20003,20004,20005,20006]
nodes = []


class NodeInfo:
    def __init__(self, ip, port, id):
        self.ip = ip
        self.port = port
        self.lastHearedTime = datetime.now()
        self.id = id
    def updateTimeToCurrentTime(self):
        self.lastHearedTime = datetime.now()


class Node:
    def __init__(self, port, ip, id):
        self.state = True
        self.uniNeighbors = []
        self.biNeighbors = []
        self.tempNeighbors = []
        self.ip = ip
        self.port = port
        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.sock.bind((self.ip, self.port))
        self.id = id
        Thread(target=self.recv).start()

        schedule.every(2).seconds.do(runThread, self.manageSend)

    def manageSend(self):



    def recv(self):
        while True:
            data, address = s.recvfrom(1024)
            print(data)
            self.processPacket(data)

    def addToUni(self, newNode):
        self.uniNeighbors.append(newNode)

    def addToBi(self, newNode):
        self.biNeighbors.append(newNode)

    def addToTemp(self, newNode):
        self.tempNeighbors.append(newNode)

    def removeFromUni(self, node):
        try:
            self.uniNeighbors.remove(node)
        except:
            print("There is no unidirectional neighbor with ip: ", node.ip, " in node with ip: ", self.ip)

    def removeFromBi(self, node):
        try:
            self.biNeighbors.remove(node)
        except:
            print("There is no unidirectional neighbor with ip: ", node.ip, " in node with ip: ", self.ip)

    def removeFromTemp(self, node):
        try:
            self.tempNeighbors.remove(node)
        except:
            print("There is no unidirectional neighbor with ip: ", node.ip, " in node with ip: ", self.ip)

    def checkNeighbors(self):
        for n in self.uniNeighbors + self.biNeighbors + self.tempNeighbors:
            if (datetime.now() - n.lastHearedTime ).total_seconds() >= 8:
                if n in self.uniNeighbors:
                    self.uniNeighbors.remove(n)
                elif n in self.biNeighbors:
                    self.biNeighbors.remove(n)
                elif n in self.tempNeighbors:
                    self.tempNeighbors.remove(n)

    def extractNode(self, packet):
        return

    def extractSender(self, packet):
        return
    
    def existsInList(self, id, l):
        for node in l:
            if id == node.id:
                return node

    def processPacket(self, packet):
        if random.choice(range(100)) < 5: #implement packet loss manually =D
            return

        isInPacket = extractNode(packet)
        sender = extranceSender(packet)
        self.checkNeighbors()
        
        node = existsInList(sender, self.tempNeighbors)
        if node 
            if isInPacket:
                self.removeFromTemp(node)
                self.addToBi(node)
                
            else:
                self.removeFromTemp(node)
                self.addToBi(node)
            node.updateTimeToCurrentTime()
            return

        node = existsInList(sender, self.uniNeighbors)
        if node 
            if isInPacket:
                self.removeFromUni(node)
                self.addToUni(node)
            node.updateTimeToCurrentTime()
            # Nothing to do if it is in uni and not in packet
            return

        node = existsInList(sender, self.biNeighbors)
        if node:
            node.updateTimeToCurrentTime()
        else:
            newNodeInfo = NodeInfo(nodes[sender].ip, nodes[sender].port, sender)
            if isInPacket:
                self.addToBi(newNodeInfo)
            else:
                self.addToUni(newNodeInfo)
            return

    def getIdList(self,l):
        idList = set()
        for node in l:
            idList.add(node.id)
        return idList

    def searchNewNighbor(self):
        if len(self.biNeighbors) == 3:
            return
        
        selectList = set(range(6)) - getIdList(self.uniNeighbors)- getIdList(self.biNeighbors) - getIdList(self.tempNeighbors)) - set([self.id])
        if(len(selectList) != 0):
            newNode = random.choice(selectList)
            newNodeInfo = NodeInfo(nodes[newNode].ip,nodes[newNode].port, newNode)
            self.addToTemp(newNodeInfo)
    


class Network:
    def __init__(self):
        self.sleptNodes = []
        for p in range(len(ports)):
            nodes.append(Node('', ports[p], p))

        schedule.every(10).seconds.do(runThread, self.manageSleep)

    def manageSleep(self):
        if(len(self.sleptNodes) == 2):
            nodes[sleptNodes[0]].state = True
            self.sleptNodes.pop(0)
            
        selectList =list( set(range(6)) - set(self.sleptNodes))
        newSleptNode = random.choices(selectList)
        self.sleptNodes.append(newSleptNode)
        nodes[newSleptNode].state = False



def runThread( jobFunc):
    jobThread = threading.Thread(target=jobFunc)
    jobThread.start()

while 1:
    schedule.run_pending()
    time.sleep(1) 
    
