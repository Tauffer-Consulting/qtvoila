from PySide2 import QtCore
from PySide2.QtWidgets import (QApplication, QMainWindow, QPushButton, QWidget,
                               QVBoxLayout, QHBoxLayout, QSplitter, QTextEdit,
                               QCheckBox, QRadioButton, QButtonGroup, QFileDialog)
from qtvoila import QtVoila
import sys


class MyApp(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(800, 600)
        self.setWindowTitle('Simple QtVoila example')

        # Voila widget
        self.voila_widget = QtVoila(
            parent=self,
            strip_sources=True,
        )

        # Left side layout
        self.button_run = QPushButton("Run code")
        self.button_run.clicked.connect(self.pass_code_to_voila_widget)
        self.check_strip = QCheckBox('Strip code from notebook')
        self.check_strip.setChecked(True)
        self.check_strip.clicked.connect(self.change_strip_voila_widget)
        self.hbox0 = QHBoxLayout()
        self.hbox0.addWidget(self.button_run)
        self.hbox0.addWidget(self.check_strip)

        # Code blocks
        self.r0 = QRadioButton("Code")
        self.r0.setChecked(True)
        self.r1 = QRadioButton("Markdown")
        self.grp1 = QButtonGroup()
        self.grp1.addButton(self.r0)
        self.grp1.addButton(self.r1)
        self.hbox1 = QHBoxLayout()
        self.hbox1.addWidget(self.r0)
        self.hbox1.addWidget(self.r1)
        self.edit1 = QTextEdit()
        code1 = """import matplotlib.pyplot as plt
            %matplotlib inline

            plt.figure()
            plt.plot([1,4,6,2,3], '-ok')
            plt.show()"""
        self.edit1.insertPlainText(code1)

        self.r2 = QRadioButton("Code")
        self.r3 = QRadioButton("Markdown")
        self.r3.setChecked(True)
        self.grp2 = QButtonGroup()
        self.grp2.addButton(self.r2)
        self.grp2.addButton(self.r3)
        self.hbox2 = QHBoxLayout()
        self.hbox2.addWidget(self.r2)
        self.hbox2.addWidget(self.r3)
        code2 = "This is a **markdown** text"
        self.edit2 = QTextEdit(code2)

        self.r4 = QRadioButton("Code")
        self.r4.setChecked(True)
        self.r5 = QRadioButton("Markdown")
        self.grp3 = QButtonGroup()
        self.grp3.addButton(self.r4)
        self.grp3.addButton(self.r5)
        self.hbox3 = QHBoxLayout()
        self.hbox3.addWidget(self.r4)
        self.hbox3.addWidget(self.r5)
        code3 = """
            plt.figure()
            plt.plot([8,6,7,7,0], '-or')
            plt.show()
        """
        self.edit3 = QTextEdit(code3)

        layout_l1 = QVBoxLayout()
        layout_l1.addLayout(self.hbox0)
        layout_l1.addLayout(self.hbox1)
        layout_l1.addWidget(self.edit1)
        layout_l1.addLayout(self.hbox2)
        layout_l1.addWidget(self.edit2)
        layout_l1.addLayout(self.hbox3)
        layout_l1.addWidget(self.edit3)

        # Right side layout
        self.button_load = QPushButton('Load external notebook')
        self.button_load.clicked.connect(self.open_file)
        self.button_clear = QPushButton("Clear")
        self.button_clear.clicked.connect(self.clear)
        layout_r1 = QVBoxLayout()
        layout_r1.addWidget(self.button_load)
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
        code1 = self.edit1.toPlainText()
        if self.r0.isChecked():
            self.voila_widget.add_notebook_cell_code(code=code1, cell_type='code')
        else:
            self.voila_widget.add_notebook_cell_code(code=code1, cell_type='markdown')

        code2 = self.edit2.toPlainText()
        if self.r2.isChecked():
            self.voila_widget.add_notebook_cell_code(code=code2, cell_type='code')
        else:
            self.voila_widget.add_notebook_cell_code(code=code2, cell_type='markdown')

        code3 = self.edit3.toPlainText()
        if self.r4.isChecked():
            self.voila_widget.add_notebook_cell_code(code=code3, cell_type='code')
        else:
            self.voila_widget.add_notebook_cell_code(code=code3, cell_type='markdown')
        # Run Voila
        self.voila_widget.run_voila()

    def change_strip_voila_widget(self):
        self.voila_widget.strip_sources = self.check_strip.isChecked()

    def clear(self):
        self.voila_widget.internal_notebook['cells'] = []
        self.voila_widget.close_renderer()

    def open_file(self):
        """Opens notebook file."""
        filename, _ = QFileDialog.getOpenFileName(None, 'Open file', '', "(*.ipynb)")
        if filename is not None:
            self.voila_widget.external_notebook = filename
            self.clear()
            self.voila_widget.run_voila()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    my_app = MyApp()
    sys.exit(app.exec_())
