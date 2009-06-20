#!/python26/python.exe
# -*- coding: UTF-8 -*-

# enable debugging
import cgitb
import cgi
import sqlite3
from myutils import sql, printHeader, printFooter, gotoButton, centsToDollarString,cell,moneyCell,getTranType

cgitb.enable()

form = cgi.FieldStorage()

c = sqlite3.connect('/temp/example')
cursor = c.cursor()

printHeader('Sale Details')

tranId = form['tranId'].value

cursor.execute('SELECT type,direction,tranDate,description,shipping FROM Trans where tranId = ?',(tranId,))
(type,direction,tranDate,description,shipping) = cursor.fetchone()

mytype = getTranType(type,direction)

print '<H2>Details for %s: %s</H2>'%(mytype,description)
print '<p>Date: %s</p>'%tranDate

cursor.execute('SELECT manufacturer,brand,name,quantity,pricePerItem FROM TransItem LEFT JOIN Item USING (itemId) WHERE tranId = ?',
               (tranId,))

print '<TABLE BORDER=1><TR><TH>Item</TH><TH>qty</TH><TH>unit price</TH><TH>tot price</TH>'
totalPrice = 0
for (manufacturer,brand,name,quantity,pricePerItem) in cursor:
    if not brand: brand = '-'
    itemsTotalPrice = (int(quantity)*int(pricePerItem))
    totalPrice += itemsTotalPrice
    print '<TR>'
    print cell('%s:%s:%s'%(manufacturer,brand,name))
    print cell(quantity)
    print moneyCell(pricePerItem)
    print moneyCell(itemsTotalPrice)
    print '</TR>'

print "<TR><TD COLSPAN=3 ALIGN=RIGHT>Shipping:</TD>",moneyCell(shipping),"</TR>"
totalPrice += shipping
print "<TR><TD COLSPAN=3 ALIGN=RIGHT><b>Total:</b></TD>",moneyCell(totalPrice),"</TR>"
print "</TABLE>"


printFooter()
