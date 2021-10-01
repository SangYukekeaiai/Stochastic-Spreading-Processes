import Reject_model
import GA
import OGA
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import math
import time
import sys


def main(argv=None):
    if argv is None:
        argv = sys.argv

    node_numberlist = range(10000, 110000, 10000)
    plt.figure()
    rjls = Reject_model.trans_data_list()
    rjlsg2 = []
    rjlsg3 = []
    for i in range(len(rjls)):
        if i< 10:
            rjlsg2.append(rjls[i])
        else:
            rjlsg3.append(rjls[i]) 
    rjg2 = plt.scatter(node_numberlist, rjlsg2, label = 'Reject, gamma = 2.0', c = 'blue', marker = 'v')
    rjg3 = plt.scatter(node_numberlist, rjlsg3, label = 'Reject, gamma = 3.0', c = 'yellow', marker = '^')


    gals = GA.trans_data_list()
    galsg2 = []
    galsg3 = []
    for i in range(len(gals)):
        if i< 10:
            galsg2.append(gals[i])
        else:
            galsg3.append(gals[i]) 
    gag2 = plt.scatter(node_numberlist, galsg2, label = 'GA, gamma = 2.0', c = 'green', marker = '>')
    gag3 = plt.scatter(node_numberlist, galsg3, label = 'GA, gamma = 3.0', c = 'orange', marker = '<')

    ogals = OGA.trans_data_list()
    ogalsg2 = []
    ogalsg3 = []
    for i in range(len(ogals)):
        if i< 10:
            ogalsg2.append(ogals[i])
        else:
            ogalsg3.append(ogals[i]) 
    ogag2 = plt.scatter(node_numberlist, ogalsg2, label = 'OGA, gamma = 2.0', c = 'red', marker = '+')
    ogag3 = plt.scatter(node_numberlist, ogalsg3, label = 'OGA, gamma = 3.0', c = 'black', marker = 'x')

    plt.xlabel("Number of Nodes")
    plt.ylabel("CPU Time per Step(s)")
    plt.legend()
    plt.show()

if __name__ == '__main__':
    sys.exit(main())