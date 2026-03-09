from pathlib import Path

file_path = Path("data/raw/wpp2024/wpp2024_population_standard.csv")

with open(file_path, "r", encoding="utf-8-sig", errors="replace") as f:
    for i in range(20):
        line = f.readline()
        if not line:
            break
        print(f"{i+1}: {line.rstrip()}")
