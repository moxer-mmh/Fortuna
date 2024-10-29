import sys
from finance_manager import FinanceManager


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
