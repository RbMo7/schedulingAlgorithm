import random
import csv

class Customer:
    def __init__(self, customer_id, arrival_time):
        self.customer_id = customer_id
        self.arrival_time = arrival_time
        self.service_time = random.uniform(1, 5)  # Random service time between 1 and 5 seconds
        self.start_time = None
        self.end_time = None

def generate_customers(num_customers):
    customers = []
    for i in range(1, num_customers + 1):
        arrival_time = random.uniform(0, 20)  # Random arrival time between 0 and 20 seconds
        customers.append(Customer(i, arrival_time))
    return customers

def fcfs(customers):
    current_time = 0
    total_service_time = 0

    for customer in customers:
        if customer.arrival_time > current_time:
            current_time = customer.arrival_time
        customer.start_time = current_time
        customer.end_time = current_time + customer.service_time
        total_service_time += customer.service_time
        current_time = customer.end_time

    return total_service_time

def main():
    num_customers = 15  # Limit to 15 customers for now
    customers = generate_customers(num_customers)

    total_service_time = fcfs(customers)

    print("Customer ID\tArrival Time\tService Time\tStart Time\tEnd Time")
    for customer in customers:
        print(f"{customer.customer_id}\t\t{customer.arrival_time:.2f}\t\t{customer.service_time:.2f}\t\t{customer.start_time:.2f}\t\t{customer.end_time:.2f}")

    print(f"\nTotal service time: {total_service_time:.2f} seconds")

    # Write the customer data to a CSV file
    with open('fcfsData.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Customer ID', 'Arrival Time', 'Service Time', 'Start Time', 'End Time'])
        for customer in customers:
            writer.writerow([customer.customer_id, customer.arrival_time, customer.service_time, customer.start_time, customer.end_time])

if __name__ == "__main__":
    main()
