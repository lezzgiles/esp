#!/python26/python.exe
# -*- caoding: UTF-8 -*-

# enable debugging
import cgitb
import cgi
import sys
import urllib
from myutils import c,cursor,sql, printHeader, printFooter, gotoButton, centsToDollarString, dollarStringToCents, cell, moneyCell, getItemName
from ebayLib import getPage
from datetime import datetime,timedelta

cgitb.enable()
form = cgi.FieldStorage()

# How many items to retrieve at a time
pageSize = 50

###########################################################################
def loadFromEbay():

    itemList = []

    # Get first page, which also gets the total number of pages
    totalNumberOfPages = getPage(1,pageSize,itemList)

    # Already got first page, so start at page 2
    for pageNo in (range(2,totalNumberOfPages+1)):
        getPage(pageNo,pageSize,itemList)

    # Clean up the table
    cursor.execute("DELETE FROM ebayList")
    
    # Add the new data to the table    
    for (title,itemId,quantity) in itemList:
        cursor.execute("INSERT INTO ebayList (title,itemId,quantity) VALUES (?,?,?)",(title,itemId,quantity))

    c.commit()        

###########################################################################
# Main program
printHeader('Ebay Listings')


###########################################################################
# Import data
if form.has_key('import'):
    try:
        loadFromEbay()
    except Exception,e:
        c.rollback()
        print "<p class=error>Problem importing data:</p><pre>",sys.exc_info(),"</pre>"

print gotoButton('Import listings from Ebay','ebayListing.py?import=1')

###########################################################################
# Add link to item
if form.has_key('linkToItem'):
    itemid = form['itemid'].value
    title = urllib.unquote_plus(form['title'].value)
    print "<p>Linking <i>"+title+"<i> to item id "+itemid+"</p>"
    cursor.execute('INSERT INTO ebayList2Item (title,itemid) VALUES (?,?)',(title,itemid))
    c.commit()
    
###########################################################################
# Add link to kit
if form.has_key('linkToKit'):
    kitid = form['kitid'].value
    title = urllib.unquote_plus(form['title'].value)
    print "<p>Linking <i>"+title+"<i> to kit id "+kitid+"</p>"
    cursor.execute('INSERT INTO ebayList2Kit (title,kitid) VALUES (?,?)',(title,kitid))
    c.commit()
    
###########################################################################
# Remove link
if form.has_key('unlink'):
    if form.has_key('itemid'):
        itemid = form['itemid'].value
        title = urllib.unquote_plus(form['title'].value)
        print "<p>Unlinking <i>"+title+"<i> from item id "+itemid+"</p>"
        cursor.execute('DELETE FROM ebayList2Item WHERE title = ? AND itemid = ?',(title,itemid))
    elif form.has_key('kitid'):
        kitid = form['kitid'].value
        title = urllib.unquote_plus(form['title'].value)
        print "<p>Unlinking <i>"+title+"<i> from kit id "+kitid+"</p>"
        cursor.execute('DELETE FROM ebayList2Kit WHERE title = ? AND kitid = ?',(title,kitid))
    
    c.commit()
    
#######################################
# Read in how many items are in kits
itemQtyInKits = {}
cursor.execute('''
SELECT
    itemId,
    SUM(Kit.quantity * kitItem.quantity)
FROM
    Kit
    LEFT JOIN kitItem USING (kitId)
GROUP BY kitId,itemId
''')
for (itemId,qty) in cursor:
    if itemId not in itemQtyInKits: itemQtyInKits[itemId] = 0
    itemQtyInKits[itemId] += qty

######################################
# Read in main table with links
cursor.execute('''
SELECT
    ebayList.title,
    ebayList.quantity,
    ebayList.itemId,
    Item.itemId AS myItemIdItem,
    manufacturer,
    Item.brand,
    Item.name,
    SUM(BinItems.quantity) AS itemQty,
    Kit.kitId as kitId,
    Kit.name as kitName,
    Kit.quantity as kitQty
FROM
    ebayList
    LEFT JOIN ebayList2Item USING (title)
    LEFT JOIN Item USING (itemId)
    LEFT JOIN BinItems USING (itemId)
    LEFT JOIN ebayList2Kit ON ebayList.title == ebayList2Kit.title
    LEFT JOIN Kit USING (kitId)
GROUP BY ebayList.itemId
ORDER BY
    ebayList.title''')

print "<TABLE BORDER=1 class='listthings sortable'>"
print "<TR><TH>Ebay Title</TH><TH>Listed<br />Qty</TH><TH>Item</TH><TH>Stock<br />Qty</TH><TH>Dup</TH></TR>"
count = 0
itemsSeen = {}
results = []
duplicates = {}
for (title,listQty,itemId,myItemId,mfr,brand,name,itemQty,kitId,kitName,kitQty) in cursor:
#    print "%s - %s<br>"%(title,itemId)
#    if title != 'OPI Nail Polish Yule Love This Silver~ Glitter~VHTF':
#        continue
    seenName = None
    if mfr:
        seenName = getItemName(mfr,brand,name)
    elif kitName:
        seenName = kitName
    if seenName:
        if seenName in itemsSeen:
            duplicates[seenName] = True
        itemsSeen[seenName] = True
    else:
        seenName = None
    if myItemId:
        unlinkField = 'itemid'
        unlinkId = myItemId
        quantity = itemQty
        if myItemId in itemQtyInKits:
            quantity -= itemQtyInKits[myItemId]
    elif kitId:
        unlinkField = 'kitid'
        unlinkId = kitId
        quantity = kitQty
    else:
        unlinkField = None
        unlinkId = None
        quantity = None
    results.append((title,listQty,seenName,quantity,unlinkId,unlinkField))
    
for (title,listQty,itemName,quantity,unlinkId,unlinkField) in results:
    count += 1
    if unlinkField == 'itemid':
        if listQty > quantity:
            rowClass = 'CLASS=error'
        elif listQty != quantity:
            rowClass = 'CLASS=warning'
        elif listQty == quantity:
            rowClass = ''
    elif unlinkField == 'kitid':
        if listQty > quantity:
            rowClass = 'CLASS=error'
        elif listQty != quantity:
            rowClass = 'CLASS=warning'
        elif listQty == quantity:
            rowClass = ''
    else:
        rowClass = 'CLASS=error'
    if itemName == None:
        linkCells = '<TD>'+gotoButton('Link to item','linkEbay2Stock.py?title=%s'%urllib.quote_plus(title))+gotoButton('Link to kit','linkEbay2Kit.py?title=%s'%urllib.quote_plus(title))+'</TD><TD> </TD>'
        seenCell = ''
    else:
        linkCells = '<TD>'+itemName+' '+gotoButton('Del','ebayListing.py?unlink=1&title=%s&%s=%s'%(urllib.quote_plus(title),unlinkField,unlinkId))+'</TD><TD>'+str(quantity)+'</TD>'


        if itemName in duplicates:
            seenCell = 'X'
        else:
            seenCell = ''
    
    print "<TR %s><TD>%s</TD><TD>%s</TD>%s<TD>%s</TD></TR>"%(rowClass,title,listQty,linkCells,seenCell)
print "</TABLE>"
print "<p><i>%d entries</i></p>"%count
printFooter()
