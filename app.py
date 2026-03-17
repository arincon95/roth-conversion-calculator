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
# Styling
# -----------------------------
st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1280px;
    }

    .hero-box {
        padding: 1.4rem 1.6rem;
        border: 1px solid rgba(128, 128, 128, 0.22);
        border-radius: 18px;
        background: linear-gradient(135deg, rgba(59,130,246,0.10), rgba(16,185,129,0.08));
        margin-bottom: 1rem;
    }

    .hero-title {
        font-size: 2.4rem;
        font-weight: 800;
        line-height: 1.1;
        margin-bottom: 0.35rem;
    }

    .hero-subtitle {
        font-size: 1.02rem;
        opacity: 0.9;
        margin-bottom: 0;
    }

    .section-title {
        font-size: 1.35rem;
        font-weight: 700;
        margin-bottom: 0.4rem;
    }

    .assumption-box {
        padding: 1rem 1.1rem;
        border: 1px solid rgba(128, 128, 128, 0.22);
        border-radius: 16px;
        background: rgba(127,127,127,0.06);
    }

    .mini-note {
        padding: 1rem 1.1rem;
        border-left: 4px solid #22c55e;
        border-radius: 12px;
        background: rgba(34,197,94,0.08);
        margin-top: 0.75rem;
    }

    .disclaimer-box {
        padding: 1rem 1.1rem;
        border: 1px solid rgba(128, 128, 128, 0.22);
        border-radius: 14px;
        background: rgba(127,127,127,0.05);
        font-size: 0.95rem;
        opacity: 0.95;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Sidebar Inputs
# -----------------------------
st.sidebar.header("Planning Inputs")
st.sidebar.caption("Adjust assumptions to estimate tax due today and compare long-term after-tax outcomes.")

age = st.sidebar.number_input(
    "Current age",
    min_value=18,
    max_value=100,
    value=45,
    step=1,
    format="%d"
)

filing_status = st.sidebar.selectbox(
    "Filing status",
    ["Single", "Married Filing Jointly"]
)

current_taxable_income = st.sidebar.number_input(
    "Current taxable income ($)",
    min_value=0.0,
    value=100000.0,
    step=1000.0,
    format="%.0f"
)

conversion_amount = st.sidebar.number_input(
    "Amount to convert to Roth ($)",
    min_value=0.0,
    value=20000.0,
    step=1000.0,
    format="%.0f"
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
    step=1,
    format="%d"
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
tax_cost_as_pct_of_conversion = (total_tax_due / conversion_amount * 100) if conversion_amount > 0 else 0

# -----------------------------
# Header / Hero
# -----------------------------
st.markdown("""
<div class="hero-box">
    <div class="hero-title">Roth Conversion Impact Calculator</div>
    <p class="hero-subtitle">
        Estimate the tax cost of a Roth conversion today and compare projected retirement outcomes
        versus keeping assets in a Traditional account.
    </p>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# KPI Row
# -----------------------------
k1, k2, k3, k4 = st.columns(4)
k1.metric("Federal Tax Due", currency(federal_tax_due))
k2.metric("State Tax Due", currency(state_tax_due))
k3.metric("Total Tax Due", currency(total_tax_due))
k4.metric("New Taxable Income", currency(new_taxable_income))

st.caption(
    f"Estimated tax cost today equals {percent(tax_cost_as_pct_of_conversion)} of the conversion amount "
    f"under the assumptions entered."
)

st.divider()

# -----------------------------
# Comparison + Assumptions
# -----------------------------
left, right = st.columns([1.25, 1])

with left:
    st.markdown('<div class="section-title">Scenario Comparison</div>', unsafe_allow_html=True)

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

    display_df = comparison_df.copy()
    display_df["Projected Value"] = display_df["Projected Value"].map(currency)

    st.dataframe(display_df, hide_index=True, use_container_width=True)

    if conversion_amount == 0:
        st.info("No conversion amount has been entered yet, so both scenarios are effectively neutral.")
    elif net_difference > 0:
        st.success(
            f"Under these assumptions, converting today creates an estimated retirement-value advantage of "
            f"{currency(net_difference)}."
        )
    elif net_difference < 0:
        st.warning(
            f"Under these assumptions, keeping the money in Traditional may retain an estimated advantage of "
            f"{currency(abs(net_difference))}."
        )
    else:
        st.info("Under these assumptions, both scenarios produce the same estimated result.")

    st.markdown(f"""
    <div class="mini-note">
        <strong>Quick interpretation:</strong><br>
        You are modeling a current tax payment of <strong>{currency(total_tax_due)}</strong> in exchange for
        potential future tax-free growth on <strong>{currency(conversion_amount)}</strong>.
    </div>
    """, unsafe_allow_html=True)

with right:
    st.markdown('<div class="section-title">Key Assumptions</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="assumption-box">
        <p><strong>Age:</strong> {age}</p>
        <p><strong>Filing status:</strong> {filing_status}</p>
        <p><strong>Current taxable income:</strong> {currency(current_taxable_income)}</p>
        <p><strong>Conversion amount:</strong> {currency(conversion_amount)}</p>
        <p><strong>Current federal marginal rate:</strong> {percent(current_federal_rate)}</p>
        <p><strong>State tax rate:</strong> {percent(state_tax_rate)}</p>
        <p><strong>Years to retirement:</strong> {years_to_retirement}</p>
        <p><strong>Annual growth rate:</strong> {percent(annual_growth_rate)}</p>
        <p style="margin-bottom:0;"><strong>Future effective tax rate on Traditional withdrawals:</strong> {percent(future_effective_tax_rate)}</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# -----------------------------
# Charts
# -----------------------------
c1, c2 = st.columns(2)

with c1:
    st.markdown('<div class="section-title">Taxes Due Today</div>', unsafe_allow_html=True)
    fig_tax = go.Figure()
    fig_tax.add_bar(
        x=["Federal Tax", "State Tax", "Total Tax"],
        y=[federal_tax_due, state_tax_due, total_tax_due]
    )
    fig_tax.update_layout(
        xaxis_title="Tax Type",
        yaxis_title="Amount ($)",
        height=420,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig_tax, use_container_width=True)

with c2:
    st.markdown('<div class="section-title">Projected Retirement Value</div>', unsafe_allow_html=True)
    fig_compare = go.Figure()
    fig_compare.add_bar(
        x=["Roth Conversion", "Traditional After Tax"],
        y=[roth_future_value, traditional_future_value_after_tax]
    )
    fig_compare.update_layout(
        xaxis_title="Scenario",
        yaxis_title="Projected Value ($)",
        height=420,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig_compare, use_container_width=True)

st.divider()

# -----------------------------
# Growth Projection
# -----------------------------
st.markdown('<div class="section-title">Growth Projection Over Time</div>', unsafe_allow_html=True)

years = list(range(years_to_retirement + 1))
roth_series = [future_value(conversion_amount, growth_rate, y) for y in years]
traditional_pre_tax_series = [future_value(conversion_amount, growth_rate, y) for y in years]
traditional_after_tax_series = [v * (1 - future_tax_rate) for v in traditional_pre_tax_series]

fig_growth = go.Figure()
fig_growth.add_scatter(
    x=years,
    y=roth_series,
    mode="lines",
    name="Roth Conversion"
)
fig_growth.add_scatter(
    x=years,
    y=traditional_after_tax_series,
    mode="lines",
    name="Traditional After Tax"
)
fig_growth.update_layout(
    xaxis_title="Years",
    yaxis_title="Projected Value ($)",
    height=500,
    margin=dict(l=20, r=20, t=20, b=20)
)
st.plotly_chart(fig_growth, use_container_width=True)

st.divider()

# -----------------------------
# Advisor Interpretation
# -----------------------------
st.markdown('<div class="section-title">Advisor Interpretation</div>', unsafe_allow_html=True)

i1, i2, i3 = st.columns(3)
with i1:
    st.info(
        f"**Tax due today:** {currency(total_tax_due)}\n\n"
        f"This is the estimated immediate tax cost created by the conversion."
    )

with i2:
    st.info(
        f"**Projected Roth value:** {currency(roth_future_value)}\n\n"
        f"This assumes the converted amount compounds tax-free for {years_to_retirement} years."
    )

with i3:
    st.info(
        f"**Traditional after-tax value:** {currency(traditional_future_value_after_tax)}\n\n"
        f"This applies the assumed future withdrawal tax rate of {percent(future_effective_tax_rate)}."
    )

# -----------------------------
# Disclaimer
# -----------------------------
st.markdown("""
<div class="disclaimer-box">
    <strong>Important disclaimer:</strong> This is a simplified educational estimate and not personalized tax,
    legal, or investment advice. Actual outcomes may differ based on tax law, account type, other sources of income,
    withdrawal timing, investment performance, Medicare considerations, and client-specific circumstances.
</div>
""", unsafe_allow_html=True)
