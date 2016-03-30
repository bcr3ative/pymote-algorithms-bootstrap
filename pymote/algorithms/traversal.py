from pymote.algorithm import NodeAlgorithm
from pymote.message import Message


class DFT(NodeAlgorithm):
    required_params = {'informationKey', }
    default_params = {'neighborsKey': 'Neighbors'}

    def initializer(self):
        ini_nodes = []
        for node in self.network.nodes():
            node.memory[self.neighborsKey] = node.compositeSensor.read()['Neighbors']
            node.status = 'IDLE'
            if self.informationKey in node.memory:
                node.status = 'INITIATOR'
                ini_nodes.append(node)
        for ini_node in ini_nodes:
            self.network.outbox.insert(0, Message(header=NodeAlgorithm.INI, destination=ini_node))

    def initiator(self, node, message):
        node.memory['unvisitedNodes'] = list(node.memory[self.neighborsKey])
        node.memory['initiator'] = True
        #print("[INITIATOR] Node {} -> has unvisited nodes {}\n".format(node, node.memory['unvisitedNodes']))
        self.visit(node, message)

    def idle(self, node, message):
        if message.header == 'T':
            node.memory['entry'] = message.source
            node.memory['unvisitedNodes'] = list(node.memory[self.neighborsKey])
            node.memory['unvisitedNodes'].remove(message.source)
            node.memory['initiator'] = False
            #print("[IDLE=T] Node {} -> has unvisited nodes {}\n".format(node, node.memory['unvisitedNodes']))
            self.visit(node, message)

    def visited(self, node, message):
        if message.header == 'T':
            node.memory['unvisitedNodes'].remove(message.source)
            node.send(Message(destination=message.source, header='Backedge', data=message.data))
            #print("[VISITED=T] Node {} -> has unvisited nodes {}, sending Backedge to {}\n".format(node, node.memory['unvisitedNodes'], message.source))
        elif message.header == 'Return':
            node.memory['unvisitedNodes'].remove(message.source)
            self.visit(node, message)
        elif message.header == 'Backedge':
            node.memory['unvisitedNodes'].remove(message.source)
            self.visit(node, message)

    def done(self, node, message):
        pass

    def visit(self, node, message):
        if node.memory['unvisitedNodes']:
            next_node = node.memory['unvisitedNodes'][0]
            node.send(Message(destination=next_node, header='T', data=message.data))
            #print("[VISIT] Node {} -> has unvisited nodes {}, sending T to {}, status to VISITED\n".format(node, node.memory['unvisitedNodes'], next_node))
            node.status = 'VISITED'
        else:
            if not node.memory['initiator']:
                node.send(Message(destination=node.memory['entry'], header='Return', data=message.data))
                #print("[VISIT=not initiator] Node {} -> sending Return to {}".format(node, node.memory['entry']))
            #print("[VISIT=no unvisited nodes] Node {} -> status to DONE".format(node))
            node.status = 'DONE'

    STATUS = {
                'INITIATOR': initiator,
                'IDLE': idle,
                'VISITED': visited,
                'DONE': done
             }
