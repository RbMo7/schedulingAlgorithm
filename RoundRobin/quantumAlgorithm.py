import threading
import queue
import random
import time
import csv

class Customer:
    def __init__(self, id, service_time):
        self.id = id
        self.service_time = service_time
    
    def __lt__(self, other):
        return self.service_time < other.service_time

class Teller(threading.Thread):
    def __init__(self, id, queue, gantt_data, quantum_time):
        threading.Thread.__init__(self)
        self.id = id
        self.queue = queue
        self.gantt_data = gantt_data
        self.quantum_time = quantum_time
        self.daemon = True

    def run(self):
        while True:
            customer = self.queue.get()
            entry_time = time.time()  # Record entry time
            print(f"Customer {customer.id} enters Teller{self.id}")
            self.gantt_data.append((customer.id, self.id, entry_time, 'arrival'))

            # Serve the customer in chunks (quantum time)
            while customer.service_time > 0:
                # Check if remaining service time is less than the quantum time
                if customer.service_time <= self.quantum_time:
                    time.sleep(customer.service_time)
                    customer.service_time = 0
                else:
                    time.sleep(self.quantum_time)
                    customer.service_time -= self.quantum_time

            exit_time = time.time()  # Record exit time
            print(f"Customer {customer.id} leaves Teller{self.id}")
            self.gantt_data.append((customer.id, self.id, exit_time, 'departure'))
            self.queue.task_done()

def generate_customers(num_customers, queue, barrier):
    barrier.wait()  # Wait for all customers to be ready
    arrival_time = time.time()  # Record arrival time for all customers
    for i in range(num_customers):
        service_time = random.uniform(1, 5)  # Random service time
        customer = Customer((i + 1), service_time)  # Unique customer IDs
        print(f"Customer {customer.id} enters the Queue with service time {service_time}")
        queue.put(customer)

def main():
    num_tellers = 3
    num_customers = 10

    # User input for quantum time
    quantum_time = float(input("Enter the quantum time for Round Robin algorithm (in seconds): "))

    q = queue.Queue()  # Using a regular queue for simplicity
    gantt_data = []  # List to store Gantt chart data

    # Create tellers
    tellers = [Teller(i+1, q, gantt_data, quantum_time) for i in range(num_tellers)]

    # Start teller threads
    for teller in tellers:
        teller.start()

    # Create a barrier for synchronizing customer threads
    barrier = threading.Barrier(num_customers)

    # Generate customers
    customers = [threading.Thread(target=generate_customers, args=(num_customers, q, barrier)) for _ in range(num_customers)]
    for customer in customers:
        customer.start()

    # Wait for all customers to be served
    q.join()

    # Write Gantt chart data to CSV file
    with open("./RoundRobin/rrData.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Customer", "Teller", "Time", "Event"])
        for item in gantt_data:
            writer.writerow(item)

if __name__ == "__main__":
    main()
