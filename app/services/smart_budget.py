"""
AI Smart Budget Recommendation Engine
Generates an optimal monthly budget breakdown based on the 50/30/20 Financial Framework:
- 50% Essential Needs (Rent, Food, Medical, Electricity, Internet, EMI, Education)
- 30% Discretionary Wants (Shopping, Travel, Entertainment, Fuel, Others)
- 20% Savings & Wealth Building (Investments & Emergency Fund)
"""

CATEGORIES_NEEDS = ['Rent', 'Food', 'Medical', 'Electricity', 'Internet', 'EMI', 'Education', 'Insurance', 'Taxes']
CATEGORIES_WANTS = ['Shopping', 'Travel', 'Entertainment', 'Fuel', 'Others']

def generate_smart_budget_recommendation(monthly_income, historical_expenses=None):
    """
    Returns category-wise recommended monthly budget allocation in INR.
    """
    income = float(monthly_income or 0.0)
    if income <= 0:
        # Default fallback baseline assuming 50,000 INR
        income = 50000.0

    needs_budget_pool = income * 0.50
    wants_budget_pool = income * 0.30
    savings_budget_pool = income * 0.20

    # Base allocations
    allocations = {
        'Rent': round(needs_budget_pool * 0.35, 2),
        'Food': round(needs_budget_pool * 0.25, 2),
        'EMI': round(needs_budget_pool * 0.15, 2),
        'Medical': round(needs_budget_pool * 0.10, 2),
        'Electricity': round(needs_budget_pool * 0.05, 2),
        'Internet': round(needs_budget_pool * 0.05, 2),
        'Education': round(needs_budget_pool * 0.05, 2),

        'Shopping': round(wants_budget_pool * 0.35, 2),
        'Travel': round(wants_budget_pool * 0.25, 2),
        'Entertainment': round(wants_budget_pool * 0.20, 2),
        'Fuel': round(wants_budget_pool * 0.10, 2),
        'Others': round(wants_budget_pool * 0.10, 2)
    }

    # Adjust using historical spending proportions if available
    if historical_expenses and len(historical_expenses) > 0:
        cat_totals = {}
        total_spent = sum(e.amount for e in historical_expenses)
        if total_spent > 0:
            for e in historical_expenses:
                cat_totals[e.category] = cat_totals.get(e.category, 0.0) + e.amount
            
            # Blend 50% rule recommendation with 50% historic spend pattern
            for cat, rec_val in allocations.items():
                hist_ratio = cat_totals.get(cat, 0.0) / total_spent
                blend_val = (rec_val * 0.6) + (income * hist_ratio * 0.4)
                allocations[cat] = round(blend_val, 2)

    total_recommended_spend = sum(allocations.values())

    return {
        'monthly_income': income,
        'needs_pool': round(needs_budget_pool, 2),
        'wants_pool': round(wants_budget_pool, 2),
        'recommended_savings': round(savings_budget_pool, 2),
        'total_recommended_spend': round(total_recommended_spend, 2),
        'category_allocations': allocations
    }
