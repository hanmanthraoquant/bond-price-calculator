import math
from datetime import datetime, date

# --- 1. Bond Pricing Theory Explained ---
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
def calculate_bond_price(face_value, coupon_rate, maturity_date_str, ytm, coupon_frequency_per_year=2):
    """
    Calculates the price of a bond based on its characteristics.

    Args:
        face_value (float): The par value of the bond, typically $1000.
                            This is the amount repaid at maturity.
        coupon_rate (float): The annual coupon rate as a decimal (e.g., 0.05 for 5%).
                             This determines the annual interest payment.
        maturity_date_str (str): The bond's maturity date in 'YYYY-MM-DD' format.
                                 This is when the face value is repaid.
        ytm (float): The annual Yield to Maturity as a decimal (e.g., 0.04 for 4%).
                     This is the discount rate used to value the bond's cash flows.
        coupon_frequency_per_year (int): How many times the coupon is paid per year.
                                         Common values: 1 (annual), 2 (semi-annual), 4 (quarterly).

    Returns:
        float: The calculated present value (price) of the bond.
        None: If there's an error in input (e.g., invalid date or past maturity).
    """
    # Input Validation: Date format
    try:
        maturity_date = datetime.strptime(maturity_date_str, '%Y-%m-%d').date()
    except ValueError:
        print("Error: Invalid maturity date format. Please use YYYY-MM-DD (e.g., 2030-12-31).")
        return None

    today = date.today()

    # Input Validation: Maturity in the past
    if maturity_date < today:
        print("Error: Maturity date cannot be in the past. Please enter a future date.")
        return None

    # Input Validation: Coupon Frequency
    if coupon_frequency_per_year <= 0:
        print("Error: Coupon frequency must be a positive integer (e.g., 1, 2, 4).")
        return None

    # Calculate years remaining until maturity
    # We approximate based on days remaining. A more precise method would involve
    # counting exact coupon periods, but this is sufficient for a basic calculator.
    years_to_maturity = (maturity_date - today).days / 365.25

    # Calculate the total number of coupon periods remaining
    # Use math.ceil to ensure we count all future payments, even if partial year remains.
    num_periods = math.ceil(years_to_maturity * coupon_frequency_per_year)

    # Handle cases where the bond is very close to maturity or already matured (though checked above)
    if num_periods <= 0:
        # If the bond matures today or very soon, its price is essentially face value + last coupon
        # For simplicity, we can just return the face value here for very short maturity.
        # In real-world, this would involve accrued interest.
        return face_value

    # Calculate the periodic coupon payment
    # This is the amount paid out each time a coupon is due.
    periodic_coupon_payment = (face_value * coupon_rate) / coupon_frequency_per_year

    # Calculate the periodic yield to maturity
    # This is the discount rate applied to each coupon period.
    periodic_ytm = ytm / coupon_frequency_per_year

    # Calculate the Present Value (PV) of all future coupon payments (annuity)
    pv_coupons = 0.0
    if periodic_ytm == 0:
        # Special case: if YTM is zero, all future cash flows are worth their nominal value
        pv_coupons = periodic_coupon_payment * num_periods
    else:
        # Standard present value of an ordinary annuity formula
        pv_coupons = periodic_coupon_payment * ((1 - (1 + periodic_ytm)**(-num_periods)) / periodic_ytm)

    # Calculate the Present Value (PV) of the bond's face value (principal)
    # This is the single payment received at maturity.
    pv_face_value = face_value / ((1 + periodic_ytm)**num_periods)

    # The total bond price is the sum of the present values of all its future cash flows.
    bond_price = pv_coupons + pv_face_value

    return bond_price

# --- 3. Command-Line Interface (CLI) for User Interaction ---
def main():
    """
    This function provides an interactive command-line interface
    for the bond pricing calculator. It prompts the user for inputs
    and displays the calculated bond price.
    """
    print("\n" + "="*40)
    print("      Simple Bond Price Calculator")
    print("="*40 + "\n")
    print("This tool helps you calculate the theoretical price of a bond.")
    print("Enter the requested details below. To exit, type 'no' when prompted.")
    print("-" * 60 + "\n")

    while True:
        try:
            # Prompt for and validate Face Value
            face_value = float(input("Enter Face Value (e.g., 1000): $"))
            if face_value <= 0:
                print("Error: Face Value must be positive. Please try again.")
                continue

            # Prompt for and validate Annual Coupon Rate
            # Convert percentage input (e.g., 5) to decimal (0.05)
            coupon_rate_percent = float(input("Enter Annual Coupon Rate (e.g., 5 for 5%): "))
            coupon_rate = coupon_rate_percent / 100.0
            if not (0 <= coupon_rate <= 1):
                print("Warning: Coupon Rate usually between 0% and 100%. Please enter as a number (e.g., 5 for 5%).")
                # Continue allowing calculation, but warn the user for unusual inputs.

            # Prompt for Maturity Date
            maturity_date_str = input("Enter Maturity Date (YYYY-MM-DD, e.g., 2030-12-31): ")

            # Prompt for and validate Annual Yield to Maturity
            # Convert percentage input (e.g., 4) to decimal (0.04)
            ytm_percent = float(input("Enter Annual Yield to Maturity (e.g., 4 for 4%): "))
            ytm = ytm_percent / 100.0
            if not (0 <= ytm <= 1):
                print("Warning: Yield to Maturity usually between 0% and 100%. Please enter as a number (e.g., 4 for 4%).")
                # Continue allowing calculation.

            # Prompt for and validate Coupon Frequency
            coupon_frequency = int(input("Enter Coupon Frequency per Year (e.g., 2 for semi-annual, 1 for annual, 4 for quarterly): "))
            if coupon_frequency <= 0:
                print("Error: Coupon frequency must be a positive integer. Please try again.")
                continue

            # Call the bond pricing function
            bond_price = calculate_bond_price(face_value, coupon_rate, maturity_date_str, ytm, coupon_frequency)

            # Display the result if calculation was successful
            if bond_price is not None:
                print("\n" + "="*40)
                print(f"      Calculated Bond Price: ${bond_price:,.2f}")
                print("="*40)

        except ValueError:
            print("\nInvalid input detected. Please ensure you enter numbers for rates/values and correct date format.")
        except Exception as e:
            print(f"\nAn unexpected error occurred: {e}. Please report this issue.")

        # Ask if the user wants to perform another calculation
        another_calculation = input("\nDo you want to calculate another bond price? (yes/no): ").lower()
        if another_calculation != 'yes':
            print("\n" + "-" * 60)
            print("Thank you for using the Bond Price Calculator. Goodbye!")
            print("-" * 60)
            break

# This ensures that the 'main()' function is called only when the script is executed directly.
# It won't run if the script is imported as a module into another Python file.
if __name__ == "__main__":
    main()
