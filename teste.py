prices = [1, 2,10, 9, 8, 9, 11, 12,3,15,3]  # your asset prices over time
peak = prices[0]
max_drawdown = 0

for p in prices:
    peak = max(peak, p)
    drawdown = (p - peak) / peak
    max_drawdown = min(max_drawdown, drawdown)

print("Max Drawdown:", max_drawdown)
