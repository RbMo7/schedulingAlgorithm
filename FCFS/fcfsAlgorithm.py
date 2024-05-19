import threading
import queue
import random
import time
import csv

class Customer:
    def __init__(self, customer_id, arrival_time):
        self.customer_id = customer_id
        self.arrival_time = arrival_time
        self.start_time = None
        self.end_time = None
        self.teller_id = None  # New attribute to store the teller ID

class Teller(threading.Thread):
    def __init__(self, teller_id, customer_queue, data_lock, timing_data):
        threading.Thread.__init__(self)
        self.teller_id = teller_id
        self.customer_queue = customer_queue
        self.data_lock = data_lock
        self.timing_data = timing_data
        self.daemon = True
        self.start()

    def run(self):
        while True:
            customer = self.customer_queue.get()
            if customer is None:
                break
            with self.data_lock:
                customer.start_time = time.time()
                customer.teller_id = self.teller_id  # Assign teller ID to the customer
            print(f"Customer {customer.customer_id} is in Teller{self.teller_id}")
            service_time = random.randint(1, 5)
            time.sleep(service_time)  # Simulate service time
            with self.data_lock:
                customer.end_time = time.time()
                self.timing_data.append(customer)
            print(f"Customer {customer.customer_id} leaves Teller{self.teller_id}")
            self.customer_queue.task_done()

def main():
    num_tellers = 3
    customer_queue = queue.Queue(maxsize=10)
    data_lock = threading.Lock()
    timing_data = []

    tellers = [Teller(i, customer_queue, data_lock, timing_data) for i in range(1, num_tellers + 1)]

    customer_id = 1
    try:
        while customer_id <= 15:  # Limit number of customers for demonstration
            if not customer_queue.full():
                arrival_time = time.time()
                customer = Customer(customer_id, arrival_time)
                print(f"Customer {customer.customer_id} enters the Queue")
                customer_queue.put(customer)
                customer_id += 1
                time.sleep(random.uniform(0.5, 1.5))  # Random arrival time
            else:
                print("Queue is FULL.")
    except KeyboardInterrupt:
        pass
    finally:
        # Signal the tellers to stop
        for teller in tellers:
            customer_queue.put(None)

        # Ensure all threads have finished
        for teller in tellers:
            teller.join()

        # Write the data to a CSV file
        write_to_csv(timing_data)

def write_to_csv(timing_data):
    with open('./FCFS/fcfsData.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Customer ID', 'Arrival Time', 'Start Time', 'End Time', 'Teller ID'])  # Include 'Teller ID' in the header
        for customer in timing_data:
            writer.writerow([customer.customer_id, customer.arrival_time, customer.start_time, customer.end_time, customer.teller_id])  # Write teller ID along with other data

if __name__ == "__main__":
    main()
