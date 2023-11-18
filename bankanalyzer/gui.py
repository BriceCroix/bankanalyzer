from PyQt6.QtWidgets import QApplication, QPushButton, QLabel, QLineEdit, QWidget, QGridLayout, QFileDialog

import sys
from pathlib import Path

from process import process


class BankAnalyzerMainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle('Bank Analyzer')
        # self.setGeometry(100, 100, 400, 100)

        layout = QGridLayout()
        self.setLayout(layout)

        dir_browse = QPushButton('Browse')
        dir_browse.clicked.connect(self.open_dir_dialog)

        self.dir_name_edit = QLineEdit()

        process_button = QPushButton('Process')
        process_button.clicked.connect(self.process)

        layout.addWidget(QLabel('Directory :'), 0, 0)
        layout.addWidget(self.dir_name_edit, 0, 1)
        layout.addWidget(dir_browse, 0, 2)
        layout.addWidget(process_button, 0, 3)

        self.show()

    def open_dir_dialog(self):
        dir_name = QFileDialog.getExistingDirectory(self, "Select a Directory")
        if dir_name:
            path = Path(dir_name)
            self.dir_name_edit.setText(str(path))

    def process(self):
        process(self.dir_name_edit.text())
        # TODO : embed plots in qt : https://matplotlib.org/stable/gallery/user_interfaces/embedding_in_qt_sgskip.html

    @staticmethod
    def execute():
        app = QApplication(sys.argv)
        window = BankAnalyzerMainWindow()
        window.show()
        app.exec()


def main():
    BankAnalyzerMainWindow.execute()


if __name__ == '__main__':
    main()
