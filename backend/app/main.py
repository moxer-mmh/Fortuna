#fortuna/backend/app/main.py
from services import ExpenseManager, IncomeManager, AccountManager, SubscriptionManager
import sys


class FinanceManager:
    def __init__(self):
        self.expense_manager = ExpenseManager()
        self.income_manager = IncomeManager()
        self.account_manager = AccountManager()
        self.subscription_manager = SubscriptionManager()

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
        # print("5. Generate Reports")
        # print("6. Settings")
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
        # elif choice == "5":
        #     self.generate_reports()
        # elif choice == "6":
        #     self.settings()
        elif choice == "0":
            print("Thank you for using Finance Manager. Goodbye!")
            exit()
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
                category_name = input("Enter category name: ")
                account_name = input("Enter account name: ")
                self.expense_manager.add_expense(
                    self.account_manager,
                    date_str,
                    amount,
                    description,
                    category_name,
                    account_name,
                )
            elif choice == "2":
                date_str = input("Enter income date (YYYY-MM-DD): ")
                amount = float(input("Enter income amount: "))
                description = input("Enter income description: ")
                category_name = input("Enter category name: ")
                account_name = input("Enter account name: ")
                self.income_manager.add_income(
                    self.account_manager,
                    date_str,
                    amount,
                    description,
                    category_name,
                    account_name,
                )
            elif choice == "3":
                expense_id = input("Enter the ID of the expense to edit: ")
                new_date_str = input("Enter new date (YYYY-MM-DD) or leave blank: ")
                new_amount_str = input("Enter new amount or leave blank: ")
                new_description = input("Enter new description or leave blank: ")
                new_category_name = input("Enter new category name or leave blank: ")
                self.expense_manager.edit_expense(
                    expense_id,
                    new_date_str,
                    new_amount_str,
                    new_description,
                    new_category_name,
                )
            elif choice == "4":
                income_id = input("Enter the ID of the income to edit: ")
                new_date_str = input("Enter new date (YYYY-MM-DD) or leave blank: ")
                new_amount_str = input("Enter new amount or leave blank: ")
                new_description = input("Enter new description or leave blank: ")
                new_category_name = input("Enter new category name or leave blank: ")
                self.income_manager.edit_income(
                    income_id,
                    new_date_str,
                    new_amount_str,
                    new_description,
                    new_category_name,
                )
            elif choice == "5":
                expense_id = input("Enter the ID of the expense to delete: ")
                self.expense_manager.delete_expense(expense_id)
            elif choice == "6":
                income_id = input("Enter the ID of the income to delete: ")
                self.income_manager.delete_income(income_id)
            elif choice == "7":
                self.move_transaction()
            elif choice == "8":
                self.expense_manager.display_expenses()
            elif choice == "9":
                self.income_manager.display_incomes()
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
                name = input("Enter category name: ")
                budget = input("Enter category budget: ")
                if not budget:
                    budget = 0
                self.expense_manager.add_category(name, float(budget))
            elif choice == "2":
                name = input("Enter category name: ")
                target = input("Enter target amount: ")
                if not target:
                    target = 0
                self.income_manager.add_category(name, target)
            elif choice == "3":
                category_name = input("Enter the name of the category to edit: ")
                new_name = input("Enter new category name: ")
                new_budget = input("Enter new budget: ")
                self.expense_manager.edit_category(category_name, new_name, new_budget)
            elif choice == "4":
                category_name = input("Enter the name of the category to edit: ")
                new_name = input("Enter new category name: ")
                new_target = input("Enter new target amount: ")
                self.income_manager.edit_category(category_name, new_name, new_target)
            elif choice == "5":
                category_name = input("Enter the name of the category to delete: ")
                self.expense_manager.delete_category(category_name)
            elif choice == "6":
                category_name = input("Enter the name of the category to delete: ")
                self.income_manager.delete_category(category_name)
            elif choice == "7":
                self.expense_manager.display_categories()
            elif choice == "8":
                self.income_manager.display_categories()
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
                balance = input("Enter initial balance: ")
                if not balance:
                    balance = 0
                self.account_manager.add_account(name, float(balance))
            elif choice == "2":
                name = input("Enter account name: ")
                new_name = input("Enter new account name: ")
                new_balance = input("Enter new balance: ")
                self.account_manager.edit_account(name, new_name, new_balance)
            elif choice == "3":
                name = input("Enter account name: ")
                self.account_manager.delete_account(name)
            elif choice == "4":
                from_account_name = input("Enter account to transfer from: ")

                to_account_name = input("Enter account to transfer to: ")

                amount = input("Enter amount to transfer: ")
                if not amount:
                    amount = 0
                self.account_manager.transfer_between_accounts(
                    from_account_name,
                    to_account_name,
                    float(amount),
                )
            elif choice == "5":
                self.account_manager.display_accounts()
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
                    raise ValueError("Invalid frequency")
                category_name = input("Enter expense category name: ")
                account_name = input("Enter account name: ")
                next_payment_str = input("Enter first payment date (YYYY-MM-DD): ")

                self.subscription_manager.add_subscription(
                    self.expense_manager,
                    self.account_manager,
                    name,
                    amount,
                    frequency,
                    category_name,
                    account_name,
                    next_payment_str,
                )
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
                    "Enter new category name or press Enter to keep current: "
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
                self.subscription_manager.edit_subscription(
                    subscription_id,
                    new_name,
                    new_amount_str,
                    new_frequency,
                    new_category_name,
                    new_account_name,
                    new_next_payment_str,
                    new_active_str,
                )
            elif choice == "3":
                subscription_id = input("Enter the ID of the subscription to delete: ")
                self.subscription_manager.delete_subscription(subscription_id)
            elif choice == "4":
                processed = self.subscription_manager.process_due_payments()
                if processed:
                    print(f"\nProcessed {len(processed)} subscription payments:")
                    for transaction in processed:
                        print(f"- {transaction}")
                else:
                    print("\nNo subscription payments were due.")
            elif choice == "5":
                self.subscription_manager.display_subscriptions()
            elif choice == "6":
                subscription_id = input(
                    "Enter the id of the Subscription or Leave Blank for all: "
                )
                self.subscription_manager.display_subscriptions_transactions(
                    subscription_id
                )
            elif choice == "0":
                break
            else:
                print("Invalid choice. Please try again.")

    # def generate_reports(self):
    #     while True:
    #         print("\n----- Generate Reports -----")
    #         print("1. Monthly Summary")
    #         print("2. Category-wise Expenses")
    #         print("3. Category-wise Income")
    #         print("4. Accounts Balances")
    #         print("5. Budget vs Actual")
    #         print("6. Subscription Overview")
    #         print("0. Back to Main Menu")

    #         choice = input("Enter your choice: ")
    #         if choice == "1":
    #             self.monthly_summary()
    #         elif choice == "2":
    #             self.category_wise_expenses()
    #         elif choice == "3":
    #             self.category_wise_income()
    #         elif choice == "4":
    #             self.accounts_balances()
    #         elif choice == "5":
    #             self.budget_vs_actual()
    #         elif choice == "6":
    #             self.subscription_overview()
    #         elif choice == "0":
    #             break
    #         else:
    #             print("Invalid choice. Please try again.")

    # def subscription_overview(self):
    #     """Generate an overview of all active subscriptions and their payment history"""
    #     print("\n----- Subscription Overview -----")
    #     subscriptions = self.subscription_manager.get_all_subscriptions()

    #     if not subscriptions:
    #         print("No subscriptions found.")
    #         return

    #     total_monthly_cost = 0
    #     print("\nActive Subscriptions:")
    #     print("-" * 80)

    #     for subscription in subscriptions:
    #         if not subscription.active:
    #             continue

    #         # Calculate monthly cost based on frequency
    #         monthly_cost = subscription.amount
    #         if subscription.frequency == "weekly":
    #             monthly_cost *= 4.33  # Average weeks per month
    #         elif subscription.frequency == "yearly":
    #             monthly_cost /= 12

    #         total_monthly_cost += monthly_cost

    #         print(f"{subscription}")
    #         transactions = subscription.get_transactions()
    #         if transactions:
    #             print(f"Last 3 payments:")
    #             for transaction in transactions[:3]:
    #                 print(
    #                     f"  - {transaction.date.strftime('%Y-%m-%d')}: "
    #                     f"${transaction.amount:.2f}"
    #                 )
    #         print("-" * 80)

    #     print(f"\nEstimated Total Monthly Cost: ${total_monthly_cost:.2f}")

    # def settings(self):
    #     while True:
    #         print("\n----- Settings -----")
    #         print("1. Set Default Currency")
    #         print("2. Set Budget Alerts")
    #         print("3. Export Data")
    #         print("4. Import Data")
    #         print("0. Back to Main Menu")

    #         choice = input("Enter your choice: ")
    #         if choice == "1":
    #             self.set_default_currency()
    #         elif choice == "2":
    #             self.set_budget_alerts()
    #         elif choice == "3":
    #             self.export_data()
    #         elif choice == "4":
    #             self.import_data()
    #         elif choice == "0":
    #             break
    #         else:
    #             print("Invalid choice. Please try again.")

    # def monthly_summary(self):
    #     print("Generating monthly summary...")

    # def category_wise_expenses(self):
    #     print("Generating category-wise expense report...")

    # def category_wise_income(self):
    #     print("Generating category-wise income report...")

    # def account_balances(self):
    #     print("Generating account balances report...")
    #     self.account_manager.display_accounts()

    # def budget_vs_actual(self):
    #     print("Generating budget vs actual report...")

    # def set_default_currency(self):
    #     print("Setting default currency...")

    # def set_budget_alerts(self):
    #     print("Setting budget alerts...")

    # def export_data(self):
    #     print("Exporting data...")

    # def import_data(self):
    #     print("Importing data...")

    def move_transaction(self):
        print("\n----- Move Transaction -----")
        print("1. Move Expense")
        print("2. Move Income")
        print("0. Cancel")
        choice = input("Enter your choice: ")
        if choice == "1":
            self.expense_manager.move_transaction()
        elif choice == "2":
            self.income_manager.move_transaction()
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
