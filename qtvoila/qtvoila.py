import asyncio
import multiprocessing
from enum import Enum
import logging
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
from voila.app import Voila
from voila.configuration import VoilaConfiguration


class VoilaThreadStatus(Enum):
    Bad=-1 
    OK=0


class QtVoila(QWebEngineView):
    """
    QtVoila - A Qt for Python extension for Voila!
    """
    finished=Signal(int)

    def __init__(
        self, 
        parent=None, 
        temp_dir=None,
        external_notebook=None, 
        strip_sources=True,
        python_process_path=None,
        max_voila_wait:int = 20
    ):
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
        self.python_process_path=python_process_path
        self.max_voila_wait=int(max_voila_wait)

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

    def on_finish(self,x):
        if x==VoilaThreadStatus.OK:
            self.update_html(url='http://localhost:' + str(self.voilathread.port))
        self.finished.emit(x)

    def run_voila(self):
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
        self.voilathread = VoilaThread(
            parent=self, 
            nbpath=self.nbpath,
            python_process_path=self.python_process_path,
            max_voila_wait=self.max_voila_wait
        )
        self.voilathread.onfinished.connect(self.on_finish)
        self.voilathread.start()

    def refresh(self):
        if self.external_notebook is None:
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
        else:
            logging.debug("prev voila proc not found")


class VoilaThread(QtCore.QThread):
    
    onfinished=Signal(VoilaThreadStatus)
    
    def __init__(self, parent, nbpath, port=None, python_process_path=None, max_voila_wait:int = 20):
        super().__init__()
        self.parent = parent
        self.nbpath = nbpath
        self.python_process_path=python_process_path
        self.max_voila_wait=max_voila_wait

        if port is None:
            self.get_free_port()
        else:
            self.port = port
    @staticmethod
    def internal_run_voila(nb,port,strip_sources):
        v = Voila(tornado_settings={'disable_check_xsrf': True,'allow_origin': '*'},
                  notebook_path=nb,port=port)
        config = VoilaConfiguration(strip_sources=strip_sources,show_tracebacks=True)
        v.voila_configuration = config
        v.setup_template_dirs()
        v.open_browser = False
        v.start()

    def run(self):
        self.voila_process=multiprocessing.Pool(1).apply_async(VoilaThread.internal_run_voila, (self.nbpath,self.port,self.parent.strip_sources))


        for k in range(self.max_voila_wait*20):
            logging.debug(('Waiting for voila to start up...'))
            time.sleep(1/20)

            try:
                result = urlopen('http://localhost:{0}'.format(self.port))
                break
            except HTTPError as e :
                logging.error((f'exception in voila {e}'))
                break
            except URLError:
                pass
            except:
                pass
        else:
            self.onfinished.emit(VoilaThreadStatus.Bad)
            return
        logging.debug(('ended'))
        self.onfinished.emit(VoilaThreadStatus.OK)

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
        logging.debug('stopping voila process')
        try:
            self.voila_process._pool.terminate()
        except:
            pass
