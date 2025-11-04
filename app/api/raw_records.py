from flask import Blueprint, request, jsonify
from .. import db
from sqlalchemy import text
from .parser import parse_transaction
import logging

raw_bp = Blueprint('raw_records', __name__)
logger = logging.getLogger(__name__)


@raw_bp.route('/raw-records/create', methods=['POST'])
def create_raw_record_flask():
    data = request.get_json() or {}
    user_id = data.get('user_id')
    date = data.get('date')
    raw_text = data.get('raw_text')

    if not user_id or not date or not raw_text:
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        # Insert raw_entries row and return it
        insert_raw_sql = text("""
            INSERT INTO raw_entries (user_id, date, raw_text)
            VALUES (:user_id, :date, :raw_text)
            RETURNING *;
        """)

        result = db.session.execute(insert_raw_sql, {'user_id': user_id, 'date': date, 'raw_text': raw_text})
        raw_entry = result.fetchone()

        # Parse lines
        lines = raw_text.strip().splitlines()
        parsed_transactions = []
        for line in lines:
            tx = parse_transaction(line.strip())
            if tx:
                tx['date'] = tx.get('date') or date
                parsed_transactions.append(tx)

        saved_transactions = []
        insert_tx_sql = text("""
            INSERT INTO transactions (user_id, amount, type, category, date)
            VALUES (:user_id, :amount, :type, :category, :date)
            RETURNING *;
        """)

        for tx in parsed_transactions:
            amount = tx.get('amount')
            tx_type = (tx.get('type') or '').upper()
            category = tx.get('category')
            tx_date = tx.get('date')

            # Skip incomplete transactions
            if amount is None or not tx_type or not category or not tx_date:
                logger.info('Skipping incomplete transaction: %s', tx)
                continue

            r = db.session.execute(insert_tx_sql, {
                'user_id': user_id,
                'amount': amount,
                'type': tx_type,
                'category': category,
                'date': tx_date
            })
            saved_transactions.append(r.fetchone())

        # commit once
        db.session.commit()

        return jsonify({
            'message': 'Raw record and transactions saved successfully',
            'raw_entry': dict(raw_entry) if raw_entry else None,
            'transactions': [dict(t) for t in saved_transactions]
        }), 201

    except Exception as e:
        logger.exception('Error in create_raw_record_flask')
        try:
            db.session.rollback()
        except Exception:
            pass
        return jsonify({'error': 'Internal Server Error'}), 500
