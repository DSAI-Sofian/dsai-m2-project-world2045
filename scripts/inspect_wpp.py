from pathlib import Path

root = Path("data")

print("Searching for WPP CSV files...\n")

for p in root.rglob("*wpp*.csv"):
    print(p)
