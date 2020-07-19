from datetime import datetime
import threading
import time
import schedule 
import random
import json
from socket import *
import os
import ctypes 
import ast

ports = [20000,20001,20002,20003,20004,20005]
nodes = []
shouldExit = False

TOTAL_TIME = 300


class Logger:
    def __init__(self, fileName):
        self.fileName = str(os.path.dirname(os.path.realpath(__file__))) + '/traces' + '/' + fileName
        os.makedirs(os.path.dirname(self.fileName), exist_ok=True)
        try:
            os.remove(self.fileName)
        except: 
            pass
    def log(self, msg):
        newLogging = msg + " " + str(datetime.now())  + "\n"
        with open(self.fileName, "a") as f:
            f.write(newLogging)

class NodeInfo:
    def __init__(self, ip, port, id):
        self.ip = ip
        self.port = port
        self.lastHearedTime = datetime.now()
        self.lastSentTime = None
        self.id = id
    def updateHearedTimeToCurrentTime(self):
        self.lastHearedTime = datetime.now()
        
    def updateSentTimeToCurrentTime(self):
        self.lastSentTime = datetime.now()


class Node:
    def __init__(self,ip , port, id):
        self.state = True
        self.uniNeighbors = []
        self.biNeighbors = []
        self.tempNeighbors = []
        self.ip = ip
        self.port = port
        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.sock.bind((self.ip, self.port))
        self.id = id
        self.logger = Logger('node' + str(id))

    def run(self):
        self.t = threading.Thread(target=self.recv)
        self.t.start()
        self.s2 = schedule.every(2).seconds.do(runThread, self.manageSend)
        self.logger.log('start')

    def createPacket(self):
        packet = {}
        packet['id'] = self.id
        packet['ip'] = self.ip
        packet['port'] = self.port
        packet['type'] = 'UDP'
        packet['neighbors'] = list(self.getIdList(self.biNeighbors))
        return packet

    def manageSend(self):
        if not self.state :
            return
        self.checkNeighbors()
        self.searchNewNighbor()
        packet = self.createPacket()
        for n in self.biNeighbors:
            packet['last heared'] = n.lastHearedTime
            packet['last sent'] = n.lastSentTime
            self.sock.sendto(json.dumps(packet, default=str).encode(), (n.ip, n.port))
            self.logger.log('s' + ' ' + str(self.ip) + ' ' + str(self.port) + ' ' + str(self.id) + ' ' + 
                            str(n.ip) + ' ' + str(n.port) + ' ' + str(n.id) + ' ' + 'bi')
        for n in self.uniNeighbors:
            packet['last heared'] = n.lastHearedTime
            packet['last sent'] = n.lastSentTime
            self.sock.sendto(json.dumps(packet, default=str).encode(), (n.ip, n.port))
            self.logger.log('s' + ' ' + str(self.ip) + ' ' + str(self.port) + ' ' + str(self.id) + ' ' + 
                            str(n.ip) + ' ' + str(n.port) + ' ' + str(n.id) + ' ' + 'uni')

        for n in self.tempNeighbors:
            packet['last heared'] = n.lastHearedTime
            packet['last sent'] = n.lastSentTime
            self.sock.sendto(json.dumps(packet, default=str).encode(), (n.ip, n.port))
            self.logger.log('s' + ' ' + str(self.ip) + ' ' + str(self.port) + ' ' + str(self.id) + ' ' + 
                            str(n.ip) + ' ' + str(n.port) + ' ' + str(n.id) + ' ' + 'temp')


    def recv(self):
        global shouldExit
        while True:
            if shouldExit:
                print('end',self.id)
                return
            if not self.state:
                continue
            data, address = self.sock.recvfrom(1024)
            data = data.decode()
            data = json.loads(data)
            self.processPacket(data)

    def addToUni(self, newNode):
        self.uniNeighbors.append(newNode)
        self.logger.log('au' + ' ' + str(newNode.id) + ' ' + str(list(self.getIdList(self.uniNeighbors))))

    def addToBi(self, newNode):
        if len(self.biNeighbors) < 3:
            self.biNeighbors.append(newNode)
            self.logger.log('ab' + ' ' + str(newNode.id) + ' ' + str(list(self.getIdList(self.biNeighbors))).replace(' ', ''))

    def addToTemp(self, newNode):
        self.tempNeighbors.append(newNode)
        self.logger.log('at' + ' ' + str(newNode.id) + ' ' + str(list(self.getIdList(self.tempNeighbors))).replace(' ', ''))


    def removeFromUni(self, node):
        try:
            self.uniNeighbors.remove(node)
            self.logger.log('du' + ' ' + str(node.id) + ' ' + str(list(self.getIdList(self.uniNeighbors))).replace(' ', ''))

        except:
            print("There is no unidirectional neighbor with ip: ", node.ip, " in node with ip: ", self.ip)

    def removeFromBi(self, node):
        try:
            self.biNeighbors.remove(node)
            self.logger.log('db' + ' ' + str(node.id) + ' ' + str(list(self.getIdList(self.biNeighbors))).replace(' ', ''))
        except:
            print("There is no unidirectional neighbor with ip: ", node.ip, " in node with ip: ", self.ip)

    def removeFromTemp(self, node):
        try:
            self.tempNeighbors.remove(node)
            self.logger.log('dt' + ' ' + str(node.id) + ' ' + str(list(self.getIdList(self.tempNeighbors))).replace(' ', ''))
        except:
            print("There is no unidirectional neighbor with ip: ", node.ip, " in node with ip: ", self.ip)

    def checkNeighbors(self):
        for n in self.uniNeighbors + self.biNeighbors + self.tempNeighbors:
            diffTime = (datetime.now() - n.lastHearedTime ).total_seconds()
            if diffTime >= 8:
                self.logger.log('c' + ' ' + str(n.id) + ' ' + str(diffTime))
                if n in self.uniNeighbors:
                    self.removeFromUni(n)
                elif n in self.biNeighbors:
                    self.removeFromBi(n)
                elif n in self.tempNeighbors:
                    self.removeFromTemp(n)

    def isNodeInPacket(self, packet):
        return self.id in packet['neighbors']

    def extractSender(self, packet):
        return packet['id']
    
    def existsInList(self, id, l):
        for node in l:
            if id == node.id:
                return node

    def processPacket(self, packet):
        if random.choice(range(100)) < 5: #implement packet loss manually =D
            return

        isInPacket = self.isNodeInPacket(packet)
        sender = self.extractSender(packet)
        self.logger.log('r' + ' ' + str(self.ip) + ' ' + str(self.port) + ' ' + str(self.id) + ' ' + packet['ip'] + ' ' +
                         str(packet['port']) + ' ' + str(packet['id']) + ' ' + str(isInPacket)) 
        self.checkNeighbors()

        node = self.existsInList(sender, self.tempNeighbors)
        if node: 
            if isInPacket:
                self.removeFromTemp(node)
                self.addToBi(node)
                
            else:
                self.removeFromTemp(node)
                self.addToBi(node)
            node.updateHearedTimeToCurrentTime()
            return

        node = self.existsInList(sender, self.uniNeighbors)
        if node: 
            if isInPacket:
                self.removeFromUni(node)
                self.addToUni(node)
            node.updateHearedTimeToCurrentTime()
            # Nothing to do if it is in uni and not in packet
            return

        node = self.existsInList(sender, self.biNeighbors)
        if node:
            node.updateHearedTimeToCurrentTime()
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
        if len(self.biNeighbors) >= 3:
            self.logger.log('max neighbor exceeds')
            self.uniNeighbors = []
            self.tempNeighbors = []
            return
        
        selectList = list(set(range(6)) - self.getIdList(self.uniNeighbors)- self.getIdList(self.biNeighbors) - 
                          self.getIdList(self.tempNeighbors) - set([self.id]))
        if(len(selectList) != 0):
            newNode = random.choice(selectList)
            newNodeInfo = NodeInfo(nodes[newNode].ip,nodes[newNode].port, newNode)
            self.addToTemp(newNodeInfo)
    

class Network:
    def __init__(self):
        self.sleptNodes = []
        for p in range(len(ports)):
            nodes.append(Node('127.0.0.1', ports[p], p))

        self.s1 = schedule.every(10).seconds.do(runThread, self.manageSleep)
        self.logger = Logger('network')

    def manageSleep(self):
        if(len(self.sleptNodes) == 2):
            nodes[self.sleptNodes[0]].state = True
            self.logger.log('w' + ' ' + str(self.sleptNodes[0]))
            self.sleptNodes.pop(0)
            
        selectList =list( set(range(6)) - set(self.sleptNodes))
        newSleptNode = random.choice(selectList)
        self.sleptNodes.append(newSleptNode)
        nodes[newSleptNode].state = False
        self.logger.log('s' + ' ' + str(self.sleptNodes[-1]))
    
    def exit(self):
        print('prepare to exit')
        global shouldExit
        schedule.clear()
        shouldExit = True
        # print('start joining')
        # for n in nodes:
        #     n.t.join()
        #     print('jonied ' + str(n.id))
        print("end of execution")

    def run(self):
        print('start')
        for n in nodes:
            n.run()
        timer = threading.Timer(TOTAL_TIME, self.exit) 
        timer.start() 


class Processor:
    def __init__(self):
        os.makedirs(os.path.dirname('./results/a.txt'), exist_ok=True)

    def run(self):
        for n in nodes:
            data = []
            filename = './traces/node' + str(n.id)
            info = self.splitFile(filename)
            data.append(self.getNeighborHistory(info))
            data.append(self.getCurrNeighbors(info))
            data.append(self.neighborsAvailability(info))
            data.append(self.getTopology(info))
            self.writeToFile('./results/Node-Port:'+str(n.port), data)

    def splitFile(self,filename):
        lines = []
        file = open(filename, 'r')
        line = file.readline()
        while line:
            lines.append(line.split())
            line = file.readline()
        return lines

    def writeToFile(self, filename, data):
        with open(filename, "w") as f:
            f.write(json.dumps(data, indent=2))

    def getNeighborHistory(self, info):
        neighborsHistory = {}
        for line in info:
            if line[0] == 'r' and line[-3] == 'True':
                if not line[5] in neighborsHistory:
                    neighborsHistory[line[5]] = {'ip':line[4], 'port': line[5], 'id':line[6], 'sentPacketsNum': 0, 'recievedPacketsNum': 1}
                else:
                    neighborsHistory[line[5]]['recievedPacketsNum'] += 1
            if line[0] == 's' and line[-3] == 'bi':
                if not line[5] in neighborsHistory:
                    neighborsHistory[line[5]] = {'ip':line[4], 'port': line[5], 'id':line[6], 'sentPacketsNum': 1, 'recievedPacketsNum': 0}
                else:
                    neighborsHistory[line[5]]['sentPacketsNum'] += 1
        return {'Neighbors History' :list(neighborsHistory.values())}

    def getCurrNeighbors(self, info):
        currNeighbors = []
        for i in range(len(info)-1,-1, -1):
            line = info[i]
            if line[0] == 'ab' or line[0] == 'db':
                currNeighbors = ast.literal_eval(line[2])
                break
        return {'Current Neighbors':currNeighbors}     

    def strToTime(self,string):
        return datetime.strptime(string, '%H:%M:%S.%f')

    def neighborsAvailability(self, info):
        availability = {}
        startTime = None
        for line in info:
            if line[0] == 'start':
                startTime = self.strToTime(line[-1])
            if line[0] == 'ab':
                if not line[1] in availability:
                    availability[line[1]] = {'id':int(line[1]), 'startTime': self.strToTime(line[-1]), 'availability':0}
                else:
                    availability[line[1]]['startTime'] = self.strToTime(line[-1])
            if line[0] == 'db':
                if not line[1] in availability or availability[line[1]]['startTime'] == None:
                    print('error in availability. db before ab :||')
                    print(line)
                else:
                    availability[line[1]]['availability'] += (self.strToTime(line[-1]) - availability[line[1]]['startTime']).total_seconds()
                    availability[line[1]]['startTime'] = None
        
        for node in availability:
            if availability[node]['startTime'] != None:
                availability[node]['availability'] += TOTAL_TIME - (availability[node]['startTime'] - startTime).total_seconds()
            availability[node]['availability'] = str(round(availability[node]['availability'] / TOTAL_TIME * 100, 2)) + '%'
            del availability[node]['startTime']
        return {'Neighbors Availability':list(availability.values())}


    def getTopology(self, info):
        topology = {}
        for line in info:
            if line[0] == 'ab':
                topology[line[1]] = 'bidirectional'
            if line[0] == 'au':
                if not line[1] in topology:
                    topology[line[1]] = 'unidirectional'
        return {'Topology':topology}


def runThread( jobFunc):
    jobThread = threading.Thread(target=jobFunc)
    jobThread.start()

network = Network()
network.run()

while not shouldExit:
    schedule.run_pending()
    time.sleep(1) 
        
print("end of program")

processor = Processor()
processor.run()
print('end')
exit(0)