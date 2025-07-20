import subprocess

# strategy is whenever stockA has a certain percentage change in a certain time span, we should buy stockB and sell after a certain time span
stockA = "AAPL"  # Example stocks
stockA_percent_change = 5
stockA_time_span = 3

stockB = "MSFT"
stockB_time_span = 10

for stock in [stockA, stockB]:
    # Write the current stock symbol to a file
    with open(f"stock.txt", "w") as f:
        f.write(stock)

    # Run the data pull script for the current stock
    subprocess.run(["python", "pull_data.py"])

with open(f"stock.txt", "w") as f:
        f.write(f"{stockA} {stockB}")
        
with open(f"perameters.txt", "w") as f:
        f.write(f"{stockA_percent_change} {stockA_time_span} {stockB_time_span}")
