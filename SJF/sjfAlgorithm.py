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
    def __init__(self, id, queue, gantt_data):
        threading.Thread.__init__(self)
        self.id = id
        self.queue = queue
        self.gantt_data = gantt_data
        self.daemon = True

    def run(self):
        while True:
            customer = self.queue.get()
            start_time = time.time()  # Record start time
            print(f"Customer {customer.id} is in Teller{self.id}")
            time.sleep(customer.service_time)
            end_time = time.time()  # Record end time
            print(f"Customer {customer.id} leaves Teller{self.id}")
            self.gantt_data.append((customer.id, self.id, start_time, end_time))
            self.queue.task_done()
def generate_customers(num_customers, queue):
    customers = []
    for i in range(num_customers):
        service_time = random.uniform(1, 5)  # Random service time
        customer = Customer(i+1, service_time)
        customers.append(customer)
    
    # Enqueue all customers simultaneously
    for customer in customers:
        print(f"Customer{customer.id} enters the Queue with service time {customer.service_time}")
        queue.put(customer)


def main():
    num_tellers = 3
    num_customers = 10
    q = queue.PriorityQueue()  # Rename the queue variable to avoid conflict
    gantt_data = []  # List to store Gantt chart data

    # Create tellers
    tellers = [Teller(i+1, q, gantt_data) for i in range(num_tellers)]

    # Start teller threads
    for teller in tellers:
        teller.start()

    # Generate customers
    generate_customers(num_customers, q)

    # Wait for all customers to be served
    q.join()

    # Write Gantt chart data to CSV file
    with open("./SJF/sjfData.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Customer", "Teller", "Start Time", "End Time"])
        for item in gantt_data:
            writer.writerow(item)

if __name__ == "__main__":
    main()
