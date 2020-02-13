from PySide2 import QtCore
from PySide2.QtWidgets import (QApplication, QMainWindow, QPushButton, QWidget,
                               QVBoxLayout, QHBoxLayout, QSplitter, QTextEdit)
from qtvoila import QtVoila
import sys


class MyApp(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(800, 600)
        self.setWindowTitle('Simple QtVoila example')

        # Voila widget
        self.voila_widget = QtVoila()

        # Left side layout
        self.edit = QTextEdit()
        sample_code = """
        import matplotlib.pyplot as plt
        %matplotlib inline

        plt.figure()
        plt.plot([1,4,6,2,3], '-ok')
        plt.show()
        """
        self.edit.insertPlainText(sample_code)
        self.button_run = QPushButton("Run code")
        self.button_run.clicked.connect(self.pass_code_to_voila_widget)
        layout_l1 = QVBoxLayout()
        layout_l1.addWidget(self.button_run)
        layout_l1.addWidget(self.edit)

        # Right side layout
        self.button_clear = QPushButton("Clear")
        self.button_clear.clicked.connect(self.voila_widget.close_renderer)
        layout_r1 = QVBoxLayout()
        layout_r1.addWidget(self.button_clear)
        layout_r1.addWidget(self.voila_widget)

        # Central layout
        left_w = QWidget()
        left_w.setLayout(layout_l1)
        right_w = QWidget()
        right_w.setLayout(layout_r1)
        splitter = QSplitter(QtCore.Qt.Horizontal)
        splitter.addWidget(left_w)
        splitter.addWidget(right_w)
        layout_central = QHBoxLayout()
        layout_central.addWidget(splitter)
        self.main_widget = QWidget(self)
        self.main_widget.setLayout(layout_central)
        self.setCentralWidget(self.main_widget)
        self.show()

    def pass_code_to_voila_widget(self):
        code = self.edit.toPlainText()
        self.voila_widget.code = code
        self.voila_widget.run_voila()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    my_app = MyApp()
    sys.exit(app.exec_())
