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
    Item.itemId AS id,
    manufacturer,
    brand,
    name,
    SUM(BinItems.quantity) AS number,
    ( SELECT title FROM ebayList2item LEFT JOIN ebayList USING (title) where ebayList2item.itemId = Item.itemId )
FROM
    Item
    INNER JOIN BinItems USING (itemId)
GROUP BY Item.itemId
ORDER BY manufacturer,brand,name
''')

stockList = []
for itemDetails in cursor: stockList.append(itemDetails)

if len(stockList) == 0:
    print "<H2>You don't have any stock</H2>"
else:
    print "<TABLE BORDER=1 class='listthings sortable'>"
    print "<TR><TH>Item</TH><TH>Qty</TH><TH>Listed?</TH></TR>"
    for (itemId,manufacturer,brand,name,number,ebayTitle) in stockList:
        print "<TR>"
        print "<TD><A HREF=singleitem.py?itemId=%s>%s</A></TD>"%(itemId,getItemName(manufacturer,brand,name))
        print "<TD>%d</TD>"%(number,)
        if ebayTitle:
            print "<TD>Yes</TD>"
        else:
            print "<TD>No</TD>"
        print "</TR>"
    print "</TABLE>"

printFooter()

