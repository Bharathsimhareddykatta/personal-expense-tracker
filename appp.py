from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from datetime import datetime
import base64

app = Flask(__name__)

# Path to store expenses data
file_path = "expenses.csv"

# Initialize the CSV file if it doesn't exist
def init_expenses_file():
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Date", "Amount", "Category", "Description"])
        df.to_csv(file_path, index=False)

# Predefined categories (customize as needed)
categories = {
    'Groceries': ['grocery', 'supermarket', 'food'],
    'Entertainment': ['movie', 'event', 'game'],
    'Bills': ['electricity', 'water', 'rent'],
    'Food & Dining': ['restaurant', 'dining', 'fast food'],
    'Transport': ['fuel', 'gas', 'car'],
    'Shopping': ['clothes', 'electronics', 'shopping']
}

# Function to automatically assign category based on description
def assign_category(description):
    for category, keywords in categories.items():
        if any(keyword in description.lower() for keyword in keywords):
            return category
    return 'Other'  # Default category if no match

# Add an expense
def add_expense(amount, description):
    date = datetime.now().strftime('%Y-%m-%d')
    category = assign_category(description)  # Automatically assign category
    expense_data = {"Date": [date], "Amount": [amount], "Category": [category], "Description": [description]}
    df = pd.DataFrame(expense_data)
    df.to_csv(file_path, mode='a', header=False, index=False)

# View total spending by category
def view_total_spending():
    df = pd.read_csv(file_path)
    spending_by_category = df.groupby('Category')['Amount'].sum()
    return spending_by_category

# Generate spending report (Visualization)
def generate_report():
    df = pd.read_csv(file_path)
    spending_by_category = df.groupby('Category')['Amount'].sum()

    # Create a bar chart for expenses by category
    plt.figure(figsize=(10, 6))
    spending_by_category.plot(kind='bar', color='red')
    plt.title('Total Spending by Category')
    plt.xlabel('Category')
    plt.ylabel('Amount Spent ($)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Convert the plot to a base64 string to embed in HTML
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    img_b64 = base64.b64encode(img.getvalue()).decode('utf-8')

    return img_b64

# Initialize file on startup
init_expenses_file()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_expense', methods=['POST'])
def add_expense_route():
    if request.method == 'POST':
        amount = float(request.form['amount'])
        description = request.form['description']
        add_expense(amount, description)
        return redirect(url_for('index'))

@app.route('/report')
def report():
    spending_by_category = view_total_spending()
    report_img = generate_report()
    return render_template('report.html', spending_by_category=spending_by_category, report_img=report_img)

if __name__ == '__main__':
    app.run(debug=True)
