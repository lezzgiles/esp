#!/python26/python.exe
# -*- coding: UTF-8 -*-

# enable debugging
import cgitb
import cgi
import sys
from myutils import c,cursor,sql, printHeader, printFooter, gotoButton, centsToDollarString, dollarStringToCents, cell, moneyCell, getItemName

cgitb.enable()

form = cgi.FieldStorage()

printHeader('New sale details')

if not form.has_key('AddSale'):
    print '<p class=error>Sorry - missing input fields; please use the navigation buttons to go to another page</p>'

buyer = form['buyer'].value
shipping = form['shipping'].value
if form.has_key('reconcile'):
    tranType = 'RECONCILE'
else:
    tranType = 'REAL'
maxItemIdx = form['addLastItem'].value

print '<H2>Select items to fill shipment</H2>'

print '<FORM ACTION=sales.py>'
print '<INPUT TYPE=HIDDEN NAME=addSale VALUE=1>'
print '<INPUT TYPE=HIDDEN NAME=buyer VALUE="%s" />'%buyer
print '<INPUT TYPE=HIDDEN NAME=shipping VALUE="%s" />'%shipping
if form.has_key('reconcile'):
    print '<INPUT TYPE=HIDDEN NAME=reconcile VALUE=1 />'
    
# Now print move table for each item
for i in range(1,int(maxItemIdx)+1):
    if form.has_key('addItem-'+str(i)):
        itemId = form['addItem-'+str(i)].value
        quantity = form['quantity-'+str(i)].value
        pricePerItem = dollarStringToCents(form['pricePerItem-'+str(i)].value)
        cursor.execute('SELECT manufacturer,brand,name FROM Item WHERE itemId = ?',(itemId,))
        (mfg,brand,name) = cursor.fetchone()
        print "<H3>Item %s</H3>"%getItemName(mfg,brand,name)

        cursor.execute('''
SELECT
    binId,Bin.name,SUM(quantity)
FROM
    Bin
    INNER JOIN BinItems using (binId)
    INNER JOIN Item USING (ItemId)
WHERE ItemId = ?
GROUP BY binId
    ''',(itemId,))

        totalFound = 0
        bins = []
        for (binId,binName,binQuantity) in cursor:
            totalFound += binQuantity
            bins.append([binId,binName,binQuantity])

        if totalFound < int(quantity):
            print "<p class=error>Cannot find enough %s to fill the order - need %s, but can only find %d</p>"%(getItemName(mfg,brand,name),quantity,totalFound)
        print '<p>Need %s items; got <INPUT TYPE=TEXT SIZE=4 VALUE=0 ID=moved-%s /> items</p>'%(quantity,itemId)
        print '<INPUT TYPE=HIDDEN NAME=numberOfBins-%s VALUE=%d />'%(itemId,len(bins))
        print '<INPUT TYPE=HIDDEN NAME=pricePerItem-%s VALUE=%d />'%(itemId,pricePerItem)
        
        print '<TABLE BORDER=1>'
        print '<TR><TH>Bin</TH><TH>Avail</TH><TH>Selected</TH></TR>'

        thisRow = 2        
        for (binId,binName,binQuantity) in bins:
            print '<TR>'
            print '<TD>%s<INPUT TYPE=HIDDEN NAME=id-%s-%d VALUE=%s></TD>'%(binName,itemId,thisRow,binId)
            print '<TD><INPUT TYPE=TEXT SIZE=4 ID=avail-%s-%s VALUE=%d /></TD>'%(itemId,thisRow,binQuantity)
            print '<TD>'
            print "<SCRIPT LANGUAGE=JAVASCRIPT>document.write(incIncDecField('qty-%s-%s',%d,'moved-%s','avail-%s-%s'));</SCRIPT>"%(itemId,thisRow,binQuantity,itemId,itemId,thisRow)
            print '</TD>'
            print '</TR>'
            thisRow += 1
        print '</TABLE>'            

print '<INPUT TYPE=SUBMIT VALUE="Add new sale">'            
print '</FORM>'

printFooter()
