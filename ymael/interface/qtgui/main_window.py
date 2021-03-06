# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

from datetime import datetime

from functools import partial
from PyQt5.QtWidgets import *

try:
    # On linux:
    # This import is unused but still needed to fix PyQt pixbuf error
    logger.info("Importing gi.")
    import gi
    gi.require_version('GdkPixbuf', '2.0')
    from gi.repository import GdkPixbuf
except ImportError:
    pass

from .custom_menu import CustomMenu


class Tabs(QWidget):

    def __init__(self, core_instance, parent=None):
        super().__init__(parent)
        self._core = core_instance

        self._buttons = {}
        self._tabs = QTabWidget()
        self._define_export_and_watch_tab()
        self._define_parameters_tab()
        self._folder_path = ""

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
        self._create_button(self._url_input, "Surveiller", self._watch_url, enable=False)
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
        for i in self._core.supported_extensions():
            self._create_button(self._export_field, i, partial(self._change_extension, i), radio=True, enable=False)
        self._create_button(self._export_field, "Exporter", self._export_selection, enable=False)
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
        self._watcher_table.setSortingEnabled(True)

        self._update_watch_table()

        header = self._watcher_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        for i in range(1, len(self._header)):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)

        self._export_watch_tab.layout.addWidget(self._watcher_table)

###############################################################################
# export & watch tab general functions
###############################################################################

    def _create_button(self, parent, text, linked_func, radio=False, enable=True):
        if not parent in self._buttons.keys():
            self._buttons[parent] = {}
        if radio:
            self._buttons[parent][text] = QRadioButton(text)
        else:
            self._buttons[parent][text] = QPushButton(text)
        width = self._buttons[parent][text].fontMetrics().boundingRect(text).width() + 50
        self._buttons[parent][text].setMaximumWidth(width)
        self._buttons[parent][text].clicked.connect(linked_func)
        self._buttons[parent][text].setEnabled(enable)
        parent.layout.addWidget(self._buttons[parent][text])

    def _watch_url(self):
        url = self._url_field.text()
        if self._core.is_url_valid(url) and not self._core._watcher.is_watched(url):
            self._core.watch(False, [url], False)
            self._update_watch_table()
            self._url_field.clear()

    def _unwatch_url(self):
        urls = self._get_selected_urls()
        if urls:
            self._core.watch(False, urls, True)
            self._update_watch_table()

    def _get_folder_path(self):
        self._folder_path = QFileDialog.getExistingDirectory(self, "Choisir un répertoire de destination")
        if self._folder_path:
            logger.debug("Setting export folder to: {}".format(self._folder_path))
            self._folder_path_field.setText(self._folder_path)

    def _change_extension(self, extension):
        for i,v in self._buttons[self._export_field].items():
            if not i == extension and v.isChecked():
                self._buttons[self._export_field][i].setChecked(False)
        self._buttons[self._export_field][extension].setChecked(True)
        logger.debug("Setting export extension to: {}".format(extension))
        self._extension = extension

    def _export_selection(self):
        if self._folder_path:
            urls = self._get_selected_urls()
            add_url = self._url_field.text()
            if self._core.is_url_valid(add_url):
                urls.append(add_url)
            if urls:
                self._core.export(urls, path_ext=(self._folder_path, self._extension))

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
        for url,values in self._core._watcher.watcher.items():
            check_box = QCheckBox()
            table_url = QTableWidgetItem(url)
            retrieved_date = QTableWidgetItem(datetime.strftime(values[0], self._core._watcher.get_storage_date_format()))
            rp_title = QTableWidgetItem(values[1])
            self._table_lines[line] = [check_box, retrieved_date, rp_title, table_url]
            line += 1

        for line in range(len(self._table_lines.keys())):
            for i in range(len(self._header)):
                if i == 0:
                    self._watcher_table.setCellWidget(line, i, self._table_lines[line][i])
                else:
                    self._watcher_table.setItem(line, i, self._table_lines[line][i])

    def _activate_buttons(self, button_list):
        for i in button_list:
            widget, name = i
            logger.debug("Activating '{}' button.".format(name))
            self._buttons[widget][name].setEnabled(True)

    def _activate_export_button(self):
        export_buttons = [(self._export_field,"Exporter")]
        for i in self._core.supported_extensions():
            if (i != ".md" and self._core.export_ready()) or i == ".md":
                export_buttons.append((self._export_field,i))
        self._activate_buttons(export_buttons)
        # pdf and md will always be supported
        if self._core.export_ready():
            self._change_extension(".pdf")
        else:
            self._change_extension(".md")

    def _activate_watch_button(self):
        self._activate_buttons([(self._url_input,"Surveiller")])

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

        domain = self._core.get_supported_domains()[0] # only Edenya is supported for now
        login, password = self._core._secrets[domain].get_secrets()
        self._login_field.setText(login)
        self._password_field.setText(password)
        if all((login, password)):
            self._activate_watch_button()
            self._activate_export_button()
        else:
            logger.debug("No secrets available. Watch & export disabled.")
            self._popup_set_secrets(domain)

    def _save_login_password(self):
        login = self._login_field.text()
        password = self._password_field.text()
        domain = self._core.get_supported_domains()[0] # only Edenya is supported for now
        if all((login, password)):
            self._core.set_domain_secrets((login, password), domain)
            self._activate_watch_button()
            self._activate_export_button()

    def _popup_set_secrets(self, domain):
        self._popup = QDialog()
        form = QFormLayout()
        self._popup.setLayout(form)
        self._popup.setWindowTitle("Login & Mot de passe")

        text_label = QLabel()
        text_label.setText("Veuillez entrer vos login & mot de passe pour le site {}.".format(domain))
        form.addRow(text_label)

        self._login = QLineEdit()
        login_label = QLabel()
        login_label.setText("Login:")
        form.addRow(login_label,self._login)

        self._password = QLineEdit()
        password_label = QLabel()
        password_label.setText("Password:")
        form.addRow(password_label, self._password)

        ok_button = QPushButton("ok")
        ok_button.clicked.connect(self._popup_exit)
        form.addRow(ok_button)
        self._popup.exec_()

    def _popup_exit(self):
        login = self._login.text()
        password = self._password.text()
        domain = self._core.get_supported_domains()[0] # only Edenya is supported for now
        if all((login,password)):
            self._core.set_domain_secrets((login, password), domain)
            self._activate_watch_button()
            self._activate_export_button()
        else:
            logger.info("Login or password not provided in secrets popup.")
        self._popup.done(0)

class MainWindow(QMainWindow):

    def __init__(self, core_instance, menu_bar_dict={}, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ymael - surveillance et export de RP")
        self.setGeometry(0, 0, 800, 600) # left, top, width, height

        self._menu_bar = self.menuBar()
        self._menu_bar_items = {}
        for string,values in menu_bar_dict.items():
            self._menu_bar_items[string] = CustomMenu(string)
            self._menu_bar_items[string].create_menu(values)
            self._menu_bar.addMenu(self._menu_bar_items[string])

        self._table_widget = Tabs(core_instance, self)
        self.setCentralWidget(self._table_widget)
        logger.info("Showing main window.")
        self.show()
