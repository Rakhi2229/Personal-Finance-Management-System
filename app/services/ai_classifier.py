"""
AI Expense Auto-Classification Service
Maps transaction descriptions/titles to standard categories automatically.
e.g. "Swiggy order" -> Food, "Uber ride" -> Travel, "Amazon purchase" -> Shopping
"""

MERCHANT_MAPPINGS = {
    'Food': ['swiggy', 'zomato', 'blinkit', 'zepto', 'dunkin', 'starbucks', 'mcdonalds', 'kfc', 'dominos', 'pizza', 'restaurant', 'cafe', 'dining', 'food', 'bakery', 'tea', 'coffee'],
    'Travel': ['uber', 'ola', 'rapido', 'indigo', 'air india', 'irctc', 'redbus', 'metro', 'taxi', 'cab', 'flight', 'railway', 'toll', 'fastag'],
    'Shopping': ['amazon', 'flipkart', 'myntra', 'nykaa', 'zara', 'h&m', 'ajio', 'tata cliq', 'mall', 'mart', 'supermarket', 'decathlon', 'retail'],
    'Medical': ['apollo', 'practo', 'pharmeasy', '1mg', 'medplus', 'hospital', 'clinic', 'doctor', 'pharmacy', 'medicine', 'lab', 'diagnostics'],
    'Entertainment': ['bookmyshow', 'netflix', 'spotify', 'hotstar', 'prime video', 'cinema', 'pvr', 'inox', 'movie', 'concert', 'gaming', 'steam'],
    'Rent': ['rent', 'landlord', 'nobroker', 'house rent', 'flat rent'],
    'Fuel': ['petrol', 'diesel', 'hpcl', 'bpcl', 'iocl', 'shell', 'fuel', 'cng'],
    'Electricity': ['electricity', 'power', 'bescom', 'tata power', 'mseb', 'discom', 'electric bill'],
    'Internet': ['airtel', 'jio broadband', 'act fibernet', 'wifi', 'broadband', 'telecom', 'recharge'],
    'EMI': ['emi', 'loan', 'credit card bill', 'hdfc bank emi', 'icici emi', 'mortgage'],
    'Insurance': ['lic', 'star health', 'hdfc ergo', 'tata aia', 'insurance', 'premium', 'policybazaar'],
    'Education': ['udemy', 'coursera', 'school', 'college', 'tuition', 'books', 'codegnan', 'course', 'fees'],
    'Taxes': ['tax', 'income tax', 'gst', 'property tax', 'challan']
}

def classify_expense_title(title):
    """
    Analyzes transaction description string and returns matched Category & AutoClassified boolean flag.
    """
    if not title:
        return 'Others', False

    title_lower = title.lower().strip()

    for category, keywords in MERCHANT_MAPPINGS.items():
        for kw in keywords:
            if kw in title_lower:
                return category, True

    return 'Others', False
