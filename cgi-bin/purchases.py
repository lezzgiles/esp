#!/python26/python.exe
# -*- coding: UTF-8 -*-

# enable debugging
import cgitb
import cgi
from myutils import c,cursor,sql, printHeader, printFooter, gotoButton, centsToDollarString, dollarStringToCents, cell, moneyCell, getTranType, getItemName

cgitb.enable()

form = cgi.FieldStorage()

printHeader('Purchases')

#cgi.print_form(form)

################
# Get list of items for add purchase form

cursor.execute("SELECT itemId,manufacturer,brand,name FROM item ORDER BY manufacturer,brand,name")
itemOptions = []
for (itemId,manufacturer,brand,name) in cursor:
    itemOptions.append('<OPTION VALUE=%s>%s</OPTION>'%(itemId,getItemName(manufacturer,brand,name)))
    
#####
# Add form

print "<div class=addthing>"
print "<H2>New purchase</H2>"
print "<FORM name=addTran>"
print "Seller: <INPUT TYPE=TEXT NAME=seller ID=seller SIZE=40/>"
print "<br />"
print "Shipping costs: <INPUT TYPE=TEXT CLASS=money VALUE=0.00 NAME=shipping ID=shipping SIZE=5 onBlur='moneyFormat(event.target)'/>"
print "Reconcile entry: <INPUT TYPE=checkbox NAME=reconcile />"
print "<p />"
print "<TABLE BORDER=1 ID=addTranItemTable>"
print "<TR><TH>Item</TH><TH>Qty</TH><TH>Cost/item</TH></TR>"
print "</TABLE>"
print "<INPUT TYPE=HIDDEN ID=addTranItemTableLastRow NAME=addLastItem VALUE=0 />"
print "<INPUT TYPE=button VALUE='add another item' onClick='addItemRow();' />"
print "<p />"
print "<INPUT TYPE=SUBMIT VALUE='Add new purchase' NAME=AddPurchase onClick='return validateForm()' />"
print "</FORM>"
print "</div>"

print '''
<SCRIPT LANGUAGE="JavaScript">
function addItemRow()
{
    var tbl = document.getElementById('addTranItemTable');
    var lastRowElt = document.getElementById('addTranItemTableLastRow');
    var thisRow = parseInt(lastRowElt.value);
    thisRow += 1;
    lastRowElt.value = thisRow.toString();
    var rowId = tbl.rows.length;
    var newRow = tbl.insertRow(tbl.rows.length);
    newRow.id = 'addTranRow-'+thisRow;
    var newCell0 = newRow.insertCell(0);
    var newCell1 = newRow.insertCell(1);
    var newCell2 = newRow.insertCell(2);
    var newCell3 = newRow.insertCell(3);
    newCell0.innerHTML = '<SELECT NAME=addItem-'+thisRow+'>''',
for option in itemOptions:
    print option,
print '''</SELECT>';
    newCell1.innerHTML = '<INPUT TYPE=TEXT NAME=quantity-'+thisRow+' VALUE=1 SIZE=5/>';
    newCell2.innerHTML = '<INPUT TYPE=TEXT CLASS=money NAME=pricePerItem-'+thisRow+' SIZE=5 VALUE="0.00" onBlur=\\\'moneyFormat(event.target)\\\' />';
    newCell3.innerHTML = '<INPUT TYPE=button VALUE="delete item details" onClick=\\\'delItemRow('+thisRow+');\\\' />';
}
function delItemRow(delRowNumber)
{
    var tbl = document.getElementById('addTranItemTable');
    for (var i=0;i<tbl.rows.length; i++) {
        if (tbl.rows[i].id == 'addTranRow-'+delRowNumber) {
            tbl.deleteRow(i);
            break;
        }
    }
}

function validateForm()
{
    return (
        checkField('seller',"You must fill out a seller name") &&
        checkField('shipping',"You must enter the shipping cost")
        );
}

document.getElementById('addTranItemTableLastRow').value = '0';
addItemRow();
</SCRIPT>
'''

##################
# Handle add purchase request
if form.has_key('AddPurchase'):
    seller = form['seller'].value
    shipping = dollarStringToCents(form['shipping'].value)
    if form.has_key('reconcile'):
        tranType = 'RECONCILE'
    else:
        tranType = 'REAL'
    maxItemIdx = form['addLastItem'].value
    cursor.execute('BEGIN IMMEDIATE TRANSACTION')
    cursor.execute("INSERT INTO Trans (type,direction,tranDate,description,shipping) VALUES (?,'ADD',DATE('now'),?,?)",
                   (tranType,seller,shipping))
    tranId = cursor.lastrowid
    for i in range(1,int(maxItemIdx)+1):
        if form.has_key('addItem-'+str(i)):
            itemId = form['addItem-'+str(i)].value
            quantity = form['quantity-'+str(i)].value
            if int(quantity) == 0: continue
            pricePerItem = dollarStringToCents(form['pricePerItem-'+str(i)].value)
            cursor.execute('INSERT INTO TransItem (tranId,itemId,quantity,pricePerItem) VALUES (?,?,?,?)',
                           (tranId,itemId,quantity,pricePerItem))
            cursor.execute('INSERT INTO binItems (binId,itemId,quantity) VALUES (1,?,?)',(itemId,quantity))
    c.commit()

###########################
# List of purchases
cursor.execute('''
SELECT
    tranId,type,direction,tranDate,description,shipping,SUM(quantity*pricePerItem)
FROM Trans
LEFT JOIN TransItem USING (tranId)
WHERE direction == 'ADD'
GROUP BY tranId
ORDER BY tranDate DESC, tranid DESC
''')

print "<TABLE BORDER=1 class='listthings sortable'>"
print "<TR><TH>Type</TH><TH>Date</TH><TH>Seller</TH><TH>Total cost</TH><TH></TH></TR>"
for (tranId,type,direction,tranDate,seller,shipping,totalCost) in cursor:
    typeDetail = getTranType(type,direction)
    
    print "<TR>"
    print cell(typeDetail)
    print cell(tranDate)
    print cell(seller)
    print moneyCell(int(shipping)+int(totalCost))
    print "<TD>",gotoButton('See details','purchaseDetails.py?tranId=%s'%tranId),"</TD>"
    print "</TR>"
print "</TABLE>"



printFooter()

