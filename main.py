import simpy
import random
import numpy as np

class Factory(object):
    def __init__(self, env: simpy.Environment):
        self._env = env
        self._station = [Workstation(env, i, [0.02, 0.01, 0.05, 0.15, 0.07, 0.06][i]) for i in range(6)]
        self._supply = [simpy.Container(env, capacity=25, init=25) for _ in range(6)]
        self._prod = env.process(self.prod())
        for station in self._station:
            station._factory = self

    # ---- Produccion Process ----

    def prod(self) -> simpy.Environment:
        item_id = 0 #Item tracker
        while True:
            item_id += 1
            print(f"Item {item_id} enters prod at {self._env.now}")
            #Easy cycle for first 3 stations
            for i in range(3):
               item_id = yield self._env.process(self._station[i].work(item_id))
            
            selection = random.randint(3, 4)
            next_selection = 3 if selection == 4 else 4
            item_id = yield self._env.process(self._station[selection].work(item_id))
            item_id = yield self._env.process(self._station[next_selection].work(item_id))

            yield self._env.process(self._station[5].work(5))

            print(f"Item {item_id} passed through all stations at {self._env.now}")

    # ---- End of produccion ----



class Workstation(object):
    def __init__(self, env, id, fail_rate):
        self._env = env
        self._id = id
        self._fail_rate = fail_rate
        self._resource = simpy.Resource(env, capacity = 1)
        self._supply = simpy.Container(env, capacity = 25, init = 25)
        self._resupply_device = simpy.Resource(env, capacity = 3)
        self._resupplying = False

    def work(self, item_id):
        while True:
            with self._resource.request() as req:
                while self.needs_resupply():
                    print("Waiting for resupply")
                    self._resupplying = True
                    yield self._env.process(self.resupply())
                    print(f"Resupply done for Station {self._id + 1} at {self._env.now}")
                
                yield req

                print(f"Starting work on station {self._id + 1} at {self._env.now}")
                yield env.timeout(np.random.normal(4))

                self._resource.release(req)

            if random.random() < self._fail_rate:
                print(f"Something went wrong with Station {self._id + 1}! at {self._env.now}")
                yield env.timeout(np.random.exponential(3))
                print(f"Station {self._id + 1} repaired at {self._env.now}")
                continue
            
            
            self._supply.get(1)
            print(f"After {self._supply.level}")
            return item_id
        
        #Resupply Request
    def resupply(self, supply):
        with self._resupply_device.request() as req:
            yield req
            print("Starting resupply at %d" % self._env.now)
            while supply.level < supply.capacity:
                yield env.timeout(abs(np.random.normal(2)))
                supply.put(min(25, supply.capacity - supply.level))
                print(supply.level)

    def needs_resupply(self):  # Helper function
        return self._supply.level < 1 and not self._resupplying
            

env = simpy.Environment()
factory = (Factory(env))
env.run(until=1000)

