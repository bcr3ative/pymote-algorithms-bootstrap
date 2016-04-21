from pymote.algorithm import NodeAlgorithm
from pymote.message import Message


class Eccentricities(NodeAlgorithm):
    # algorithm input
    required_params = ()
    # values that are exposed to other algorithms
    default_params = {'neighborsKey': 'Neighbors'}

    def initializer(self):
        for node in self.network.nodes():
            node.memory[self.neighborsKey] = node.compositeSensor.read()['Neighbors']
            node.status = 'AVAILABLE'
        # make first node initiator
        ini_node = self.network.nodes()[0]
        ini_node.status = 'INITIATOR'
        self.network.outbox.insert(0, Message(header=NodeAlgorithm.INI, destination=ini_node))

    def initiator(self, node, message):
        node.send(Message(header='Activate', data=message.data))
        self.initialize(node)
        node.memory['neighbors'] = list(node.memory[self.neighborsKey])
        if len(node.memory['neighbors']) == 1:
            msg = self.prepare_message(node)
            parent = node.memory['neighbors'].pop()
            node.send(Message(destination=parent, header='M', data=msg))
            node.status = 'PROCESSING'
        else:
            node.status = 'ACTIVE'

    def available(self, node, message):
        if message.header == 'Activate':
            for i in node.memory[self.neighborsKey]:
                if i is not message.source:
                    node.send(Message(destination=i, header='Activate', data=message.data))
            self.initialize(node)
            node.memory['neighbors'] = list(node.memory[self.neighborsKey])
            if len(node.memory['neighbors']) == 1:
                msg = self.prepare_message(node)
                parent = node.memory['neighbors'].pop()
                node.send(Message(destination=parent, header='M', data=msg))
                node.status = 'PROCESSING'
            else:
                node.status = 'ACTIVE'

    def active(self, node, message):
        if message.header == 'M':
            self.process_message(node, message)
            node.memory['neighbors'].remove(message.source)
            if len(node.memory['neighbors']) == 1:
                msg = self.prepare_message()
                parent = node.memory['neighbors'].pop()
                node.send(Message(destination=parent, header='M', data=msg))
                node.status = 'PROCESSING'

    def processing(self, node, message):
        if message.header == 'Resolution':
            self.resolve(node, message)

    def saturated(self, node, message):
        pass

    def initialize(self, node):
        node.memory['distance'] = {}
        for i in node.memory[self.neighborsKey]:
            node.memory['distance'][id(i)] = 0

    def prepare_message(self, node):
        maxdist = 1 + max(list(node.memory['distance'].values()))
        return {'type': 'Saturation', 'maxdist': maxdist}

    def process_message(self, node, message):
        node.memory['distance'][id(message.source)] = message.data['maxdist']

    def resolve(self, node, message):
        pass

    def calculate_eccentricity(self, node):
        ecc = max(list(node.memory['distance'].values()))

    STATUS = {
        'INITIATOR': initiator,
        'AVAILABLE': available,
        'ACTIVE': active,
        'PROCESSING': processing,
        'SATURATED': saturated
    }