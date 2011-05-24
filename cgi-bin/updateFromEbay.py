#!/python26/python.exe

# Designed to be called from Ajax

import cgitb
import cgi
import sys

from myutils import c,cursor,getItemName
from ebayLib import ebayFindItem

print "Content-Type: text/html;charset=utf-8"
print

form = cgi.FieldStorage()

###############################################################################
def importCountFromEbay(itemId):

    cursor.execute('''SELECT manufacturer,brand,name,countOnEbay FROM Item WHERE itemId = ?''',(int(itemId),))

    for itemDetails in cursor:
        (manufacturer,brand,name,countOnEbay) = itemDetails
        (manufacturer,brand,name,countOnEbay) = itemDetails
        count = ebayFindItem(getItemName(manufacturer,brand,name))
        
        print count
        if count != countOnEbay:
            cursor.execute('UPDATE Item SET countOnEbay = ? WHERE itemId = ?',(count,itemId))

            c.commit()

###############################################################################
if form.has_key('itemId'):
    try:
        itemid = form['itemId'].value
        importCountFromEbay(itemid)
    except Exception,e:
        c.rollback()
        print "INVALID"
else:
    print "INVALID"
