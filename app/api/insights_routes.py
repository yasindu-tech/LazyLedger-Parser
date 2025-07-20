from flask import Blueprint, jsonify
from ..insights.generate_insights import generate_insights

# Create the insights blueprint
insights_bp = Blueprint('insights', __name__)

@insights_bp.route('/insights/<user_id>', methods=['GET'])
def get_insights(user_id):

    try:
        if not user_id:
            return jsonify({'error': 'userId is required'}), 400
        
        # Call the generate_insights function
        insights = generate_insights(user_id)
        
        # Check if insights is an error string
        if isinstance(insights, str):
            return jsonify({'error': insights}), 400
        
        # Return the insights
        return jsonify({
            'userId': user_id,
            'insights': insights
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error generating insights: {str(e)}'}), 500
