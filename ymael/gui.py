# -*- coding: utf-8 -*-

import sys
import datetime
import logging
logger = logging.getLogger(__name__)

from PyQt5.QtWidgets import *
from functools import partial

from .core import Core


class GraphicInterface(QMainWindow):

    def __init__(self, rps_folder, login_file, exit_func):
        self._app = QApplication(sys.argv)
        QMainWindow.__init__(self)
        self.setWindowTitle("Ymael - surveillance et export de RP")
        self.setGeometry(0, 0, 800, 600) # left, top, width, height

        self._table_widget = Tabs(self, rps_folder, login_file)
        self.setCentralWidget(self._table_widget)

        sys.exit(self._gui_exit(exit_func))

    def _gui_exit(self, exit_func):
        self.show()
        self._app.exec()
        exit_func()

class Tabs(Core, QWidget):

    def __init__(self, parent, rps_folder, login_file):
        Core.__init__(self, rps_folder, cli=False)
        self.init_watcher()

        QWidget.__init__(self, parent)
        self._buttons = {}
        self._tabs = QTabWidget()
        self._define_export_and_watch_tab()
        self._define_parameters_tab()

        self._layout = QVBoxLayout(self)
        self._layout.addWidget(self._tabs)

###############################################################################
# export & watch tab
###############################################################################

    def _define_export_and_watch_tab(self):
        self._export_watch_tab = QWidget()
        self._export_watch_tab.layout = QVBoxLayout(self._export_watch_tab)
        self._tabs.addTab(self._export_watch_tab, "Export et surveillance")

        self._create_url_input()
        self._create_export_section()
        self._create_table_modifiers()
        self._create_watch_table()

    def _create_url_input(self):
        self._url_input = QWidget()
        self._url_input.layout = QHBoxLayout(self._url_input)
        self._url_field = QLineEdit(self._url_input)
        self._url_field.setFixedWidth(600)
        self._url_input.layout.addWidget(self._url_field)
        self._create_button(self._url_input, "Surveiller", self._watch_url)
        self._export_watch_tab.layout.addWidget(self._url_input)

    def _create_export_section(self):
        self._export_field = QWidget()
        self._export_field.layout = QHBoxLayout(self._export_field)
        self._export_field.layout.addStretch(1)
        self._export_field.layout.setSpacing(0)
        self._folder_path_field = QLabel(self._export_field)
        self._folder_path_field.setFixedWidth(600)
        self._create_button(self._export_field, "Ouvrir", self._get_folder_path)
        self._export_field.layout.addItem(QSpacerItem(20, 20))
        for i in self.supported_extensions():
            self._create_button(self._export_field, i, partial(self._change_extension, i), radio=True)
        self._change_extension(".pdf") # pdf will always be supported
        self._create_button(self._export_field, "Exporter", self._export_selection)
        self._export_watch_tab.layout.addWidget(self._export_field)

    def _create_table_modifiers(self):
        self._table_modifiers = QWidget()
        self._table_modifiers.layout = QHBoxLayout(self._table_modifiers)
        self._create_button(self._table_modifiers, "Sélectionner tout", self._select_all)
        self._create_button(self._table_modifiers, "Arrêter la surveillance", self._unwatch_url)
        self._export_watch_tab.layout.addWidget(self._table_modifiers)

    def _create_watch_table(self):
        self._header = ("Sélection", "Date de récupération", "Titre", "Adresse")
        self._watcher_table = QTableWidget(100, len(self._header)) # lines, columns
        self._watcher_table.setSelectionBehavior(QTableView.SelectRows)

        self._update_watch_table()

        header = self._watcher_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        for i in range(1, len(self._header)):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)

        self._export_watch_tab.layout.addWidget(self._watcher_table)

###############################################################################
# export & watch tab general functions
###############################################################################

    def _create_button(self, parent, text, linked_func, radio=False):
        if not parent in self._buttons.keys():
            self._buttons[parent] = {}
        if radio:
            self._buttons[parent][text] = QRadioButton(text)
        else:
            self._buttons[parent][text] = QPushButton(text)
        width = self._buttons[parent][text].fontMetrics().boundingRect(text).width() + 50
        self._buttons[parent][text].setMaximumWidth(width)
        self._buttons[parent][text].clicked.connect(linked_func)
        parent.layout.addWidget(self._buttons[parent][text])

    def _watch_url(self):
        url = self._url_field.text()
        if self.is_url_valid(url) and not self._watcher.is_watched(url):
            self.watch(False, url, False)
            self._update_watch_table()
            self._url_field.clear()

    def _unwatch_url(self):
        urls = self._get_selected_urls()
        if urls:
            for url in urls:
                self.watch(False, url, True)
            self._update_watch_table()

    def _get_folder_path(self):
        self._folder_path = QFileDialog.getExistingDirectory(self, "Choisir un répertoire de destination")+"/"
        self._folder_path_field.setText(self._folder_path)

    def _change_extension(self, extension):
        for i,v in self._buttons[self._export_field].items():
            if not i == extension and v.isChecked():
                self._buttons[self._export_field][i].setChecked(False)
        self._buttons[self._export_field][extension].setChecked(True)
        self._extension = extension

    def _export_selection(self):
        if self._folder_path:
            urls = self._get_selected_urls()
            add_url = self._url_field.text()
            if self.is_url_valid(add_url):
                urls.append(add_url)
            if urls:
                self.export(urls, path_ext=(self._folder_path, self._extension))

    def _select_all(self):
        select_all = False
        for line in range(len(self._table_lines.keys())):
            if not self._table_lines[line][0].isChecked():
                select_all = True

        for line in range(len(self._table_lines.keys())):
            self._table_lines[line][0].setChecked(select_all)

    def _get_selected_urls(self):
        urls = []
        for line in range(len(self._table_lines.keys())):
            if self._table_lines[line][0].isChecked():
                urls.append(self._table_lines[line][-1].text())
        return urls

    def _update_watch_table(self):
        self._watcher_table.clear()
        self._watcher_table.setHorizontalHeaderLabels(self._header)

        line = 0
        self._table_lines = {}
        for url,values in self._watcher.watcher.items():
            check_box = QCheckBox()
            table_url = QTableWidgetItem(url)
            retrieved_date = QTableWidgetItem(datetime.datetime.strftime(values[0], self._watcher.get_storage_date_format()))
            rp_title = QTableWidgetItem(values[1])
            self._table_lines[line] = [check_box, retrieved_date, rp_title, table_url]
            line += 1

        for line in range(len(self._table_lines.keys())):
            for i in range(len(self._header)):
                if i == 0:
                    self._watcher_table.setCellWidget(line, i, self._table_lines[line][i])
                else:
                    self._watcher_table.setItem(line, i, self._table_lines[line][i])

###############################################################################
# parameters tab
###############################################################################

    def _define_parameters_tab(self):
        self._parameters_tab = QWidget()
        self._parameters_tab.layout = QVBoxLayout(self._parameters_tab)
        self._parameters_tab.layout.addStretch(1)
        self._parameters_tab.layout.setSpacing(0)
        self._tabs.addTab(self._parameters_tab, "Paramètres")

        self._secrets_section = QWidget()
        self._secrets_section.layout = QVBoxLayout(self._secrets_section)

        self._login_section = QWidget()
        self._login_section.layout = QHBoxLayout(self._login_section)
        self._login_section.layout.addStretch(1)
        self._login_section.layout.setSpacing(0)
        login_label = QLabel(self._login_section)
        login_label.setFixedWidth(70)
        login_label.setText("Login :")
        self._login_section.layout.addWidget(login_label)
        self._login_field = QLineEdit(self._login_section)
        self._login_field.setFixedWidth(200)
        self._login_section.layout.addWidget(self._login_field)
        self._secrets_section.layout.addWidget(self._login_section)

        self._password_section = QWidget()
        self._password_section.layout = QHBoxLayout(self._password_section)
        self._password_section.layout.addStretch(1)
        self._password_section.layout.setSpacing(0)
        password_label = QLabel(self._password_section)
        password_label.setFixedWidth(70)
        password_label.setText("Password :")
        self._password_section.layout.addWidget(password_label)
        self._password_field = QLineEdit(self._password_section)
        self._password_field.setFixedWidth(200)
        self._password_section.layout.addWidget(self._password_field)
        self._create_button(self._password_section, "Appliquer login et password", self._save_login_password)
        self._secrets_section.layout.addWidget(self._password_section)

        self._parameters_tab.layout.addWidget(self._secrets_section)

        domain = self.get_supported_domains()[0] # only Edenya is supported for now
        login, password = self._secrets[domain].get_secrets()
        self._login_field.setText(login)
        self._password_field.setText(password)

    def _save_login_password(self):
        login = self._login_field.text()
        password = self._password_field.text()
        domain = self.get_supported_domains()[0] # only Edenya is supported for now
        self.set_domain_secrets((login, password), domain)
