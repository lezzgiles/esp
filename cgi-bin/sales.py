#!/python26/python.exe
# -*- coding: UTF-8 -*-

# enable debugging
import cgitb
import cgi
import sys
from myutils import c,cursor,sql, printHeader, printFooter, gotoButton, centsToDollarString, dollarStringToCents, cell, moneyCell, getItemName

cgitb.enable()

form = cgi.FieldStorage()

printHeader('Sales')

#cgi.print_form(form)
################
# Get list of items for add sale form

cursor.execute("SELECT itemId,manufacturer,brand,name FROM item ORDER BY manufacturer,brand,name")
itemOptions = []
for (itemId,manufacturer,brand,name) in cursor:
    itemOptions.append('<OPTION VALUE=%s>%s</OPTION>'%(itemId,getItemName(manufacturer,brand,name)))
    
#####
# Add form

print '''
<div class=addthing>
<FORM name=addTran ACTION=newSaleDetails.py>
<H2>Add new sale</H2>
<p />
Buyer: <INPUT TYPE=TEXT NAME=buyer ID=buyer SIZE=40 />
<br />
Shipping costs: <INPUT TYPE=TEXT CLASS=money NAME=shipping ID=shipping VALUE=0.00 SIZE=5 onBlur='moneyFormat(event.target)'/>
Reconcile entry: <INPUT TYPE=checkbox NAME=reconcile />
<br />
<TABLE BORDER=1 ID=addTranItemTable>
<TR><TH>Item</TH><TH>Qty</TH><TH>Cost/item</TH></TR>
</TABLE>
<INPUT TYPE=HIDDEN ID=addTranItemTableLastRow NAME=addLastItem VALUE=0 />
<INPUT TYPE=button VALUE='add another item' onClick='addItemRow();' />
<p />
<INPUT TYPE=SUBMIT VALUE='Add new sale' NAME=AddSale onClick='return validateForm();' />
</FORM>
</div>
'''

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
        checkField('buyer',"You must enter the buyer name") &&
        checkField('shipping','You must enter a value (possibly 0) for shipping')
        );
}

document.getElementById('addTranItemTableLastRow').value = '0';
addItemRow();
</SCRIPT>
'''

################
# Handle add sale

if form.has_key('addSale'):
    try:
        #cgi.print_form(form)
        buyer = form['buyer'].value
        shipping = dollarStringToCents(form['shipping'].value)
        if form.has_key('reconcile'):
            tranType = 'RECONCILE'
        else:
            tranType = 'REAL'
        cursor.execute('BEGIN IMMEDIATE TRANSACTION')
        cursor.execute("INSERT INTO Trans (type,direction,tranDate,description,shipping) VALUES (?,'DEL',DATE('now'),?,?)",
                       (tranType,buyer,shipping))
        tranId = cursor.lastrowid

        numberOfBins = {}
        for field in form.keys():
            if field.startswith('numberOfBins-'):
                numberOfBins[field.replace('numberOfBins-','')] = int(form[field].value)

        for itemId in numberOfBins.keys():
            totalQuantity = 0
            pricePerItem = form['pricePerItem-'+itemId].value
            for binNumber in range(2,numberOfBins[itemId]+2):
                binId = form['id-%s-%d'%(itemId,binNumber)].value
                qty = int(form['qty-%s-%d'%(itemId,binNumber)].value)
                totalQuantity += qty
                cursor.execute("SELECT SUM(quantity) FROM binItems WHERE binId = ? AND itemId = ?",(binId,itemId))
                (foundQty,)= cursor.fetchone()
                foundQty = int(foundQty)
                if foundQty < qty:
                    raise ValueError,'<p class=error>Database changed - needed %d items but only found %d - aborting sale</p>'%(qty,foundQty)
                cursor.execute('DElETE FROM binItems WHERE binId = ? AND itemId = ?',(binId,itemId))
                if foundQty != qty:
                    cursor.execute('INSERT INTO binItems (binId,itemId,quantity) VALUES (?,?,?)',(binId,itemId,foundQty-qty))
                
            cursor.execute('INSERT INTO TransItem (tranId,itemId,quantity,pricePerItem) VALUES (?,?,?,?)',
                           (tranId,itemId,totalQuantity,pricePerItem))
        c.commit()
    except Exception,e:
        c.rollback()
        print "<p class=error>Problem with database update:</p><pre>",sys.exc_info(),"</pre>"
    
################
# List of sales
cursor.execute('''
SELECT
    tranId,type, direction,tranDate,description,shipping,SUM(quantity*pricePerItem)
FROM Trans
LEFT JOIN TransItem USING (tranId)
WHERE direction == 'DEL'
GROUP BY tranId
ORDER BY tranDate DESC
''')

print "<TABLE BORDER=1 class='listthings sortable'>"
print "<TR><TH>Type</TH><TH>Date</TH><TH>Buyer</TH><TH>Total cost</TH><TH></TH></TR>"
for (tranId,type,direction,tranDate,buyer,shipping,totalCost) in cursor:
    if type == 'REAL':
        if direction == 'ADD':
            typeDetail = 'Purchase'
        else:
            typeDetail = 'Sale'
    else:
        if direction == 'ADD':
            typeDetail = 'Reconcile<br />add'
        else:
            typeDetail = 'Reconcile<br />del'

    
    print "<TR>"
    print cell(typeDetail)
    print cell(tranDate)
    print cell(buyer)
    print moneyCell(int(shipping)+int(totalCost))
    print "<TD>",gotoButton('See details','saleDetails.py?tranId=%s'%tranId),"</TD>"
    print "</TR>"
print "</TABLE>"

printFooter()
