#!/python26/python.exe
# -*- coding: UTF-8 -*-

# enable debugging
import cgitb
import cgi
from myutils import c,cursor,sql, printHeader, printFooter, printOptions, centsToDollarString, getTranType, getItemName

cgitb.enable()

form = cgi.FieldStorage()

printHeader('Stock detail')

itemId = form['itemId'].value

cursor.execute('SELECT manufacturer,brand,name FROM item WHERE itemId = ?',(itemId,))
(manufacturer,brand,name) = cursor.fetchone()
print "<b>Item transactions for %s</b>"%getItemName(manufacturer,brand,name)

cursor.execute('''
SELECT
    TransItem.quantity,
    TransItem.pricePerItem,
    tranDate,
    type,
    direction,
    description,
    shipping*priceperitem/(SELECT SUM(quantity*priceperitem) FROM transitem WHERE tranid = trans.tranid)
FROM
    transItem
    INNER JOIN Trans USING (tranId)
WHERE
    itemId = ?
ORDER BY tranDate DESC
''',(itemId,))
print "<TABLE BORDER=1 class=listthings><TR>"
print "<TH>Date</TH>"
print "<TH>Type</TH>"
print "<TH>Party</TH>"
print "<TH>Qty</TH>"
print "<TH>Price/item</TH>"
print "<TH>Prorated<br />shipping</TH>"
print "<TH>Total<br />per unit</TH>"
print "</TR>"
for (quantity,pricePerItem,purchaseDate,type,direction,description,proratedShipping) in cursor:
    if not proratedShipping: proratedShipping = 0
    tranType = getTranType(type,direction)
    print "<TR>"
    print "<TD>%s</TD>"%purchaseDate
    print "<TD>%s</TD>"%tranType
    print "<TD>%s</TD>"%description
    print "<TD>%d</TD>"%quantity
    print "<TD>%s</TD>"%centsToDollarString(pricePerItem)
    print "<TD>%s</TD>"%centsToDollarString(proratedShipping)
    print "<TD>%s</TD>"%centsToDollarString(pricePerItem+proratedShipping)
    print "</TR>"
print "</TABLE>"


printFooter()