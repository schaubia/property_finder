import math


def calculate_monthly_payment(principal: float, annual_rate: float, term_years: int) -> float:
    """Calculate monthly mortgage payment using standard amortization formula."""
    if annual_rate == 0:
        return principal / (term_years * 12)
    monthly_rate = annual_rate / 100 / 12
    n = term_years * 12
    payment = principal * (monthly_rate * (1 + monthly_rate) ** n) / ((1 + monthly_rate) ** n - 1)
    return payment


def calculate_max_loan(monthly_income: float, annual_rate: float, term_years: int,
                       debt_to_income_ratio: float = 0.40) -> float:
    """Calculate maximum loan based on income and DTI ratio."""
    max_monthly_payment = monthly_income * debt_to_income_ratio
    monthly_rate = annual_rate / 100 / 12
    n = term_years * 12
    if monthly_rate == 0:
        return max_monthly_payment * n
    max_loan = max_monthly_payment * ((1 + monthly_rate) ** n - 1) / (monthly_rate * (1 + monthly_rate) ** n)
    return max_loan


def calculate_amortization_schedule(principal: float, annual_rate: float, term_years: int):
    """Generate full amortization schedule."""
    monthly_rate = annual_rate / 100 / 12
    n = term_years * 12
    monthly_payment = calculate_monthly_payment(principal, annual_rate, term_years)

    schedule = []
    balance = principal
    total_interest = 0

    for month in range(1, n + 1):
        interest = balance * monthly_rate
        principal_payment = monthly_payment - interest
        balance -= principal_payment
        total_interest += interest

        if month % 12 == 0 or month == 1 or month == n:
            schedule.append({
                "month": month,
                "year": math.ceil(month / 12),
                "payment": monthly_payment,
                "principal": principal_payment,
                "interest": interest,
                "balance": max(0, balance),
                "total_interest_paid": total_interest,
            })

    return schedule


def calculate_total_cost(principal: float, annual_rate: float, term_years: int,
                          processing_fee_pct: float = 1.0) -> dict:
    """Calculate total cost of mortgage including fees."""
    monthly = calculate_monthly_payment(principal, annual_rate, term_years)
    total_payments = monthly * term_years * 12
    total_interest = total_payments - principal
    processing_fee = principal * processing_fee_pct / 100

    # Estimate notary fee (approx 1% of property value)
    notary_fee = principal * 0.01

    # Estimate property insurance (approx 0.15% per year)
    property_insurance_total = principal * 0.0015 * term_years

    return {
        "monthly_payment": monthly,
        "total_payments": total_payments,
        "total_interest": total_interest,
        "processing_fee": processing_fee,
        "notary_fee": notary_fee,
        "property_insurance_total": property_insurance_total,
        "grand_total": total_payments + processing_fee + notary_fee,
        "interest_ratio": total_interest / principal * 100,
    }


def format_currency(amount: float, currency: str = "€") -> str:
    """Format number as currency string."""
    return f"{currency} {amount:,.0f}"


def format_bgn(amount: float) -> str:
    return f"{amount:,.0f} лв."


def eur_to_bgn(amount: float) -> float:
    return amount * 1.9558


def bgn_to_eur(amount: float) -> float:
    return amount / 1.9558
