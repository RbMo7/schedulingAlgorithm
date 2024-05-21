import threading
import time
import random
import queue
from collections import deque

# Constants
NUM_TELLERS = 3
QUEUE_SIZE = 10
MAX_SERVICE_TIME = 8
QUANTUM_TIME = 2

# Thread-safe queue for customers
customer_queue = queue.Queue(QUEUE_SIZE)

# Statistics tracking
arrival_times = {}
service_times = {}
completion_times = {}
turnaround_times = []
waiting_times = []

# Lock for thread-safe updates to statistics
lock = threading.Lock()

# Common Customer Arrival Function
def customer_arrival(customer_id):
    service_time = random.randint(4, MAX_SERVICE_TIME)
    arrival_time = time.time()
    local_time = time.localtime(arrival_time)

# Format the struct_time object into a human-readable string
    formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
    with lock:
        arrival_times[customer_id] = arrival_time
        service_times[customer_id] = service_time
    print(f"Customer{customer_id} enters the Queue with service time {service_time} at {formatted_time}")
    try:
        customer_queue.put((service_time, customer_id), timeout=1)
    except queue.Full:
        print("Queue is FULL.")

# FCFS Teller Service Function
def teller_service_fcfs(teller_id):
    while True:
        try:
            service_time, customer_id = customer_queue.get(timeout=1)
            start_time = time.time()
            print(f"Customer {customer_id} is in Teller {teller_id}")
            time.sleep(service_time)
            end_time = time.time()
            with lock:
                completion_times[customer_id] = end_time
                turnaround_time = end_time - arrival_times[customer_id]
                turnaround_times.append(turnaround_time)
                waiting_time = start_time - arrival_times[customer_id]
                waiting_times.append(waiting_time)
            print(f"Customer {customer_id} leaves the Teller {teller_id}")
        except queue.Empty:
            continue

# SJF Teller Service Function
def teller_service_sjf(teller_id):
    while True:
        try:
            with lock:
                sorted_customers = sorted(list(customer_queue.queue), key=lambda x: x[0])
                customer_queue.queue.clear()
                for customer in sorted_customers:
                    customer_queue.put_nowait(customer)

            service_time, customer_id = customer_queue.get(timeout=1)
            start_time = time.time()
            print(f"Customer {customer_id} is in Teller{teller_id}")
            time.sleep(service_time)
            end_time = time.time()
            with lock:
                completion_times[customer_id] = end_time
                turnaround_time = end_time - arrival_times[customer_id]
                turnaround_times.append(turnaround_time)
                waiting_time = start_time - arrival_times[customer_id]
                waiting_times.append(waiting_time)
            print(f"Customer {customer_id} leaves the Teller{teller_id}")
        except queue.Empty:
            continue

# Round Robin Teller Service Function
def teller_service_rr(teller_id):
    while True:
        try:
            service_time, customer_id = customer_queue.get(timeout=1)
            print(f"Customer {customer_id} is in Teller{teller_id} for a quantum of {QUANTUM_TIME}")
            start_time = time.time()
            if service_time <= QUANTUM_TIME:
                time.sleep(service_time)
                end_time = time.time()
                with lock:
                    completion_times[customer_id] = end_time
                    turnaround_time = end_time - arrival_times[customer_id]
                    turnaround_times.append(turnaround_time)
                    waiting_time = start_time - arrival_times[customer_id]
                    waiting_times.append(waiting_time)
                print(f"Customer {customer_id} leaves the Teller{teller_id}")
            else:
                time.sleep(QUANTUM_TIME)
                remaining_time = service_time - QUANTUM_TIME
                customer_queue.put((remaining_time, customer_id))
        except queue.Empty:
            continue

# Start Tellers as Threads for a Given Service Function
def start_tellers(service_function):
    tellers = []
    for i in range(1, NUM_TELLERS + 1):
        t = threading.Thread(target=service_function, args=(i,))
        t.start()
        tellers.append(t)
    return tellers

# Main Loop to Simulate Customer Arrivals
def main(service_function, description):
    customer_id = 1
    try:
        tellers = start_tellers(service_function)
        start_time = time.time()
        while customer_id <= 50:
            customer_arrival(customer_id)
            customer_id += 1
            time.sleep(random.uniform(0.5, 2))  # Random arrival time
    except KeyboardInterrupt:
        print("Simulation stopped.")
    finally:
        time.sleep(20)  # Allow all threads to complete
        calculate_stats(description)

# Calculate and Print Statistics
def calculate_stats(description):
    with lock:
        avg_turnaround_time = sum(turnaround_times) / len(turnaround_times)
        avg_waiting_time = sum(waiting_times) / len(waiting_times)
    print(f"\nStatistics for {description}:")
    print(f"Average Turnaround Time: {avg_turnaround_time:.4f} seconds")
    print(f"Average Waiting Time: {avg_waiting_time:.4f} seconds")
    print(f"Waiting time list: {waiting_times}")
    

# Run the Simulations
if __name__ == "__main__":
    print("Starting FCFS Simulation...")
    main(teller_service_fcfs, "FCFS")
    print("\nStarting SJF Simulation...")
    main(teller_service_sjf, "SJF")
    print("\nStarting Round Robin Simulation...")
    main(teller_service_rr, "Round Robin")


