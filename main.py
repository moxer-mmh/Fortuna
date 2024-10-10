from finance_manager import BudgetTracker, Category, Transaction
from datetime import datetime, timedelta

def setup_budget_tracker() -> BudgetTracker:
    tracker = BudgetTracker()

    categories = [
        Category("Food", 500),
        Category("Transportation", 200),
        Category("Entertainment", 150),
        Category("Utilities", 300),
    ]

    for category in categories:
        tracker.add_category(category)

    # Add some sample transactions
    today = datetime.now()
    tracker.add_transaction("Food", Transaction(today - timedelta(days=2), 25.50, "Grocery shopping"))
    tracker.add_transaction("Food", Transaction(today - timedelta(days=1), 15.75, "Lunch"))
    tracker.add_transaction("Transportation", Transaction(today - timedelta(days=3), 50.00, "Gas"))
    tracker.add_transaction("Entertainment", Transaction(today, 30.00, "Movie tickets"))

    return tracker

if __name__ == "__main__":
    budget_tracker = setup_budget_tracker()
    budget_tracker.run_cli()