#!/python26/python.exe
# -*- coding: UTF-8 -*-

# enable debugging
import cgitb
import cgi
import sqlite3
from myutils import sql, printHeader, printFooter, printOptions, centsToDollarString, getTranType

cgitb.enable()

form = cgi.FieldStorage()

c = sqlite3.connect('/temp/example')
cursor = c.cursor()

printHeader('Stock detail')

itemId = form['itemId'].value

cursor.execute('SELECT manufacturer,brand,name FROM item WHERE itemId = ?',(itemId))
(manufacturer,brand,name) = cursor.fetchone()
if not brand: brand = '-'
print "<b>Item transactions for %s:%s:%s</b>"%(manufacturer,brand,name)

cursor.execute('''
SELECT
    TransItem.quantity,TransItem.pricePerItem,tranDate,type,direction,description
FROM
    transItem
    INNER JOIN Trans USING (tranId)
WHERE
    itemId = ?
ORDER BY tranDate DESC
''',(itemId,))
print "<TABLE BORDER=1 class=listthings><TR>"
print "<TH>Purchase date</TH>"
print "<TH>Type</TH>"
print "<TH>Party</TH>"
print "<TH>Quantity</TH>"
print "<TH>Price/item</TH>"
print "</TR>"
for (quantity,pricePerItem,purchaseDate,type,direction,description) in cursor:
    tranType = getTranType(type,direction)
    print "<TR>"
    print "<TD>%s</TD>"%purchaseDate
    print "<TD>%s</TD>"%tranType
    print "<TD>%s</TD>"%description
    print "<TD>%d</TD>"%quantity
    print "<TD>%s</TD>"%centsToDollarString(pricePerItem)
    print "</TR>"
print "</TABLE>"


printFooter()