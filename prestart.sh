#! /usr/bin/env bash
# Run custom Python script before starting
cd /app

echo "Initial MySQL Database" 
python -m app.initializeMysql

echo "Check if no QA data in MySQL Database then we import QA to MySQL" 
python -m app.checkQAmysql