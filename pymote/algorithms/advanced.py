from pymote.algorithm import NodeAlgorithm
from pymote.message import Message


class Saturation(NodeAlgorithm):
    """
    Author: Iva Petrovic (swimR)
    """
    required_params = {}
    default_params = {'neighborsKey': 'Neighbors'}

    def initializer(self):
        for node in self.network.nodes():
            node.memory[self.neighborsKey] = node.compositeSensor.read()['Neighbors']
            node.status = 'AVAILABLE'
        ini_node = self.network.nodes()[0]
        self.network.outbox.insert(0, Message(header=NodeAlgorithm.INI, destination=ini_node))

    def available(self, node, message):
        node_neighbors = list(node.memory[self.neighborsKey])

        if message.header == NodeAlgorithm.INI:
            self.send_message(node, message, node_neighbors)
        elif message.header == 'Activate':
            node_neighbors.remove(message.source)
            self.send_message(node, message, node_neighbors)

    def active(self, node, message):
        if message.header == 'Message':
            self.process_message(node, message)
            node.memory['neighbors'].remove(message.source)

            if len(node.memory['neighbors']) == 1:
                dist = self.prepare_message(node, message)
                node.memory['parent'] = node.memory['neighbors'].pop()
                node.send(Message(destination=node.memory['parent'], header='Message', data=dist))
                node.status = 'PROCESSING'

    def processing(self, node, message):
        if message.header == 'Message':
            self.process_message(node, message)
            self.resolve(node, message)

    def saturated(self, node, message):
        pass

    def initialize(self, node, message):
        raise NotImplementedError

    def prepare_message(self, node, message):
        m = ['Saturation']

    def process_message(self, node, message):
        raise NotImplementedError

    def send_message(self, node, message, node_neighbors):
        for i in node_neighbors:
            node.send(Message(destination=i, header='Activate', data=message.data))

        self.initialize(node, message)

        node.memory['neighbors'] = list(node.memory[self.neighborsKey])
        if len(node.memory['neighbors']) == 1:
            self.prepare_message(node, message)
            node.memory['parent'] = node.memory['neighbors'].pop()
            node.send(Message(destination=node.memory['parent'], header='Message', data=message.data))
            node.status = 'PROCESSING'
        else:
            node.status = 'ACTIVE'

    def resolve(self, node, message):
        node.status = 'SATURATED'

    STATUS = {
                'AVAILABLE': available,
                'ACTIVE': active,
                'PROCESSING': processing,
                'SATURATED': saturated
             }


class Eccentricities(Saturation):
    # algorithm input
    required_params = ()
    # values that are exposed to other algorithms
    default_params = {'neighborsKey': 'Neighbors'}

    def processing(self, node, message):
        super(Eccentricities, self).processing(node, message)
        if message.header == 'Resolution':
            self.resolve(node, message)

    def done(self, node, message):
        pass

    def initialize(self, node, message):
        node.memory['distance'] = {}
        for i in node.memory[self.neighborsKey]:
            node.memory['distance'][i] = 0

    def prepare_message(self, node, message):
        return 1 + max(list(node.memory['distance'].values()))

    def resolve(self, node, message):
        self.process_message(node, message)
        self.calculate_eccentricity(node)
        for i in list(node.memory[self.neighborsKey]):
            if i is not node.memory['parent']:
                distances = dict(node.memory['distance'])
                distances.pop(i, None)
                max_dist = 1 + max(list(distances.values()))
                node.send(Message(destination=i, header='Resolution', data=max_dist))
        node.status = 'DONE'

    def process_message(self, node, message):
        node.memory['distance'][message.source] = message.data

    def calculate_eccentricity(self, node):
        node.memory['eccentricity'] = max(list(node.memory['distance'].values()))

    def send_message(self, node, message, node_neighbors):
        for i in node_neighbors:
            node.send(Message(destination=i, header='Activate', data=message.data))

        self.initialize(node, message)

        node.memory['neighbors'] = list(node.memory[self.neighborsKey])
        if len(node.memory['neighbors']) == 1:
            dist = self.prepare_message(node, message)
            node.memory['parent'] = node.memory['neighbors'].pop()
            node.send(Message(destination=node.memory['parent'], header='Message', data=dist))
            node.status = 'PROCESSING'
        else:
            node.status = 'ACTIVE'

    STATUS = {
        'AVAILABLE': Saturation.STATUS.get('AVAILABLE'),
        'ACTIVE': Saturation.STATUS.get('ACTIVE'),
        'PROCESSING': processing,
        'SATURATED': Saturation.STATUS.get('SATURATED'),
        'DONE': done
    }