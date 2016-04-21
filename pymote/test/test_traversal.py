import sys
import traceback
import unittest
import pdb

from pymote.algorithms import traversal
from pymote.networkgenerator import NetworkGenerator
from pymote.npickle import write_pickle
from pymote.simulation import Simulation
from pymote.network import Network


class NetArch(object):
    def __init__(self):
        pass

    @staticmethod
    def get_line():
        net1 = Network()
        net1.add_node(pos=(50, 100), commRange=101)
        net1.add_node(pos=(150, 100), commRange=101)
        net1.add_node(pos=(250, 100), commRange=101)
        net1.add_node(pos=(350, 100), commRange=101)
        net1.add_node(pos=(450, 100), commRange=101)
        net1.add_node(pos=(550, 100), commRange=101)
        return net1

    @staticmethod
    def get_arch_unique1():
        net2 = Network()
        net2.add_node(pos=(300, 0), commRange=150)
        net2.add_node(pos=(400, 100), commRange=150)
        net2.add_node(pos=(500, 200), commRange=150)
        net2.add_node(pos=(599, 300), commRange=150)
        net2.add_node(pos=(500, 400), commRange=150)
        net2.add_node(pos=(400, 500), commRange=150)
        net2.add_node(pos=(300, 599), commRange=150)
        net2.add_node(pos=(200, 500), commRange=150)
        net2.add_node(pos=(100, 400), commRange=150)
        net2.add_node(pos=(0, 300), commRange=150)
        net2.add_node(pos=(100, 200), commRange=150)
        net2.add_node(pos=(200, 100), commRange=150)
        return net2

    @staticmethod
    def get_arch_unique2():
        net3 = Network()
        net3.add_node(pos=(300, 0), commRange=101)
        net3.add_node(pos=(300, 100), commRange=101)
        net3.add_node(pos=(300, 200), commRange=150)
        net3.add_node(pos=(200, 300), commRange=150)
        net3.add_node(pos=(400, 300), commRange=150)
        net3.add_node(pos=(300, 300), commRange=101)
        net3.add_node(pos=(300, 0), commRange=101)
        net3.add_node(pos=(300, 400), commRange=150)
        net3.add_node(pos=(300, 500), commRange=101)
        net3.add_node(pos=(300, 599), commRange=101)
        net3.add_node(pos=(100, 300), commRange=101)
        net3.add_node(pos=(0, 300), commRange=101)
        net3.add_node(pos=(500, 300), commRange=101)
        net3.add_node(pos=(599, 300), commRange=101)
        return net3

    @staticmethod
    def get_arch_unique3():
        net4 = Network()
        net4.add_node(pos=(300, 0), commRange=599)
        net4.add_node(pos=(400, 100), commRange=599)
        net4.add_node(pos=(500, 200), commRange=599)
        net4.add_node(pos=(599, 300), commRange=599)
        net4.add_node(pos=(500, 400), commRange=599)
        net4.add_node(pos=(400, 500), commRange=599)
        net4.add_node(pos=(300, 599), commRange=599)
        net4.add_node(pos=(200, 500), commRange=599)
        net4.add_node(pos=(100, 400), commRange=599)
        net4.add_node(pos=(0, 300), commRange=599)
        net4.add_node(pos=(100, 200), commRange=599)
        net4.add_node(pos=(200, 100), commRange=599)
        return net4

    @staticmethod
    def get_arch_random1():
        net_gen = NetworkGenerator(5, comm_range=300)
        net5 = net_gen.generate_random_network()
        return net5

    @staticmethod
    def get_arch_random2():
        net_gen = NetworkGenerator(10, comm_range=400)
        net6 = net_gen.generate_random_network()
        return net6

    @staticmethod
    def get_arch_random3():
        net_gen = NetworkGenerator(15, comm_range=300)
        net7 = net_gen.generate_random_network()
        return net7

    @staticmethod
    def get_arch_random4():
        net_gen = NetworkGenerator(20, comm_range=400)
        net8 = net_gen.generate_random_network()
        return net8


class DFTestRunner(unittest.TestCase):

    def __init__(self, testname, algorithm):
        super(DFTestRunner, self).__init__(testname)
        self.algorithm = algorithm
        self.test_name = testname

    def test_line(self):
        self.net = NetArch.get_line()
        self.run_test()

    def test_arch_unique1(self):
        self.net = NetArch.get_arch_unique1()
        self.run_test()

    def test_arch_unique2(self):
        self.net = NetArch.get_arch_unique2()
        self.run_test()

    def test_arch_unique3(self):
        self.net = NetArch.get_arch_unique3()
        self.run_test()

    def test_arch_random1(self):
        self.net = NetArch.get_arch_random1()
        self.run_test()

    def test_arch_random2(self):
        self.net = NetArch.get_arch_random2()
        self.run_test()

    def test_arch_random3(self):
        self.net = NetArch.get_arch_random3()
        self.run_test()

    def test_arch_random4(self):
        self.net = NetArch.get_arch_random4()
        self.run_test()

    def run_test(self):
        self.net.algorithms = (self.algorithm,)
        self.sim = Simulation(self.net)
        try:
            self.sim.run()
        except Exception, e:
            write_pickle(self.net, "{}_{}_exception.npc.gz".format(self.algorithm.__class__.__name__, self.test_name))
            pdb.set_trace()
            traceback.print_exc(file=sys.stdout)
            raise e
        for node in self.net.nodes():
            try:
                self.assertEqual(node.status, 'DONE')
                self.assertEqual(len(node.memory['unvisited_nodes']), 0)
            except AssertionError:
                write_pickle(self.net, "{}_{}_asserterror.npc.gz".format(self.algorithm.__class__.__name__, self.test_name))


def form_suite(algorithm):
    tests = ['test_line', 'test_arch_unique1', 'test_arch_unique2', 'test_arch_unique3',
             'test_arch_random1', 'test_arch_random2', 'test_arch_random3', 'test_arch_random4']
    suite = unittest.TestSuite()
    for i in tests:
        suite.addTest(DFTestRunner(i, algorithm))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(form_suite(traversal.DF))
    # unittest.TextTestRunner(verbosity=2).run(form_suite(traversal.DFp))
    # unittest.TextTestRunner(verbosity=2).run(form_suite(traversal.DFpp))
    # unittest.TextTestRunner(verbosity=2).run(form_suite(traversal.DFStar))
