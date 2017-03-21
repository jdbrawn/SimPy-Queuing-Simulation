from __future__ import division
from SimPy.Simulation import *

from numpy.random import seed, uniform
from matplotlib import pyplot as plt
import numpy as np
import SimPy

# First Name: John
# Last Name: Brawn
# BU ID: U32447749

class Parameters:
    '''In this class, you must just define the following variables of your distribution:
    These variables will be hardcoded with values. Please refer to the assignment handout what
    these values must be. You can use the values appropriately in your code by calling Parameters.NAME_OF_VARIABLE
    --For Poisson Arrivals and Exponential Service Time
      1) lambda for poisson arrivals
      2) Ts for service time

    --For Uniform Arrivals and Uniform Service Time
       3) interarrivalTimeMin and interarrivalTimeMax for Uniform distribution.
       4) serviceTimeMin and serviceTimeMax for Uniform distribution.
    5. numberOfServers in your computing system
    6. simulationTime in hrs. '''

    MAX_TIME = 100

    LAMBDA = 0.025
    TScpu = 0.02
    TSdisk = 0.1
    TSnet = 0.025

    xVal = 1
    xPasta = []
    yPasta = []
    #y = [0 for x in range(100)]
    x = []
    y = []
    total = 0

    packetTimes = []

    Lcpu = 0
    Lnet = 0
    Ldisk = 0

    Prob3 = False
    MIN_SERVICE = 0.001
    MAX_SERVICE = 0.039


##### Processes #####
# Customer
class Packet(Process):

    def behavior_of_single_packet(self,cs, disk, net):
        '''You must implement this method. This method is the behavior of a single packet
        when it interacts with the queue of your computing system. These are some questions you will want to think about
        1. What happens when the packet arrives? Does it get serviced immediately or gets put in the queue?
        2. If it does get serviced, how long will it be serviced for? Or does it get put in the queue?
        3. When does it depart?

        The cs in the method is an instance of the Computing System class'''

        currentProc = "CPU"
        inSystem = True
        tCreate = now()

        while inSystem:


            if now() >= Parameters.xVal:
                Parameters.xPasta.append(now())
                Parameters.yPasta.append(len(cs.waitQ))
                Parameters.xVal += 1


            if currentProc == "CPU":

                Parameters.Lcpu += 1
                # Customer arrives, joins queue
                #arrive = now()
                #print ('Time {}: {} arrived and about to join the CPU queue'.format(now(), self.name))
                yield request, self, cs
                #wait = now() - arrive
                #c.observe(wait)

                if now() > 00:
                    Parameters.x.append(now())
                    Parameters.y.append(len(cs.waitQ))
                    Parameters.total += len(cs.waitQ)


                #print ('Time {}: {} is about to get its CPU service initiated'.format(now(), self.name))
                if Parameters.Prob3:
                    t = uniform(Parameters.MIN_SERVICE, Parameters.MAX_SERVICE)
                else:
                    t = np.random.exponential(Parameters.TScpu)
                yield hold, self, t
                yield release, self, cs
                #print ('Time {}: {} CPU service terminated and exits'.format(now(), self.name))

                prob = np.random.uniform()
                if prob < 0.1:
                    currentProc = "Disk"
                elif prob < 0.5:
                    currentProc = "Net"
                else:
                    inSystem = False
                    Parameters.packetTimes.append(now()-tCreate)

            elif currentProc == "Disk":

                Parameters.Ldisk += 1
                # Customer arrives, joins queue
                # print ('Time {}: {} arrived and about to join the DISK queue'.format(now(), self.name))
                yield request, self, disk

                # print ('Time {}: {} is about to get its service initiated'.format(now(), self.name))
                if Parameters.Prob3:
                    t = np.random.normal(0.1, 0.03)
                    while t <= 0:
                        t = np.random.normal(0.1, 0.03)
                else:
                    t = np.random.exponential(Parameters.TSdisk)
                yield hold, self, t
                yield release, self, disk
                # print ('Time {}: {} service terminated and exits'.format(now(), self.name))

                prob = np.random.uniform()
                if prob < 0.5:
                    currentProc = "CPU"
                else:
                    currentProc = "Net"

            elif currentProc == "Net":

                Parameters.Lnet += 1
                # Customer arrives, joins queue
                # print ('Time {}: {} arrived and about to join the NET queue'.format(now(), self.name))
                yield request, self, net

                # print ('Time {}: {} is about to get its service initiated'.format(now(), self.name))
                if Parameters.Prob3:
                    t = 0.025
                else:
                    t = np.random.exponential(Parameters.TSnet)

                arriveS = now()
                yield hold, self, t
                yield release, self, net
                # print ('Time {}: {} service terminated and exits'.format(now(), self.name))

                currentProc = "CPU"



# Packet Generator class.
class PacketGenerator(Process):
        def createPackets(self,cs, disk, net):
            '''You must complete this method. This method generates and creates packets as per the
            arrival rate distribution defined'''
            i = 0

            while True:

                t = np.random.exponential(Parameters.LAMBDA)

                yield hold, self, t
                c = Packet(name='Packet ' + str(i))
                activate(c, c.behavior_of_single_packet(cs, disk, net))
                i += 1


#You do not need to modify this class.
class ComputingSystem(Resource):
    pass


#You can modify this model method#.
def model():
    # Seed the generator using seed value of 123.
    seed(123)
    initialize()
    cpu = ComputingSystem(capacity=2, monitored=True)
    disk = ComputingSystem(capacity=1, monitored=True)
    net = ComputingSystem(capacity=1, monitored=True)

    generator = PacketGenerator()
    activate(generator, generator.createPackets(cpu, disk, net))


    simulate(until=Parameters.MAX_TIME)



# TOGGLE ON/OFF FOR PROBLEM 3
Parameters.Prob3 = False

for i in range(1):
    model()

# TOGGLE ON/OFF FOR PLOTTING TRACKING EVERY PACKET
plt.plot(Parameters.x, Parameters.y, 'ro')
plt.title("Average Length in CPU Queue = " + str(Parameters.total / len(Parameters.y)))
plt.ylabel("Length of Queue")
plt.xlabel("Time (seconds)")
plt.show()

# TOGGLE ON/OFF FOR PLOTTING TRACKING AT EVERY SECOND
plt.plot(Parameters.xPasta, Parameters.yPasta, 'ro')
plt.title("Average Length in CPU Queue = " + str(np.mean(Parameters.yPasta)))
plt.ylabel("Length of Queue")
plt.xlabel("Time (seconds)")
plt.show()

print "TRACKING EACH PACKET:"
print "Standard Deviation: " + str(np.std(Parameters.y))
print "CPU Queue Mean: " + str(np.mean(Parameters.y))
print "Number of Samples: " + str(len(Parameters.y))
print "CPU Queue 95% Confidence interval = +- " + str(1.96 * (np.std(Parameters.y)/np.sqrt(len(Parameters.y))))
print "CPU Queue 98% Confidence interval = +- " + str(2.33 * (np.std(Parameters.y)/np.sqrt(len(Parameters.y))))
print
print "Response Time Mean: " + str(np.mean(Parameters.packetTimes))
print "Response Time 95% Confidence interval = +- " + str(1.96 * (np.std(Parameters.packetTimes)/np.sqrt(len(Parameters.packetTimes))))
print "Response Time 98% Confidence interval = +- " + str(2.33 * (np.std(Parameters.packetTimes)/np.sqrt(len(Parameters.packetTimes))))
print
print "Lambda CPU = " + str(Parameters.Lcpu / Parameters.MAX_TIME)
print "Lambda Network = " + str(Parameters.Lnet / Parameters.MAX_TIME)
print "Lambda Disk = " + str(Parameters.Ldisk / Parameters.MAX_TIME)
print
print "TAKING SIZE AT EACH SECOND:"
print "Standard Deviation: " + str(np.std(Parameters.yPasta))
print "CPU Queue Mean: " + str(np.mean(Parameters.yPasta))
print "Number of Samples: " + str(len(Parameters.yPasta))
print "CPU Queue 95% Confidence interval = +- " + str(1.96 * (np.std(Parameters.yPasta)/np.sqrt(len(Parameters.yPasta))))
print "CPU Queue 98% Confidence interval = +- " + str(2.33 * (np.std(Parameters.yPasta)/np.sqrt(len(Parameters.yPasta))))
