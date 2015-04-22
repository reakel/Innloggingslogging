#!/bin/bash
# soerger for at innloggingsserver kjoerer

if ps aux | grep innloggingserver | grep -v grep > /dev/null; then
    exit
else
    python /usr/local/share/innloggingslogging/innloggingserver.py&
    exit
fi

exit
