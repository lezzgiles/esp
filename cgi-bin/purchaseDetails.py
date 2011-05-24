#!/python26/python.exe
# -*- coding: UTF-8 -*-

# enable debugging
import cgitb
import cgi
from myutils import c,cursor,sql, printHeader, printFooter, gotoButton, centsToDollarString,cell,moneyCell,getTranType,getItemName

cgitb.enable()

form = cgi.FieldStorage()

printHeader('Purchase Details')

tranId = form['tranId'].value

cursor.execute('SELECT type,direction,tranDate,description,shipping FROM Trans where tranId = ?',(tranId,))
(type,direction,tranDate,description,shipping) = cursor.fetchone()

mytype = getTranType(type,direction)

print '<H2>Details for %s: %s</H2>'%(mytype,description)
print '<p>Date: %s</p>'%tranDate

sql = '''
SELECT
    manufacturer,
    brand,
    name,
    quantity,
    pricePerItem,
    shipping*priceperitem/(SELECT SUM(quantity*priceperitem) FROM transitem WHERE tranid = trans.tranid)
FROM
    TransItem
    LEFT JOIN Item USING (itemId)
    LEFT JOIN Trans ON transItem.tranId = Trans.tranid
    WHERE transitem.tranId = ?
'''

cursor.execute(sql,(tranId,))

print '<TABLE BORDER=1><TR><TH>Item</TH><TH>qty</TH><TH>unit price</TH><TH>prorated shipping</TH><TH>total per unit</TH><TH>tot price w/o shipping</TH></TR>'
totalPrice = 0
for (manufacturer,brand,name,quantity,pricePerItem,proratedShipping) in cursor:
    if not proratedShipping: proratedShipping = 0
    itemsTotalPrice = (int(quantity)*int(pricePerItem))
    totalPrice += itemsTotalPrice
    print '<TR>'
    print cell(getItemName(manufacturer,brand,name))
    print cell(quantity)
    print moneyCell(pricePerItem)
    print moneyCell(proratedShipping)
    print moneyCell(proratedShipping+pricePerItem)
    print moneyCell(itemsTotalPrice)
    print '</TR>'

print "<TR><TD COLSPAN=5 ALIGN=RIGHT>Shipping:</TD>",moneyCell(shipping),"</TR>"
totalPrice += shipping
print "<TR><TD COLSPAN=5 ALIGN=RIGHT><b>Total:</b></TD>",moneyCell(totalPrice),"</TR>"
print "</TABLE>"


printFooter()
