from PySide2 import QtCore
from PySide2.QtWebEngineWidgets import QWebEngineView
import nbformat as nbf
import numpy as np
import tempfile
import socket
import psutil
import os


class QtVoila(QWebEngineView):
    def __init__(self, parent=None, code_imports={}, code="", temp_dir=None):
        super().__init__()
        self.parent = parent
        # Temporary folder path
        if temp_dir is None:
            self.temp_dir = tempfile.mkdtemp()
        else:
            self.temp_dir = temp_dir
        # User-provided code imports dictionary
        self.code_imports = code_imports
        # User provided code
        self.code = code

    def make_notebook_cell_code(self):
        """Makes the code to run on a Jupyter Notebook cell."""
        # Imports extension modules
        imports_code = ""
        for k, v in self.code_imports.items():
            imports_code += "from " + k + " import " + ", ".join(v) + "\n"
        self.code = imports_code + self.code

    def run_voila(self):
        """Set up notebook and run it with a dedicated Voila thread."""
        # Stop any current Voila thread
        self.close_renderer()
        # Make notebook code
        self.make_notebook_cell_code()
        # Write content to a .ipynb file
        nb = nbf.v4.new_notebook()
        nb['cells'] = [nbf.v4.new_code_cell(self.code)]
        nbpath = os.path.join(self.temp_dir, 'temp_notebook.ipynb')
        nbf.write(nb, nbpath)
        # Run instance of Voila with the just saved .ipynb file
        port = self.get_free_port()
        self.voilathread = voilaThread(parent=self, port=port, nbpath=nbpath)
        self.voilathread.start()
        # Load Voila instance on main Widget
        self.update_html(url='http://localhost:'+str(port))

    def update_html(self, url):
        """Loads temporary HTML file and render it."""
        self.load(QtCore.QUrl(url))
        self.show()

    def close_renderer(self):
        """Close current renderer"""
        if hasattr(self, 'voilathread'):
            # Stop Voila thread
            self.voilathread.stop()

    def get_free_port(self):
        """Searches for a random free port number."""
        not_free = True
        while not_free:
            port = np.random.randint(7000, 7999)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                res = sock.connect_ex(('localhost', port))
                if res != 0:
                    not_free = False
        return port


class voilaThread(QtCore.QThread):
    def __init__(self, parent, port, nbpath):
        super().__init__()
        self.parent = parent
        self.port = port
        self.nbpath = nbpath

    def run(self):
        os.system("voila " + self.nbpath + " --no-browser --port "+str(self.port))

    def stop(self):
        pid = os.getpid()
        process = psutil.Process(pid)
        proc_list = []
        for child in process.children(recursive=True):
            is_listening = self.is_listening_to_port(child, self.port)
            if is_listening:
                proc_list.append(child)
        for proc in proc_list:
            if proc.status() != 'terminated':
                proc.kill()

    def is_listening_to_port(self, process, port):
        is_listening = False
        # iterate over processe's children
        for child in process.children(recursive=True):
            # iterate over child connections
            for con in child.connections():
                if con.status == 'LISTEN':
                    if isinstance(con.laddr.port, int):
                        is_listening = con.laddr.port == port
                    elif isinstance(con.laddr.port, list):
                        is_listening = port in con.laddr.port
                    return is_listening
        return is_listening
