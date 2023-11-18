from bankanalyzer import BankAccountRecord


def process(directory: str):
    accounts = BankAccountRecord.load_in_dir(directory)
    accounts = BankAccountRecord.merge_account_records(accounts)

    for account in accounts:
        account.show_plot()
    BankAccountRecord.stack_plot_account_records(accounts)
