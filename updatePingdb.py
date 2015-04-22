#!/usr/bin/python
#-*- coding:utf-8 -*-


#bare midlertidig. Erik
import sys
import sqlite3 as lite

dbcon = lite.connect("/usr/local/share/innloggingslogging/innlogging.db")
with dbcon:
    cur = dbcon.cursor()
    cur.execute("UPDATE maskiner SET uttidspunkt ='0' WHERE maskinnavn='NT-07700'")
