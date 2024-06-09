import threading
import queue
import random
import time
import os
import csv
import matplotlib.pyplot as plt

class Customer:
    def __init__(self, id, service_time, arrival_time):
        self.id = id
        self.service_time = service_time
        self.remaining_time = service_time
        self.arrival_time = arrival_time
        self.start_time = None
        self.end_time = None

    def __lt__(self, other):
        return self.remaining_time < other.remaining_time

class Teller(threading.Thread):
    def __init__(self, id, queue, lock, completed_customers, stop_event):
        threading.Thread.__init__(self)
        self.id = id
        self.queue = queue
        self.lock = lock
        self.current_customer = None
        self.start_time = None
        self.completed_customers = completed_customers
        self.stop_event = stop_event
        self.customers_attended = 0  # Initialize the count of customers served by the teller
        self.daemon = True

    def run(self):
        while not self.stop_event.is_set() or not self.queue.empty():
            with self.lock:
                if self.current_customer is None and not self.queue.empty():
                    self.current_customer = self.queue.get()
                    self.start_time = time.time()
                    self.current_customer.start_time = self.start_time
                    print(f"Customer {self.current_customer.id} starts at Teller {self.id} with remaining time {self.current_customer.remaining_time}")

            if self.current_customer is not None:
                time.sleep(0.1)  # Simulate processing time slice
                with self.lock:
                    if self.current_customer is not None:  # Re-check to ensure no preemption has occurred
                        self.current_customer.remaining_time -= 0.1
                        if self.current_customer.remaining_time <= 0:
                            self.current_customer.end_time = time.time()
                            print(f"Customer {self.current_customer.id} leaves Teller {self.id}")
                            self.completed_customers.append(self.current_customer)
                            self.customers_attended += 1  # Increment the count of customers served
                            self.current_customer = None
                        elif not self.queue.empty() and self.queue.queue[0].remaining_time < self.current_customer.remaining_time:
                            self.queue.put(self.current_customer)
                            print(f"Customer {self.current_customer.id} is preempted by Customer {self.queue.queue[0].id} at Teller {self.id}")
                            self.current_customer = None

def generate_customers(num_customers, queue, lock, tellers):  # Added 'tellers' as an argument
    for i in range(num_customers):
        service_time = random.uniform(1, 5)  # Random service time
        arrival_time = time.time()
        customer = Customer(i + 1, service_time, arrival_time)
        print(f"Customer {customer.id} enters the Queue with service time {customer.service_time}")

        with lock:
            # Preempt current customers if needed
            preempted_customers = []
            for teller in tellers:
                if teller.current_customer and customer.remaining_time < teller.current_customer.remaining_time:
                    preempted_customers.append(teller.current_customer)
                    teller.current_customer = None

            # Put preempted customers back in the queue
            for pc in preempted_customers:
                queue.put(pc)

            queue.put(customer)

        time.sleep(random.uniform(0.1, 0.5))  # Simulate random arrival times

def calculate_averages(completed_customers):
    total_turnaround_time = 0
    total_waiting_time = 0
    total_response_time = 0
    num_customers = len(completed_customers)

    with open("./SJF/sjfData.csv", "a", newline="") as file:
        writer = csv.writer(file)
        for customer in completed_customers:
            turnaround_time = customer.end_time - customer.arrival_time
            waiting_time = customer.start_time - customer.arrival_time
            response_time = customer.start_time - customer.arrival_time
            
            total_turnaround_time += turnaround_time
            total_waiting_time += waiting_time
            total_response_time += response_time

            writer.writerow([customer.id, customer.service_time, customer.arrival_time, customer.start_time, customer.end_time])

    avg_turnaround_time = total_turnaround_time / num_customers
    avg_waiting_time = total_waiting_time / num_customers
    avg_response_time = total_response_time / num_customers

    print(f"Average Turnaround Time: {avg_turnaround_time:.2f} seconds")
    print(f"Average Waiting Time: {avg_waiting_time:.2f} seconds")
    print(f"Average Response Time: {avg_response_time:.2f} seconds")
    generate_graph(avg_turnaround_time, avg_waiting_time, avg_response_time)

def main():
    num_tellers = 3
    num_customers = 50
    q = queue.PriorityQueue()
    lock = threading.Lock()
    completed_customers = []
    stop_event = threading.Event()

    try:
        # Create tellers
        tellers = [Teller(i + 1, q, lock, completed_customers, stop_event) for i in range(num_tellers)]

        # Start teller threads
        for teller in tellers:
            teller.start()

        # Generate customers
        generate_customers(num_customers, q, lock, tellers)  # Pass 'tellers' as an argument
    except KeyboardInterrupt:
        print("Simulation stopped")
    finally:
        while not q.empty() or any(teller.current_customer is not None for teller in tellers):
            time.sleep(1)
        stop_event.set()
        for teller in tellers:
            teller.join()
        for teller in tellers:
            print(f"Teller {teller.id} served {teller.customers_attended} customers.")
        calculate_averages(completed_customers)

def generate_graph(avg_turnaround_time, avg_waiting_time, avg_response_time):
    labels = ['Turnaround Time', 'Waiting Time', 'Response Time']
    values = [avg_turnaround_time, avg_waiting_time, avg_response_time]

    plt.figure(figsize=(8, 6))
    plt.plot(labels, values, marker='o', linestyle='-')
    plt.xlabel('Metrics')
    plt.ylabel('Time (seconds)')
    plt.title('Average Turnaround Time, Waiting Time, and Response Time')
    plt.grid(True)  # Add grid lines
    plt.show()

if __name__ == "__main__":
    main()
