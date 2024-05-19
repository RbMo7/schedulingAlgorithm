import csv
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def plot_gantt_chart(csv_file):
    timing_data = []

    # Read the data from the CSV file
    with open(csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            customer_id = int(row['Customer ID'])
            teller_id = int(row['Teller ID'])
            arrival_time = float(row['Arrival Time'])
            start_time = float(row['Start Time'])
            end_time = float(row['End Time'])
            timing_data.append((customer_id, teller_id, arrival_time, start_time, end_time))

    # Sort timing data based on customer ID
    timing_data.sort(key=lambda x: x[0])

    # Plotting the Gantt chart
    fig, gnt = plt.subplots(figsize=(12, 8))

    # Set the labels and limits
    min_start_time = min([start_time for _, _, _, start_time, _ in timing_data])
    max_end_time = max([end_time for _, _, _, _, end_time in timing_data])
    
    gnt.set_ylim(0, len(timing_data) + 2)
    gnt.set_xlim(0, max_end_time - min_start_time + 1)
    gnt.set_xlabel('Time (seconds)', fontsize=14)
    gnt.set_ylabel('Customers (Teller)', fontsize=14)

    # Set the y-ticks
    gnt.set_yticks([i + 1 for i in range(len(timing_data))])
    gnt.set_yticklabels([f'Customer {customer_id} (Teller {teller_id})' for customer_id, teller_id, _, _, _ in timing_data], fontsize=12)

    # Define colors for each customer
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

    # Plot the bars with colors
    for i, (customer_id, _, arrival_time, start_time, end_time) in enumerate(timing_data):
        gnt.broken_barh(
            [(start_time - min_start_time, end_time - start_time)], 
            (i + 0.5, 1), 
            facecolors=(colors[i % len(colors)])
        )

    # Add a legend
    patches = [mpatches.Patch(color=colors[i % len(colors)], label=f'Customer {customer_id}') for i, (customer_id, _, _, _, _) in enumerate(timing_data)]
    plt.legend(handles=patches, bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)

    plt.title('FCFS Scheduling Gantt Chart', fontsize=16)
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# Plot the Gantt chart from the CSV file
plot_gantt_chart('fcfsData.csv')
