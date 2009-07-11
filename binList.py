#!/python26/python.exe
# -*- coding: UTF-8 -*-

# enable debugging
import cgitb
import cgi
import sys
from myutils import c,cursor,sql, printHeader, printFooter, printOptions, centsToDollarString, gotoButton, getItemName
cgitb.enable()

form = cgi.FieldStorage()

printHeader('Bin/stock list')

#########################################
if form.has_key('moveStock'):
    try:
        tableSize = int(form['tableSize'].value)

        moveDetails = []
        totalToMove = 0
        for i in range(2,tableSize+1):
            binId = form['addBin-'+str(i)].value
            binQty = int(form['addQty-'+str(i)].value)
            if binQty == 0: continue
            totalToMove += binQty
            moveDetails.append([binId,binQty])

        delBin = form['delBin'].value
        delItem= form['delItem'].value

        cursor.execute('SELECT SUM(quantity) FROM binItems WHERE binId = ? and itemId = ? GROUP BY binId',(delBin,delItem))
        (foundQty,) = cursor.fetchone()

        if foundQty < totalToMove:
           raise ValueError, "<p class=error>Didn't find enough items to move</p>"

        cursor.execute('DELETE FROM binItems WHERE binId = ? and itemId = ?',(delBin,delItem))

        for (binId,binQty) in moveDetails:
            cursor.execute('INSERT INTO binItems (binId,itemId,quantity) VALUES (?,?,?)',(binId,delItem,binQty))

        if foundQty > totalToMove:
            cursor.execute('INSERT INTO binItems (binId,itemId,quantity) VALUES (?,?,?)',(delBin,delItem,foundQty-totalToMove))
            
        c.commit()

    except Exception,e:
        c.rollback()
        print "<p class=error>Problem with database update:</p><pre>",sys.exc_info(),"</pre>"
    
#########################################    
cursor.execute('''
SELECT
    binId,itemId,Bin.name,Item.manufacturer,Item.brand,Item.name,SUM(quantity)
FROM
    Bin
    INNER JOIN BinItems using (binId)
    INNER JOIN Item USING (itemId)
GROUP BY binId,itemId
''')

binList = []
for binDetails in cursor: binList.append(binDetails)

# Sort the list by words
def sortLists(a,b):
    # if either is 'unstocked', it comes first
    if a[0] == 'unstocked': return -1
    if b[0] == 'unstocked': return 1
    matchLength = min((len(a),len(b)))
    for i in range(matchLength):
        if a[i] == b[i]: continue
        try:
            return int(a[i]) - int(b[i])
        except:
            pass
        if a[i] > b[i]: return 1
        if a[i] < b[i]: return -1
    return 0

def nameToList(a):
    (binId,itemId,binName,itemMfr,itemBrand,itemName,qty) = a
    return binName.split()

binList.sort(sortLists,nameToList)

if len(binList) == 0:
    print "<H2>You don't have any stock</H2>"
else:
    print "<TABLE BORDER=1 class=listthings>"
    print "<TR><TH>Bin</TH><TH>Item</TH><TH>Quantity</TH></TR>"
    for (binId,itemId,binName,manufacturer,brand,name,number) in binList:
        print "<TR>"
        print "<TD>%s</TD>"%binName
        print "<TD>%s</TD>"%getItemName(manufacturer,brand,name)
        print "<TD>%d</TD>"%(number,)
        print "<TD>",gotoButton('Move','moveStock.py?binId=%s&itemId=%s'%(binId,itemId)),"</TD>"
        print "</TR>"
    print "</TABLE>"

printFooter()

