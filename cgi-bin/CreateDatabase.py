#!/python26/python.exe
# -*- coding: UTF-8 -*-

# enable debugging
import cgitb
import sqlite3
from myutils import c,cursor,sql

cgitb.enable()

print "Content-Type: text/html;charset=utf-8"
print
print "Creating database..."


sqlStatements = (
# Transactions - purchases & sales
'DROP TABLE IF EXISTS Trans',
# type is 'REAL' or 'RECONCILE'
# direction is 'ADD' or 'DELETE'
'''CREATE TABLE Trans (
    tranId INTEGER PRIMARY KEY,
    type TEXT,
    direction TEXT,
    tranDate TEXT NOT NULL,
    description STRING NOT NULL,
    shipping INTEGER NOT NULL
)''',
# items bought or sold
'DROP TABLE IF EXISTS TransItem',
'''CREATE TABLE TransItem(
    tranId INTEGER NOT NULL,
    itemId INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    pricePerItem INTEGER NOT NULL
)''',
# item types
'DROP TABLE IF EXISTS Item',
'''CREATE TABLE Item (
    itemId INTEGER PRIMARY KEY,
    manufacturer TEXT NOT NULL,
    brand TEXT,
    name TEXT NOT NULL
)''',
'''CREATE UNIQUE INDEX IF NOT EXISTS FullItemName ON Item(manufacturer,name)''',
# bins
'DROP TABLE IF EXISTS Bin',
'''CREATE TABLE Bin (
    binId INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    slots INTEGER
)''',
# The system assumes unstocked exists, and its index is 1
'INSERT INTO Bin (name) VALUES ("unstocked")',
# items stored in bins
'DROP TABLE IF EXISTS BinItems',
'''CREATE TABLE BinItems (
    binId INTEGER NOT NULL,
    itemId INTEGER NOT NULL,
    quantity INTEGER NOT NULL
)''',

# List of items in ebay
'DROP TABLE IF EXISTS ebayList',
'''CREATE TABLE ebayList (
 title TEXT NOT NULL,
 quantity INTEGER NOT NULL
)''',
# Link table from ebay listing items to stock items
'DROP TABLE IF EXISTS ebayList2Item',
'''CREATE TABLE ebayList2Item (
    title TEXT PRIMARY KEY,
    itemId INTEGER NOT NULL
)''')

for stmt in sqlStatements: sql(c,stmt)
print '<HR>'