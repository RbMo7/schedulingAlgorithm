import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import date2num
from matplotlib.ticker import MultipleLocator, FixedFormatter

# Read the data from the CSV file
data = pd.read_csv("./RoundRobin/rrData.csv")

# Convert entering and exiting time columns to datetime objects
data["Entering Time"] = pd.to_datetime(data["Entering Time"], unit="s")
data["Exiting Time"] = pd.to_datetime(data["Exiting Time"], unit="s")

# Calculate the duration of each task
data["Duration"] = data["Exiting Time"] - data["Entering Time"]

# Set up the figure and axis
fig, ax = plt.subplots(figsize=(12, 8))

# Plot each task as a horizontal bar
for i, row in data.iterrows():
    ax.barh(row["Customer ID"], row["Duration"].total_seconds() / 3600, left=date2num(row["Entering Time"]),
            color="skyblue", edgecolor="black")

# Set y-axis labels and ticks
ax.set_yticks(data["Customer ID"])
ax.set_yticklabels(["Customer " + str(cid) for cid in data["Customer ID"]])
ax.invert_yaxis()  # Invert y-axis to have Customer 1 at the top

# Set x-axis labels and ticks
ax.xaxis_date()  # Set x-axis as dates
ax.set_xlabel("Time")
ax.xaxis.set_major_locator(MultipleLocator(1))  # Set major ticks every 1 hour
ax.xaxis.set_minor_locator(MultipleLocator(0.25))  # Set minor ticks every 15 minutes
ax.xaxis.set_major_formatter(FixedFormatter(["{:02d}:{:02d}".format(int(h), int(m)) for h, m in 
                                             zip(range(24), [0]*24)]))  # Format major ticks as hours:minutes

# Add grid lines
ax.grid(True, which='both', linestyle='--', linewidth=0.5)

# Add title and labels
ax.set_title("Gantt Chart for Customer Service")
ax.set_ylabel("Customer")
plt.tight_layout()

# Save the plot as an image file (optional)
plt.savefig("gantt_chart.png")

# Show the plot
plt.show()
