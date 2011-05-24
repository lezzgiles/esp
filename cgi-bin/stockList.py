#!/python26/python.exe

# enable debugging
import cgitb
import cgi
import sys
from myutils import c,cursor,sql, printHeader, printFooter, printOptions, centsToDollarString, getItemName, gotoButton
from ebayLib import ebayFindItem
cgitb.enable()
from datetime import datetime    # Used to timestamp events

form = cgi.FieldStorage()

printHeader('Stock list')

###############################################################################
# AJAX code
print '''
<script type="text/javascript">
function dumpProps(obj, parent) {
   // Go through all the properties of the passed-in object
   for (var i in obj) {
      // if a parent (2nd parameter) was passed in, then use that to
      // build the message. Message includes i (the object's property name)
      // then the object's property value on a new line
      if (parent) { var msg = parent + "." + i + "\\n" + obj[i]; } else { var msg = i + "\\n" + obj[i]; }
      // Display the message. If the user clicks "OK", then continue. If they
      // click "CANCEL" then quit this level of recursion
      if (!confirm(msg)) { return; }
      // If this property (i) is an object, then recursively process the object
      if (typeof obj[i] == "object") {
         if (parent) { dumpProps(obj[i], parent + "." + i); } else { dumpProps(obj[i], i); }
      }
   }
}
function updateFromEbay(itemId)
{
  var xmlhttp;
  if (window.XMLHttpRequest)
  {// code for IE7+, Firefox, Chrome, Opera, Safari
    xmlhttp=new XMLHttpRequest();
  }
  else
  {// code for IE6, IE5
    xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
  }
  xmlhttp.onreadystatechange=function()
  {
    if (xmlhttp.readyState == 4) {
      document.getElementById('itemId-'+itemId).innerHTML=xmlhttp.responseText;
    }
  }
  xmlhttp.open("GET",'updateFromEbay.py?itemId='+itemId,true);
  xmlhttp.send(null);
}
function updateAllFromEbay()
{
    table = document.getElementById('stockTable');
    for (i in table.rows) {
        if (i == 0) { continue }
        row = table.rows[i];
        //dumpProps(row.cells[2].childNodes[2]);
        try {
            row.cells[2].childNodes[2].click();
        }
        catch(err) {
            alert("row ",i);
        }
        //row.cells[2].click();
        //alert(row.cells[2].lastChild);
        //alert(row.cells[2].childNodes[0]);
        //alert(row.cells[2].innerHtml());
        //row.cells[2].button.click();
    }
}
</script>
'''


###############################################################################
def importCountFromEbay(itemId):

    cursor.execute('''SELECT manufacturer,brand,name,countOnEbay FROM Item WHERE itemId = ?''',(int(itemId),))

    for itemDetails in cursor:
        (manufacturer,brand,name,countOnEbay) = itemDetails
        print "Looking for %s on EBay... "%getItemName(manufacturer,brand,name)
        (manufacturer,brand,name,countOnEbay) = itemDetails
        count = ebayFindItem(getItemName(manufacturer,brand,name))
        
        print "Found %d listings<br />"%count
        if count != countOnEbay:
            cursor.execute('UPDATE Item SET countOnEbay = ? WHERE itemId = ?',(count,itemId))

            c.commit()

###############################################################################
if form.has_key('import'):
    try:
        itemid = form['import'].value
        importCountFromEbay(itemid)
    except Exception,e:
        c.rollback()
        print "<p class=error>Problem importing data:</p><pre>",sys.exc_info(),"</pre>"

###############################################################################
# Count total items

cursor.execute('''
SELECT
    Item.itemId AS id,
    manufacturer,
    brand,
    name,
    countOnEbay,
    SUM(BinItems.quantity) AS number,
    ( SELECT title FROM ebayList2item INNER JOIN ebayList USING (title) where ebayList2item.itemId = Item.itemId )
FROM
    Item
    INNER JOIN BinItems USING (itemId)
GROUP BY Item.itemId
ORDER BY manufacturer,brand,name
''')

stockList = []
total = 0
for itemDetails in cursor:
    stockList.append(itemDetails)
    total += itemDetails[5]

#######################################
# Read in how many items are in kits
itemQtyInKits = {}
cursor.execute('''
SELECT
    itemId,
    SUM(Kit.quantity * kitItem.quantity)
FROM
    Kit
    LEFT JOIN kitItem USING (kitId)
GROUP BY kitId,itemId
''')

for (itemId,qty) in cursor:
    if itemId not in itemQtyInKits: itemQtyInKits[itemId] = 0
    itemQtyInKits[itemId] += qty

#######################################
#print '<button type=button onclick=\"updateAllFromEbay()\">Update all from ebay</button>'

if len(stockList) == 0:
    print "<H2>You don't have any stock</H2>"
else:
    print "<TABLE BORDER=1 class='listthings sortable' id=stockTable>"
    print "<TR><TH>Item</TH><TH>Qty not<br />in kits</TH><TH>Qty<br />in kits</TH><TH># on ebay</TH><TH>Listed?</TH></TR>"
    for (itemId,manufacturer,brand,name,countOnEbay,number,ebayTitle) in stockList:
        if itemId in itemQtyInKits:
            qtyInKits = itemQtyInKits[itemId]
        else:
            qtyInKits = 0
        print "<TR>"
        print "<TD><A HREF=singleitem.py?itemId=%s>%s</A></TD>"%(itemId,getItemName(manufacturer,brand,name))
        print "<TD>%d</TD>"%(number-qtyInKits,)
        print "<TD>%d</TD>"%(qtyInKits,)
        print "<TD><font id=itemId-%d>%d</font> <button type=button onclick=\"updateFromEbay(%d)\">Update</button></TD>"%(itemId,countOnEbay,itemId)
        if ebayTitle:
            print "<TD>Yes</TD>"
        else:
            print "<TD>No</TD>"
        print "</TR>"
    print "</TABLE>"

print "<p><i>Total items: %d</i></p>"%total
printFooter()

