from flask import Blueprint, request, jsonify
import spacy
import re

parser = Blueprint('parser', __name__)
nlp = spacy.load("en_core_web_sm")

# ---- Transaction Parsing ----
def parse_transaction(entry):
    doc = nlp(entry)
    amount = None
    category = "other"
    transaction_type = "expense"

    # Extract amount
    amount_match = re.search(r"\b\d+(?:\.\d{1,2})?\b", entry)
    if amount_match:
        amount = float(amount_match.group())

    # Lowercase for keyword detection
    entry_lower = entry.lower()

    # Category keywords
    category_keywords = {
        "groceries": ["groceries", "supermarket", "food"],
        "entertainment": ["netflix", "spotify", "movies", "game"],
        "salary": ["salary", "income", "paycheck", "got"],
        "freelance": ["freelance", "project"],
        "transport": ["bus", "uber", "train", "taxi", "wheel", "pickme"],
        "bills": ["electricity", "water", "bill", "mobile", "reload"],
        "food": ["restaurant", "cafe", "dinner", "lunch", "breakfast", "snack", "tea", "coffee"],
    }

    # Detect category
    for key, keywords in category_keywords.items():
        if any(word in entry_lower for word in keywords):
            category = key
            break

    # Detect income
    if any(w in entry_lower for w in ["got", "received", "income", "salary", "paid me"]):
        transaction_type = "income"

    return {
        "amount": amount,
        "type": transaction_type,
        "category": category
    }


@parser.route('/parse-text', methods=['POST'])
def parse_text():
    data = request.get_json()
    raw_text = data.get('raw_text', '')
    default_date = data.get('date', None)

    if not raw_text:
        return jsonify({'error': 'No raw_text provided'}), 400

    lines = raw_text.strip().splitlines()
    transactions = []

    for line in lines:
        tx = parse_transaction(line.strip())
        if tx:
            tx['date'] = default_date  
            transactions.append(tx)

    return jsonify(transactions), 200

@parser.route('/health', methods=['GET'])
def health():
    return {"status": "healthy"}, 200

