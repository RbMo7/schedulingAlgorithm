import threading
import queue
import random
import time
import csv
import matplotlib.pyplot as plt

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
        avg_turnaround_time, avg_waiting_time, avg_response_time = write_to_csv(timing_data)

        # Generate the graph
        generate_graph(avg_turnaround_time, avg_waiting_time, avg_response_time)

def write_to_csv(timing_data):
    total_turnaround_time = 0
    total_waiting_time = 0
    total_response_time = 0
    num_customers = len(timing_data)

    with open('./FCFS/fcfsData.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Customer ID', 'Arrival Time', 'Start Time', 'End Time', 'Teller ID', 'Turnaround Time', 'Waiting Time', 'Response Time'])  # Include 'Teller ID' in the header
        for customer in timing_data:
            turnaround_time = customer.end_time - customer.arrival_time
            waiting_time = customer.start_time - customer.arrival_time
            response_time = customer.start_time - customer.arrival_time
            
            total_turnaround_time += turnaround_time
            total_waiting_time += waiting_time
            total_response_time += response_time
            
            writer.writerow([customer.customer_id, customer.arrival_time, customer.start_time, customer.end_time, customer.teller_id, turnaround_time, waiting_time, response_time])  # Write teller ID along with other data

    avg_turnaround_time = total_turnaround_time / num_customers
    avg_waiting_time = total_waiting_time / num_customers
    avg_response_time = total_response_time / num_customers

    print(f"Average Turnaround Time: {avg_turnaround_time:.2f} seconds")
    print(f"Average Waiting Time: {avg_waiting_time:.2f} seconds")
    print(f"Average Response Time: {avg_response_time:.2f} seconds")

    return avg_turnaround_time, avg_waiting_time, avg_response_time

def generate_graph(avg_turnaround_time, avg_waiting_time, avg_response_time):
    labels = ['Turnaround Time', 'Waiting Time', 'Response Time']
    values = [avg_turnaround_time, avg_waiting_time, avg_response_time]

    plt.figure(figsize=(8, 6))
    plt.bar(labels, values, color=['blue', 'orange', 'green'])
    plt.xlabel('Metrics')
    plt.ylabel('Time (seconds)')
    plt.title('Average Turnaround Time, Waiting Time, and Response Time')
    plt.show()

if __name__ == "__main__":
    main()
