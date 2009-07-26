#!/python26/python.exe
# -*- coding: UTF-8 -*-

# enable debugging
import cgitb
import cgi
from myutils import c,cursor,sql, printHeader, printFooter, gotoButton, centsToDollarString, dollarStringToCents, cell, moneyCell, getTranType, getItemName

cgitb.enable()

form = cgi.FieldStorage()

printHeader('Unlisted items')

print '<p>This page lists items that are not listed on Ebay</p>'

cursor.execute('''
SELECT manufacturer,brand,name
FROM
    item
    LEFT JOIN ebayList2Item USING (itemid)
    LEFT JOIN ebayList USING (title)
WHERE
    ebayList.title IS NULL
ORDER BY manufacturer,brand,name''')

print '<TABLE BORDER=1 CLASS="listthings sortable">'
for (mfr,brand,name) in cursor:
    print '<TR><TD>',getItemName(mfr,brand,name),'</TD></TR>'

print '</TABLE>'    
printFooter()

