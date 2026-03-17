import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(
    page_title="Roth Conversion Impact Calculator",
    page_icon="📈",
    layout="wide"
)

# -----------------------------
# Helpers
# -----------------------------
def currency(x):
    return f"${x:,.2f}"

def percent(x):
    return f"{x:.1f}%"

def future_value(pv, rate, years):
    return pv * ((1 + rate) ** years)

# -----------------------------
# Title
# -----------------------------
st.title("Roth Conversion Impact Calculator")
st.caption("Educational estimator for analyzing the potential tax impact of a Roth conversion.")

# -----------------------------
# Sidebar Inputs
# -----------------------------
st.sidebar.header("Client Inputs")

age = st.sidebar.number_input("Current age", min_value=18, max_value=100, value=45, step=1)

filing_status = st.sidebar.selectbox(
    "Filing status",
    ["Single", "Married Filing Jointly"]
)

current_taxable_income = st.sidebar.number_input(
    "Current taxable income ($)",
    min_value=0.0,
    value=100000.0,
    step=1000.0
)

conversion_amount = st.sidebar.number_input(
    "Amount to convert to Roth ($)",
    min_value=0.0,
    value=20000.0,
    step=1000.0
)

current_federal_rate = st.sidebar.slider(
    "Current federal marginal tax rate (%)",
    min_value=0.0,
    max_value=50.0,
    value=24.0,
    step=1.0
)

state_tax_rate = st.sidebar.slider(
    "State tax rate (%)",
    min_value=0.0,
    max_value=15.0,
    value=5.0,
    step=0.5
)

years_to_retirement = st.sidebar.number_input(
    "Years until retirement",
    min_value=1,
    max_value=50,
    value=20,
    step=1
)

annual_growth_rate = st.sidebar.slider(
    "Expected annual growth rate (%)",
    min_value=0.0,
    max_value=15.0,
    value=7.0,
    step=0.5
)

future_effective_tax_rate = st.sidebar.slider(
    "Estimated future effective tax rate on Traditional withdrawals (%)",
    min_value=0.0,
    max_value=50.0,
    value=22.0,
    step=1.0
)

# -----------------------------
# Calculations
# -----------------------------
fed_rate = current_federal_rate / 100
state_rate = state_tax_rate / 100
growth_rate = annual_growth_rate / 100
future_tax_rate = future_effective_tax_rate / 100

new_taxable_income = current_taxable_income + conversion_amount

federal_tax_due = conversion_amount * fed_rate
state_tax_due = conversion_amount * state_rate
total_tax_due = federal_tax_due + state_tax_due

roth_future_value = future_value(conversion_amount, growth_rate, years_to_retirement)
traditional_future_value_pre_tax = future_value(conversion_amount, growth_rate, years_to_retirement)
traditional_future_value_after_tax = traditional_future_value_pre_tax * (1 - future_tax_rate)

net_difference = roth_future_value - traditional_future_value_after_tax

# -----------------------------
# Top Summary
# -----------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Federal Tax Due", currency(federal_tax_due))
col2.metric("State Tax Due", currency(state_tax_due))
col3.metric("Total Tax Due", currency(total_tax_due))
col4.metric("New Taxable Income", currency(new_taxable_income))

st.divider()

# -----------------------------
# Comparison Section
# -----------------------------
left, right = st.columns([1.2, 1])

with left:
    st.subheader("Scenario Comparison")

    comparison_df = pd.DataFrame({
        "Scenario": [
            "Convert to Roth Today",
            "Keep in Traditional (After Estimated Future Tax)"
        ],
        "Projected Value": [
            roth_future_value,
            traditional_future_value_after_tax
        ]
    })

    st.dataframe(
        comparison_df.style.format({"Projected Value": "${:,.2f}"}),
        use_container_width=True
    )

    if net_difference > 0:
        st.success(
            f"Converting today produces an estimated advantage of {currency(net_difference)} "
            f"by retirement, based on the assumptions entered."
        )
    elif net_difference < 0:
        st.warning(
            f"Keeping the money in Traditional may produce an estimated advantage of "
            f"{currency(abs(net_difference))} by retirement, based on the assumptions entered."
        )
    else:
        st.info("Under these assumptions, both scenarios produce the same estimated result.")

with right:
    st.subheader("Key Assumptions")
    st.write(f"**Age:** {age}")
    st.write(f"**Filing status:** {filing_status}")
    st.write(f"**Current taxable income:** {currency(current_taxable_income)}")
    st.write(f"**Conversion amount:** {currency(conversion_amount)}")
    st.write(f"**Current federal marginal rate:** {percent(current_federal_rate)}")
    st.write(f"**State tax rate:** {percent(state_tax_rate)}")
    st.write(f"**Years to retirement:** {years_to_retirement}")
    st.write(f"**Annual growth rate:** {percent(annual_growth_rate)}")
    st.write(f"**Future effective tax rate on Traditional withdrawals:** {percent(future_effective_tax_rate)}")

st.divider()

# -----------------------------
# Charts
# -----------------------------
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("Taxes Due Today")
    fig_tax = go.Figure()
    fig_tax.add_bar(
        x=["Federal Tax", "State Tax", "Total Tax"],
        y=[federal_tax_due, state_tax_due, total_tax_due]
    )
    fig_tax.update_layout(
        xaxis_title="Tax Type",
        yaxis_title="Amount ($)",
        height=420
    )
    st.plotly_chart(fig_tax, use_container_width=True)

with chart_col2:
    st.subheader("Projected Retirement Value")
    fig_compare = go.Figure()
    fig_compare.add_bar(
        x=["Roth Conversion", "Traditional After Tax"],
        y=[roth_future_value, traditional_future_value_after_tax]
    )
    fig_compare.update_layout(
        xaxis_title="Scenario",
        yaxis_title="Projected Value ($)",
        height=420
    )
    st.plotly_chart(fig_compare, use_container_width=True)

st.divider()

# -----------------------------
# Growth Projection
# -----------------------------
st.subheader("Growth Projection Over Time")

years = list(range(years_to_retirement + 1))
roth_series = [future_value(conversion_amount, growth_rate, y) for y in years]
traditional_pre_tax_series = [future_value(conversion_amount, growth_rate, y) for y in years]
traditional_after_tax_series = [v * (1 - future_tax_rate) for v in traditional_pre_tax_series]

fig_growth = go.Figure()
fig_growth.add_scatter(x=years, y=roth_series, mode="lines", name="Roth Conversion")
fig_growth.add_scatter(x=years, y=traditional_after_tax_series, mode="lines", name="Traditional After Tax")
fig_growth.update_layout(
    xaxis_title="Years",
    yaxis_title="Projected Value ($)",
    height=500
)
st.plotly_chart(fig_growth, use_container_width=True)

# -----------------------------
# Explanation
# -----------------------------
st.subheader("How to Read These Results")
st.write(
    "This tool estimates the tax cost of converting part of a Traditional retirement account "
    "to a Roth account today. In exchange for paying taxes now, the model assumes the converted "
    "Roth amount can grow tax-free going forward. The Traditional scenario estimates a future "
    "after-tax value by applying an assumed future tax rate at withdrawal."
)

st.info(
    "Important: This is a simplified educational estimate and not personalized tax, legal, or investment advice. "
    "Actual outcomes depend on tax law, account type, withdrawal timing, investment performance, and individual circumstances."
)
