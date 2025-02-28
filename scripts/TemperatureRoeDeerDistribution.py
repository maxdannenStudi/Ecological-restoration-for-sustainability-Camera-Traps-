import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# Ensure the graph save directory exists
save_path = r"C:\Users\maxda\Uni\SUS3\WeatherAnimalData2025\graphs"
os.makedirs(save_path, exist_ok=True)

# File paths
observations_file = r"C:\Users\maxda\Uni\SUS3\WeatherAnimalData2025\rawData\filtered_observations.csv"
weather_file = r"C:\Users\maxda\Uni\SUS3\WeatherAnimalData2025\rawData\merged_weather_data.csv"
output_image_path = os.path.join(save_path, "Temperature_Capreolus_Distribution.png")

# Read files
observations_data = pd.read_csv(observations_file)
weather_data = pd.read_csv(weather_file)

# Extract date from observations
observations_data["eventStart"] = pd.to_datetime(observations_data["eventStart"], errors="coerce")
observations_data["eventDate"] = observations_data["eventStart"].dt.strftime("%Y-%m-%d")

# Format date in weather Data
weather_data["date"] = pd.to_datetime(weather_data["date"]).dt.strftime("%Y-%m-%d")

# Merge observations with weather Data on date
merged_data = pd.merge(
    observations_data,
    weather_data,
    left_on="eventDate",
    right_on="date",
    how="inner"
)

# Filter for Capreolus capreolus
capreolus_data = merged_data[merged_data["scientificName"] == "Capreolus capreolus"]

# Define temperature bins (steps of 5)
temp_bins = np.arange(-15, 41, 5)  # Ranges from -15 to 40
temp_labels = [f"{temp_bins[i]} to {temp_bins[i+1]}" for i in range(len(temp_bins)-1)]

# Add a temperature bin column
capreolus_data["temp_bin"] = pd.cut(capreolus_data["tavg"], bins=temp_bins, labels=temp_labels, right=False)
weather_data["temp_bin"] = pd.cut(weather_data["tavg"], bins=temp_bins, labels=temp_labels, right=False)

# Count actual captures per temperature bin
actual_counts = capreolus_data["temp_bin"].value_counts().sort_index()

# Count days per temperature bin
days_per_bin = weather_data["temp_bin"].value_counts().sort_index()

# Total days and total deer captures
total_days = days_per_bin.sum()
total_deer_captures = actual_counts.sum()

# Calculate expected captures per temperature bin
expected_counts = (days_per_bin / total_days) * total_deer_captures

# Create a summary DataFrame
summary = pd.DataFrame({
    "Temperature Range": temp_labels,
    "Actual Captures": actual_counts.values,
    "Expected Captures": expected_counts.values,
    "Days": days_per_bin.values
}).fillna(0)

# Add a percentage difference column
summary["Percentage Difference"] = (
    (summary["Actual Captures"] - summary["Expected Captures"]) / summary["Expected Captures"]
) * 100

# Print the summary
print(summary)

# Bar plot for actual vs expected captures
plt.figure(figsize=(12, 8))
x = np.arange(len(temp_labels))  # X positions for bars
width = 0.4  # Bar width

# Plot actual and expected captures
plt.bar(x - width/2, summary["Actual Captures"], width=width, color="skyblue", edgecolor="black", label="Actual Captures")
plt.bar(x + width/2, summary["Expected Captures"], width=width, color="orange", edgecolor="black", label="Expected Captures")

# Add numbers on top of the bars
for i in range(len(summary)):
    plt.text(x[i] - width/2, summary["Actual Captures"].iloc[i] + 1,
             int(summary["Actual Captures"].iloc[i]), ha="center", fontsize=10)
    plt.text(x[i] + width/2, summary["Expected Captures"].iloc[i] + 1,
             f"{summary['Expected Captures'].iloc[i]:.1f}", ha="center", fontsize=10)

# Customize plot
plt.title("Actual vs Expected Deer Captures by Temperature Range", fontsize=16)
plt.xlabel("Temperature Range (°C)", fontsize=12)
plt.ylabel("Number of Captures", fontsize=12)
plt.xticks(x, temp_labels, rotation=45, ha="right")
plt.legend(loc="upper right")
plt.tight_layout()

# Save the graph
plt.savefig(output_image_path, dpi=300)
print(f"Graph saved at: {output_image_path}")

# Show plot
plt.show()
