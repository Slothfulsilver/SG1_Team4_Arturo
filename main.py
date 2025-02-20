import simpy
import random
import numpy as np

class Factory(object):
    def __init__(self, env: simpy.Environment):
        self._env = env
        self._total_products = 0  
        self._total_faulty_products = 0 
        self._resupply_device_occupancy = 0 
        self._resupply_device_start_time = 0
        self._total_uptime = 0 
        self._total_downtime = 0 
        self._fixing_times = []  
        self._bottleneck_delays = []
        self._station = [Workstation(env, i, [0.02, 0.01, 0.05, 0.15, 0.07, 0.06][i]) for i in range(6)]
        self._supply = [simpy.Container(env, capacity=25, init=25) for _ in range(6)]
        self._resupply_device = simpy.Resource(env, capacity = 3)
        self._resupplying = False
        self._prod = env.process(self.prod())
        for station in self._station:
            station._factory = self

    # ---- Produccion Process ----
    def prod(self) -> simpy.Environment:
        item_id = 0 #Item tracker
        while True:
            item_id += 1
            #Easy cycle for first 3 stations
            for i in range(3):
               item_id = yield self._env.process(self._station[i].work(item_id))
            
            #Random selection of stations 4 and 5
            selection = random.randint(3, 4)
            next_selection = 3 if selection == 4 else 4
            item_id = yield self._env.process(self._station[selection].work(item_id))
            item_id = yield self._env.process(self._station[next_selection].work(item_id))

            yield self._env.process(self._station[5].work(5))

            #Random selection of faulty products
            if random.random() < 0.05:
                self._total_faulty_products += 1
            else:
                self._total_products += 1

    # ---- End of produccion ----

    #Resupply Request
    def resupply(self, supply):
        self._resupply_device_start_time = self._env.now
        with self._resupply_device.request() as req:
            yield req
            resupply_start_time = self._env.now
            while supply.level < supply.capacity:
                yield env.timeout(abs(np.random.normal(2)))
                supply.put(min(25, supply.capacity - supply.level))
            resupply_end_time = self._env.now
            self._resupply_device_occupancy += resupply_end_time - resupply_start_time


class Workstation(object):
    def __init__(self, env, id, fail_rate):
        self._env = env
        self._id = id 
        self._fail_rate = fail_rate
        self._products_processed = 0
        self._resource = simpy.Resource(env, capacity = 1)
        self._supply = simpy.Container(env, capacity = 25, init = 25)
        self._resupplying = False
        self._factory = None
        self._products_processed = 0
        self._occupancy_time = 0 
        self._uptime = 0
        self._downtime = 0  
        self._start_time = 0 

    #Helper function for Resupply Vheck
    def _needs_resupply(self):
            return self._supply.level < 1 and not self._resupplying

    def work(self, item_id):
        while True:
            #Resupply Check
            while self._needs_resupply():
                self._resupplying = True
                yield self._env.process(self._factory.resupply(self._supply))
                self._resupplying = False
                
            #Start of work of a Station
            self.start_time = self._env.now
            with self._resource.request() as req:
                yield req
                work_start_time = self._env.now 
                yield env.timeout(np.random.normal(4))
                work_end_time = self._env.now
                self._occupancy_time += work_end_time - work_start_time
                self._factory._total_uptime += work_end_time - work_start_time
                self._resource.release(req)
            
            self._products_processed += 1

            #Check for failures every 5 products and within the fail probabilities
            if random.random() < self._fail_rate and self._products_processed % 5 == 0:
                failure_start_time = self._env.now 
                self._downtime += self._env.now - failure_start_time 
                self._broken = True
                yield env.timeout(np.random.exponential(3))
                failure_end_time = self._env.now 
                self._factory._total_downtime += failure_end_time - failure_start_time 
                continue
            
            #Removal of a simpy resource in container
            self._supply.get(1)
            return item_id

env = simpy.Environment()
factory = (Factory(env))
env.run(until=5000)

print(f"Final Production: {factory._total_products}")
for i, station in enumerate(factory._station):
    occupancy_rate = station._occupancy_time / 5000 
    print(f"Station {i+1} Occupancy Rate: {occupancy_rate:.2%}")
    print(f"Station {i+1} Downtime: {station._downtime}")
resupply_device_occupancy_rate = factory._resupply_device_occupancy / 5000
print(f"Total Uptime (all stations): {factory._total_uptime}")
print(f"Total Downtime (all stations): {factory._total_downtime}")
print(f"Resupply Device Occupancy Rate: {resupply_device_occupancy_rate:.2%}")
# ... (Calculate and print other statistics)
faulty_rate = factory._total_faulty_products / factory._total_products if factory._total_products > 0 else 0
print(f"Average Rate of Faulty Products: {faulty_rate:.2%}")