from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import os

app = Flask(__name__)

# MongoDB bağlantısı
mongo_uri = os.getenv("MONGO_URI", "mongodb://mongo:27017/gelir_gider_db")
client = MongoClient(mongo_uri)
db = client.gelir_gider_db

@app.route('/')
def home():
    return render_template("home.html", title="Ana Sayfa")

@app.route('/income')
def income_page():
    return render_template("income.html", title="Gelir Ekle")

@app.route('/expense')
def expense_page():
    return render_template("expense.html", title="Gider Ekle")

"""@app.route('/report')
def report_page():
    return render_template("report.html", title="Rapor")"""

@app.route('/income', methods=['POST'])
def add_income():
    data = request.get_json()
    category = data.get('category')
    amount = data.get('amount')
    date = data.get('date', datetime.utcnow())

    if not category or not amount:
        return jsonify({"error": "Kategori ve tutar gereklidir"}), 400

    try:
        amount = float(amount)
    except ValueError:
        return jsonify({"error": "Tutar geçerli bir sayı olmalıdır"}), 400

    income_data = {
        "category": category,
        "amount": amount,
        "date": date
    }
    db.income.insert_one(income_data)
    return jsonify({"message": "Gelir başarıyla eklendi"}), 201

@app.route('/expense', methods=['POST'])
def add_expense():
    data = request.get_json()
    description = data.get('description')
    amount = data.get('amount')
    date = data.get('date', datetime.utcnow())

    if not description or not amount:
        return jsonify({"error": "Açıklama ve tutar gereklidir"}), 400

    try:
        amount = float(amount)
    except ValueError:
        return jsonify({"error": "Tutar geçerli bir sayı olmalıdır"}), 400

    expense_data = {
        "description": description,
        "amount": amount,
        "date": date
    }
    db.expense.insert_one(expense_data)
    return jsonify({"message": "Gider başarıyla eklendi"}), 201

@app.route('/report', methods=['GET'])
def get_report():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    response_type = request.args.get('format', 'html')  # Varsayılan olarak 'html'

    query = {}
    if start_date and end_date:
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
            query['date'] = {"$gte": start_date, "$lte": end_date}
        except ValueError:
            return jsonify({"error": "Tarih formatı YYYY-MM-DD olmalıdır"}), 400

    incomes = list(db.income.find(query, {"_id": 0}))
    expenses = list(db.expense.find(query, {"_id": 0}))

    total_income = sum(i['amount'] for i in incomes)
    total_expense = sum(e['amount'] for e in expenses)
    net_balance = total_income - total_expense

    print("total_income", total_income)
    print("total_expense", total_expense)
    print("net_balance", net_balance)
    print("incomes", incomes)
    print("expenses", expenses)

    if response_type == 'json':
        # JSON formatında döndür
        return jsonify({
            "total_income": total_income,
            "total_expense": total_expense,
            "net_balance": net_balance,
            "incomes": incomes,
            "expenses": expenses
        })

    # HTML şablonunu döndür
    return render_template("report.html", title="Rapor", incomes=incomes, expenses=expenses, total_income=total_income, total_expense=total_expense, net_balance=net_balance)




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
