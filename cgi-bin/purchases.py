#!/python26/python.exe

# enable debugging
import cgitb
import cgi
from myutils import c,cursor,sql,printRedirect, printHeader1,printHeader2, printFooter, gotoButton, centsToDollarString, dollarStringToCents, cell, moneyCell, getTranType, getItemName
import sys

cgitb.enable()

form = cgi.FieldStorage()

printHeader1('Purchases')

errorString = None

#cgi.print_form(form)

##################
# Handle add purchase request
if form.has_key('AddPurchase'):
    try:
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

        history = "BUY %d"%tranId

        for i in range(1,int(maxItemIdx)+1):
            if form.has_key('addItem-'+str(i)):
                itemId = form['addItem-'+str(i)].value
                quantity = form['quantity-'+str(i)].value
                if int(quantity) == 0: continue
                history += " %s OF %s TO 1"%(quantity,itemId)    # binId 1 - unstocked - is hard-coded
                pricePerItem = dollarStringToCents(form['pricePerItem-'+str(i)].value)
                cursor.execute('INSERT INTO TransItem (tranId,itemId,quantity,pricePerItem) VALUES (?,?,?,?)',
                               (tranId,itemId,quantity,pricePerItem))
                cursor.execute('INSERT INTO binItems (binId,itemId,quantity) VALUES (1,?,?)',(itemId,quantity))
            elif form.has_key('addMfr-'+str(i)):
                mfr = form['addMfr-'+str(i)].value.strip()
                if len(mfr) == 0: mfr = None
                if form.has_key('addBrand-'+str(i)):
                    brand = form['addBrand-'+str(i)].value.strip()
                    if len(brand) == 0: brand = None
                else:
                    brand = None
                if form.has_key('addName-'+str(i)):
                    name = form['addName-'+str(i)].value.strip()
                    if len(name) == 0: name = None
                else:
                    name = None
                name = form['addName-'+str(i)].value.strip()
                quantity = int(form['quantity-'+str(i)].value)
                if quantity == 0: continue
                if not name: raise ValError,"Empty item type name"
                cursor.execute("INSERT INTO item (manufacturer,brand,name) VALUES (?,?,?)",(mfr,brand,name))
                itemId = cursor.lastrowid
                history += " %s OF %s TO 1"%(quantity,itemId)    # binId 1 - unstocked - is hard-coded
                pricePerItem = dollarStringToCents(form['pricePerItem-'+str(i)].value)
                cursor.execute('INSERT INTO TransItem (tranId,itemId,quantity,pricePerItem) VALUES (?,?,?,?)',
                               (tranId,itemId,quantity,pricePerItem))
                cursor.execute('INSERT INTO binItems (binId,itemId,quantity) VALUES (1,?,?)',(itemId,quantity))

        cursor.execute('''INSERT INTO history (historyDate,body) VALUES (DATETIME('now'),?)''',(history,))
        c.commit()
        # redirect to same page, so reload doesn't re-add purchase
        printRedirect('Added purchase','purchases.py',0)
        sys.exit()

    except Exception,e:
        c.rollback()
        errorString = "<p class=error>Problem with database updte:</p><pre>%s</pre>"%str(sys.exc_info())

printHeader2('Purchases',errorString)

################
# Get list of items for add purchase form

cursor.execute("SELECT itemId,manufacturer,brand,name FROM item ORDER BY manufacturer,brand,name")
itemOptions = []
for (itemId,manufacturer,brand,name) in cursor:
    itemOptions.append('<OPTION VALUE=%s>%s</OPTION>'%(itemId,getItemName(manufacturer,brand,name)))
    
#####
# Add form

print '''
<div class=addthing>
<H2>New purchase</H2>
<FORM name=addTran>
Seller: <INPUT TYPE=TEXT NAME=seller ID=seller SIZE=40/>
<br />
Reconcile entry: <INPUT TYPE=checkbox NAME=reconcile />
<br />
<TABLE BORDER=1 ID=addTranItemTable>
<TR><TH>Item</TH><TH>Qty</TH><TH>Cost/item</TH><TH>Total</TH></TR>
<TR><TD COLSPAN=3>Shipping costs:</TD><TD><INPUT TYPE=TEXT CLASS=money VALUE=0.00 NAME=shipping ID=shipping SIZE=5 onBlur='moneyFormat(event.target);calcTotals()'/></TD></TR>
<TR><TD COLSPAN=3>Total:</TD><TD><INPUT TYPE=TEXT CLASS=money ID=total VALUE=0.00 SIZE=5 READONLY /></TD>
</TABLE>
<INPUT TYPE=HIDDEN ID=addTranItemTableLastRow NAME=addLastItem VALUE=0 />
<INPUT TYPE=button VALUE='add another item' onClick='addItemRow();' />
<INPUT TYPE=button VALUE='add new item' onClick='addNewItemRow();' />
<p />
<INPUT TYPE=SUBMIT VALUE='Add new purchase' NAME=AddPurchase onClick='return validateForm()' />
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
    newCell1.innerHTML = '<INPUT TYPE=TEXT NAME=quantity-'+thisRow+' ID=quantity-'+thisRow+' VALUE=1 SIZE=5/  onBlur=\\\'calcTotals()\\\'>';
    newCell2.innerHTML = '<INPUT TYPE=TEXT CLASS=money NAME=pricePerItem-'+thisRow+' ID=pricePerItem-'+thisRow+' SIZE=5 VALUE="0.00" onBlur=\\\'moneyFormat(event.target);calcTotals()\\\' />';
    newCell3.innerHTML = '<INPUT TYPE=TEXT CLASS=money NAME=total-'+thisRow+' ID=total-'+thisRow+' SIZE=5 VALUE="0.00" READONLY />';
    newCell4.innerHTML = '<INPUT TYPE=button VALUE="delete item details" onClick=\\\'delItemRow('+thisRow+');;calcTotals()\\\' />';
}
function addNewItemRow()
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
    newCell0.innerHTML = '<INPUT NAME=addMfr-'+thisRow+' SIZE=7 /><INPUT NAME=addBrand-'+thisRow+' SIZE=7 /><INPUT NAME=addName-'+thisRow+' SIZE=25 />';
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
        checkField('seller',"You must fill out a seller name") &&
        checkField('shipping',"You must enter the shipping cost")
        );
}

document.getElementById('addTranItemTableLastRow').value = '0';
addItemRow();

function setFocus()
{
   document.getElementById('seller').focus();
}
window.onload = setFocus;
</SCRIPT>
'''

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
LIMIT 200
''')

print "<H2>Last 200 purchases</H2>"
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

