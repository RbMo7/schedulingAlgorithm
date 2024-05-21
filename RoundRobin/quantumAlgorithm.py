import threading
import time
import random
import queue
import matplotlib.pyplot as plt

# Constants
NUM_TELLERS = 3
QUEUE_CAPACITY = 10
MAX_SERVICE_DURATION = 8
TIME_QUANTUM = 2

# Shared queue for customers
customer_queue = queue.Queue(QUEUE_CAPACITY)

# Statistics dictionaries
arrival_times = {}
service_durations = {}
completion_times = {}
first_service_start_times = {}
remaining_service_times = {}
turnaround_times = []
waiting_times = []
response_times = []

# Lock for safe updates to statistics
stats_lock = threading.Lock()

# Event to stop threads
stop_simulation = threading.Event()


def clear_queue(q):
    while not q.empty():
        q.get()

# Function to simulate customer arrival
def simulate_customer_arrival(customer_id):
    service_duration = random.randint(3, MAX_SERVICE_DURATION)
    arrival_timestamp = time.time()
    with stats_lock:
        arrival_times[customer_id] = arrival_timestamp
        service_durations[customer_id] = service_duration
        remaining_service_times[customer_id] = service_duration
    print(f"Customer {customer_id} arrives with service time {service_duration}")
    try:
        customer_queue.put((service_duration, customer_id), timeout=1)
    except queue.Full:
        print("Queue is FULL.")

# Round Robin teller service function
def teller_round_robin_service(teller_id):
    while not stop_simulation.is_set():
        try:
            service_duration, customer_id = customer_queue.get(timeout=1)
            start_timestamp = time.time()
            with stats_lock:
                if customer_id not in first_service_start_times:
                    first_service_start_times[customer_id] = start_timestamp
                    response_times.append(start_timestamp - arrival_times[customer_id])
            print(f"Customer {customer_id} is at Teller {teller_id} for {TIME_QUANTUM} seconds")
            if service_duration <= TIME_QUANTUM:
                time.sleep(service_duration)
                end_timestamp = time.time()
                with stats_lock:
                    completion_times[customer_id] = end_timestamp
                    turnaround_time = end_timestamp - arrival_times[customer_id]
                    turnaround_times.append(turnaround_time)
                    waiting_time = start_timestamp - arrival_times[customer_id]
                    waiting_times.append(waiting_time)
                    remaining_service_times.pop(customer_id, None)
                print(f"Customer {customer_id} completed at Teller {teller_id}")
            else:
                time.sleep(TIME_QUANTUM)
                remaining_time = service_duration - TIME_QUANTUM
                with stats_lock:
                    remaining_service_times[customer_id] = remaining_time
                customer_queue.put((remaining_time, customer_id))
                print(f"Customer {customer_id} remaining service time: {remaining_time} seconds")
        except queue.Empty:
            continue

# Function to start teller threads
def launch_teller_threads(service_function):
    threads = []
    for teller_id in range(1, NUM_TELLERS + 1):
        thread = threading.Thread(target=service_function, args=(teller_id,))
        thread.start()
        threads.append(thread)
    return threads

# Main function to handle customer arrivals and manage simulation
def main_simulation(service_function, description):
    clear_queue(customer_queue)
    customer_id = 1
    try:
        tellers = launch_teller_threads(service_function)
        while customer_id <= 50:
            simulate_customer_arrival(customer_id)
            customer_id += 1
            time.sleep(random.uniform(0.5, 2))  # Randomized inter-arrival time
    except KeyboardInterrupt:
        print("Simulation interrupted.")
        stop_simulation.set()
    finally:
        for teller in tellers:
            teller.join()
        compute_statistics(description)
        stop_simulation.clear()

# Function to compute and display statistics
def compute_statistics(description):
    with stats_lock:
        avg_turnaround_time = sum(turnaround_times) / len(turnaround_times)
        avg_waiting_time = sum(waiting_times) / len(waiting_times)
        avg_response_time = sum(response_times) / len(response_times)
    print(f"\nStatistics for {description}:")
    print(f"Average Turnaround Time: {avg_turnaround_time:.4f} seconds")
    print(f"Average Waiting Time: {avg_waiting_time:.4f} seconds")
    print(f"Average Response Time: {avg_response_time:.4f} seconds")
    plot_statistics(avg_turnaround_time, avg_waiting_time, avg_response_time)

# Function to plot statistics
def plot_statistics(turnaround_time, waiting_time, response_time):
    labels = ['Turnaround Time', 'Waiting Time', 'Response Time']
    values = [turnaround_time, waiting_time, response_time]

    plt.figure(figsize=(8, 6))
    plt.bar(labels, values, color=['blue', 'orange', 'green'])
    plt.xlabel('Metrics')
    plt.ylabel('Time (seconds)')
    plt.title('Average Times for Turnaround, Waiting, and Response')
    plt.show()

# Execute the simulation
if __name__ == "__main__":
    main_simulation(teller_round_robin_service, "Round Robin Scheduling")
