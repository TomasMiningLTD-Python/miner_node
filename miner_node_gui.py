#!/usr/bin/which python3
import sys,argparse
from PyQt5.QtWidgets import QApplication, QDialog,QMainWindow,QFileDialog
from gui import mainWindow
from node import application


if __name__ == '__main__':
    app = application.minerApp()
    app.run()
