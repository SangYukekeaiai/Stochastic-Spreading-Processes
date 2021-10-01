import Reject_model
import GA
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
    rjg2 = plt.scatter(node_numberlist, rjlsg2, label = r'Reject, $\gamma$ = 2.0', c = 'blue', marker = 'v')
    rjg3 = plt.scatter(node_numberlist, rjlsg3, label = r'Reject, $\gamma$ = 3.0', c = 'yellow', marker = '^')


    gals = GA.trans_data_list()
    galsg2 = []
    galsg3 = []
    for i in range(len(gals)):
        if i< 10:
            galsg2.append(gals[i])
        else:
            galsg3.append(gals[i]) 
    gag2 = plt.scatter(node_numberlist, galsg2, label = r'GA, $\gamma$ = 2.0', c = 'green', marker = '>')
    gag3 = plt.scatter(node_numberlist, galsg3, label = r'GA, $\gamma$ = 3.0', c = 'orange', marker = '<')

    plt.xlabel("Number of Nodes")
    plt.ylabel("CPU Time per Step(s)")
    plt.legend()
    plt.show()

if __name__ == '__main__':
    sys.exit(main())