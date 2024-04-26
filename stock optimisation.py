import cvxpy as cp
import pandas as pd

# Load data
df = pd.read_excel("Investments.xlsx")

# Input for initial funds and minimum number of stocks
initial_funds = float(input("Enter initial investment funds: "))
min_stocks = int(input("Enter the minimum number of stocks to purchase: "))
max_lots = int(input("Enter the maximum number of lots for each stock: "))

# Variables
n = len(df)
x = cp.Variable(n, integer=True)  # Number of lots to buy for each stock

# Objective: Maximize dividend returns
returns = df["Estimated Dividend Yield (%)"].values * df["Price per Lot (MYR)"].values
objective = cp.Maximize(cp.sum(cp.multiply(x, returns)))

# Constraints
costs = df["Price per Lot (MYR)"].values * 1.1  # Including 10% tax
budget_constraint = cp.sum(cp.multiply(x, costs)) <= initial_funds
max_lots_constraints = [x[i] <= max_lots for i in range(n)]  # Max lots constraint

# Minimum stock constraint
# A binary variable for each stock that is 1 if the stock is part of the portfolio
binary_vars = cp.Variable(n, boolean=True)
min_stock_constraint = cp.sum(binary_vars) >= min_stocks
linking_constraints = [
    x[i] <= binary_vars[i] * max_lots
    for i in range(n)  # Link lots with binary variable
]
min_lots_constraints = [x[i] >= binary_vars[i] * 1 for i in range(n)]

# Problem definition
problem = cp.Problem(
    objective,
    [budget_constraint, min_stock_constraint]
    + linking_constraints
    + min_lots_constraints,
)

# Solve the problem
problem.solve()

# Output results
print("\nOptimal Portfolio:")
total_return = 0
for i, stock_name in enumerate(df["Stock Name"]):
    lots = x.value[i]
    if lots > 0:
        price_per_lot = df.loc[i, "Price per Lot (MYR)"]
        yield_percent = df.loc[i, "Estimated Dividend Yield (%)"]
        cost = lots * price_per_lot * 1.1
        annual_return = lots * price_per_lot * yield_percent
        total_return += annual_return

        print(f"{stock_name}: Buy {lots:.2f} lots")
        print(f"  Estimated Cost: ${cost:.2f}")
        print(f"  Estimated Annual Return: ${annual_return:.2f}")

print(f"Estimated Total Annual Return: ${total_return:.2f}")
