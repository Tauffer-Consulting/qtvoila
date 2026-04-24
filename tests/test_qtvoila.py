#!/usr/bin/env python
"""Standalone smoke test for qtvoila.

Loads a notebook with QtVoila in a Qt window.

Usage:
    python test_qtvoila.py path/to/notebook.ipynb
"""
import argparse
import logging
import os
import sys

from PySide6.QtWidgets import QApplication, QDialog, QPushButton, QVBoxLayout
from qtvoila import QtVoila


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("notebook")
    parser.add_argument("--wait", type=int, default=30)
    args = parser.parse_args()

    if not os.path.isfile(args.notebook):
        sys.exit(f"notebook not found: {args.notebook}")

    logging.basicConfig(level=logging.DEBUG)

    app = QApplication.instance() or QApplication(sys.argv)

    qtvoila = QtVoila(external_notebook=args.notebook, max_voila_wait=args.wait)

    dialog = QDialog()
    dialog.setWindowTitle(f"QtVoila: {os.path.basename(args.notebook)}")
    dialog.setMinimumSize(1000, 600)
    layout = QVBoxLayout(dialog)
    layout.addWidget(qtvoila)
    close = QPushButton("Close", dialog)
    close.pressed.connect(dialog.close)
    layout.addWidget(close)

    qtvoila.run_voila()
    try:
        dialog.exec()
    finally:
        qtvoila.close_renderer()


if __name__ == "__main__":
    main()
