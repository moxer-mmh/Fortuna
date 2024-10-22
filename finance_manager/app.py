from .core import ExpenseManager, IncomeManager, AccountManager, SubscriptionManager


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
                self.expense_manager.input_expense(self.account_manager)
            elif choice == "2":
                self.income_manager.input_income(self.account_manager)
            elif choice == "3":
                self.expense_manager.edit_expense()
            elif choice == "4":
                self.income_manager.edit_income()
            elif choice == "5":
                self.expense_manager.delete_expense()
            elif choice == "6":
                self.income_manager.delete_income()
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
                self.expense_manager.input_category()
            elif choice == "2":
                self.income_manager.input_category()
            elif choice == "3":
                self.expense_manager.edit_category()
            elif choice == "4":
                self.income_manager.edit_category()
            elif choice == "5":
                self.expense_manager.delete_category()
            elif choice == "6":
                self.income_manager.delete_category()
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
                self.account_manager.input_account()
            elif choice == "2":
                self.account_manager.edit_account()
            elif choice == "3":
                self.account_manager.delete_account()
            elif choice == "4":
                self.account_manager.transfer_between_accounts()
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
                self.subscription_manager.input_subscription(
                    self.expense_manager, self.account_manager
                )
            elif choice == "2":
                self.subscription_manager.edit_subscription()
            elif choice == "3":
                self.subscription_manager.delete_subscription()
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
                self.subscription_manager.display_subscriptions_transactions()
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
