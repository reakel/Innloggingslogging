#!/usr/bin/python
#-*- coding: utf-8 -*-

# Skript som tar tar inn info fra pridewatcher som argument og føyer det 
# inn i innlogging.db

# testing!

import sys

fil = open("testOut.txt", "a")
fil.write(str(sys.argv))
fil.close()
