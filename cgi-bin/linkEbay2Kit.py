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

printHeader('Link Ebay title to kit')

if not form.has_key('title'):
    print "No ebay listing title specified"
    sys.exit()

title = form['title'].value

print "<p>Please select a kit to link to ebay listing item <b>%s</b></p>"%title

# Get a list of all items
cursor.execute("SELECT kitId,name FROM Kit ORDER BY name")
itemOptions = []
for (itemId,name) in cursor:
    itemOptions.append('<OPTION VALUE=%s>%s</OPTION>'%(itemId,name))
print '<FORM ACTION=ebayListing.py>'
print '<SELECT NAME=kitid>'
for option in itemOptions: print option
print '</SELECT>'
print '<INPUT TYPE=HIDDEN NAME=title VALUE=%s />'%urllib.quote_plus(title)
print '<INPUT TYPE=SUBMIT VALUE="Add link" NAME=linkToKit>'
print '</FORM>'

printFooter()
