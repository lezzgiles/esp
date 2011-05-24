#!/python26/python.exe
#-*- coding: UTF-8 -*-

# enable debugging
import cgitb
import cgi
from myutils import c,cursor,sql,printRedirect, printHeader1,printHeader2, printFooter, gotoButton, centsToDollarString, dollarStringToCents, cell, moneyCell, getTranType, getItemName
import sys

cgitb.enable()

form = cgi.FieldStorage()

printHeader1('Kits')

errorString = None

#cgi.print_form(form)

##################
# Handle add kit request
if form.has_key('AddKit'):
    try:
        name = form['name'].value
        maxItemIdx = form['addLastItem'].value
        cursor.execute('BEGIN IMMEDIATE TRANSACTION')
        cursor.execute("INSERT INTO Kit (name) VALUES (?)",(name,))
        kitId = cursor.lastrowid

        for i in range(1,int(maxItemIdx)+1):
            if form.has_key('addItem-'+str(i)):
                itemId = form['addItem-'+str(i)].value
                quantity = form['quantity-'+str(i)].value
                if int(quantity) == 0: continue
                cursor.execute('INSERT INTO KitItem (kitId,itemId,quantity) VALUES (?,?,?)',
                               (kitId,itemId,quantity))

        c.commit()
        # redirect to same page, so reload doesn't re-add purchase
        printRedirect('Added kit','kits.py',0)
        sys.exit()

    except Exception,e:
        c.rollback()
        errorString = "<p class=error>Problem with database update:</p><pre>%s</pre>"%str(sys.exc_info())


##################
# Handle delete kit request
if form.has_key('delId'):
    try:
        delId = form['delId'].value
        cursor.execute('BEGIN IMMEDIATE TRANSACTION')
        cursor.execute("DELETE FROM Kit WHERE kitId = ?",(delId,))
        cursor.execute("DELETE FROM KitItem WHERE kitId = ?",(delId,))
        c.commit()
        # redirect to same page, so reload doesn't re-add purchase
        printRedirect('Deleted kit','kits.py',0)
        sys.exit()

    except Exception,e:
        c.rollback()
        errorString = "<p class=error>Problem with database update:</p><pre>%s</pre>"%str(sys.exc_info())

###################
# Handle set quantity request
if form.has_key('setId'):
    try:
        setId = form['setId'].value
        setQty = form['setQty'].value
        cursor.execute('BEGIN IMMEDIATE TRANSACTION')
        cursor.execute('UPDATE Kit SET quantity = ? WHERE kitId = ?',(setQty,setId))
        c.commit()
        # redirect to same page, so reload doesn't re-add purchase
        printRedirect('Deleted kit','kits.py',0)
        sys.exit()

    except Exception,e:
        c.rollback()
        errorString = "<p class=error>Problem with database update:</p><pre>%s</pre>"%str(sys.exc_info())

printHeader2('Kits',errorString)

################
# Get list of items for add kit form

cursor.execute("SELECT itemId,manufacturer,brand,name FROM item ORDER BY manufacturer,brand,name")
itemOptions = []
for (itemId,manufacturer,brand,name) in cursor:
    itemOptions.append('<OPTION VALUE=%s>%s</OPTION>'%(itemId,getItemName(manufacturer,brand,name)))
    
#####
# Add form

print "<div class=addthing>"
print "<H2>New kit</H2>"
print "<FORM name=addKit>"
print "Kit name: <INPUT TYPE=TEXT NAME=name ID=name SIZE=40/>"
print "<br />"
print "<TABLE BORDER=1 ID=addKitItemTable>"
print "<TR><TH>Item</TH><TH>Qty</TH></TR>"
print "</TABLE>"
print "<INPUT TYPE=HIDDEN ID=addKitItemTableLastRow NAME=addLastItem VALUE=0 />"
print "<INPUT TYPE=button VALUE='add another item' onClick='addItemRow();' />"
print "<p />"
print "<INPUT TYPE=SUBMIT VALUE='Add new kit' NAME=AddKit onClick='return validateForm()' />"
print "</FORM>"
print "</div>"

print '''
<SCRIPT LANGUAGE="JavaScript">
function addItemRow()
{
    var tbl = document.getElementById('addKitItemTable');
    var lastRowElt = document.getElementById('addKitItemTableLastRow');
    var thisRow = parseInt(lastRowElt.value);
    thisRow += 1;
    lastRowElt.value = thisRow.toString();
    var rowId = tbl.rows.length;
    var newRow = tbl.insertRow(tbl.rows.length);
    newRow.id = 'addTranRow-'+thisRow;
    var newCell0 = newRow.insertCell(0);
    var newCell1 = newRow.insertCell(1);
    var newCell2 = newRow.insertCell(2);
    newCell0.innerHTML = '<SELECT NAME=addItem-'+thisRow+'>''',
for option in itemOptions:
    print option,
print '''</SELECT>';
    newCell1.innerHTML = '<INPUT TYPE=TEXT NAME=quantity-'+thisRow+' VALUE=1 SIZE=5/>';
    newCell2.innerHTML = '<INPUT TYPE=button VALUE="delete item details" onClick=\\\'delItemRow('+thisRow+');\\\' />';
}
function delItemRow(delRowNumber)
{
    var tbl = document.getElementById('addKitItemTable');
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
        checkField('seller',"You must enter a kit name")
        );
}

document.getElementById('addKitItemTableLastRow').value = '0';
addItemRow();
</SCRIPT>
'''

###########################
# List of kits

# Read in the items table completely
kitQty = {}
allItems = set()
cursor.execute('''
SELECT
  kitId,
  itemId,
  quantity
FROM
  KitItem
'''
)
for (kitId,itemId,quantity) in cursor:
    if kitId not in kitQty: kitQty[kitId] = {}
    kitQty[kitId][itemId] = quantity
    allItems.add(itemId)

# Read in details of the items we are interested in
itemDetails = {}
cursor.execute('''
SELECT
  itemId,
  manufacturer,
  brand,
  name,
  SUM(quantity)
FROM
  Item
  LEFT JOIN BinItems USING (itemId)
WHERE itemId in ('''+ ','.join(["'%s'"%i for i in allItems])  +''')
GROUP BY itemId
''')
for (itemId,mfr,brand,name,qty) in cursor:
    if qty == None: qty = 0
    itemDetails[itemId] = (getItemName(mfr,brand,name),qty)

# Read in the kits details
kits = []
cursor.execute('''
SELECT
    kitId,name,quantity
FROM Kit
ORDER BY name
''')
for (kitId,name,quantity) in cursor:
    kits.append((kitId,name,quantity))

# Go through all items and find out how many are not assigned to kits
totalAvail = {}
for itemId in itemDetails:
    (name,qty) = itemDetails[itemId]
    totalAvailable = qty
    for (kitId,kitName,kitQuantity) in kits:
        if itemId in kitQty[kitId]:
            totalAvailable -= kitQty[kitId][itemId]*kitQuantity
    totalAvail[itemId] = totalAvailable

# Go through all kits and see how many we could have, given the available items
maxAvail = {}
for (kitId,name,quantity) in kits:
    maxAvail[kitId] = 99999
    # Go through each item in the kit and reduce maxAvail appropriately
    for itemId in kitQty[kitId]:
        itemQty = kitQty[kitId][itemId]
        usedByMe = quantity*itemQty
        # Total available for this kit is total available plus any already used by this kit
        available = totalAvail[itemId]+quantity*itemQty
        # possible # of kits = divide avable by number used
        possibleKits = int(available/itemQty)
        maxAvail[kitId] = min(maxAvail[kitId],possibleKits)

# Go through all kits and
if len(kits) == 0:
    print "<H2>No kits</H2>"
else:
    print "<TABLE BORDER=1 class='listthings sortable'>"
    print "<TR><TH>Name</TH><TH>Qty</TH><TH>Contents</TH><TH></TH><TH></TH></TR>"
    for (kitId,name,quantity) in kits:
        print "<TR>"
        print "<TD VALIGN=TOP>%s</TD>"%name
        print "<TD VALIGN=TOP>%s</TD>"%quantity
        print "<TD>"
        for itemId in kitQty[kitId]:
            itemQty = kitQty[kitId][itemId]
            (name,qty) = itemDetails[itemId]
            print "%s %s<br />"%(itemQty,name)
        print "</TD>"
        print "<TD VALIGN=TOP><FORM><SELECT NAME=setQty>"
        for i in range(0,maxAvail[kitId]+1):
            if i == quantity:
                selected = 'SELECTED'
            else:
                selected = ''
            print "<OPTION %s>%d</OPTION>"%(selected,i)
        print "</SELECT>"
        print "<INPUT TYPE=HIDDEN NAME=setId VALUE=%s />"%kitId
        print "<INPUT TYPE=SUBMIT VALUE=upd></FORM></TD>"
        print "<TD VALIGN=TOP>",gotoButton('Delete','kits.py?delId=%s'%kitId),"</TD>"
        print "</TR>"
    print "</TABLE>"



printFooter()

