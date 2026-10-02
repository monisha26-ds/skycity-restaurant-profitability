
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="SkyCity Restaurant Profitability",
    page_icon="🍽️",
    layout="wide"
)

DATA_PATH = "data/SkyCity Auckland Restaurants & Bars.csv"
df = pd.read_csv(DATA_PATH)

channels = {
    "In-Store": ("InStoreRevenue", "InStoreOrders", "InStoreNetProfit"),
    "Uber Eats": ("UberEatsRevenue", "UberEatsOrders", "UberEatsNetProfit"),
    "DoorDash": ("DoorDashRevenue", "DoorDashOrders", "DoorDashNetProfit"),
    "Self Delivery": ("SelfDeliveryRevenue", "SelfDeliveryOrders", "SelfDeliveryNetProfit"),
}

# Derived values
df["TotalRevenue"] = df[[x[0] for x in channels.values()]].sum(axis=1)
df["TotalProfit"] = df[[x[2] for x in channels.values()]].sum(axis=1)
df["TotalOrders"] = df[[x[1] for x in channels.values()]].sum(axis=1)
df["OverallMargin"] = np.where(df.TotalRevenue != 0, df.TotalProfit / df.TotalRevenue, 0)
df["AggregatorCommissionCost"] = (
    df.UberEatsRevenue * df.CommissionRate +
    df.DoorDashRevenue * df.CommissionRate
)
df["SelfDeliveryCost"] = df.SelfDeliveryOrders * df.DeliveryCostPerOrder

st.title("🍽️ Cost Structure & Channel-Wise Profitability")
st.caption("SkyCity Auckland Restaurants & Bars | Multi-channel restaurant profitability analysis")

# Sidebar filters
st.sidebar.header("Filters")
cuisines = st.sidebar.multiselect(
    "Cuisine Type", sorted(df.CuisineType.unique()), default=sorted(df.CuisineType.unique())
)
segments = st.sidebar.multiselect(
    "Business Segment", sorted(df.Segment.unique()), default=sorted(df.Segment.unique())
)
subregions = st.sidebar.multiselect(
    "Subregion", sorted(df.Subregion.unique()), default=sorted(df.Subregion.unique())
)

filtered = df[
    df.CuisineType.isin(cuisines) &
    df.Segment.isin(segments) &
    df.Subregion.isin(subregions)
].copy()

# What-if controls
st.sidebar.header("What-if Analysis")
commission_slider = st.sidebar.slider(
    "Commission Rate (%)", 0.0, 50.0, float(filtered.CommissionRate.mean() * 100), 1.0
)
delivery_slider = st.sidebar.slider(
    "Self-Delivery Cost / Order ($)", 0.0, 10.0, float(filtered.DeliveryCostPerOrder.mean()), 0.25
)

# KPIs
total_revenue = filtered.TotalRevenue.sum()
total_profit = filtered.TotalProfit.sum()
total_orders = filtered.TotalOrders.sum()
margin = total_profit / total_revenue if total_revenue else 0
profit_per_order = total_profit / total_orders if total_orders else 0

a, b, c, d = st.columns(4)
a.metric("Total Revenue", f"${total_revenue:,.0f}")
b.metric("Total Net Profit", f"${total_profit:,.0f}")
c.metric("Overall Margin", f"{margin*100:.1f}%")
d.metric("Profit / Order", f"${profit_per_order:.2f}")

st.divider()

# Channel summary
rows = []
for channel, (rev, orders, profit) in channels.items():
    revenue = filtered[rev].sum()
    order_count = filtered[orders].sum()
    net_profit = filtered[profit].sum()
    rows.append({
        "Channel": channel,
        "Orders": order_count,
        "Revenue": revenue,
        "Net Profit": net_profit,
        "Profit per Order": net_profit / order_count if order_count else 0,
        "Margin %": (net_profit / revenue * 100) if revenue else 0,
    })
summary = pd.DataFrame(rows)

st.subheader("Channel-wise Profitability")
col1, col2 = st.columns(2)

with col1:
    fig = px.bar(summary, x="Channel", y="Net Profit", title="Net Profit by Channel")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.bar(summary, x="Channel", y="Margin %", title="Channel Margin (%)")
    st.plotly_chart(fig, use_container_width=True)

st.dataframe(
    summary.style.format({
        "Orders": "{:,.0f}",
        "Revenue": "${:,.2f}",
        "Net Profit": "${:,.2f}",
        "Profit per Order": "${:,.2f}",
        "Margin %": "{:.2f}%"
    }),
    use_container_width=True,
    hide_index=True
)

# Cost breakdown
st.subheader("Cost Component Breakdown")
cost_data = pd.DataFrame({
    "Component": ["COGS", "OPEX", "Aggregator Commission", "Self-Delivery Cost"],
    "Cost": [
        (filtered.TotalRevenue * filtered.COGSRate).sum(),
        (filtered.TotalRevenue * filtered.OPEXRate).sum(),
        filtered.AggregatorCommissionCost.sum(),
        filtered.SelfDeliveryCost.sum(),
    ]
})
fig = px.bar(cost_data, x="Component", y="Cost", title="Major Cost Components")
st.plotly_chart(fig, use_container_width=True)

# Cuisine heatmap
st.subheader("Cuisine & Segment Profitability")
grouped = filtered.groupby(["CuisineType", "Segment"], as_index=False).agg(
    Revenue=("TotalRevenue", "sum"),
    Profit=("TotalProfit", "sum")
)
grouped["Margin %"] = np.where(grouped.Revenue != 0, grouped.Profit / grouped.Revenue * 100, 0)
pivot = grouped.pivot(index="CuisineType", columns="Segment", values="Margin %")
fig = px.imshow(
    pivot,
    text_auto=".1f",
    aspect="auto",
    title="Average Margin by Cuisine and Segment (%)"
)
st.plotly_chart(fig, use_container_width=True)

# What-if calculations
st.subheader("🎚️ What-if Profitability Analysis")
st.write("Adjust commission and self-delivery cost to see the estimated effect on channel profits.")

whatif = []
for channel, (rev, orders, profit) in channels.items():
    revenue = filtered[rev].sum()
    order_count = filtered[orders].sum()
    if channel == "Uber Eats":
        new_profit = revenue * (1 - filtered.COGSRate.mean() - filtered.OPEXRate.mean() - commission_slider/100)
    elif channel == "DoorDash":
        new_profit = revenue * (1 - filtered.COGSRate.mean() - filtered.OPEXRate.mean() - commission_slider/100)
    elif channel == "Self Delivery":
        new_profit = (
            revenue * (1 - filtered.COGSRate.mean() - filtered.OPEXRate.mean())
            - order_count * delivery_slider
        )
    else:
        new_profit = revenue * (1 - filtered.COGSRate.mean() - filtered.OPEXRate.mean())
    whatif.append({"Channel": channel, "Estimated Profit": new_profit})

whatif_df = pd.DataFrame(whatif)
fig = px.bar(whatif_df, x="Channel", y="Estimated Profit", title="Estimated Profit Under Selected Assumptions")
st.plotly_chart(fig, use_container_width=True)

# Loss flags
st.subheader("⚠️ Loss-Prone Channel Records")
loss_counts = pd.DataFrame({
    "Channel": list(channels.keys()),
    "Loss-making Records": [
        int((filtered.InStoreNetProfit < 0).sum()),
        int((filtered.UberEatsNetProfit < 0).sum()),
        int((filtered.DoorDashNetProfit < 0).sum()),
        int((filtered.SelfDeliveryNetProfit < 0).sum()),
    ]
})
fig = px.bar(loss_counts, x="Channel", y="Loss-making Records", title="Loss-Making Restaurant-Month Records")
st.plotly_chart(fig, use_container_width=True)

st.caption("Note: Profitability is based on the supplied restaurant-month dataset. What-if values are scenario estimates, not forecasts of actual future financial results.")
