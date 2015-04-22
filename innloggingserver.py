#!/usr/bin/python
# -*- coding: utf-8 -*-

# Dette skriptet kjører kontinuerlig, og tar imot innloggingsmeldinger 
# fra salmaskiner. Disse parses og loggføres i databasen.

import socket
import sys
import sqlite3 as lite
from datetime import datetime
import os

HOST = ''
PORT = 5673

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)

try:
    s.bind((HOST,PORT))
except socket.error, msg:
    s.close()
    sys.exit()
s.listen(10)

# Databasetilkobling
dbcon = lite.connect('/usr/local/share/innloggingslogging/innlogging.db')
dbcon.text_factory = str

# Finn datasaler og maskinnummerintervall
cur = dbcon.cursor()
cmd = "SELECT * FROM datasaler"
cur.execute(cmd)
saler = cur.fetchall()

#print rows
#salfil = open("/usr/local/share/innloggingslogging/datasaler.txt")
#saler = salfil.readlines()
#salfil.close()

#print saler[0][0]
while 1:
    conn, addr = s.accept()
    # Dette må endres hvis annen informasjon skal sendes
    data = conn.recv(1024)
    # Dette deler opp data-str, første string skal være 'login', ellers forkastes meldingen
#   print data
    info = data.split('Z')
    id = info[0]
    mnavn = info[1]
    inntid = info[2]
    dprinter = info[3]
    try:
        sistinst=info[4]
    except:
        #i tilfelle maskinen ikke er oppdatert til å sende sist installasjonsdato
        sistinst = 'ukjent'
#   try:
    #   id,mnavn,inntid,dprinter = data.split('Z')
    #except:
    #   conn.close()
    mnr = mnavn[4:]
    if id == 'login':
        conn.close()
        with dbcon:
            cur = dbcon.cursor()
            cmd1 = "UPDATE maskiner SET inntidspunkt = ? WHERE maskinnavn = ?"
            cur.execute(cmd1, (inntid,mnavn))
            cmd2 = "UPDATE maskiner SET defaultprinter = ? WHERE maskinnavn = ?"
            cur.execute(cmd2, (dprinter,mnavn))
            for saldict in saler:
                sal = saldict[0]
                m1 = saldict[1]
                m2 = saldict[2]
                printer = saldict[3]
                #[sal,m1,m2,printer]=line.split()
                if m1 <= mnr <= m2:
                    dsal = sal
                    break
            else:
                 dsal = 'unknown'

            # Bruker isoformat YYYY-MM-DD HH:MM for sortering
            isotid = inntid[6:10] + '-' + inntid[3:5] + '-' \
                   + inntid[:2] + ' ' + inntid[11:]
            if sistinst != 'ukjent':
                isoinsttid = sistinst[6:10] + '-' + sistinst[3:5] + '-' \
                           + sistinst[:2]
            else:   
                isoinsttid = 'ukjent'
            cmd3 = "INSERT INTO tider VALUES(?,?,?,?)"
            cur.execute(cmd3, (mnavn,isotid,dsal,isoinsttid))
            cmd4 = "UPDATE maskiner SET sistinst = ? WHERE maskinnavn = ?"
            cur.execute(cmd4, (isoinsttid,mnavn))
#           print info
    elif id == 'logout': # Kjør utloggingsgreier
#       print info
        conn.close()
        with dbcon:
            cur = dbcon.cursor()
            cmd1 = "INSERT INTO uttider VALUES (?,?,?,?)"
            isotid = inntid[6:10] + '-' + inntid[3:5] + '-' \
                   + inntid[:2] + ' ' + inntid[11:]
            cur.execute(cmd1, (mnavn,isotid,"",""))          
            
            # Lag entry i sessions-table: finn siste innloggingstid
            try:
                # Litt haxx for kanskje aa utelukke noen feil
                if (isotid[-5:] != "03:01"): 
#                   print "utlogg: "+mnavn+" "+isotid

                    # Hvis alt ok:
                    cmd2 = "SELECT * FROM tider WHERE maskinnavn = ? ORDER BY inntidspunkt DESC LIMIT 1"
                    cur.execute(cmd2, (mnavn,))
                    lastinnlogging = cur.fetchone()
                    lastinntid = lastinnlogging[1]
                    # Test om denne innloggingen allerede finnes i sessions:
                    # hvis ja mangler en innlogging, og sessionen må droppes(?)
                    cmd3 = "SELECT * FROM sessions WHERE maskinnavn = ? ORDER BY inntidspunkt DESC LIMIT 1"
                    cur.execute(cmd3, (mnavn,))
                    lastsess = cur.fetchone()
                    #print lastsess
                    #print lastsess[1]
                    if (lastsess[1] != lastinntid):
                        cmd4 = "INSERT INTO sessions VALUES (?,?,?)"
                        cur.execute(cmd4, (mnavn,lastinntid,isotid))
                #print isotid
                #print lastinntid
            except:
                # Ingen gyldig session kunne lages
                with open("log.txt", "a") as myfile:
                    myfile.write("Invalid session")


    else:
        conn.close()
    
s.close()
sys.exit()
