#!/bin/bash

rm accounts.db
rm -r *.pyc
python db_create.py
python run.py