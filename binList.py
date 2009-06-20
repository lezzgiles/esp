#!/python26/python.exe
# -*- coding: UTF-8 -*-

# enable debugging
import cgitb
import cgi
import sqlite3
import sys
from myutils import sql, printHeader, printFooter, printOptions, centsToDollarString, gotoButton
cgitb.enable()

form = cgi.FieldStorage()

c = sqlite3.connect('/temp/example')
c.isolation_level = "EXCLUSIVE"

cursor = c.cursor()

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
            totalToMove += binQty
            moveDetails.append([binId,binQty])

        delBin = form['delBin'].value
        delItem= form['delItem'].value

        cursor.execute('SELECT SUM(quantity) FROM binItems WHERE binId = ? and itemId = ? GROUP BY binId',(delBin,delItem))
        (foundQty) = cursor.fetchone()

        if foundQty < totalToMove:
           raise ValueError, "<p class=error>Didn't find enough items to move</p>"

        cursor.execute('DELETE FROM binItems WHERE binId = ? and itemId = ?',(delBin,delItem))

        
        for (binId,binQty) in moveDetails:
            cursor.execute('INSERT INTO binItems (binId,itemId,quantity) VALUES (?,?,?)',(binId,delItem,binQty))
            
        c.commit()

    except Exception,e:
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
ORDER BY Item.manufacturer,Item.brand,Item.name
''')

binList = []
for binDetails in cursor: binList.append(binDetails)

if len(binList) == 0:
    print "<H2>You don't have any stock</H2>"
else:
    print "<TABLE BORDER=1 class=listthings>"
    print "<TR><TH>Bin</TH><TH>Item</TH><TH>Quantity</TH></TR>"
    for (binId,itemId,binName,manufacturer,brand,name,number) in binList:
        if not brand: brand = '-'
        print "<TR>"
        print "<TD>%s</TD>"%binName
        print "<TD>%s:%s:%s</TD>"%(manufacturer,brand,name)
        print "<TD>%d</TD>"%(number,)
        print "<TD>",gotoButton('Move','moveStock.py?binId=%s&itemId=%s'%(binId,itemId)),"</TD>"
        print "</TR>"
    print "</TABLE>"

printFooter()

