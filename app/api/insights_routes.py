from flask import Blueprint, jsonify
from ..insights.generate_insights import generate_insights, get_latest_insight

# Create the insights blueprint
insights_bp = Blueprint('insights', __name__)

@insights_bp.route('/insights/<user_id>', methods=['GET'])
def get_insights(user_id):

    try:
        if not user_id:
            return jsonify({'error': 'userId is required'}), 400
        
        # Call the generate_insights function
        insights = generate_insights(user_id)
        
        # Check if insights is an error string (errors start with "Error")
        if isinstance(insights, str) and insights.startswith("Error"):
            return jsonify({'error': insights}), 400
        
        # Return the insights (can be string content or dict)
        return jsonify({
            'userId': user_id,
            'insights': insights
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error generating insights: {str(e)}'}), 500


@insights_bp.route('/insights/<user_id>/latest', methods=['GET'])
def get_latest_user_insight(user_id):
    """Get the latest stored insight for a user"""
    try:
        if not user_id:
            return jsonify({'error': 'userId is required'}), 400
        
        # Get the latest insight from database
        latest_insight = get_latest_insight(user_id)
        
        # Check if it's an error string
        if isinstance(latest_insight, str) and latest_insight.startswith("Error"):
            return jsonify({'error': latest_insight}), 500
        
        # Check if no insights found
        if latest_insight is None:
            return jsonify({
                'userId': user_id,
                'message': 'No insights found for this user',
                'insight': None
            }), 200
        
        # Return the latest insight
        return jsonify({
            'userId': user_id,
            'insight': latest_insight
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error fetching latest insight: {str(e)}'}), 500
