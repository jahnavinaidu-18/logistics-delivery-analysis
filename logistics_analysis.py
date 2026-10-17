
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Project folders
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"

# Create output folder if it does not exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load dataset
file_path = DATA_DIR / "logistics_data.csv"

if not file_path.exists():
    raise FileNotFoundError(
        f"Dataset not found: {file_path}\n"
        "Place logistics_data.csv inside the data folder."
    )

df = pd.read_csv(file_path)

print("=" * 45)
print("LOGISTICS DELIVERY PERFORMANCE ANALYSIS")
print("=" * 45)

# 1. Explore dataset
print("\nFirst five records:")
print(df.head())

print("\nDataset information:")
df.info()

print("\nMissing values:")
print(df.isnull().sum())

# 2. Remove duplicate records
df = df.drop_duplicates().copy()

# 3. Validate required columns
required_columns = [
    "promised_delivery_date",
    "actual_delivery_date"
]

missing_columns = [
    col for col in required_columns if col not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}. "
        "Update the column names to match your CSV."
    )

# 4. Convert dates
for col in required_columns:
    df[col] = pd.to_datetime(df[col], errors="coerce")

# Keep records with both delivery dates
df = df.dropna(subset=required_columns).copy()

if df.empty:
    raise ValueError("No valid delivery records found.")

# 5. Calculate delivery performance
df["delay_days"] = (
    df["actual_delivery_date"] -
    df["promised_delivery_date"]
).dt.total_seconds() / 86400

df["on_time"] = df["delay_days"] <= 0

total = len(df)
on_time = int(df["on_time"].sum())
late = total - on_time

on_time_rate = on_time / total * 100
late_rate = late / total * 100

# 6. Display KPIs
print("\n--- KEY PERFORMANCE INDICATORS ---")
print(f"Total deliveries: {total}")
print(f"On-time deliveries: {on_time}")
print(f"Late deliveries: {late}")
print(f"On-time delivery rate: {on_time_rate:.2f}%")
print(f"Late delivery rate: {late_rate:.2f}%")
print(
    f"Average delay relative to promised date: "
    f"{df['delay_days'].mean():.2f} days"
)

# 7. Calculate shipping cost KPI if available
if "shipping_cost" in df.columns:
    df["shipping_cost"] = pd.to_numeric(
        df["shipping_cost"], errors="coerce"
    )

    print(
        "Average shipping cost per delivery: "
        f"{df['shipping_cost'].mean():.2f}"
    )

# 8. Plot delivery performance
plt.figure(figsize=(7, 5))
plt.bar(
    ["On time", "Late"],
    [on_time, late]
)
plt.title("Logistics Delivery Performance")
plt.xlabel("Delivery status")
plt.ylabel("Number of deliveries")
plt.tight_layout()

# Save chart
chart_path = OUTPUT_DIR / "delivery_performance.png"
plt.savefig(chart_path)
plt.show()

# 9. Save cleaned dataset
cleaned_path = OUTPUT_DIR / "cleaned_logistics_data.csv"
df.to_csv(cleaned_path, index=False)

print("\nAnalysis completed successfully!")
print(f"Cleaned dataset: {cleaned_path}")
print(f"Performance chart: {chart_path}")
