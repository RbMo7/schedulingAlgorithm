import threading
import queue
import random
import time
from queue import PriorityQueue
import matplotlib.pyplot as plt

class Customer:
    def __init__(self, id, service_time):
        self.id = id
        self.service_time = service_time
        self.remaining_time = service_time
        self.arrival_time = time.time()
        self.start_time = None
        self.end_time = None

    def start_service(self):
        self.start_time = time.time()

    def end_service(self):
        self.end_time = time.time()
    
    def turnaround_time(self):
        return self.end_time - self.arrival_time
    
    def waiting_time(self):
        return self.start_time - self.arrival_time
    
    def response_time(self):
        return self.start_time - self.arrival_time


def fcfs_scheduler():
    customer_queue = queue.Queue(MAX_QUEUE_SIZE)
    teller_threads = []

    def teller(teller_id):
        while True:
            customer = customer_queue.get()
            if customer is None:
                break
            customer.start_service()
            print(f"Customer {customer.id} is in Teller {teller_id}")
            time.sleep(customer.service_time)
            customer.end_service()
            print(f"Customer {customer.id} leaves Teller {teller_id}")
            customer_queue.task_done()
            log_metrics(customer)

    def generate_customers():
        customer_id = 1
        while True:
            time.sleep(random.randint(*ARRIVAL_INTERVAL))
            if not customer_queue.full():
                service_time = random.randint(MIN_SERVICE_TIME, MAX_SERVICE_TIME)
                customer = Customer(customer_id, service_time)
                print(f"Customer {customer_id} enters the Queue")
                customer_queue.put(customer)
                customer_id += 1
            else:
                print("Queue is FULL.")

    for i in range(NUM_TELLERS):
        t = threading.Thread(target=teller, args=(i + 1,))
        t.start()
        teller_threads.append(t)

    threading.Thread(target=generate_customers).start()

    time.sleep(SIMULATION_TIME)
    for i in range(NUM_TELLERS):
        customer_queue.put(None)
    for t in teller_threads:
        t.join()


def sjf_scheduler():
    customer_queue = PriorityQueue()
    teller_threads = []

    def teller(teller_id):
        while True:
            if customer_queue.empty():
                continue
            _, customer = customer_queue.get()
            if customer is None:
                break
            customer.start_service()
            print(f"Customer {customer.id} is in Teller {teller_id}")
            time.sleep(customer.service_time)
            customer.end_service()
            print(f"Customer {customer.id} leaves Teller {teller_id}")
            log_metrics(customer)

    def generate_customers():
        customer_id = 1
        while True:
            time.sleep(random.randint(*ARRIVAL_INTERVAL))
            if customer_queue.qsize() < MAX_QUEUE_SIZE:
                service_time = random.randint(MIN_SERVICE_TIME, MAX_SERVICE_TIME)
                customer = Customer(customer_id, service_time)
                print(f"Customer {customer_id} enters the Queue")
                customer_queue.put((service_time, customer))
                customer_id += 1
            else:
                print("Queue is FULL.")

    for i in range(NUM_TELLERS):
        t = threading.Thread(target=teller, args=(i + 1,))
        t.start()
        teller_threads.append(t)

    threading.Thread(target=generate_customers).start()

    time.sleep(SIMULATION_TIME)
    for i in range(NUM_TELLERS):
        customer_queue.put((0, None))
    for t in teller_threads:
        t.join()


def rr_scheduler(quantum):
    customer_queue = queue.Queue(MAX_QUEUE_SIZE)
    teller_threads = []
    lock = threading.Lock()

    def teller(teller_id):
        while True:
            customer = None
            with lock:
                if not customer_queue.empty():
                    customer = customer_queue.get()
            if customer is None:
                continue
            customer.start_service()
            print(f"Customer {customer.id} is in Teller {teller_id}")
            if customer.remaining_time <= quantum:
                time.sleep(customer.remaining_time)
                customer.end_service()
                print(f"Customer {customer.id} leaves Teller {teller_id}")
                log_metrics(customer)
            else:
                time.sleep(quantum)
                customer.remaining_time -= quantum
                with lock:
                    customer_queue.put(customer)
            customer_queue.task_done()

    def generate_customers():
        customer_id = 1
        while True:
            time.sleep(random.randint(*ARRIVAL_INTERVAL))
            if not customer_queue.full():
                service_time = random.randint(MIN_SERVICE_TIME, MAX_SERVICE_TIME)
                customer = Customer(customer_id, service_time)
                print(f"Customer {customer_id} enters the Queue")
                customer_queue.put(customer)
                customer_id += 1
            else:
                print("Queue is FULL.")

    for i in range(NUM_TELLERS):
        t = threading.Thread(target=teller, args=(i + 1,))
        t.start()
        teller_threads.append(t)

    threading.Thread(target=generate_customers).start()

    time.sleep(SIMULATION_TIME)
    for t in teller_threads:
        t.join()


metrics = {
    'turnaround_times': [],
    'waiting_times': [],
    'response_times': []
}

def log_metrics(customer):
    metrics['turnaround_times'].append(customer.turnaround_time())
    metrics['waiting_times'].append(customer.waiting_time())
    metrics['response_times'].append(customer.response_time())

def calculate_averages():
    avg_turnaround_time = sum(metrics['turnaround_times']) / len(metrics['turnaround_times'])
    avg_waiting_time = sum(metrics['waiting_times']) / len(metrics['waiting_times'])
    avg_response_time = sum(metrics['response_times']) / len(metrics['response_times'])
    return avg_turnaround_time, avg_waiting_time, avg_response_time

def plot_metrics():
    plt.figure(figsize=(10, 5))

    plt.subplot(131)
    plt.hist(metrics['turnaround_times'], bins=20, alpha=0.7, color='blue')
    plt.title('Turnaround Times')
    plt.xlabel('Time')
    plt.ylabel('Frequency')

    plt.subplot(132)
    plt.hist(metrics['waiting_times'], bins=20, alpha=0.7, color='green')
    plt.title('Waiting Times')
    plt.xlabel('Time')
    plt.ylabel('Frequency')

    plt.subplot(133)
    plt.hist(metrics['response_times'], bins=20, alpha=0.7, color='red')
    plt.title('Response Times')
    plt.xlabel('Time')
    plt.ylabel('Frequency')

    plt.tight_layout()
    plt.show()


NUM_TELLERS = 3
MAX_QUEUE_SIZE = 10
MIN_SERVICE_TIME = 1
MAX_SERVICE_TIME = 5
ARRIVAL_INTERVAL = (1, 3)  # Range for random arrival intervals
SIMULATION_TIME = 30  # Duration to run the simulation

if __name__ == '__main__':
    print("Starting FCFS Scheduler")
    fcfs_scheduler()
    avg_turnaround, avg_waiting, avg_response = calculate_averages()
    print(f"FCFS Average Turnaround Time: {avg_turnaround}")
    print(f"FCFS Average Waiting Time: {avg_waiting}")
    print(f"FCFS Average Response Time: {avg_response}")
    plot_metrics()

    metrics = {'turnaround_times': [], 'waiting_times': [], 'response_times': []}
    
    print("Starting SJF Scheduler")
    sjf_scheduler()
    avg_turnaround, avg_waiting, avg_response = calculate_averages()
    print(f"SJF Average Turnaround Time: {avg_turnaround}")
    print(f"SJF Average Waiting Time: {avg_waiting}")
    print(f"SJF Average Response Time: {avg_response}")
    plot_metrics()

    metrics = {'turnaround_times': [], 'waiting_times': [], 'response_times': []}

    quantum = 2  # Quantum time for Round Robin
    print("Starting Round Robin Scheduler")
    rr_scheduler(quantum)
    avg_turnaround, avg_waiting, avg_response = calculate_averages()
    print(f"RR Average Turnaround Time: {avg_turnaround}")
    print(f"RR Average Waiting Time: {avg_waiting}")
    print(f"RR Average Response Time: {avg_response}")
    plot_metrics()
