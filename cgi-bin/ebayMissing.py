#!/python26/python.exe
# -*- coding: UTF-8 -*-

# enable debugging
import cgitb
import cgi
from myutils import c,cursor,sql, printHeader, printFooter, gotoButton, centsToDollarString, dollarStringToCents, cell, moneyCell, getTranType, getItemName

cgitb.enable()

form = cgi.FieldStorage()

printHeader('Unlisted items')

print '<p>This page lists items that are not listed on Ebay, or that are not linked to an Ebay item.</p>'

cursor.execute('''
SELECT manufacturer,brand,name,item.itemid,SUM(binItems.quantity)
FROM
    item
    LEFT JOIN binItems USING (itemid)
    LEFT JOIN ebayList2Item USING (itemid)
    LEFT JOIN ebayList USING (title)
WHERE
    ebayList.title IS NULL
GROUP BY item.itemid
ORDER BY manufacturer,brand,name''')

print '<TABLE BORDER=1 CLASS="listthings sortable">'
print '<TR><TH>Item</TH><TH>Qty</TH></TR>'
for (mfr,brand,name,itemId,qty) in cursor:
    print '<TR><TD>',getItemName(mfr,brand,name),'</TD><TD>',qty,'</TD></TR>'

print '</TABLE>'    
printFooter()

