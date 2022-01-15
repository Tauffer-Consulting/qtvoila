import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from PySide6 import QtCore
from PySide6.QtWebEngineWidgets import QWebEngineView
import nbformat as nbf
import numpy as np
import tempfile
import socket
import psutil
import os
from PySide6.QtCore import Signal

os.environ['QTWEBENGINE_CHROMIUM_FLAGS'] = '--single-process'

class QtVoila(QWebEngineView):
    """
    QtVoila - A Qt for Python extension for Voila!
    """
    def __init__(self, parent=None, temp_dir=None,
                 external_notebook=None, strip_sources=True):
        super().__init__()
        self.parent = parent
        # Temporary folder path
        if temp_dir is None:
            self.temp_dir = tempfile.mkdtemp()
        else:
            self.temp_dir = temp_dir
        # Strip sources
        self.strip_sources = strip_sources
        # external_notebook option
        self.external_notebook = external_notebook
        # iternal_notebook option
        self.internal_notebook = nbf.v4.new_notebook()
        self.internal_notebook['cells'] = []
    def clear(self):
        self.internal_notebook['cells'] = []

    def add_notebook_cell(self, code_imports={}, code="", cell_type='code'):
        """
        Adds new cell to run on a Jupyter Notebook.

        Parameters:
        -----------
        code_imports: dict
            Key:Value pairs containing modules to be imported in this cell.
            Example: {'matplotlib': 'pyplot'}
        code: string
            String containing code to be run in this cell.
            Example: "pyplot.plot([1, 2, 3], [10, 15, 13])"
        cell_type: str
            'code' or 'markdown'
        """
        # Imports extension modules
        imports_code = ""
        for k, v in code_imports.items():
            if len(v) > 0:
                imports_code += "from " + k + " import " + ", ".join(v) + "\n"
            else:
                imports_code += "import " + k + "\n"
        code = imports_code + code
        # Make notebook cell
        if cell_type == 'code':
            new_cell = nbf.v4.new_code_cell(code)
        elif cell_type == 'markdown':
            new_cell = nbf.v4.new_markdown_cell(code)
        self.internal_notebook['cells'].append(new_cell)

    def save_notebook_as(self,filename):
        return nbf.write(self.internal_notebook,filename)

    def run_voila(self):
        self.save_notebook_as(r'c:\temp\zz.ipynb')
        """Set up notebook and run it with a dedicated Voila thread."""
        # Stop any current Voila thread
        self.close_renderer()
        # Check for internal or external notebook

        if self.external_notebook is None:
            self.nbpath = os.path.join(self.temp_dir, 'temp_notebook.ipynb')
            nbf.write(self.internal_notebook, self.nbpath)
        else:
            self.nbpath= self.external_notebook
        # Run instance of Voila with the just saved .ipynb file
        self.voilathread = VoilaThread(parent=self, nbpath=self.nbpath)
        self.voilathread.finished.connect(lambda: self.update_html(url='http://localhost:' + str(self.voilathread.port)))
        self.voilathread.start()

        # Load Voila instance on main Widget

    def refresh(self):
        nbf.write(self.internal_notebook, self.nbpath)
        self.reload()

    def update_html(self, url):
        """Loads temporary HTML file and render it."""
        self.load(QtCore.QUrl(url))
        self.show()

    def close_renderer(self):
        """Close current renderer"""
        if hasattr(self, 'voilathread'):
            # Stop Voila thread
            self.voilathread.stop()


class VoilaThread(QtCore.QThread):
    finished=Signal()
    def __init__(self, parent, nbpath, port=None):
        super().__init__()
        self.parent = parent
        self.nbpath = nbpath
        if port is None:
            self.get_free_port()
        else:
            self.port = port

    def run(self):
        self.voila_process = psutil.Popen([sys.executable,"-m","voila" , "--no-browser", "--port" , str(self.port)

                  , "--strip_sources="+ str(self.parent.strip_sources),'--VoilaConfiguration.show_tracebacks=True', self.nbpath ])
        while True:

            print('Waiting for voila to start up...')
            time.sleep(1)

            try:
                result = urlopen('http://localhost:{0}'.format(self.port))
                break
            except HTTPError as e :
                print(f'except {e}')
                break
            except URLError:
                pass
        print('ended')
        self.finished.emit()


    def get_free_port(self):
        """Searches for a random free port number."""
        not_free = True
        while not_free:
            port = np.random.randint(7000, 7999)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                res = sock.connect_ex(('localhost', port))
                if res != 0:
                    not_free = False
        self.port = port

    def stop(self):

        try:
            parent = self.voila_process
            for child in parent.children(recursive=True):  # or parent.children() for recursive=False
                child.kill()
            parent.kill()
            parent.wait()
        except:
            pass


