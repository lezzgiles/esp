#!/python26/python.exe

# enable debugging
import sqlite3
import sys
from types import TupleType

version = '1.4'

#c = sqlite3.connect('/home/lezzgiles/esp/example',isolation_level='EXCLUSIVE')
c = sqlite3.connect('C:/temp/example',isolation_level='EXCLUSIVE')
cursor = c.cursor()

def sql(c,sql):
    print '<pre>',sql,'</pre>'
    c.cursor().execute(sql)
    c.commit()

def printHeader1(header):
    print "Content-Type: text/html;charset=utf-8"
    print
    print '''
<HTML>
<HEAD>
<TITLE>%s</TITLE>
'''%header

def printHeader2(header,errorString):
    print '''
<link rel="stylesheet" href="/esp-docs/css/esp.css" type="text/css">
<script src="/esp-docs/js/sorttable.js"></script>
<script src="/esp-docs/js/myutils.js"></script>
</HEAD>
<BODY>
<div class=mainbody>
'''
    printNavigation()
    print '<H1>%s</H1>'%header
    if errorString:
        print errorString
#    print version

def printRedirect(header,url,delay):
    print '''
<META http-equiv="REFRESH" content="%d,%s">
</HEAD>
<BODY>
<div class=mainbody>
'''%(delay,url)
    print '<H1>%s</H1>'%header
    if delay == 0:
        print "Redirecting to %s"%(url)
    else:
        print "Redirecting to %s in %d seconds...."%(url,delay)
    print '</div>'
    print '</BODY>'
    print '</HTML>'

def printHeader(header):
    printHeader1(header)
    printHeader2(header,None)

def printFooter():
    printNavigation()
    print "</div>"
    print "</BODY>"
    print "</HTML>"

def gotoButton(name,url):
    return "<INPUT TYPE=button onClick='this.disabled = true; location.href=\"%s\"' VALUE='%s' />"%(url,name)

def printNavigation():
    print '<div class=navibar>'
    print gotoButton('top','index.py')
    print gotoButton('Purchases','purchases.py')
    print gotoButton('Sales','sales.py')
    print gotoButton('Stock list','stockList.py')
    print gotoButton('Bin list','binList.py')
    print gotoButton('Ebay Listings','ebayListing.py')
    print '<br />'
    print gotoButton('Expenses','expenses.py')
    print gotoButton('Bins','bins.py')
    print gotoButton('Items','items.py')
    print gotoButton('Kits','kits.py')
    print gotoButton('History','history.py')
    print gotoButton('Report','report.py')
    print '<input type=button onClick="alert(\'ESP version %s\\n\\n\\nChanges in 1.4:\\nAdded kits\\nChanges in 1.3.1:\\nAdded delete button for links to ebay listings\\nAdded check on #of listings found on ebay\\nChanges in 1.3:\\nTracking number & actual shipping costs recorded per sale\\nActual shipping cost factored into weekly report\\nAdd sale,purchase,move redirects so that page reload does not re-add transaction.\\nAdded expenses & fees\\nChanges in 1.2:\\nDates in history are localtime.\\nConsistent formatting in history table.\\nOn move, max possible items are automatically prefilled.\\nChanges in 1.1:\\nEnter key disabled in forms, so you cannot accidentally submit form by hitting enter.\\nNumber of slots is a numeric field instead of fixed to just 6, 17 or infinite.\\nBins are sorted in drop-down lists.\\nTotal number of items displayed at bottom of item list.\\nImproved table sort performance.\\nMove, purchase and sale are all entered into history and can be undone.\\nNew history page showing details of old transactions & moves.\\nAbility to add new item types in purchase form.\');" value=About />'%version
    print "</div>"

def printOptions(label,field,valueList):
    print '%s: <SELECT NAME=%s>'%(label,field)
    for (thisValue,display) in valueList:
        print '<OPTION VALUE=%s>%s</OPTION>'%(thisValue,display)
    print '</SELECT>'

def centsToString(cents):
    if not cents: return '0.00'
    dollars = cents // 100
    cents = cents % 100
    return "%d.%02d"%(dollars,cents)

def centsToDollarString(cents):
    return "$%s"%centsToString(cents)

def dollarStringToCents(dollarString):
    (dollars,cents) = dollarString.split('.')
    return int(dollars)*100+int(cents)

def getTranType(type,direction):
    if type == 'REAL':
        if direction == 'ADD':
            typeDetail = 'Purchase'
        else:
            typeDetail = 'Sale'
    else:
        if direction == 'ADD':
            typeDetail = 'Reconcile add'
        else:
            typeDetail = 'Reconcile del'
    
    return typeDetail

def getItemName(manufacturer,brand,name):
    manufacturer = manufacturer.replace("'","\\'")
    if brand: brand = brand.replace("'","\\'")
    name = name.replace("'","\\'")
    if not brand: return '%s %s'%(manufacturer,name)
    else: return '%s %s %s'%(manufacturer,brand,name)

def getName(name):
    return name.replace("'","\\'")
    
def cell(contents):
    return '<TD>%s</TD>'%contents

def moneyCell(value):
    return '<TD class=money>%s</TD>'%centsToDollarString(value)
                                                         
# Sort the list by words
def sortLists(a,b):
    # if either is 'unstocked', it comes first
    if a[0] == 'unstocked': return -1
    if b[0] == 'unstocked': return 1
    matchLength = min((len(a),len(b)))
    for i in range(matchLength):
        if a[i] == b[i]: continue
        try:
            return int(a[i]) - int(b[i])
        except:
            pass
        if a[i] > b[i]: return 1
        if a[i] < b[i]: return -1
    return 0

# Various queries and updates
def checkZero(qty):
    if isinstance(qty,TupleType): qty = qty[0]
    try:
        return int(qty)
    except Exception,e:
        return 0

def db_howManyInBin(binId,itemId):
    cursor.execute('SELECT SUM(quantity) FROM BinItems WHERE binId = ? AND itemId = ?',
                   (binId,itemId))
    qty = checkZero(cursor.fetchone())
    return qty

def db_enoughEmptySlotsInBin(binId,qty):
    cursor.execute('SELECT slots FROM Bin WHERE binId = ?',(binId,))
    totalSlots = checkZero(cursor.fetchone())
    if totalSlots == 0: return True    # 0 = infinite slots

    cursor.execute('SELECT SUM(quantity) FROM BinItems WHERE binId = ?',(binId,))
    usedSlots = checkZero(cursor.fetchone())
    if (totalSlots - usedSlots) >= qty:
        return True
    else:
        return False

def db_removeFromBin(binId,itemId,qty):
    # First, make sure there's enough
    oldQty = db_howManyInBin(binId,itemId)
    if qty > oldQty:
        raise ValueError, '<p class=error>Update failed - not enough items to move</p>'

    cursor.execute('DELETE FROM binItems WHERE binId = ? and itemId = ?',(binId,itemId))
    if oldQty-qty != 0:
        cursor.execute('INSERT INTO binItems (binId,itemId,quantity) VALUES (?,?,?)',
                       (binId,itemId,oldQty-qty))

def db_addToBin(binId,itemId,qty):
    # First, make sure there's space
    if not db_enoughEmptySlotsInBin(binId,qty):
        raise ValueError, '<p class=error>Update failed - not enough space to add items</p>'

    oldQty = db_howManyInBin(binId,itemId)

    cursor.execute('DELETE FROM binItems WHERE binId = ? and itemId = ?',(binId,itemId))
    cursor.execute('INSERT INTO binItems (binId,itemId,quantity) VALUES (?,?,?)',
                   (binId,itemId,oldQty+qty))

    
