
import pandas as pd
import numpy as np

DATA_PATH = "data/SkyCity Auckland Restaurants & Bars.csv"

df = pd.read_csv(DATA_PATH)

# Basic derived fields
channels = {
    "In-Store": ("InStoreRevenue", "InStoreOrders", "InStoreNetProfit"),
    "Uber Eats": ("UberEatsRevenue", "UberEatsOrders", "UberEatsNetProfit"),
    "DoorDash": ("DoorDashRevenue", "DoorDashOrders", "DoorDashNetProfit"),
    "Self Delivery": ("SelfDeliveryRevenue", "SelfDeliveryOrders", "SelfDeliveryNetProfit"),
}

df["TotalRevenue"] = df[[v[0] for v in channels.values()]].sum(axis=1)
df["TotalProfit"] = df[[v[2] for v in channels.values()]].sum(axis=1)
df["TotalOrders"] = df[[v[1] for v in channels.values()]].sum(axis=1)
df["OverallMargin"] = np.where(df["TotalRevenue"] != 0, df["TotalProfit"] / df["TotalRevenue"], 0)

# Validate supplied profit formulas
df["Calc_InStoreProfit"] = df.InStoreRevenue * (1 - df.COGSRate - df.OPEXRate)
df["Calc_UberEatsProfit"] = df.UberEatsRevenue * (1 - df.COGSRate - df.OPEXRate - df.CommissionRate)
df["Calc_DoorDashProfit"] = df.DoorDashRevenue * (1 - df.COGSRate - df.OPEXRate - df.CommissionRate)
df["Calc_SelfDeliveryProfit"] = (
    df.SelfDeliveryRevenue * (1 - df.COGSRate - df.OPEXRate)
    - df.SelfDeliveryOrders * df.DeliveryCostPerOrder
)

# KPI helpers
def channel_summary(data):
    rows = []
    for channel, (rev, orders, profit) in channels.items():
        revenue = data[rev].sum()
        order_count = data[orders].sum()
        net_profit = data[profit].sum()
        margin = net_profit / revenue if revenue else 0
        profit_per_order = net_profit / order_count if order_count else 0
        rows.append({
            "Channel": channel,
            "Orders": order_count,
            "Revenue": revenue,
            "Net Profit": net_profit,
            "Profit per Order": profit_per_order,
            "Margin": margin,
        })
    return pd.DataFrame(rows)

summary = channel_summary(df)

# Commission and delivery KPIs
df["UberCommissionCost"] = df.UberEatsRevenue * df.CommissionRate
df["DoorDashCommissionCost"] = df.DoorDashRevenue * df.CommissionRate
df["AggregatorCommissionCost"] = df.UberCommissionCost + df.DoorDashCommissionCost
df["SelfDeliveryCost"] = df.SelfDeliveryOrders * df.DeliveryCostPerOrder

# Commission Drag Index = percentage-point margin loss caused by commission.
df["UberCommissionDragPct"] = df.CommissionRate * 100
df["DoorDashCommissionDragPct"] = df.CommissionRate * 100

# Self-delivery ROI = profit / delivery logistics cost.
df["SelfDeliveryROI"] = np.where(
    df["SelfDeliveryCost"] > 0,
    df["SelfDeliveryNetProfit"] / df["SelfDeliveryCost"],
    np.nan,
)

# Profit volatility score = standard deviation of restaurant-level overall margin,
# expressed in percentage points. Higher = more variable.
profit_volatility_score = df["OverallMargin"].std() * 100

print("Dataset shape:", df.shape)
print("\nMissing values:\n", df.isna().sum().sum())
print("\nChannel summary:\n", summary.to_string(index=False))
print("\nTotal revenue: $", round(df.TotalRevenue.sum(), 2))
print("Total profit: $", round(df.TotalProfit.sum(), 2))
print("Overall margin: ", round(df.TotalProfit.sum()/df.TotalRevenue.sum()*100, 2), "%")
print("Average profit volatility score:", round(profit_volatility_score, 2), "percentage points")

print("\nLoss-making restaurant-month records:")
for c in ["InStoreNetProfit","UberEatsNetProfit","DoorDashNetProfit","SelfDeliveryNetProfit"]:
    print(c, int((df[c] < 0).sum()))

# Export useful files
summary.to_csv("channel_summary.csv", index=False)
df.to_csv("processed_restaurant_data.csv", index=False)
