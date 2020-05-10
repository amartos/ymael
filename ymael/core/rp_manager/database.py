#!/usr/bin/env python3

import os
import sqlite3
import atexit
import logging
logger = logging.getLogger(__name__)


class Database:

    def __init__(self, db_path, db_script=""):
        self._date_format = "%Y-%m-%d %H:%M:%S"
        self._db_conn = sqlite3.connect(db_path)
        self._db_curs = self._db_conn.cursor()
        atexit.register(self.close)
        if not os.path.exists(db_path) and db_script:
            self._create_new_db(db_script)

###############################################################################
# Public functions
###############################################################################

    def insert_rows(self, table_name, column_names, values, replace=False):
        # column_names is a list and values a list of tuples (aka rows) with
        # data in same order of column_names
        fallback = "ignore"
        if replace:
            fallback = "replace"
        table_name = self._escape_str(table_name)
        column_names = [self._escape_str(n) for n in column_names]

        query = "insert or "+fallback+" into "+table_name+" ("+",".join(column_names)
        query += ") values "
        for row in values:
            query += "("+"?,"*(len(row)-1)+"?), "
        query = query[:-2]+";" # remove the last ", " and close the query

        args = self._unpack_list(values)

        self._db_curs.execute(query, tuple(args))

    def delete_rows(self, table_name, conditions, use_or=False):
        self._search("delete", table_name, conditions, use_or)

    def search_rows(self, table_name, conditions=[], use_or=False, column_order="", reverse=False):
        self._search("select *", table_name, conditions, use_or, column_order, reverse)

    def get_results(self):
        return self._db_curs.fetchone()

    def get_row(self, table_name, conditions, use_or=False):
        self.search_rows(table_name, conditions, use_or)
        return self._db_curs.fetchone()

    def is_table(self, table_name):
        conditions = [
                ("type", "table"),
                ("name", table_name)
                ]
        return self.is_row("sqlite_master", conditions, search_key="name")

    def is_row(self, table_name, conditions, use_or=False, search_key="*"):
        command_string = "select "+search_key
        self._search(command_string, table_name, conditions, use_or)
        if self._db_curs.fetchone() == None:
            return False
        return True

    def create_table(self, table_name, columns, primary_keys, foreign_keys=[]):
        table_name = self._escape_str(table_name)
        primary_keys = [self._escape_str(k) for k in primary_keys]

        query = "create table if not exists "+table_name+"("
        for c in columns:
            c = [self._escape_str(c[0]), *c[1:]]
            query += " ".join(c)+", "

        if foreign_keys:
            for keys in foreign_keys:
                keys = [self._escape_str(k) for k in keys]
                query += "foreign key ("+keys[0]+") references "+keys[1]+"("+keys[2]+"), "

        query += "primary key ("+",".join(primary_keys)+"));"
        self._db_curs.execute(query)

    def get_date_format(self):
        return self._date_format

###############################################################################
# Private functions
###############################################################################

    def close(self):
        try:
            self._db_conn.commit()
            self._db_conn.close()
        except sqlite3.ProgrammingError:
            # if database is already closed
            pass

    def _create_new_db(self, db_script):
        self._db_curs.executescript(db_script)

    def _search(self, command_string, table_name, conditions=[], use_or=False, column_order="", reverse=False):
        # conditions is a list of tuples containing (key,values) used for the
        # search all values in condtions are linked by AND by default, or OR if
        # use_or is True

        table_name = self._escape_str(table_name)

        ordering = ""
        if column_order:
            column_order = self._escape_str(column_order)
            direction = "asc"
            if reverse:
                direction = "desc"
            ordering = " order by "+column_order+" "+direction

        if not conditions:
            query = "select * from "+table_name+ordering+";"
            self._db_curs.execute(query)
            return

        query = command_string+" from "+table_name+" where "
        operator = " and "
        if use_or:
            operator = " or "
        for c in conditions:
            s = self._escape_str(c[0])
            query += s+"=?"+operator
        query = query[:-len(operator)]+ordering+";" # remove last operator and close

        args = tuple([c[1] for c in conditions])
        self._db_curs.execute(query, args)

    def _unpack_list(self, packed):
        return [i for l in packed for i in l]

    def _escape_str(self, string):
        temp = string.replace(" ", "_")
        temp = temp.replace("\"", "")
        temp = temp.replace("'", "")
        return temp
