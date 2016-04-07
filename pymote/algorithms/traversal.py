from pymote.algorithm import NodeAlgorithm
from pymote.message import Message


class DF(NodeAlgorithm):
    # algorithm input
    required_params = ()
    # values that are exposed to other algorithms
    default_params = {'neighborsKey': 'Neighbors'}

    def initializer(self):
        for node in self.network.nodes():
            node.memory[self.neighborsKey] = node.compositeSensor.read()['Neighbors']
            node.status = 'IDLE'
        # make first node initiator
        ini_node = self.network.nodes()[0]
        ini_node.status = 'INITIATOR'
        self.network.outbox.insert(0, Message(header=NodeAlgorithm.INI, destination=ini_node))

    def initiator(self, node, message):
        node.memory['unvisitedNodes'] = list(node.memory[self.neighborsKey])
        self.visit(node, message)

    def idle(self, node, message):
        if message.header == 'Token':
            node.memory['entry'] = message.source
            node.memory['unvisitedNodes'] = list(node.memory[self.neighborsKey])
            node.memory['unvisitedNodes'].remove(message.source)
            self.visit(node, message)

    def visited(self, node, message):
        if message.header == 'Token':
            node.memory['unvisitedNodes'].remove(message.source)
            node.send(Message(destination=message.source, header='Backedge', data=message.data))
        elif message.header == 'Return' or message.header == 'Backedge':
            self.visit(node, message)

    def done(self, node, message):
        pass

    def visit(self, node, message):
        if node.memory['unvisitedNodes']:
            next_node = node.memory['unvisitedNodes'].pop()
            node.send(Message(destination=next_node, header='Token', data=message.data))
            node.status = 'VISITED'
        else:
            if 'entry' in node.memory:
                node.send(Message(destination=node.memory['entry'], header='Return', data=message.data))
            node.status = 'DONE'

    STATUS = {
                'INITIATOR': initiator,
                'IDLE': idle,
                'VISITED': visited,
                'DONE': done
             }


class DFStar(NodeAlgorithm):
    # algorithm input
    required_params = ()
    # values that are exposed to other algorithms
    default_params = {'neighborsKey': 'Neighbors'}

    def initializer(self):
        for node in self.network.nodes():
            node.memory[self.neighborsKey] = node.compositeSensor.read()['Neighbors']
            node.status = 'IDLE'
        # make first node initiator
        ini_node = self.network.nodes()[0]
        ini_node.status = 'INITIATOR'
        self.network.outbox.insert(0, Message(header=NodeAlgorithm.INI, destination=ini_node))

    def initiator(self, node, message):
        node.memory['unvisitedNodes'] = list(node.memory[self.neighborsKey])
        node.memory['next_node'] = node.memory['unvisitedNodes'].pop()
        node.send(Message(destination=node.memory['next_node'], header='Token', data=message.data))
        for i in list(node.memory[self.neighborsKey]):
            if i is not node.memory['next_node']:
                node.send(Message(destination=i, header='Visited', data=message.data))
        node.status = 'VISITED'

    def idle(self, node, message):
        if message.header == 'Token':
            node.memory['unvisitedNodes'] = list(node.memory[self.neighborsKey])
            self.first_visit(node, message)
        elif message.header == 'Visited':
            node.memory['unvisitedNodes'] = list(node.memory[self.neighborsKey])
            node.memory['unvisitedNodes'].remove(message.source)
            node.status = 'AVAILABLE'

    def available(self, node, message):
        if message.header == 'Token':
            self.first_visit(node, message)
        elif message.header == 'Visited':
            node.memory['unvisitedNodes'].remove(message.source)

    def visited(self, node, message):
        if message.header == 'Visited' or message.header == 'Token':
            node.memory['unvisitedNodes'].remove(message.source)
            if node.memory['next_node'] is message.source:
                self.visit(node, message)
        elif message.header == 'Return':
            self.visit(node, message)

    def done(self, node, message):
        pass

    def first_visit(self, node, message):
        node.memory['entry'] = message.source
        node.memory['unvisitedNodes'].remove(message.source)

        if node.memory['unvisitedNodes']:
            node.memory['next_node'] = node.memory['unvisitedNodes'].pop()
            node.send(Message(destination=node.memory['next_node'], header='Token', data=message.data))
            for i in list(node.memory[self.neighborsKey]):
                if i is not node.memory['next_node'] and i is not node.memory['entry']:
                    node.send(Message(destination=i, header='Visited', data=message.data))
            node.status = 'VISITED'
        else:
            node.send(Message(destination=node.memory['entry'], header='Return', data=message.data))
            for i in list(node.memory[self.neighborsKey]):
                if i is not node.memory['entry']:
                    node.send(Message(destination=i, header='Visited', data=message.data))
            node.status = 'DONE'

    def visit(self, node, message):
        if node.memory['unvisitedNodes']:
            node.memory['next_node'] = node.memory['unvisitedNodes'].pop()
            node.send(Message(destination=node.memory['next_node'], header='Token', data=message.data))
        else:
            if 'entry' in node.memory:
                node.send(Message(destination=node.memory['entry'], header='Return', data=message.data))
            node.status = 'DONE'

    STATUS = {
                'INITIATOR': initiator,
                'IDLE': idle,
                'AVAILABLE': available,
                'VISITED': visited,
                'DONE': done
             }