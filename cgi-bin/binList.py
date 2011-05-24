#!/python26/python.exe
# -*- coding: UTF-8 -*-

# enable debugging
import cgitb
import cgi
import sys
from myutils import c,cursor,sql, printRedirect,printHeader1,printHeader2, printFooter, printOptions, centsToDollarString, gotoButton, getItemName, sortLists
cgitb.enable()

form = cgi.FieldStorage()

printHeader1('Bin/stock list')

errorString = None

#########################################
if form.has_key('moveStock'):
    try:
        tableSize = int(form['tableSize'].value)

        delBin = form['delBin'].value
        delItem= form['delItem'].value

        history = "MOVE %s FROM %s"%(delItem,delBin)

        moveDetails = []
        totalToMove = 0
        for i in range(2,tableSize+1):
            binId = form['addBin-'+str(i)].value
            binQty = int(form['addQty-'+str(i)].value)
            if binQty == 0: continue
            totalToMove += binQty
            moveDetails.append([binId,binQty])
            
            history += " %d TO %s"%(binQty,binId)

        cursor.execute('SELECT SUM(quantity) FROM binItems WHERE binId = ? and itemId = ? GROUP BY binId',(delBin,delItem))
        (foundQty,) = cursor.fetchone()

        if foundQty < totalToMove:
           raise ValueError, "<p class=error>Didn't find enough items to move</p>"

        cursor.execute('DELETE FROM binItems WHERE binId = ? and itemId = ?',(delBin,delItem))

        for (binId,binQty) in moveDetails:
            cursor.execute('INSERT INTO binItems (binId,itemId,quantity) VALUES (?,?,?)',(binId,delItem,binQty))

        if foundQty > totalToMove:
            cursor.execute('INSERT INTO binItems (binId,itemId,quantity) VALUES (?,?,?)',(delBin,delItem,foundQty-totalToMove))
            
        cursor.execute('''INSERT INTO history (historyDate,body) VALUES (DATETIME('now'),?)''',(history,))
        c.commit()
        # Redirect to same page, so page reload doesn't re-add move
        printRedirect('Move completed','binList.py',0)
        sys.exit()

    except Exception,e:
        c.rollback()
        errorString = "<p class=error>Problem with database update:</p><pre>%s</pre>"%str(sys.exc_info())
    
printHeader2('Bin/stock list',errorString)

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

def nameToList(a):
    (binId,itemId,binName,itemMfr,itemBrand,itemName,qty) = a
    return binName.split()

binList.sort(sortLists,nameToList)

if len(binList) == 0:
    print "<H2>You don't have any stock</H2>"
else:
    print "<TABLE BORDER=1 class='listthings sortable'>"
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

