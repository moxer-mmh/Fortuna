import json
from datetime import datetime
from ..core import Category, Transaction

class DataManager:
    @staticmethod
    def save_data(filename: str, expense_tracker):
        data = {
            "categories": [
                {
                    "name": category.name,
                    "budget": category.budget,
                    "transactions": [
                        {
                            "id": t.id,
                            "date": t.date.strftime("%Y-%m-%d"),
                            "amount": t.amount,
                            "description": t.description
                        } for t in category.get_transactions_from_category()
                    ]
                } for category in expense_tracker.categories
            ]
        }
        with open(filename, "w") as file:
            json.dump(data, file, indent=2)

    @staticmethod
    def load_data(filename: str, expense_tracker):
        with open(filename, "r") as file:
            data = json.load(file)
        
        expense_tracker.categories = []
        for cat_data in data["categories"]:
            category = Category(cat_data["name"], cat_data["budget"])
            for trans_data in cat_data["transactions"]:
                transaction = Transaction(
                    datetime.strptime(trans_data["date"], "%Y-%m-%d"),
                    trans_data["amount"],
                    trans_data["description"]
                )
                transaction.id = trans_data["id"]
                category.add_transaction_to_category(transaction)
            expense_tracker.add_category(category)
