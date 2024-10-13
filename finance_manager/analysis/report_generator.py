

class ReportGenerator:
    def __init__(self, expense_tracker):
        self.expense_tracker = expense_tracker

    def generate_report(self):
        total_budget = sum(c.budget for c in self.expense_tracker.categories)
        total_spent = sum(c.get_total_transactions_in_category() for c in self.expense_tracker.categories)
        remaining_budget = total_budget - total_spent

        report = f"Budget Report:\n"
        report += f"Total Budget: ${total_budget:.2f}\n"
        report += f"Total Spent: ${total_spent:.2f}\n"
        report += f"Remaining Budget: ${remaining_budget:.2f}\n\n"
        report += "Category Breakdown:\n"

        for category in self.expense_tracker.categories:
            spent = category.get_total_transactions_in_category()
            remaining = category.budget - spent
            report += f"- {category.name}:\n"
            report += f"  Budget: ${category.budget:.2f}\n"
            report += f"  Spent: ${spent:.2f}\n"
            report += f"  Remaining: ${remaining:.2f}\n"

        return report
