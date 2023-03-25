#Nefeli Lefa
#Práctica 2 PRPA
#Monitors


from multiprocessing import Process
from multiprocessing import Condition, Lock
from multiprocessing import Value
from multiprocessing import current_process
import time, random

nc1=4
nc2=3
nh=4

class Monitor():
    def __init__(self):
        self.nhumans = Value('i', 0)
        self.ncars1 = Value('i', 0)
        self.ncars2 = Value('i', 0)
        self.nhumans_waiting = Value('i', 0)
        self.ncars1_waiting = Value('i', 0)
        self.ncars2_waiting = Value('i', 0)
        self.turn = Value('i', random.randint(0,2))
        #turn 0 for humans
        #turn 1 for cars1
        #turn 2 for cars2
        self.mutex = Lock()
        self.no_cars = Condition(self.mutex)

        self.nobody1= Condition(self.mutex)
        self.nobody2 = Condition(self.mutex)

    def are_no_cars(self):
        return self.ncars1.value == 0 and self.ncars2.value==0 and \
               (self.turn.value == 0 or self.ncars1_waiting.value == 0 or self.ncars2_waiting.value == 0)
    
    def are_nobody1(self):
        return self.nhumans.value == 0 and \
            self.ncars2.value == 0  and \
            self.nhumans_waiting.value == 0 and \
            (self.turn.value == 1 or self.ncars2_waiting.value == 0)
    
    def are_nobody2(self):
        return self.nhumans.value == 0 and \
            self.ncars1.value == 0  and \
            self.nhumans_waiting.value == 0 and \
            (self.turn.value == 2 or  self.ncars1_waiting.value == 0)
    
    def want_walk(self):
        self.mutex.acquire()
        self.nhumans_waiting.value += 1
        self.no_cars.wait_for(self.are_no_cars)
        self.nhumans_waiting.value -= 1
        self.nhumans.value += 1
        self.mutex.release()

    def stop_walking(self):
        self.mutex.acquire()
        self.nhumans.value -= 1
        self.turn.value = random.randint(1,2)
        if self.nhumans.value == 0:
            self.nobody1.notify_all()
            self.nobody2.notify_all()
        self.mutex.release()

    def want_drive1(self):
        self.mutex.acquire()
        self.ncars1_waiting.value += 1
        self.nobody1.wait_for(self.are_nobody1)
        self.ncars1_waiting.value -= 1
        self.ncars1.value += 1
        self.mutex.release()

    def stop_driving1(self):
        self.mutex.acquire()
        self.ncars1.value -= 1
        self.turn.value = 0
        if self.ncars1.value == 0:
            self.no_cars.notify_all()
            self.nobody2.notify_all()
        self.mutex.release()

    def want_drive2(self):
        self.mutex.acquire()
        self.ncars2_waiting.value += 1
        self.nobody2.wait_for(self.are_nobody2)
        self.ncars2_waiting.value -= 1
        self.ncars2.value += 1
        self.mutex.release()

    def stop_driving2(self):
        self.mutex.acquire()
        self.ncars2.value -= 1
        self.turn.value = 0
        if self.ncars2.value == 0:
            self.no_cars.notify_all()
            self.nobody1.notify_all()
        self.mutex.release()

    def __str__(self):
        return f"M<humans:{self.nhumans.value}, humans waiting:{self.nhumans_waiting.value}, cars1:{self.ncars1.value}, cars1 waiting:{self.ncars1_waiting.value}, cars2:{self.ncars2.value}, cars2 waiting:{self.ncars2_waiting.value}, turn:{self.turn.value}>"



def delay(d):
    time.sleep(random.random()/d)


def human(monitor):
    
    time.sleep(5)
    print(f"human {current_process().name} wants to walk. Status: {monitor}")
    monitor.want_walk()
    print(f"human {current_process().name} walking.       Status: {monitor}")
    time.sleep(20)
    monitor.stop_walking()
    print(f"human {current_process().name} has passed.    Status: {monitor}")

def car1(monitor):
    
    time.sleep(0.5)
    print(f"car1 {current_process().name} wants to drive. Status: {monitor}")
    monitor.want_drive1()
    print(f"car1 {current_process().name} driving.        Status: {monitor}")
    delay(0.5)
    print(f"car1 {current_process().name} has passed.     Status: {monitor}")
    monitor.stop_driving1()

def car2(monitor):
   
    time.sleep(0.5)
    print(f"car2 {current_process().name} wants to drive. Status: {monitor}")
    monitor.want_drive2()
    print(f"car2 {current_process().name} driving.        Status: {monitor}")
    delay(0.5)
    print(f"car2 {current_process().name} has passed.     Status: {monitor}")
    monitor.stop_driving2()


def main():

    monitor = Monitor()
    humans = [Process(target=human, name=f"h{i}", args=(monitor,)) \
               for i in range(nh)]
    cars1 = [Process(target=car1, name=f"c1{i}", args=(monitor,)) \
               for i in range(nc1)]
    cars2 = [Process(target=car2, name=f"c2{i}", args=(monitor,)) \
               for i in range(nc2)]
    for x in humans + cars1 + cars2:
        x.start()
    for x in humans + cars1 + cars2:
        x.join()

if __name__ == '__main__':
    main()
