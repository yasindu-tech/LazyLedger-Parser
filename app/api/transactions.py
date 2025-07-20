from flask import Blueprint, request, jsonify
from .. import db
from sqlalchemy import text

# Create the blueprint
transactions_bp = Blueprint('transactions', __name__)

@transactions_bp.route('/transactions/<user_id>', methods=['GET'])
def get_transactions(user_id):

    try:
        # Validate user_id
        if not user_id:
            return jsonify({'error': 'userId is required'}), 400
        
        # Query to get the transactions for the user
        query = text("""
            SELECT transaction_id, user_id, amount, date, type, created_at, category
            FROM transactions 
            WHERE user_id = :user_id 
            ORDER BY created_at DESC
        """)

        # Execute the query with the user_id parameter
        result = db.session.execute(query, {'user_id': user_id})
        transactions = []
        
        # Process the result set and structure the response
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
        
        return jsonify({
            'userId': user_id,
            'transactions': transactions,
            'count': len(transactions)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
