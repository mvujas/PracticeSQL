#!/bin/bash

if [ -z $1 ]
then
	echo You must enter password
	exit 1
fi

PASSWORD=$1

if [ ! -f database.db ]
then
	cat init.sql | sqlite3 database.db
	echo Database initialized successfully
fi

SECRET_KEY=$(python init.py)
FILE=settings.py
echo \# ------CONFIG FILE------ > $FILE
echo PASSWORD = \'$PASSWORD\' >> $FILE
echo SECRET_KEY = $SECRET_KEY >> $FILE
echo DATABASE = \'database.db\' >> $FILE
echo New config file is initialized
