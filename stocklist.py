#!/python26/python.exe
# -*- coding: UTF-8 -*-

# enable debugging
import cgitb
import cgi
import sqlite3
from myutils import sql, printHeader, printFooter, printOptions, centsToDollarString

cgitb.enable()

form = cgi.FieldStorage()

c = sqlite3.connect('/temp/example')
cursor = c.cursor()

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
    print "<TABLE BORDER=1 class=listthings>"
    for (itemId,manufacturer,brand,name,number) in stockList:
        if not brand: brand = '-'
        print "<TR>"
        print "<TD><A HREF=singleitem.py?itemId=%s>%s:%s:%s</A></TD>"%(itemId,manufacturer,brand,name)
        print "<TD>%d</TD>"%(number,)
        print "</TR>"
    print "</TABLE>"

printFooter()

