import re
from datetime import date
from app.services.ai_classifier import classify_expense_title

def parse_receipt_text(raw_text):
    """
    Parses receipt text (simulated OCR or text extracted from receipt upload)
    to automatically discover: Merchant/Title, Total Amount, Date, and Category.
    """
    if not raw_text:
        return {
            'title': 'Store Purchase',
            'amount': 0.0,
            'category': 'Shopping',
            'date': date.today().strftime('%Y-%m-%d'),
            'auto_classified': False
        }

    lines = [line.strip() for line in raw_text.split('\n') if line.strip()]

    # 1. Title / Merchant (Usually the first non-empty line)
    title = lines[0] if lines else 'Store Receipt'
    # Clean up title if it contains numbers/symbols
    title = re.sub(r'[^a-zA-Z0-9\s&]', '', title)[:50] or 'Store Receipt'

    # 2. Extract Amount (Looks for patterns like Total 450.00, Rs. 1,250, INR 89.50)
    amount = 0.0
    amount_matches = re.findall(r'(?:total|amount|rs|inr|\u20b9)?\s*[:\=]?\s*(\d+(?:,\d+)*(?:\.\d{1,2})?)', raw_text.lower())
    if amount_matches:
        # Pick the largest number found near "total" or in receipt
        valid_amounts = []
        for match in amount_matches:
            try:
                val = float(match.replace(',', ''))
                if val > 0 and val < 1000000:
                    valid_amounts.append(val)
            except ValueError:
                pass
        if valid_amounts:
            amount = max(valid_amounts)

    # 3. AI Category Classification
    category, auto_classified = classify_expense_title(title)

    return {
        'title': title,
        'amount': round(amount, 2),
        'category': category,
        'date': date.today().strftime('%Y-%m-%d'),
        'auto_classified': auto_classified
    }
