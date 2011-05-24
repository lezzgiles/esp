#!/python26/python.exe
# -*- coding: UTF-8 -*-

# enable debugging
import cgitb
import cgi
import sys
from myutils import c,cursor,sql, printRedirect,printHeader1,printHeader2, printFooter, gotoButton, centsToDollarString, centsToString,dollarStringToCents,cell,moneyCell,getTranType,getItemName

cgitb.enable()

form = cgi.FieldStorage()

printHeader1('Sale Details')

errorString = None

tranId = form['tranId'].value

if form.has_key('tracking'):
    try:
        tracking = form['tracking'].value
        actualShipping = dollarStringToCents(form['actualShipping'].value)
        cursor.execute('BEGIN IMMEDIATE TRANSACTION')
        cursor.execute('UPDATE Trans SET tracking=?, actualShipping=? WHERE tranId = ?',(tracking,actualShipping,tranId))
        c.commit()
        # redirect to page, so page reload doesn't re-add change
        printRedirect('Updating Sale','sales.py',0)
        sys.exit()
    except Exception,e:
        c.rollback()
        errorString = "<p class=error>Problem with database updte:</p><pre></pre>"%str(sys.exc_info())

printHeader2('Sale Details',errorString)

cursor.execute('SELECT type,direction,tranDate,description,shipping,actualShipping,tracking FROM Trans where tranId = ?',(tranId,))
(type,direction,tranDate,description,shipping,actualShipping,tracking) = cursor.fetchone()


mytype = getTranType(type,direction)

print '<H2>Details for %s: %s</H2>'%(mytype,description)
print '<p>Date: %s</p>'%tranDate

cursor.execute('SELECT manufacturer,brand,name,quantity,pricePerItem FROM TransItem LEFT JOIN Item USING (itemId) WHERE tranId = ?',
               (tranId,))

print '<TABLE BORDER=1><TR><TH>Item</TH><TH>qty</TH><TH>unit price</TH><TH>tot price</TH>'
totalPrice = 0
for (manufacturer,brand,name,quantity,pricePerItem) in cursor:
    itemsTotalPrice = (int(quantity)*int(pricePerItem))
    totalPrice += itemsTotalPrice
    print '<TR>'
    print cell(getItemName(manufacturer,brand,name))
    print cell(quantity)
    print moneyCell(pricePerItem)
    print moneyCell(itemsTotalPrice)
    print '</TR>'

print "<TR><TD COLSPAN=3 ALIGN=RIGHT>Shipping:</TD>",moneyCell(shipping),"</TR>"
totalPrice += shipping
print "<TR><TD COLSPAN=3 ALIGN=RIGHT><b>Total:</b></TD>",moneyCell(totalPrice),"</TR>"
print "</TABLE>"

print "<FORM name=modTran ACTION=saleDetails.py>"
print "<INPUT TYPE=hidden NAME=tranId VALUE=%s>"%tranId
print "Actual shipping costs: <INPUT TYPE=TEXT CLASS=money NAME=actualShipping ID=actualShipping VALUE=%s SIZE=5 onBlur='moneyFormat(event.target)'/>"%centsToString(actualShipping)
print "Tracking number: <INPUT TYPE=TEXT NAME=tracking ID=tracking VALUE=%s SIZE=25/>"%tracking
print "<BR />"
print "<INPUT TYPE=submit VALUE=update />"
print "</FORM name=modTran>"

printFooter()
