#!/python26/python.exe
# -*- coding: UTF-8 -*-

# enable debugging
import cgitb
import cgi
import sys
import urllib
from myutils import c,cursor,sql, printHeader, printFooter, gotoButton, centsToDollarString, dollarStringToCents, cell, moneyCell, getItemName

cgitb.enable()

form = cgi.FieldStorage()

printHeader('Link Ebay title to stock item')

if not form.has_key('title'):
    print "No ebay listing title specified"
    sys.exit()

title = form['title'].value

print "<p>Please select a stock item to link to ebay listing item <b>%s</b></p>"%title

# Get a list of all items
cursor.execute("SELECT itemId,manufacturer,brand,name FROM item ORDER BY manufacturer,brand,name")
itemOptions = []
for (itemId,manufacturer,brand,name) in cursor:
    itemOptions.append('<OPTION VALUE=%s>%s</OPTION>'%(itemId,getItemName(manufacturer,brand,name)))
print '<FORM ACTION=ebayListing.py>'
print '<SELECT NAME=itemid>'
for option in itemOptions: print option
print '</SELECT>'
print '<INPUT TYPE=HIDDEN NAME=title VALUE=%s />'%urllib.quote_plus(title)
print '<INPUT TYPE=SUBMIT VALUE="Add link" NAME=link>'
print '</FORM>'

printFooter()
