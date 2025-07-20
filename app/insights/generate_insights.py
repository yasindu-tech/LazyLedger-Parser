from .. import db
from sqlalchemy import text
from .insights_chain import insight_chain  # Import the LangChain pipeline
import json


def get_transactions(user_id):

    if not user_id:
        return "No userId provided"

    try:
        # Query using the actual column structure
        query = text("""
            SELECT transaction_id, user_id, amount, date, type, created_at, category
            FROM transactions 
            WHERE user_id = :user_id 
            ORDER BY created_at DESC
        """)
        
        result = db.session.execute(query, {'user_id': user_id})
        transactions = []
        
        for row in result:
            transaction = {
                'id': row.transaction_id,
                'user_id': row.user_id,
                'amount': float(row.amount) if row.amount else None,
                'type': row.type,
                'category': row.category,
                'date': row.date.isoformat() if row.date else None,
                'created_at': row.created_at.isoformat() if row.created_at else None
            }
            transactions.append(transaction)
        
        return {
            'userId': user_id,
            'transactions': transactions,
            'count': len(transactions)
        }
    except Exception as e:
        return f"Error fetching transactions: {str(e)}"
        
        
def calculate_stats(transactions):
    if not transactions or 'transactions' not in transactions:
        return "No transactions found"

    total_amount = 0
    income_count = 0
    expense_count = 0
    categories = {}
    weekly_totals = {}
    monthly_totals = {}

    for tx in transactions['transactions']:
        amount = tx.get('amount', 0)
        tx_type = tx.get('type', 'expense')
        category = tx.get('category', 'other')
        date = tx.get('date')

        # Update total amount
        total_amount += amount

        # Count income and expenses
        if tx_type == 'income':
            income_count += 1
        else:
            expense_count += 1

        # Count categories
        if category not in categories:
            categories[category] = 0
        categories[category] += amount

        # Weekly totals
        week = date[:10]
        if week not in weekly_totals:
            weekly_totals[week] = 0
        weekly_totals[week] += amount
        # Monthly totals
        month = date[:7]
        if month not in monthly_totals:
            monthly_totals[month] = 0   
        monthly_totals[month] += amount
    return {
        'total_amount': total_amount,   
        'income_count': income_count,
        'expense_count': expense_count,
        'categories': categories,
        'weekly_totals': weekly_totals,
        'monthly_totals': monthly_totals
    }


def generate_insights(user_id):
    # Step 1: Get transaction data
    transactions = get_transactions(user_id)
    if isinstance(transactions, str):  
        return transactions  # Return error message if fetch failed

    # Step 2: Calculate stats from the data
    stats = calculate_stats(transactions)
    if isinstance(stats, str): 
        return stats  # Return error message if calculation failed

    # Step 3: Generate natural language insights using LangChain
    try:
        response = insight_chain.invoke({
            "total_amount": stats['total_amount'],
            "income_count": stats['income_count'],
            "expense_count": stats['expense_count'],
            "categories": json.dumps(stats['categories']),
            "weekly_totals": json.dumps(stats['weekly_totals']),
            "monthly_totals": json.dumps(stats['monthly_totals']),
        })
        
        # Return the LLM's generated content
        return response.content  # or response['content'] if using older LangChain
    except Exception as e:
        return f"Error generating insights: {str(e)}"
