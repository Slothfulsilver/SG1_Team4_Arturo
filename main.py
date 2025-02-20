import simpy
import random
import numpy as np

class Factory(object):
    def __init__(self, env: simpy.Environment):
        self._env = env
        self._station = [simpy.Resource(env, capacity=1)] * 6
        self._station_fail = [False] * 6
        self._resupply_device = simpy.Resource(env, capacity = 3)
        self._prod = env.process(self.prod())

    # ---- Produccion Process ----

    def prod(self) -> simpy.Environment:
        while True:
            #Easy cycle for first 3 stations
            for i in range(3):
                yield self._env.process(self.work(i))
            
            #Hardcoding rest of process /// Find a way to make it a cycle or make it simplier
            selection = random.randint(3, 4)
            if selection == 4:
                yield self._env.process(self.work(selection))
                yield self._env.process(self.work(selection - 1))
            else:
                yield self._env.process(self.work(selection))
                yield self._env.process(self.work(selection + 1))

            yield self._env.process(self.work(5))

    # ---- End of produccion ----

    #Resupply Request
    def resupply(self):
        with self._resupply_device.request() as req:
            yield req
            yield env.timeout(np.random.normal(2))
            print("Starting resupply at %d" % self._env.now)

    
    #WorkStation Rquest
    def work(self, num):
        with self._station[num].request() as req:
            yield req

            #Fail Check
            fail_rate = [0.02, 0.01, 0.05, 0.15, 0.07, 0.06]
            fail = random.random()
            if fail < fail_rate[num]:
                print(f"Something went wrong with Station {num + 1}! at {self._env.now}")
            else:
                yield env.timeout(np.random.normal(4))
                print(f"Starting work on station {num + 1} at {self._env.now}")
            

env = simpy.Environment()
factory = (Factory(env))
env.run(until=100)

