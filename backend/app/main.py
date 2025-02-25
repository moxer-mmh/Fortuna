# fortuna/backend/app/main.py
from datetime import datetime
import sys
from db import DatabaseConnection
from services import (
    ExpenseService,
    AccountService,
    CategoryService,
    IncomeService,
    SubscriptionService,
)


# Helper functions to look up IDs by name
def lookup_account_id(account_service: AccountService, name: str) -> str:
    accounts = account_service.get_all_accounts()
    for acc in accounts:
        if acc.name.lower() == name.lower():
            return acc.id
    return None


def lookup_category_id(category_service: CategoryService, name: str, type_: str) -> str:
    categories = category_service.get_all_categories()
    for cat in categories:
        if cat.name.lower() == name.lower() and cat.type.lower() == type_.lower():
            return cat.id
    return None


class FinanceManager:
    def __init__(self):
        # Create a shared DB session
        db = DatabaseConnection().get_session()
        self.db = db
        self.account_service = AccountService(db)
        self.expense_service = ExpenseService(db)
        self.income_service = IncomeService(db)
        self.subscription_service = SubscriptionService(db)
        self.category_service = CategoryService(db)

    def run(self):
        while True:
            self.display_main_menu()
            choice = input("Enter your choice: ")
            self.process_main_choice(choice)

    def display_main_menu(self):
        print("\n===== Finance Manager =====")
        print("1. Manage Transactions")
        print("2. Manage Categories")
        print("3. Manage Accounts")
        print("4. Manage Subscriptions")
        print("0. Exit")

    def process_main_choice(self, choice):
        if choice == "1":
            self.manage_transactions()
        elif choice == "2":
            self.manage_categories()
        elif choice == "3":
            self.manage_accounts()
        elif choice == "4":
            self.manage_subscriptions()
        elif choice == "0":
            print("Thank you for using Finance Manager. Goodbye!")
            sys.exit(0)
        else:
            print("Invalid choice. Please try again.")

    def manage_transactions(self):
        while True:
            print("\n----- Manage Transactions -----")
            print("1. Add Expense")
            print("2. Add Income")
            print("3. Edit Expense")
            print("4. Edit Income")
            print("5. Delete Expense")
            print("6. Delete Income")
            print("7. Move Transaction")
            print("8. View Expense Transactions")
            print("9. View Income Transactions")
            print("0. Back to Main Menu")
            choice = input("Enter your choice: ")
            if choice == "1":
                date_str = input("Enter expense date (YYYY-MM-DD): ")
                amount = float(input("Enter expense amount: "))
                description = input("Enter expense description: ")
                category_name = input("Enter expense category name: ")
                account_name = input("Enter account name: ")
                acc_id = lookup_account_id(self.account_service, account_name)
                if not acc_id:
                    print("Account not found")
                    continue
                cat_id = lookup_category_id(
                    self.category_service, category_name, "expense"
                )
                if not cat_id:
                    print("Expense category not found")
                    continue
                from schemas.expense import (
                    ExpenseCreate,
                )  # Adjust import path as needed

                try:
                    expense_data = ExpenseCreate(
                        date=datetime.strptime(date_str, "%Y-%m-%d"),
                        amount=amount,
                        description=description,
                        account_id=acc_id,
                        category_id=cat_id,
                    )
                    expense = self.expense_service.create_expense(expense_data)
                    print("Expense added successfully. ID:", expense.id)
                except Exception as e:
                    print("Error adding expense:", e)
            elif choice == "2":
                date_str = input("Enter income date (YYYY-MM-DD): ")
                amount = float(input("Enter income amount: "))
                description = input("Enter income description: ")
                category_name = input("Enter income category name: ")
                account_name = input("Enter account name: ")
                acc_id = lookup_account_id(self.account_service, account_name)
                if not acc_id:
                    print("Account not found")
                    continue
                cat_id = lookup_category_id(
                    self.category_service, category_name, "income"
                )
                if not cat_id:
                    print("Income category not found")
                    continue
                from schemas.income import IncomeCreate

                try:
                    income_data = IncomeCreate(
                        date=datetime.strptime(date_str, "%Y-%m-%d"),
                        amount=amount,
                        description=description,
                        account_id=acc_id,
                        category_id=cat_id,
                    )
                    income = self.income_service.create_income(income_data)
                    print("Income added successfully. ID:", income.id)
                except Exception as e:
                    print("Error adding income:", e)
            elif choice == "3":
                expense_id = input("Enter the ID of the expense to edit: ")
                new_date_str = input("Enter new date (YYYY-MM-DD) or leave blank: ")
                new_amount_str = input("Enter new amount or leave blank: ")
                new_description = input("Enter new description or leave blank: ")
                new_category_name = input(
                    "Enter new expense category name or leave blank: "
                )
                from schemas.expense import ExpenseUpdate

                update_fields = {}
                if new_date_str:
                    update_fields["date"] = datetime.strptime(new_date_str, "%Y-%m-%d")
                if new_amount_str:
                    update_fields["amount"] = float(new_amount_str)
                if new_description:
                    update_fields["description"] = new_description
                if new_category_name:
                    cat_id = lookup_category_id(
                        self.category_service, new_category_name, "expense"
                    )
                    if not cat_id:
                        print("Expense category not found")
                        continue
                    update_fields["category_id"] = cat_id
                try:
                    expense = self.expense_service.update_expense(
                        expense_id, ExpenseUpdate(**update_fields)
                    )
                    print("Expense updated successfully. ID:", expense.id)
                except Exception as e:
                    print("Error updating expense:", e)
            elif choice == "4":
                income_id = input("Enter the ID of the income to edit: ")
                new_date_str = input("Enter new date (YYYY-MM-DD) or leave blank: ")
                new_amount_str = input("Enter new amount or leave blank: ")
                new_description = input("Enter new description or leave blank: ")
                new_category_name = input(
                    "Enter new income category name or leave blank: "
                )
                from schemas.income import IncomeUpdate

                update_fields = {}
                if new_date_str:
                    update_fields["date"] = datetime.strptime(new_date_str, "%Y-%m-%d")
                if new_amount_str:
                    update_fields["amount"] = float(new_amount_str)
                if new_description:
                    update_fields["description"] = new_description
                if new_category_name:
                    cat_id = lookup_category_id(
                        self.category_service, new_category_name, "income"
                    )
                    if not cat_id:
                        print("Income category not found")
                        continue
                    update_fields["category_id"] = cat_id
                try:
                    income = self.income_service.update_income(
                        income_id, IncomeUpdate(**update_fields)
                    )
                    print("Income updated successfully. ID:", income.id)
                except Exception as e:
                    print("Error updating income:", e)
            elif choice == "5":
                expense_id = input("Enter the ID of the expense to delete: ")
                try:
                    self.expense_service.delete_expense(expense_id)
                    print("Expense deleted successfully.")
                except Exception as e:
                    print("Error deleting expense:", e)
            elif choice == "6":
                income_id = input("Enter the ID of the income to delete: ")
                try:
                    self.income_service.delete_income(income_id)
                    print("Income deleted successfully.")
                except Exception as e:
                    print("Error deleting income:", e)
            elif choice == "7":
                self.move_transaction()
            elif choice == "8":
                expenses = self.expense_service.get_all_expenses()
                if expenses:
                    for exp in expenses:
                        print(
                            f"ID: {exp.id}, Date: {exp.date}, Amount: {exp.amount}, Description: {exp.description}"
                        )
                else:
                    print("No expenses found.")
            elif choice == "9":
                incomes = self.income_service.get_all_incomes()
                if incomes:
                    for inc in incomes:
                        print(
                            f"ID: {inc.id}, Date: {inc.date}, Amount: {inc.amount}, Description: {inc.description}"
                        )
                else:
                    print("No incomes found.")
            elif choice == "0":
                break
            else:
                print("Invalid choice. Please try again.")

    def manage_categories(self):
        while True:
            print("\n----- Manage Categories -----")
            print("1. Add Expense Category")
            print("2. Add Income Category")
            print("3. Edit Expense Category")
            print("4. Edit Income Category")
            print("5. Delete Expense Category")
            print("6. Delete Income Category")
            print("7. View Expense Categories")
            print("8. View Income Categories")
            print("0. Back to Main Menu")
            choice = input("Enter your choice: ")
            if choice == "1":
                name = input("Enter expense category name: ")
                budget = float(input("Enter expense category budget: ") or 0)
                from schemas.category import CategoryCreate

                try:
                    cat = self.category_service.create_category(
                        CategoryCreate(name=name, budget=budget, type="expense")
                    )
                    print("Expense category added. ID:", cat.id)
                except Exception as e:
                    print("Error adding expense category:", e)
            elif choice == "2":
                name = input("Enter income category name: ")
                target = float(input("Enter income category target: ") or 0)
                from schemas.category import CategoryCreate

                try:
                    cat = self.category_service.create_category(
                        CategoryCreate(name=name, budget=target, type="income")
                    )
                    print("Income category added. ID:", cat.id)
                except Exception as e:
                    print("Error adding income category:", e)
            elif choice == "3":
                category_id = input("Enter the ID of the expense category to edit: ")
                new_name = input("Enter new expense category name or leave blank: ")
                new_budget_str = input("Enter new budget or leave blank: ")
                from schemas.category import CategoryUpdate

                update_fields = {}
                if new_name:
                    update_fields["name"] = new_name
                if new_budget_str:
                    update_fields["budget"] = float(new_budget_str)
                try:
                    cat = self.category_service.update_category(
                        category_id, CategoryUpdate(**update_fields)
                    )
                    print("Expense category updated. ID:", cat.id)
                except Exception as e:
                    print("Error updating expense category:", e)
            elif choice == "4":
                category_id = input("Enter the ID of the income category to edit: ")
                new_name = input("Enter new income category name or leave blank: ")
                new_target_str = input("Enter new target or leave blank: ")
                from schemas.category import CategoryUpdate

                update_fields = {}
                if new_name:
                    update_fields["name"] = new_name
                if new_target_str:
                    update_fields["budget"] = float(new_target_str)
                try:
                    cat = self.category_service.update_category(
                        category_id, CategoryUpdate(**update_fields)
                    )
                    print("Income category updated. ID:", cat.id)
                except Exception as e:
                    print("Error updating income category:", e)
            elif choice == "5":
                category_id = input("Enter the ID of the expense category to delete: ")
                try:
                    self.category_service.delete_category(category_id)
                    print("Expense category deleted successfully.")
                except Exception as e:
                    print("Error deleting expense category:", e)
            elif choice == "6":
                category_id = input("Enter the ID of the income category to delete: ")
                try:
                    self.category_service.delete_category(category_id)
                    print("Income category deleted successfully.")
                except Exception as e:
                    print("Error deleting income category:", e)
            elif choice == "7":
                categories = self.category_service.get_all_categories()
                expense_cats = [
                    cat for cat in categories if cat.type.lower() == "expense"
                ]
                if expense_cats:
                    for cat in expense_cats:
                        print(f"ID: {cat.id}, Name: {cat.name}, Budget: {cat.budget}")
                else:
                    print("No expense categories found.")
            elif choice == "8":
                categories = self.category_service.get_all_categories()
                income_cats = [
                    cat for cat in categories if cat.type.lower() == "income"
                ]
                if income_cats:
                    for cat in income_cats:
                        print(f"ID: {cat.id}, Name: {cat.name}, Target: {cat.budget}")
                else:
                    print("No income categories found.")
            elif choice == "0":
                break
            else:
                print("Invalid choice. Please try again.")

    def manage_accounts(self):
        while True:
            print("\n----- Manage Accounts -----")
            print("1. Add Account")
            print("2. Edit Account")
            print("3. Delete Account")
            print("4. Transfer Between Accounts")
            print("5. View Accounts")
            print("0. Back to Main Menu")
            choice = input("Enter your choice: ")
            if choice == "1":
                name = input("Enter account name: ")
                balance = float(input("Enter initial balance: ") or 0)
                from schemas.account import AccountCreate

                try:
                    acc = self.account_service.create_account(
                        AccountCreate(name=name, balance=balance)
                    )
                    print("Account created. ID:", acc.id)
                except Exception as e:
                    print("Error creating account:", e)
            elif choice == "2":
                account_id = input("Enter the ID of the account to edit: ")
                new_name = input("Enter new account name or leave blank: ")
                new_balance_str = input("Enter new balance or leave blank: ")
                from schemas.account import AccountUpdate

                update_fields = {}
                if new_name:
                    update_fields["name"] = new_name
                if new_balance_str:
                    update_fields["balance"] = float(new_balance_str)
                try:
                    acc = self.account_service.update_account(
                        account_id, AccountUpdate(**update_fields)
                    )
                    print("Account updated. ID:", acc.id)
                except Exception as e:
                    print("Error updating account:", e)
            elif choice == "3":
                account_id = input("Enter the ID of the account to delete: ")
                try:
                    self.account_service.delete_account(account_id)
                    print("Account deleted successfully.")
                except Exception as e:
                    print("Error deleting account:", e)
            elif choice == "4":
                from_account_name = input("Enter account name to transfer from: ")
                to_account_name = input("Enter account name to transfer to: ")
                amount = float(input("Enter amount to transfer: ") or 0)
                from_id = lookup_account_id(self.account_service, from_account_name)
                to_id = lookup_account_id(self.account_service, to_account_name)
                if not from_id or not to_id:
                    print("One or both accounts not found.")
                else:
                    try:
                        self.account_service.transfer_between_accounts(
                            from_id, to_id, amount
                        )
                        print("Transfer completed successfully.")
                    except Exception as e:
                        print("Error transferring funds:", e)
            elif choice == "5":
                accounts = self.account_service.get_all_accounts()
                if accounts:
                    for acc in accounts:
                        print(f"ID: {acc.id}, Name: {acc.name}, Balance: {acc.balance}")
                else:
                    print("No accounts found.")
            elif choice == "0":
                break
            else:
                print("Invalid choice. Please try again.")

    def manage_subscriptions(self):
        while True:
            print("\n----- Manage Subscriptions -----")
            print("1. Add Subscription")
            print("2. Edit Subscription")
            print("3. Delete Subscription")
            print("4. Process Due Payments")
            print("5. View Subscriptions")
            print("6. View Subscriptions Transactions")
            print("0. Back to Main Menu")
            choice = input("Enter your choice: ")
            if choice == "1":
                name = input("Enter subscription name: ")
                amount = float(input("Enter subscription amount: "))
                frequency = input("Enter frequency (weekly/monthly/yearly): ").lower()
                if frequency not in ["weekly", "monthly", "yearly"]:
                    print("Invalid frequency")
                    continue
                category_name = input("Enter expense category name for subscription: ")
                account_name = input("Enter account name: ")
                next_payment_str = input("Enter first payment date (YYYY-MM-DD): ")
                acc_id = lookup_account_id(self.account_service, account_name)
                cat_id = lookup_category_id(
                    self.category_service, category_name, "expense"
                )
                if not acc_id or not cat_id:
                    print("Account or category not found.")
                    continue
                from schemas.subscription import SubscriptionCreate

                try:
                    sub = self.subscription_service.create_subscription(
                        SubscriptionCreate(
                            name=name,
                            amount=amount,
                            frequency=frequency,
                            next_payment=datetime.strptime(
                                next_payment_str, "%Y-%m-%d"
                            ),
                            category_id=cat_id,
                            account_id=acc_id,
                        )
                    )
                    print("Subscription created successfully. ID:", sub.id)
                except Exception as e:
                    print("Error creating subscription:", e)
            elif choice == "2":
                subscription_id = input("Enter the ID of the subscription to edit: ")
                new_name = input(
                    "Enter new name or press Enter to keep current: "
                ).strip()
                new_amount_str = input(
                    "Enter new amount or press Enter to keep current: "
                ).strip()
                new_frequency = (
                    input(
                        "Enter new frequency (weekly/monthly/yearly) or press Enter to keep current: "
                    )
                    .strip()
                    .lower()
                )
                new_category_name = input(
                    "Enter new expense category name or press Enter to keep current: "
                ).strip()
                new_account_name = input(
                    "Enter new account name or press Enter to keep current: "
                ).strip()
                new_next_payment_str = input(
                    "Enter new next payment date (YYYY-MM-DD) or press Enter to keep current: "
                ).strip()
                new_active_str = (
                    input(
                        "Enter new status (active/inactive) or press Enter to keep current: "
                    )
                    .strip()
                    .lower()
                )
                from schemas.subscription import SubscriptionUpdate

                update_fields = {}
                if new_name:
                    update_fields["name"] = new_name
                if new_amount_str:
                    update_fields["amount"] = float(new_amount_str)
                if new_frequency:
                    update_fields["frequency"] = new_frequency
                if new_category_name:
                    cat_id = lookup_category_id(
                        self.category_service, new_category_name, "expense"
                    )
                    if not cat_id:
                        print("Expense category not found")
                        continue
                    update_fields["category_id"] = cat_id
                if new_account_name:
                    acc_id = lookup_account_id(self.account_service, new_account_name)
                    if not acc_id:
                        print("Account not found")
                        continue
                    update_fields["account_id"] = acc_id
                if new_next_payment_str:
                    update_fields["next_payment"] = datetime.strptime(
                        new_next_payment_str, "%Y-%m-%d"
                    )
                if new_active_str:
                    if new_active_str == "active":
                        update_fields["active"] = True
                    elif new_active_str == "inactive":
                        update_fields["active"] = False
                    else:
                        print("Invalid status.")
                        continue
                try:
                    sub = self.subscription_service.update_subscription(
                        subscription_id, SubscriptionUpdate(**update_fields)
                    )
                    print("Subscription updated successfully. ID:", sub.id)
                except Exception as e:
                    print("Error updating subscription:", e)
            elif choice == "3":
                subscription_id = input("Enter the ID of the subscription to delete: ")
                try:
                    self.subscription_service.delete_subscription(subscription_id)
                    print("Subscription deleted successfully.")
                except Exception as e:
                    print("Error deleting subscription:", e)
            elif choice == "4":
                processed = self.subscription_service.process_due_payments()
                if processed:
                    print(f"\nProcessed {len(processed)} subscription payments:")
                    for transaction in processed:
                        print(f"- {transaction}")
                else:
                    print("\nNo subscription payments were due.")
            elif choice == "5":
                subs = self.subscription_service.get_all_subscriptions()
                if subs:
                    for sub in subs:
                        print(
                            f"ID: {sub.id}, Name: {sub.name}, Amount: {sub.amount}, Frequency: {sub.frequency}, Next Payment: {sub.next_payment}, Active: {sub.active}"
                        )
                else:
                    print("No subscriptions found.")
            elif choice == "6":
                subscription_id = input(
                    "Enter the ID of the Subscription or leave blank for all: "
                )
                # For simplicity, here we display all subscriptions transactions
                if subscription_id:
                    sub = self.subscription_service.get_subscription(subscription_id)
                    if sub:
                        print(f"\nTransactions for subscription {sub.name}:")
                        # Assuming a method exists to fetch transactions for a subscription
                        transactions = []  # Replace with actual fetch if available
                        if transactions:
                            for tx in transactions:
                                print(f"  - {tx}")
                        else:
                            print("  No transactions found.")
                    else:
                        print("Subscription not found.")
                else:
                    subs = self.subscription_service.get_all_subscriptions()
                    for sub in subs:
                        print(f"\nTransactions for subscription {sub.name}:")
                        transactions = []  # Replace with actual fetch if available
                        if transactions:
                            for tx in transactions:
                                print(f"  - {tx}")
                        else:
                            print("  No transactions found.")
            elif choice == "0":
                break
            else:
                print("Invalid choice. Please try again.")

    def move_transaction(self):
        print("\n----- Move Transaction -----")
        print("1. Move Expense")
        print("2. Move Income")
        print("0. Cancel")
        choice = input("Enter your choice: ")
        if choice == "1":
            print("Move Expense functionality is not implemented yet.")
        elif choice == "2":
            print("Move Income functionality is not implemented yet.")
        elif choice == "0":
            pass
        else:
            print("Invalid choice.")


def main():
    try:
        finance_manager = FinanceManager()
        finance_manager.run()
    except KeyboardInterrupt:
        print("\nProgram interrupted. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
