#!/python26/python.exe
# -*- coding: UTF-8 -*-

# enable debugging
import cgitb
import cgi
import sqlite3
from myutils import sql, printHeader, printFooter, printOptions, centsToDollarString, cell, getItemName

cgitb.enable()

form = cgi.FieldStorage()

c = sqlite3.connect('/temp/example')
cursor = c.cursor()

printHeader('Bin list')

itemId = form['itemId'].value
binId = form['binId'].value

##################################
# Get the details of what we're transferring from
cursor.execute('''
SELECT
    binId,itemId,Bin.name,Item.manufacturer,Item.brand,Item.name,quantity
FROM
    Bin
    INNER JOIN BinItems using (binId)
    INNER JOIN Item USING (itemId)
    WHERE itemId = ? AND binId = ?
''',(itemId,binId))

quantities = []
total = 0
for (thisBinId,thisItemId,binName,mfr,brand,name,quantity) in cursor:
    quantities.append(quantity)
    total += quantity
    itemName = getItemName(mfr,brand,name)

###################################
# Get list of all bins and their size
cursor.execute('''
SELECT binId,name,slots,SUM(quantity)
FROM
    Bin
    LEFT JOIN BinItems USING (binId)
WHERE
    binId != ?
GROUP BY binId
''',(binId,))

toBins = []
for (thisBinId,name,slots,used) in cursor:
    if not used: used = 0
    if slots:
        if slots == used: continue   # No space left in this bin
        slots = slots - used
    toBins.append((thisBinId,name,slots))

###################################
# Tell javascript what's happening
print '<SCRIPT LANGUAGE=JavaScript>'
print 'binsWithSpaces = new Array();'
for (thisBinId,name,slots) in toBins:
    print 'binsWithSpaces[%s] = {name: "%s", slots: %s};'%(thisBinId,name,slots)

print '</SCRIPT>'

###################################
# Print out stuff
print '<H2>Move %s from bin %s</H2>'%(itemName,binName)
print '<FORM ACTION=binList.py>'
print '<p>You have <INPUT TYPE=text CLASS=number READONLY ID=moved VALUE=%s SIZE=2/> of %s items remaining to move</p>'%(total,total)
print '<INPUT TYPE=hidden NAME=delBin VALUE=%s />'%binId
print '<INPUT TYPE=hidden NAME=delItem VALUE=%s />'%itemId
print '''
<TABLE BORDER=1 ID=movelist>
<TR><TH>Move to bin</TH><TH>Qty</TH></TR>
</TABLE>
<SELECT ID=addBinId></SELECT>
<INPUT TYPE=button onClick='addBinRow();' VALUE='Add bin'/>
<P>
<INPUT TYPE=hidden NAME=moveStock VALUE=1 />
<INPUT TYPE=hidden ID=tableSize NAME=tableSize VALUE=0 />
<INPUT TYPE=submit VALUE='Move stock' />
</p>
</FORM>


<SCRIPT LANGUAGE=JavaScript>

selectList = document.getElementById('addBinId');
for (binId in binsWithSpaces) {
    thisBin = binsWithSpaces[binId];
    option = document.createElement('option');
    option.text = thisBin.name;
    option.value = binId;
    selectList.add(option,null);
}

function addBinRow()
{
    var tbl = document.getElementById('movelist');
    thisRow = tbl.rows.length+1;
    var newRow = tbl.insertRow(tbl.rows.length);
    var newCell0 = newRow.insertCell(0);
    var newCell1 = newRow.insertCell(1);
    binId = document.getElementById("addBinId").value;
    name = binsWithSpaces[binId].name;
    slots = binsWithSpaces[binId].slots;
    newCell0.innerHTML = binsWithSpaces[binId].name + "<INPUT TYPE=HIDDEN NAME=addBin-"+thisRow+" VALUE="+binId+" />"
    newCell1.innerHTML = incDecField('addQty-'+thisRow,slots,'moved');
    selectList = document.getElementById('addBinId');
    for (option in selectList.options) {
        if (selectList.options[option].value == binId) {
            selectList.options[option].disabled = true;
        }
    }
    document.getElementById('tableSize').value = thisRow;
}
</SCRIPT>'''
printFooter()    