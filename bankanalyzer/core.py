from __future__ import annotations

import sys
from typing import List, Tuple
from dataclasses import dataclass
from ofxparse import OfxParser
from datetime import date as Date, timedelta as TimeDelta
import matplotlib.pyplot as plt


@dataclass
class BankAccountBalance:
    """
    An account balance at the end of a day.
    """
    date: Date
    amount: float

    def apply(self, transaction: BankAccountTransaction) -> BankAccountBalance:
        """
        Applies transaction to balance :
        - If transaction is anterior to balance, returns balance before transaction.
        - If transaction is posterior to balance, returns balance after transaction.
        """
        if transaction.date > self.date:
            return BankAccountBalance(transaction.date, self.amount + transaction.amount)
        else:
            return BankAccountBalance(transaction.date, self.amount - transaction.amount)

    def is_before(self, other: BankAccountBalance) -> bool:
        return self.date < other.date


@dataclass
class BankAccountTransaction:
    date: Date
    type: str
    amount: float
    memo: str

    def is_before(self, other: BankAccountTransaction) -> bool:
        return self.date < other.date

    def __repr__(self) -> str:
        return repr(
            repr(self.date) + ';' + repr(self.type) + ';' + repr(self.amount) + ';' + repr(self.memo) + ';')


class BankAccountRecord:
    def __init__(self, name: str, account_id: str, reference_balance: BankAccountBalance, currency: str,
                 start_time: Date, end_time: Date, transactions: List[BankAccountTransaction] | None = None):
        self.name = name
        self.account_id = account_id
        self.reference_balance = reference_balance
        self.transactions: List[BankAccountTransaction] = transactions if transactions is not None else list()
        self.currency = currency
        # Excluded start time
        self.start_time = start_time
        # Included end time
        self.end_time = end_time

    def add_transaction(self, transaction: BankAccountTransaction) -> None:
        """
        Inserts transaction into account and keeps the transactions ordered.
        """
        self.transactions.append(transaction)
        self.sort_transactions()

    def sort_transactions(self) -> None:
        self.transactions.sort(key=lambda transaction: transaction.date)

    def balance_at(self, date: Date) -> BankAccountBalance:
        """
        Returns the balance of the bank account at the end of a given date.
        """
        amount = self.reference_balance.amount
        # Transactions are in chronological order, iterate in reverse to construct balance at given date
        if date <= self.reference_balance.date:
            for transaction in self.transactions:
                if transaction.date <= date:
                    continue
                elif transaction.date <= self.reference_balance.date:
                    amount -= transaction.amount
                else:
                    break
        else:
            for transaction in self.transactions:
                if transaction.date <= self.reference_balance.date:
                    continue
                elif transaction.date <= date:
                    amount += transaction.amount
                else:
                    break
        return BankAccountBalance(date, amount)

    def get_balances(self, time_span: Tuple[Date, Date] | None = None) -> List[BankAccountBalance]:
        """
        Returns a balance for this bank account for each day between given bounds.
        Bounds default to self.get_time_span()
        """
        if time_span is None:
            time_span = (self.start_time, self.end_time)
        balances = list()
        # TODO : optimize this horrible loop, each date balance can be computed from the day after / before.
        date = time_span[0]
        while date <= time_span[1]:
            balances.append(self.balance_at(date))
            date += TimeDelta(days=1)
        return balances

    def merge(self, other: BankAccountRecord):
        """
        Tries to merge with another record, that must be of the same bank account for this method to succeed.
        :param other: Other record of same bank account
        :return: None
        """
        if self.account_id != other.account_id:
            sys.stderr.write(f'Cannot merge bank accounts {self.account_id} and {other.account_id} !')
            return

        for transaction in other.transactions:
            if transaction.date <= self.start_time or transaction.date > self.end_time:
                self.transactions.append(transaction)
        self.sort_transactions()

        if other.reference_balance.date > self.reference_balance.date:
            self.reference_balance = other.reference_balance
        if other.end_time > self.end_time:
            self.end_time = other.end_time
        if other.start_time < self.start_time:
            self.start_time = other.start_time

    @staticmethod
    def _draw_alternate_month_colors(ax, start: Date, stop: Date):
        for year in range(start.year, stop.year+1):
            for month in range(1, 12+1, 2):
                left = Date(year=year, month=month, day=1)
                right = Date(year=year, month=month+1, day=1)
                ax.axvspan(left, right, facecolor='gray', alpha=0.2)

    def show_plot(self):
        """
        Plots the current record. Pauses program to show.
        :return: None
        """

        balances = self.get_balances()
        dates = [balance.date for balance in balances]
        amounts = [balance.amount for balance in balances]

        fig, ax = plt.subplots()

        # Draw background
        BankAccountRecord._draw_alternate_month_colors(ax, self.start_time, self.end_time)

        # Draw line
        ax.plot(dates, amounts)
        ax.set_title(f'Bank records for account {self.name}')
        ax.set_xlabel('Date')
        ax.set_ylabel(f'Balance ({self.currency})')
        ax.set_xlim(self.start_time, self.end_time)
        ax.yaxis.grid()
        fig.tight_layout()
        plt.show()

    def get_average_transaction(self) -> float:
        """
        Computes the average absolute transaction amount per day on this account.
        :return:
        """
        date = self.start_time
        average = 0
        count = 0
        while date <= self.end_time:
            date += TimeDelta(days=1)
            transactions_this_day = list(filter(lambda transaction: transaction.date == date, self.transactions))
            for transaction in transactions_this_day:
                average += abs(transaction.amount)
            count += 1
        average /= count
        return average

    @staticmethod
    def load_from_ofx(filenames: str | List[str]) -> List[BankAccountRecord]:
        """
        Load every bank account record in given ofx file(s).
        :param filenames: path or list of paths to ofx files.
        :return:
        """
        if not type(filenames) is list:
            filenames = [filenames]

        accounts = list()

        for filename in filenames:
            with open(filename, 'r') as ofx_file:
                ofx = OfxParser.parse(ofx_file)

                # Iterate over each account in the OFX file
                for account in ofx.accounts:
                    transactions = list()

                    # Iterate over each transaction in the account
                    for transaction in account.statement.transactions:
                        transactions.append(
                            BankAccountTransaction(transaction.date.date(), transaction.type, transaction.amount,
                                                   transaction.memo))
                    accounts.append(BankAccountRecord(name=account.account_id,
                                                      account_id=account.account_id,
                                                      transactions=transactions,
                                                      reference_balance=BankAccountBalance(
                                                          account.statement.available_balance_date.date(),
                                                          account.statement.available_balance),
                                                      currency=account.curdef,
                                                      start_time=account.statement.start_date.date(),
                                                      end_time=account.statement.end_date.date()))
        return accounts

    @staticmethod
    def merge_account_records(records: List[BankAccountRecord]) -> List[BankAccountRecord]:
        """
        Tries to simplify the given bank records by merging the ones belonging to the same bank account.
        """
        output = []
        # For all records
        for record in records:
            found = False
            # Search if it has already been registered in the outputs
            for other in output:
                # If so, merge it
                if record.account_id == other.account_id and record.name == other.name:
                    other.merge(record)
                    found = True
                    break
            # If not, add it to the output
            if not found:
                output.append(record)
        return output

    @staticmethod
    def stack_plot_account_records(accounts: List[BankAccountRecord], short_period: bool = False):
        """
        Creates and shows a stack plot of given bank accounts.
        :param accounts: Accounts to show.
        :param short_period: if true, will only show dates where all accounts have data.
            Otherwise, the plot is extended as far as possible, as long as at least one account has data.
        """
        if len(accounts) < 1:
            return
        # Check that all accounts have same currency
        currency = accounts[0].currency
        for account in accounts:
            if currency != account.currency:
                sys.stderr.write(f'Cannot draw stack plot : not all accounts have the same currency,'
                                 f'found {currency} and {account.currency}')
                return

        # Prepare timespan
        start_time = accounts[0].start_time
        end_time = accounts[0].end_time
        for account in accounts:
            if short_period:
                start_time = max(start_time, account.start_time)
                end_time = min(end_time, account.end_time)
            else:
                start_time = min(start_time, account.start_time)
                end_time = max(end_time, account.end_time)
        # Prepare all dates in this span
        dates = []
        date = start_time
        while date <= end_time:
            dates.append(date)
            date += TimeDelta(days=1)

        # Sort accounts by least amount of variations (savings below)
        accounts.sort(key=lambda record: record.get_average_transaction())

        # Prepare all balances of every account
        data = dict()
        for account in accounts:
            data[account.name] = [balance.amount for balance in account.get_balances((start_time, end_time))]
        # Prepare sum line
        sum_line = list()
        for k in range(len(dates)):
            sum_line.append(0)
            for balance in iter(data.values()):
                sum_line[-1] += balance[k]
        # Prepare average line
        average_line = list()
        average_on_days = 31
        for k in range(len(sum_line)):
            value = 0
            count = 0
            for k2 in range(max(0, k - average_on_days), k + 1):
                value += sum_line[k2]
                count += 1
            value /= count
            average_line.append(value)

        fig, ax = plt.subplots()

        # Draw background
        BankAccountRecord._draw_alternate_month_colors(ax, start_time, end_time)

        # Finally plot grap
        ax.stackplot(dates, data.values(),
                     labels=data.keys())
        ax.plot(dates, average_line, label=f'{average_on_days}-days avg', linestyle='--')
        ax.legend(reverse=True, loc='lower right')
        ax.set_title(f'Accounts balance between {start_time} and {end_time}')
        ax.set_xlabel('Time')
        ax.set_ylabel(f'Balance ({currency})')
        ax.grid()

        fig.tight_layout()
        plt.show()
