# insights_chain.py
import os
import json

# Try multiple LLM options with proper fallbacks
llm = None

# Option 1: Try Hugging Face Hub (free API)
try:
    from langchain_huggingface import HuggingFaceEndpoint
    
    hf_token = os.environ.get('HUGGINGFACE_API_TOKEN')
    if hf_token:
        llm = HuggingFaceEndpoint(
            repo_id="microsoft/DialoGPT-medium",  # Free model
            model_kwargs={"temperature": 0.7, "max_length": 512},
            huggingfacehub_api_token=hf_token
        )
        print("Using Hugging Face Endpoint LLM")
except Exception as e:
    print(f"Hugging Face Hub failed: {e}")
    llm = None

# Option 2: Enhanced rule-based system (always works)
if llm is None:
    class EnhancedFinancialLLM:
        def __call__(self, prompt):
            # Extract data from prompt
            import re
            
            total_match = re.search(r'Total Amount: ([\d\.\-]+)', prompt)
            income_match = re.search(r'Income Count: (\d+)', prompt)
            expense_match = re.search(r'Expense Count: (\d+)', prompt)
            categories_match = re.search(r'Categories: ({.*?})', prompt, re.DOTALL)
            
            total_amount = float(total_match.group(1)) if total_match else 0
            income_count = int(income_match.group(1)) if income_match else 0
            expense_count = int(expense_match.group(1)) if expense_match else 0
            
            try:
                categories = json.loads(categories_match.group(1)) if categories_match else {}
            except:
                categories = {}
            
            return self.generate_advanced_insights(total_amount, income_count, expense_count, categories)
        
        def generate_advanced_insights(self, total_amount, income_count, expense_count, categories):
            # Advanced financial analysis
            insights = []
            
            # Calculate financial ratios
            total_expenses = sum(amount for cat, amount in categories.items() if amount > 0 and cat not in ['salary', 'income', 'freelance'])
            total_income = sum(amount for cat, amount in categories.items() if cat in ['salary', 'income', 'freelance'])
            
            if total_income == 0:
                total_income = max(0, total_amount)
            
            # Financial metrics
            expense_ratio = (total_expenses / total_income * 100) if total_income > 0 else 0
            savings_rate = ((total_income - total_expenses) / total_income * 100) if total_income > 0 else 0
            
            # Generate comprehensive summary
            summary = f"Financial Overview: With {income_count} income sources totaling ${total_income:,.2f} and {expense_count} expense transactions totaling ${total_expenses:,.2f}, your savings rate is {savings_rate:.1f}%. "
            
            if savings_rate >= 20:
                summary += "Excellent savings discipline! You're building strong financial foundations."
            elif savings_rate >= 10:
                summary += "Good progress on savings, but there's room for improvement."
            else:
                summary += "Critical: Your expenses are consuming most of your income."
            
            insights.append(f"Summary: {summary}")
            
            # Detailed insights
            if categories:
                top_expense = max((cat for cat, amount in categories.items() if cat not in ['salary', 'income', 'freelance']), 
                                key=lambda x: categories.get(x, 0), default=None)
                if top_expense:
                    top_amount = categories[top_expense]
                    top_percentage = (top_amount / total_income * 100) if total_income > 0 else 0
                    insights.append(f"Insight 1: Your largest expense category '{top_expense}' represents {top_percentage:.1f}% of your income (${top_amount:,.2f}). Industry benchmarks suggest this category should be under {self.get_category_benchmark(top_expense):.1f}% of income.")
            
            # Cash flow insight
            if expense_ratio > 80:
                insights.append(f"Insight 2: Your expense-to-income ratio is {expense_ratio:.1f}%, which is concerning. Consider the 50/30/20 rule: 50% needs, 30% wants, 20% savings. You're currently at {100-savings_rate:.1f}% expenses.")
            else:
                insights.append(f"Insight 2: Your expense-to-income ratio of {expense_ratio:.1f}% is manageable. Focus on optimizing your largest expense categories for better savings.")
            
            # Behavioral insight
            avg_transaction = total_expenses / expense_count if expense_count > 0 else 0
            if avg_transaction < 50:
                insights.append(f"Insight 3: Your average transaction size is ${avg_transaction:.2f}, indicating frequent small purchases. Consider using the 24-hour rule for purchases under $100 to reduce impulse spending by 15-20%.")
            else:
                insights.append(f"Insight 3: Your average transaction size is ${avg_transaction:.2f}, suggesting planned purchases. Focus on negotiating better rates for your larger recurring expenses to maximize savings impact.")
            
            return "\n\n".join(insights)
        
        def get_category_benchmark(self, category):
            benchmarks = {
                'food': 15, 'groceries': 12, 'transport': 15, 'entertainment': 10,
                'bills': 25, 'shopping': 10, 'health': 8, 'other': 10
            }
            return benchmarks.get(category.lower(), 15)
    
    llm = EnhancedFinancialLLM()
    print("Using enhanced rule-based financial LLM")

# Create prompt template for financial analysis (only needed for real LLMs)
try:
    from langchain_core.prompts import ChatPromptTemplate
    
    prompt_template = ChatPromptTemplate.from_template("""
    You are an expert financial advisor analyzing personal finance data. Provide detailed, actionable insights.

    Financial Data:
    Total Amount: {total_amount}
    Income Count: {income_count}
    Expense Count: {expense_count}
    Categories: {categories}
    Weekly Totals: {weekly_totals}
    Monthly Totals: {monthly_totals}

    Analyze this data and provide:
    1. A comprehensive financial health summary (2-3 sentences)
    2. Three specific, actionable insights with numerical benchmarks
    3. Recommendations based on financial best practices

    Focus on:
    - Savings rate analysis
    - Spending pattern optimization
    - Category-specific recommendations with percentages
    - Cash flow management
    - Financial goal suggestions

    Format your response clearly with Summary and numbered Insights.
    """)
except ImportError:
    prompt_template = None

# Create the insight chain
if hasattr(llm, '__call__'):
    # For our enhanced rule-based system
    class FinancialInsightChain:
        def invoke(self, data):
            if prompt_template:
                prompt_text = prompt_template.format(
                    total_amount=data['total_amount'],
                    income_count=data['income_count'],
                    expense_count=data['expense_count'],
                    categories=data['categories'],
                    weekly_totals=data['weekly_totals'],
                    monthly_totals=data['monthly_totals']
                )
            else:
                # Create a simple prompt text for the rule-based system
                prompt_text = f"""
                Financial Data:
                Total Amount: {data['total_amount']}
                Income Count: {data['income_count']}
                Expense Count: {data['expense_count']}
                Categories: {data['categories']}
                Weekly Totals: {data['weekly_totals']}
                Monthly Totals: {data['monthly_totals']}
                """
            
            try:
                # Use the new invoke method instead of deprecated __call__
                content = llm.invoke(prompt_text)
            except AttributeError:
                # Fallback for custom LLM classes that don't have invoke
                content = llm(prompt_text)
            
            class Response:
                def __init__(self, content):
                    self.content = content
            
            return Response(content)
    
    insight_chain = FinancialInsightChain()
else:
    # For HuggingFace models with LangChain
    insight_chain = prompt_template | llm
