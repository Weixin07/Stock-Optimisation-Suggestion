import cvxpy as cp
import pandas as pd

def run_optimization(df, initial_funds, min_stocks, max_lots):
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
    binary_vars = cp.Variable(n, boolean=True)  # A binary variable for each stock
    min_stock_constraint = cp.sum(binary_vars) >= min_stocks
    linking_constraints = [x[i] <= binary_vars[i] * max_lots for i in range(n)]  # Link lots with binary variable
    min_lots_constraints = [x[i] >= binary_vars[i] * 1 for i in range(n)]
    
    # Problem definition
    problem = cp.Problem(
        objective,
        [budget_constraint, min_stock_constraint] + linking_constraints + min_lots_constraints + max_lots_constraints,
    )
    
    # Solve the problem
    problem.solve()
    
    # Collect results
    results = {
        "Stock Name": [],
        "Lots": [],
        "Estimated Cost": [],
        "Estimated Annual Return": []
    }
    total_return = 0
    total_cost = 0
    for i, stock_name in enumerate(df["Stock Name"]):
        lots = x.value[i]
        if lots > 0:
            price_per_lot = df.loc[i, "Price per Lot (MYR)"]
            yield_percent = df.loc[i, "Estimated Dividend Yield (%)"]
            cost = lots * price_per_lot * 1.01
            annual_return = lots * price_per_lot * yield_percent
            total_return += annual_return
            total_cost += cost

            results["Stock Name"].append(stock_name)
            results["Lots"].append(f"{lots:.2f}")
            results["Estimated Cost"].append(f"${cost:.2f}")
            results["Estimated Annual Return"].append(f"${annual_return:.2f}")

    results["Total Annual Return"] = f"${total_return:.2f}"
    results["Total Estimated Cost"] = f"${total_cost:.2f}"
    results["Leftover Funds"] = f"${initial_funds - total_cost:.2f}"
    return results

# Input for initial funds and minimum number of stocks
initial_funds = float(input("Enter initial investment funds: "))
min_stocks = int(input("Enter the minimum number of stocks to purchase: "))
max_lots = int(input("Enter the maximum number of lots for each stock: "))

# Data files
files = ["Stocks with Owned.xlsx", "Stocks without Owned.xlsx"]
results = []

for file in files:
    df = pd.read_excel(file)
    result = run_optimization(df, initial_funds, min_stocks, max_lots)
    results.append(result)

# Display results in a tabular format
for result, file in zip(results, files):
    print(f"\nResults for {file}:")
    print("Stock Name | Lots | Estimated Cost | Estimated Annual Return")
    for i in range(len(result["Stock Name"])):
        print(f"{result['Stock Name'][i]} | {result['Lots'][i]} | {result['Estimated Cost'][i]} | {result['Estimated Annual Return'][i]}")
    print(f"Total Estimated Annual Return: {result['Total Annual Return']}")
    print(f"Total Estimated Cost: {result['Total Estimated Cost']}")
    print(f"Leftover Funds: {result['Leftover Funds']}")