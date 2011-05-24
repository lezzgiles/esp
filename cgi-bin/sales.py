#!/python26/python.exe

# enable debugging
import cgitb
import cgi
import sys
from myutils import c,cursor,sql, printRedirect, printHeader1,printHeader2, printFooter, gotoButton, centsToDollarString, dollarStringToCents, cell, moneyCell, getItemName, getName

cgitb.enable()

form = cgi.FieldStorage()

printHeader1('Sales')

errorString = None

#cgi.print_form(form)

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

        history = "SELL %d"%tranId

        numberOfBins = {}
        kitSales = []

        for field in form.keys():
            if field.startswith('numberOfBins-'):
                numberOfBins[field.replace('numberOfBins-','')] = int(form[field].value)
            if field.startswith('kitId-'):
                key = field.replace('kitId-','')
                kitId = form[field].value
                qty = int(form['kitQty-'+key].value)
                kitSales.append((kitId,qty))

        for itemId in numberOfBins.keys():
            totalQuantity = 0
            pricePerItem = form['pricePerItem-'+itemId].value
            for binNumber in range(2,numberOfBins[itemId]+2):
                binId = form['id-%s-%d'%(itemId,binNumber)].value
                qty = int(form['qty-%s-%d'%(itemId,binNumber)].value)
                if qty != 0:
                    history += " %d %s FROM %s"%(qty,itemId,binId)
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

        for (kitId,qty) in kitSales:
            cursor.execute("SELECT quantity FROM Kit WHERE kitId = ?",(kitId,))
            (foundQty,) = cursor.fetchone()
            foundQty = int(foundQty)
            if foundQty < qty:
                raise ValueError,'<p class=error>Database changed - needed %s kit %s but only found %d - aborting sale</p>'%(qty,kitId,foundQty)
            cursor.execute('UPDATE Kit SET quantity = ? WHERE kitId = ?',(foundQty-qty,kitId))
                
        cursor.execute('''INSERT INTO history (historyDate,body) VALUES (DATETIME('now'),?)''',(history,))
        c.commit()
        # Redirect to same page, so page reload doesn't re-add sale
        printRedirect('Added Sale','sales.py',0)
        sys.exit()

    except Exception,e:
        c.rollback()
        errorString = "<p class=error>Problem with database update:</p><pre>%s</pre>"%str(sys.exc_info())

printHeader2('Sales',errorString)
    
################
# Get list of items for add sale form

cursor.execute("SELECT itemId,manufacturer,brand,name FROM item INNER JOIN binItems USING (itemId) WHERE quantity > 0 GROUP BY manufacturer,brand,name ORDER BY manufacturer,brand,name")
itemOptions = []
for (itemId,manufacturer,brand,name) in cursor:
    itemOptions.append('<OPTION VALUE=Item%s>%s</OPTION>'%(itemId,getItemName(manufacturer,brand,name)))
###################
# Get list of kits for add sale form

cursor.execute("SELECT kitId,name FROM Kit ORDER BY name")
for (kitId,name) in cursor:
    itemOptions.append('<OPTION VALUE=Kit%s>Kit: %s</OPTION>'%(kitId,getName(name)))

#####
# Add form

print '''
<div class=addthing>
<H2>Add new sale</H2>
<FORM name=addTran ACTION=newSaleDetails.py>
Buyer: <INPUT TYPE=TEXT NAME=buyer ID=buyer SIZE=40 />
<br />
Reconcile entry: <INPUT TYPE=checkbox NAME=reconcile />
<br />
<TABLE BORDER=1 ID=addTranItemTable>
<TR><TH>Item</TH><TH>Qty</TH><TH>Cost/item</TH><TH>Total</TH></TR>
<TR><TD COLSPAN=3>Shipping costs:</TD><TD><INPUT TYPE=TEXT CLASS=money NAME=shipping ID=shipping VALUE=0.00 SIZE=5 onBlur='moneyFormat(event.target);calcTotals()'/></TD></TR>
<TR><TD COLSPAN=3>Total:</TD><TD><INPUT TYPE=TEXT CLASS=money ID=total VALUE=0.00 SIZE=5 READONLY /></TD>
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
    var newRow = tbl.insertRow(tbl.rows.length-2);
    newRow.id = 'addTranRow-'+thisRow;
    var newCell0 = newRow.insertCell(0);
    var newCell1 = newRow.insertCell(1);
    var newCell2 = newRow.insertCell(2);
    var newCell3 = newRow.insertCell(3);
    var newCell4 = newRow.insertCell(4);
    newCell0.innerHTML = '<SELECT NAME=addItem-'+thisRow+'>''',
for option in itemOptions:
    print option,
print '''</SELECT>';
    newCell1.innerHTML = '<INPUT TYPE=TEXT NAME=quantity-'+thisRow+' ID=quantity-'+thisRow+' VALUE=1 SIZE=5 onBlur=\\\'calcTotals()\\\'/>';
    newCell2.innerHTML = '<INPUT TYPE=TEXT CLASS=money NAME=pricePerItem-'+thisRow+' ID=pricePerItem-'+thisRow+' SIZE=5 VALUE="0.00" onBlur=\\\'moneyFormat(event.target);calcTotals()\\\' />';
    newCell3.innerHTML = '<INPUT TYPE=TEXT CLASS=money NAME=total-'+thisRow+' ID=total-'+thisRow+' SIZE=5 VALUE="0.00" READONLY />';
    newCell4.innerHTML = '<INPUT TYPE=button VALUE="delete item details" onClick=\\\'delItemRow('+thisRow+');calcTotals()\\\' />';
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

function calcTotals()
{
    var table = document.getElementById('addTranItemTable');
    var totalTotal = 0;
    for (var rowId=1; rowId<table.rows.length-2; rowId++) {
        row = table.rows[rowId]
        rowQty = row.cells[1].childNodes[0];
        rowPrice = row.cells[2].childNodes[0];
        rowTotal = row.cells[3].childNodes[0];
        rowTotal.value = rowPrice.value * rowQty.value;
        moneyFormat(rowTotal);
        totalTotal += dollars2cents(rowTotal);
    }
    totalTotal += dollars2cents(document.getElementById('shipping'))
    total = document.getElementById('total');
    total.value = cents2dollars(totalTotal);
    moneyFormat(total);
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

function setFocus()
{
   document.getElementById('buyer').focus();
}
window.onload = setFocus;
</SCRIPT>
'''

################
# List of sales
cursor.execute('''
SELECT
    tranId,type, direction,tranDate,description,shipping,SUM(quantity*pricePerItem)
FROM Trans
LEFT JOIN TransItem USING (tranId)
WHERE direction == 'DEL'
GROUP BY tranId
ORDER BY tranDate DESC, tranid DESC
LIMIT 200
''')
print "<H2>Last 200 sales:</H2>"
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
