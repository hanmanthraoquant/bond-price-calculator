import streamlit as st
import pandas as pd
from datetime import datetime, date
import plotly.graph_objects as go
import plotly.express as px
import numpy as np # For numerical operations, especially for generating YTM ranges

# --- 1. Bond Pricing Theory Explained (for reference in comments) ---
# A bond's price is the present value of its future cash flows.
# These cash flows consist of:
#   a) Periodic coupon payments (annuity)
#   b) The face value (principal) paid back at maturity
#
# The formula used is a combination of the present value of an annuity (for coupons)
# and the present value of a lump sum (for face value).
#
# PV_Coupons = C * [1 - (1 + r)^-n] / r
# PV_Face_Value = FV / (1 + r)^n
# Bond Price = PV_Coupons + PV_Face_Value
#
# Where:
#   C = Periodic Coupon Payment (Face Value * Coupon Rate / Coupon Frequency)
#   FV = Face Value (Par Value)
#   r = Periodic Yield to Maturity (Annual YTM / Coupon Frequency)
#   n = Total Number of Periods until Maturity (Years to Maturity * Coupon Frequency)

# --- 2. Core Calculation Function ---
def calculate_bond_price(face_value, coupon_rate, maturity_date, ytm, coupon_frequency_per_year):
    """
    Calculates the price of a bond based on its characteristics.
    Adjusted for Streamlit to take datetime.date objects directly for maturity_date.

    Args:
        face_value (float): The par value of the bond.
        coupon_rate (float): The annual coupon rate as a decimal (e.g., 0.05).
        maturity_date (datetime.date): The bond's maturity date.
        ytm (float): The annual Yield to Maturity as a decimal (e.g., 0.04).
        coupon_frequency_per_year (int): How many times the coupon is paid per year.

    Returns:
        float: The calculated present value (price) of the bond.
        None: If calculation inputs are invalid or bond is matured.
    """
    today = date.today()

    # Input Validation: Maturity in the past
    if maturity_date < today:
        st.error("Error: Maturity date cannot be in the past. Please select a future date.")
        return None

    # Input Validation: Coupon Frequency
    if coupon_frequency_per_year <= 0:
        st.error("Error: Coupon frequency must be a positive integer.")
        return None

    # Calculate years remaining until maturity
    years_to_maturity = (maturity_date - today).days / 365.25 # Approximate

    # Calculate the total number of coupon periods remaining
    num_periods = np.ceil(years_to_maturity * coupon_frequency_per_year)

    if num_periods <= 0:
        # If the bond matures very soon (within the current period), its price is essentially face value.
        # For simplicity, we return face value here. Real-world would involve accrued interest.
        return face_value

    # Calculate the periodic coupon payment
    periodic_coupon_payment = (face_value * coupon_rate) / coupon_frequency_per_year

    # Calculate the periodic yield to maturity
    periodic_ytm = ytm / coupon_frequency_per_year

    # Calculate the Present Value (PV) of all future coupon payments (annuity)
    pv_coupons = 0.0
    if periodic_ytm == 0:
        pv_coupons = periodic_coupon_payment * num_periods
    else:
        pv_coupons = periodic_coupon_payment * ((1 - (1 + periodic_ytm)**(-num_periods)) / periodic_ytm)

    # Calculate the Present Value (PV) of the bond's face value (principal)
    pv_face_value = face_value / ((1 + periodic_ytm)**num_periods)

    bond_price = pv_coupons + pv_face_value

    return bond_price

# --- 3. Streamlit Application Layout ---
def main():
    st.set_page_config(layout="centered", page_title="Interactive Bond Price Calculator", page_icon="💰")

    # Title and Introduction
    st.title("💰 Interactive Bond Price Calculator")
    st.markdown("""
    This tool allows you to calculate the theoretical price of a bond based on its characteristics.
    Adjust the inputs on the left to see how the bond price changes.
    """)

    st.markdown("---") # Separator

    # --- Sidebar for Inputs ---
    st.sidebar.header("Bond Parameters")

    # Input widgets for bond characteristics
    face_value = st.sidebar.number_input(
        "Face Value ($)",
        min_value=1.0,
        value=1000.0,
        step=100.0,
        format="%.2f",
        help="The par value of the bond, typically $1000. This is repaid at maturity."
    )

    coupon_rate_percent = st.sidebar.number_input(
        "Annual Coupon Rate (%)",
        min_value=0.0,
        max_value=100.0,
        value=5.0, # Default to 5%
        step=0.1,
        format="%.1f",
        help="The annual interest rate paid by the bond. (e.g., 5 for 5%)"
    )
    coupon_rate = coupon_rate_percent / 100.0 # Convert to decimal for calculation

    maturity_date = st.sidebar.date_input(
        "Maturity Date",
        value=date(2030, 12, 31), # Default maturity date
        min_value=date.today(), # Cannot set maturity in the past
        help="The date when the bond's face value is repaid."
    )

    ytm_percent = st.sidebar.number_input(
        "Annual Yield to Maturity (YTM) (%)",
        min_value=0.0,
        max_value=100.0,
        value=4.0, # Default to 4%
        step=0.1,
        format="%.1f",
        help="The total return anticipated on a bond if it is held until it matures. (e.g., 4 for 4%)"
    )
    ytm = ytm_percent / 100.0 # Convert to decimal for calculation

    coupon_frequency_options = {
        "Annual (1x)": 1,
        "Semi-Annual (2x)": 2,
        "Quarterly (4x)": 4,
        "Monthly (12x)": 12
    }
    selected_frequency_label = st.sidebar.selectbox(
        "Coupon Frequency per Year",
        options=list(coupon_frequency_options.keys()),
        index=1, # Default to Semi-Annual
        help="How many times per year the bond pays interest."
    )
    coupon_frequency = coupon_frequency_options[selected_frequency_label]


    # --- Main Content Area for Results and Charts ---
    st.header("Bond Price Calculation")

    # Calculate and display the bond price
    bond_price = calculate_bond_price(face_value, coupon_rate, maturity_date, ytm, coupon_frequency)

    if bond_price is not None:
        st.success(f"**Calculated Bond Price:** **${bond_price:,.2f}**")

        # Display bond status (premium, discount, par)
        if bond_price > face_value:
            st.info(f"This is a **Premium Bond** (Price > Face Value)")
        elif bond_price < face_value:
            st.warning(f"This is a **Discount Bond** (Price < Face Value)")
        else:
            st.info(f"This is a **Par Bond** (Price = Face Value)")

        st.markdown("---")

        # --- Dynamic Chart: Bond Price vs. YTM ---
        st.subheader("Bond Price Sensitivity to YTM")
        st.markdown("Observe how the bond price changes across different Yields to Maturity, holding other factors constant.")

        # Generate data for the chart
        ytm_range = np.linspace(max(0.0, ytm_percent - 5), ytm_percent + 5, 50) # YTM from current -5% to +5%
        ytm_range = np.round(ytm_range, 1) # Round to 1 decimal for cleaner display

        # Calculate bond prices for the YTM range
        prices_for_ytm_range = []
        for y in ytm_range:
            price = calculate_bond_price(face_value, coupon_rate, maturity_date, y / 100.0, coupon_frequency)
            if price is not None:
                prices_for_ytm_range.append(price)
            else:
                prices_for_ytm_range.append(np.nan) # Handle cases where calculation might fail for an extreme YTM

        # Create a DataFrame for Plotly
        df_price_sensitivity = pd.DataFrame({
            'YTM (%)': ytm_range,
            'Bond Price ($)': prices_for_ytm_range
        }).dropna() # Drop any rows where price calculation failed

        if not df_price_sensitivity.empty:
            fig = px.line(df_price_sensitivity,
                          x='YTM (%)',
                          y='Bond Price ($)',
                          title='Bond Price vs. Yield to Maturity',
                          labels={'YTM (%)': 'Yield to Maturity (%)', 'Bond Price ($)': 'Bond Price ($)'},
                          markers=True) # Add markers for clarity

            # Highlight the current YTM and its corresponding price
            fig.add_trace(go.Scatter(
                x=[ytm_percent],
                y=[bond_price],
                mode='markers',
                marker=dict(size=12, color='red', symbol='circle'),
                name='Current YTM & Price'
            ))

            fig.update_layout(hovermode="x unified",
                              xaxis_title="Yield to Maturity (%)",
                              yaxis_title="Bond Price ($)",
                              legend_title_text='') # Remove legend title if only one main trace

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Could not generate YTM sensitivity chart due to invalid inputs across the range.")

    st.markdown("---")
    st.caption("Developed by [Your Name/GitHub Profile] for educational purposes.")

# Run the main function when the script is executed
if __name__ == "__main__":
    main()
