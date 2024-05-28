import sys

from .core import BankAccountRecord


def process(directory: str):
    accounts = BankAccountRecord.load_in_dir(directory)

    if len(accounts) == 0:
        sys.stderr.write(f'No OFX file found in {directory}')
        return

    accounts = BankAccountRecord.merge_account_records(accounts)

    for account in accounts:
        account.plot(show=False)
    BankAccountRecord.stack_plot_account_records(accounts, show=True)


def main():
    process('../tmp')


if __name__ == '__main__':
    main()
