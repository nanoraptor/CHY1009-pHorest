import joblib
import pandas as pd
import time
import random
import os

# ANSI Colors for a cool terminal look
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"

# Load model
try:
    model = joblib.load("soil_model.pkl")
except:
    print(f"{RED}Error: soil_model.pkl not found!{RESET}")
    exit()

os.system("clear")
print(f"{BOLD}--- AI SUSTAINABILITY: SOIL CHEMISTRY MONITOR ---{RESET}")

while True:
    # Simulated values
    ph = round(random.uniform(4.5, 8.5), 2)
    tds = random.randint(300, 800)

    # Matching your CSV columns exactly
    cols = [
        "Nitrogen",
        "phosphorus",
        "potassium",
        "temperature",
        "humidity",
        "ph",
        "rainfall",
    ]
    # Using TDS/3 as a proxy for N,P,K
    data = pd.DataFrame(
        [[tds / 3, tds / 3, tds / 3, 28.0, 60.0, ph, 100.0]], columns=cols
    )

    prediction = model.predict(data)[0]

    print(f"Sensors -> pH: {ph} | TDS: {tds} ppm")
    print(f"AI Result -> {GREEN}{BOLD}{prediction.upper()}{RESET}")

    # Chemistry EVS Logic
    if ph < 5.5:
        print(f"{RED}STATUS: Acidic. Action: Apply CaCO3 (Neutralization).{RESET}")
    elif ph > 7.5:
        print(f"{YELLOW}STATUS: Alkaline. Action: Apply Organic Matter.{RESET}")
    else:
        print("STATUS: Chemical Equilibrium maintained.")

    print("-" * 40)
    time.sleep(2)
