import argparse

from gui import BankAnalyzerMainWindow
from process import process


def main():
    parser = argparse.ArgumentParser(
        prog='bankanalyzer',
        description='Uses ofx files to plot bank account records.',
        epilog='')

    parser.add_argument('dir_name', nargs='?', help='Directory to analyze. GUI is opened if nothing is specified')

    args = parser.parse_args()

    if args.dir_name is None:
        BankAnalyzerMainWindow.execute()
    else:
        process(args.dir_name)


if __name__ == "__main__":
    main()
