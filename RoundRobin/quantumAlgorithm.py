import threading
import queue
import random
import time
import csv

NUM_TELLERS = 3
MAX_SERVICE_TIME = 10
NUM_CUSTOMERS = 15
QUANTUM_TIME = 3

class Teller(threading.Thread):
    def __init__(self, teller_id, customer_queue, print_lock, writer_lock, writer):
        super().__init__()
        self.teller_id = teller_id
        self.customer_queue = customer_queue
        self.print_lock = print_lock
        self.writer_lock = writer_lock
        self.writer = writer

    def run(self):
        while True:
            try:
                customer_id, service_time, entering_time = self.customer_queue.get(timeout=1)
            except queue.Empty:
                continue

            with self.print_lock:
                print(f"Customer {customer_id} is in Teller{self.teller_id}")

            while service_time > 0:
                if service_time > QUANTUM_TIME:
                    time.sleep(QUANTUM_TIME)
                    service_time -= QUANTUM_TIME
                else:
                    time.sleep(service_time)
                    service_time = 0

                with self.writer_lock:
                    self.writer.writerow([customer_id, entering_time, time.time()])
                
                with self.print_lock:
                    print(f"Customer {customer_id} is being served by Teller{self.teller_id}. Remaining service time: {service_time}")

                if service_time > 0:
                    next_customer = self.customer_queue.get()
                    self.customer_queue.put((customer_id, service_time, entering_time))
                    customer_id, service_time, entering_time = next_customer
                    with self.print_lock:
                        print(f"Customer {customer_id} is in Teller{self.teller_id}")

            with self.writer_lock:
                self.writer.writerow([customer_id, entering_time, time.time()])
                print(f"Customer {customer_id} leaves Teller{self.teller_id}")

if __name__ == "__main__":
    customer_queue = queue.Queue()

    print_lock = threading.Lock()
    writer_lock = threading.Lock()
    
    # Open CSV file for writing
    with open("./RoundRobin/rrData.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Customer ID", "Entering Time", "Exiting Time"])
        
        # Start teller threads
        tellers = []
        for i in range(NUM_TELLERS):
            teller = Teller(i+1, customer_queue, print_lock, writer_lock, writer)
            teller.start()
            tellers.append(teller)

        # Generate customers and put them in the queue with random arrival times
        for customer_id in range(1, NUM_CUSTOMERS+1):
            service_time = random.randint(1, MAX_SERVICE_TIME)
            entering_time = time.time()
            customer_queue.put((customer_id, service_time, entering_time))
            print(f"Customer {customer_id} enters the Queue")
            time.sleep(random.uniform(0.1, 1))  # Random delay between customer arrivals
