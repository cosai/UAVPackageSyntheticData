import statistics
import numpy as np
import random
import math
import matplotlib.pyplot as plt
import sys

alpha = 40 * 60  # eventA happens mean 40 minutes
beta = 30 * 60  # eventB happens mean 30 minutes
nameOfStation=["A","B"]
#requestTimesAverage = [alpha, beta]

#those will be cleaned
requestTimesAverage = []
maxServiceTimes = []
serviceTimeAverage = []  # with exponential distribution

chargeTime = 60 * 5  # 5 minutes
fullBatteryLife = 60 * 30  # battery life is 30 minutes

a = 100  # distance between chargong center to A (seconds flight time)
b = 50  # distance between charging center to B
stationDistances = [] # [a,b]
maxtime = 60 * 60 * 24 * 15

numberOfUAVs = 1
currentLife = []
nextAvailableTime = []

_AservicedAt = []
_BservicedAt = []
delayA = []
delayB = []
time = 0

#exponential random variable generator with expected value given as mu
def expoRandom(mu: float):
    #n = random.random()
    #return round(-math.log(n) / mu)
    return np.random.exponential(mu, 1)

#not used
def poissonRandom(lamb:float):
    return numpy.random.poisson(lamb,1)

def createServiceTime(stationName:int):
    mymu=serviceTimeAverage[stationName]
    result=expoRandom(mymu)
    if result > maxserviceTime(stationName):
        return maxserviceTime(stationName)
    return result

def createRequestTimes(stationName:int):
    mymu = requestTimesAverage[stationName]
    result = expoRandom(mymu)
    return result

def exponentialRandVarGen(stationName: int):
    mylambda = 1 / eventHappenTimesAverage[stationName]

    # Get a random probability value from the uniform distribution's PDF
    n = random.random()

    # Generate the inter-event time from the exponential distribution's CDF using the Inverse-CDF technique
    # time intervals between poisson processes are exponentially distributed
    # https: // www.johndcook.com / blog / 2010 / 06 / 14 / generating - poisson - random - values /
    exponVar = round(-math.log(1.0 - n) / mylambda)
    return exponVar


# given delays, prints the graph
def plotGraph(fname: str, arr):
    # print the mean number of events per unit time
    fname = "delay" + fname + ".pdf"
    fig = plt.figure()
    fig.suptitle('Delay times')
    plot, = plt.plot(range(len(arr)), arr, 'bo-', label='Inter-event time')
    plt.legend(handles=[plot])
    plt.xlabel('Index of event')
    plt.ylabel('Time')
    plt.show()
    plt.savefig(fname)


# maximum service time for a station
def maxserviceTime(stationName: int):
    if stationName < len(maxServiceTimes):
        return maxServiceTimes[stationName]
    return -1


# if battery is enough to go to stationName
def isBatteryEnough(stationName: int, uavName: int) -> bool:
    if currentLife[uavName] > 2 * stationDistances[stationName] + maxserviceTime(stationName):
        return True
    return False


# charges battery and consumes charging Time as chargeTime
def chargeBattery(uavName: int):
    global currentLife
    currentLife[uavName] = fullBatteryLife
    nextAvailableTime[uavName] = time + chargeTime


# goes to the station and service it
# If service is called it means the uav is on charging station.
# At the end of the method it goes to charging station again.

def service(stationName: int, requestTime: int, uavName: int):
    global currentLife
    global _BservicedAt
    global _AservicedAt
    global delayA
    global delayB
    delay = 0
    eventSTime = 0
    if stationName == 0:  # A
        eventSTime = createServiceTime(stationName)
        servicedtime = time + stationDistances[stationName] + eventSTime
        # finished service
        _AservicedAt.append(servicedtime)
        delay = int(servicedtime) - requestTime
        if delay < 0:
            print("Delay negative A")
            print(f"{nameOfStation[stationName]}  Time:{time} Rtime:{requestTime} Delay:{delay}")
        delayA.append(delay)
        nextAvailableTime[uavName] = servicedtime + stationDistances[stationName]
        # returned station
        # battery consumed
        currentLife[uavName] = currentLife[uavName] - 2 * stationDistances[stationName] - eventSTime
    elif stationName == 1:
        eventSTime = createServiceTime(stationName)
        servicedtime = time + stationDistances[stationName] + eventSTime
        # finished service
        _BservicedAt.append(servicedtime)
        delay = int(servicedtime) - requestTime
        if delay < 0:
            print("Delay negative B")
            print(f"{nameOfStation[stationName]}  Time:{time} Rtime:{requestTime} Delay:{delay}")
        delayB.append(delay)
        nextAvailableTime[uavName] = servicedtime + stationDistances[stationName]
        # returned station
        # battery consumed
        currentLife[uavName] = currentLife[uavName] - 2 * stationDistances[stationName] - eventSTime


def SimulationCheck():
    for sname in range(len(stationDistances)):
        if fullBatteryLife < 2 * stationDistances[sname] + maxserviceTime(sname):
            #print("Battery not enough for " + str(sname))
            return False
    return True


## returns 2D array, sorted in 2nd column
# |stationname | requestTime |
# | 0          | 15          |
# | 1          | 17          |
# | 0          | 27          |
# | 0          | 29          |
def eventsCreator(timelimit: int) -> np.array:
    # event generator
    dtype = [('eventName', int), ('time', int)]

    _event_numA = []
    _inter_event_timesA = []
    _event_timesA = []
    _event_timeA = 0

    _event_numB = []
    _inter_event_timesB = []
    _event_timesB = []
    _event_timeB = 0
    events = []
    i = 1
    while _event_timeA < timelimit and _event_timeB < timelimit:
        # Generating for EventA
        _event_numA.append(i)
        _inter_event_time = createRequestTimes(0)
        _inter_event_timesA.append(_inter_event_time)
        _event_timeA = _event_timeA + _inter_event_time
        _event_timesA.append(_event_timeA)

        events.append((0, _event_timeA))

        # Generating for EventB
        _event_numB.append(i)
        _inter_event_time = createRequestTimes(1)
        _inter_event_timesB.append(_inter_event_time)
        _event_timeB = _event_timeB + _inter_event_time
        _event_timesB.append(_event_timeB)

        events.append((1, _event_timeB))
        i = i + 1

    npevents = np.array(events, dtype=dtype)
    npevents = np.sort(npevents, order='time')
    #print(npevents)
    return npevents  # _event_timesA,_event_timesB


def stationService(stationname: int, rtime: int, uavname: int):
    if not isBatteryEnough(stationname, uavname):
        chargeBattery(uavname)
    service(stationname, rtime, uavname)


####
# main block

def simulator(ag: int, bg: int, gmaxtime: int, requestTimeAverageA: int, requestTimeAverageB: int,serviceTimeAverageA:int,serviceTimeAverageB:int,maxServiceTimeA:int,maxServiceTimeB:int):
    global a
    global b
    global maxtime
    global alpha
    global beta
    global time
    global stationDistances
    global requestTimesAverage
    global maxServiceTimes
    global serviceTimeAverage
    global _BservicedAt
    global _AservicedAt
    global nextAvailableTime
    global currentLife

    if gmaxtime != -1:
        maxtime = gmaxtime

    if bg != -1:
        b = bg

    if ag != -1:
        a = ag

    if requestTimeAverageA != -1:
        alpha = requestTimeAverageA

    if requestTimeAverageB != -1:
        beta = requestTimeAverageB

    stationDistances = [a, b]
    requestTimesAverage = [alpha, beta]

    maxServiceTimes = [maxServiceTimeA,maxServiceTimeB]
    #120 175
    serviceTimeAverage = [serviceTimeAverageA,serviceTimeAverageB]  # with exponential distribution
    #60 75

    for i in range(numberOfUAVs):
        currentLife.append(fullBatteryLife)
        nextAvailableTime.append(-1)
    
    chk = SimulationCheck()
    if not chk:
        #print("ERROR:Parameters are not appropriate")
        return [-1, -1, -1]

    #print(f"Adist:{a} Bdist:{b} time:{maxtime} alpha:{alpha} beta:{beta}")
    AllEvents = eventsCreator(maxtime)
    eventsPointer = 0
    numberOfEvents = len(AllEvents)
    time = 0
    while time < maxtime:
        name, etime = AllEvents[eventsPointer]
        etime = int(etime)
        name = int(name)
        #While UAV is servicing a location a request might have came
        if etime <= time:
            #print("Request Came at "+str(etime))
            #A request Came
            for el in range(numberOfUAVs):
                #if one UAV is available it can service
                if nextAvailableTime[el] <= time:
                    nextAvailableTime[el] = -1
                    stationService(name, etime, el)
                    break
            #Prepare for the next one
            eventsPointer = eventsPointer + 1
        if eventsPointer >= numberOfEvents:
            break
        #print(eventsPointer)
        time = time + 1

    # print(" B "+str(len(delayB))+" A "+str(len(delayA)))

    # routingMath.plotGraph("A",delayA)
    # routingMath.plotGraph("B",delayB)

    #print(f"eventA mean {statistics.mean(delayA)} stddev:{statistics.stdev(delayA)} median:{statistics.median(delayA)}")
    #print(f"eventB mean {statistics.mean(delayB)} stddev:{statistics.stdev(delayB)} median:{statistics.median(delayB)}")
    alldelays = delayA + (delayB)
    mmean = statistics.mean(alldelays)
    mstd = statistics.stdev(alldelays)
    mmed = statistics.median(alldelays)
    #print(f"All mean {mmean} stddev:{mstd} median:{mmed}")
    retArray = [mmean, mstd, mmed,statistics.mean(delayA),statistics.stdev(delayA),statistics.median(delayA),statistics.mean(delayB),statistics.stdev(delayB),statistics.median(delayB)]

    
    _AservicedAt.clear()
    _BservicedAt.clear()
    delayA.clear()
    delayB.clear()
    time=0
    stationDistances.clear()
    requestTimesAverage.clear()
    nextAvailableTime.clear()
    maxServiceTimes.clear()
    serviceTimeAverage.clear()
    currentLife.clear()
    nextAvailableTime.clear()
    
    return retArray


#this method creates a random data entry
#returns the input parameters and the output results separated by comma
#if the simulation is not possible with the random parameters, this method will return "XXX"
#meaning impossible case
#the units in this method are all in seconds.
def randomDataGenerator():
    totaldistance = random.randrange(100,1600,1)
    #totaldistance is in seconds. That means the distance that UAV can travel in that seconds time.
    #the speed of UAV is constant but it is not important, not stated in this simulator.
    adistance = random.randrange(10,totaldistance-10,1)
    maxsimtimehere = 604800*2
    reqTimeA = random.randrange(20*60,24*60*60,30)
    reqTimeB = random.randrange(20*60,24*60*60,30)
    maxServiceA=random.randrange(60,20*60,5)
    maxServiceB=random.randrange(60,20*60,5)
    serviceTimeA=random.randrange(30,maxServiceA,10)
    serviceTimeB=random.randrange(30,maxServiceB,10)
    bdistance=totaldistance-adistance
    params=[adistance, totaldistance, reqTimeA, reqTimeB, serviceTimeA, serviceTimeB, maxServiceA, maxServiceB]
    arr=[]
    arr=simulator(adistance, bdistance, maxsimtimehere, reqTimeA, reqTimeB, serviceTimeA, serviceTimeB, maxServiceA, maxServiceB)
    if arr[0]!=-1 and arr[1]!=-1 and arr[2]!=-1:
        allparams=",".join(str(v) for v in params)
        lastlog=','.join(str(round(v,2)) for v in arr)
        return allparams+","+lastlog
    return "XXX"


#datanum is the number of data points to create
def bigRandomDataGenerator(datanum:int):
    countermy=0
    with open(f"randomdata{datanum}.csv","w",buffering=1) as file1:
        file1.write("Adistance,totaldistance,reqTimeA,reqTimeB,serviceTimeA,serviceTimeB,maxServiceA,maxServiceB,mean,std,median,amean,astd,amedian,bmean,bstd,bmedian,noOfUAVs\n") 
        while countermy<datanum:
            csvresult=randomDataGenerator()
            #if the returned result is valid then write it to file
            if csvresult != "XXX":               
                file1.write(csvresult+","+numberOfUAVs+"\n")
                countermy=countermy+1
                #print(f"data {countermy}")
            #else:
            #    print("XXXXX ",i)

numberofdatatocreate=100
bigRandomDataGenerator(numberofdatatocreate)    
