#!/python26/python.exe
# -*- coding: UTF-8 -*-

# enable debugging
import cgitb
import cgi
from myutils import c,cursor,sql, printHeader, printFooter, printOptions, centsToDollarString, getItemName

cgitb.enable()

form = cgi.FieldStorage()

printHeader('Stock list')

cursor.execute('''
SELECT
    itemId,manufacturer,brand,name,SUM(quantity) AS number
FROM
    Item
    INNER JOIN BinItems using (itemId)
GROUP BY itemId
ORDER BY manufacturer,brand,name
''')

stockList = []
for itemDetails in cursor: stockList.append(itemDetails)

if len(stockList) == 0:
    print "<H2>You don't have any stock</H2>"
else:
    print "<TABLE BORDER=1 class='listthings sortable'>"
    print "<TR><TH>Item</TH><TH>Qty</TH></TR>"
    for (itemId,manufacturer,brand,name,number) in stockList:
        print "<TR>"
        print "<TD><A HREF=singleitem.py?itemId=%s>%s</A></TD>"%(itemId,getItemName(manufacturer,brand,name))
        print "<TD>%d</TD>"%(number,)
        print "</TR>"
    print "</TABLE>"

printFooter()

