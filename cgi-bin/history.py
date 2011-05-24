#!/python26/python.exe

# enable debugging
import cgitb
import cgi
from myutils import c,cursor,sql, printHeader, printFooter, printOptions, centsToDollarString, getItemName, gotoButton, db_removeFromBin, db_addToBin
import sys

cgitb.enable()

form = cgi.FieldStorage()

printHeader('History')

# Read in the bin names and the item names - we're going to need them later
cursor.execute('SELECT binId,name FROM Bin')
binName = {}
for (thisId,thisName) in cursor: binName[thisId] = thisName

cursor.execute('SELECT itemId,manufacturer,brand,name FROM Item')
itemName = {}
for (thisId,thisMfr,thisBrand,thisName) in cursor:
    thisLongName = getItemName(thisMfr,thisBrand,thisName)
    itemName[thisId] = thisLongName

###############################################################################
if form.has_key('undo'):
    try:
        undo = int(form['undo'].value)

        cursor.execute('BEGIN IMMEDIATE TRANSACTION')

        cursor.execute('SELECT body FROM history WHERE historyId = ?',(undo,))

        (s,) = cursor.fetchone()

        sl = s.split()
        stype = sl.pop(0)
        if stype == 'MOVE':
            itemId = int(sl.pop(0))
            sl.pop(0)
            binId = int(sl.pop(0))
            total = 0
            while len(sl) > 0:
                qty = int(sl.pop(0))
                sl.pop(0)
                to = int(sl.pop(0))
                total += qty

                # reduce quantity in 'to' by qty
                db_removeFromBin(to,itemId,qty)

            # add total to binId
            db_addToBin(binId,itemId,total)

        elif stype == 'SELL':
            tranId = int(sl.pop(0))

            while len(sl) > 0:
                qty = int(sl.pop(0))
                itemId = int(sl.pop(0))
                sl.pop(0)
                binId = int(sl.pop(0))
                db_addToBin(binId,itemId,qty)

            cursor.execute('DELETE FROM TransItem WHERE tranId = ?',(tranId,))
            cursor.execute('DELETE FROM Trans WHERE tranId = ?',(tranId,))

        elif stype == 'BUY':
            tranId = int(sl.pop(0))

            while len(sl) > 0:
                qty = int(sl.pop(0))
                sl.pop(0)
                itemId = int(sl.pop(0))
                sl.pop(0)
                binId = int(sl.pop(0))
                db_removeFromBin(binId,itemId,qty)

            cursor.execute('DELETE FROM TransItem WHERE tranId = ?',(tranId,))
            cursor.execute('DELETE FROM Trans WHERE tranId = ?',(tranId,))

        # delete history
        cursor.execute('DELETE FROM history WHERE historyId = ?',(undo,))

        # Commit changes
        c.commit()
    except Exception,e:
        c.rollback()
        print "<p class=error>Problem with database update:</p><pre>",sys.exc_info(),"</pre>"
        raise

###############################################################################
cursor.execute('''
SELECT
    historyId, datetime(historyDate,'localtime'), body
FROM
    history
ORDER BY historyDate DESC
''')

history = []

for itemDetails in cursor:
    history.append(itemDetails)

def display(s):
    sl = s.split()
    stype = sl.pop(0)
    if stype == 'MOVE': return displayMove(sl)
    if stype == 'SELL': return displaySell(sl)
    if stype == 'BUY': return displayBuy(sl)

def getBinName(binId):
    if binId in binName: return binName[binId]
    return 'Deleted bin'

def displayMove(sl):
    itemId = int(sl.pop(0))
    sl.pop(0)
    binId = int(sl.pop(0))
    thisBinName = getBinName(binId)
    value = "Moved <b><i>%s</i></b> from <b><i>%s</i></b>:"%(itemName[itemId],thisBinName)
    while len(sl) > 0:
        qty = sl.pop(0)
        sl.pop(0)
        to = int(sl.pop(0))
        value += "<br>&nbsp;&nbsp;&middot; %s to <b><i>%s</i></b>"%(qty,binName[to])

    return value

def displaySell(sl):
    value = "Sale:"
    tranId = int(sl.pop(0))
    while len(sl) > 0:
        qty = int(sl.pop(0))
        itemId = int(sl.pop(0))
        sl.pop(0)
        binId = int(sl.pop(0))
        thisBinName = getBinName(binId)
        value += "<br>&nbsp;&nbsp;&middot; %d <b><i>%s</i></b> from <b><i>%s</i></b></b>"%(qty,itemName[itemId],thisBinName)

    return value
    
def displayBuy(sl):
    value = "Buy:"
    tranId = int(sl.pop(0))
    while len(sl) > 0:
        qty = int(sl.pop(0))
        sl.pop(0)
        itemId = int(sl.pop(0))
        sl.pop(0)
        binId = int(sl.pop(0))
        thisBinName = getBinName(binId)
        value += "<br>&nbsp;&nbsp;&middot; %d <b><i>%s</i></b> to <b><i>%s</i></b></b>"%(qty,itemName[itemId],thisBinName)

    return value
    
if len(history) == 0:
    print "<H2>You don't have any history yet</H2>"
else:
    print "<TABLE BORDER=1>"
    print "<TR><TH>Date/time</TH><TH>Description</TH><TD></TD></TR>"

    for (historyId,historyDate,body) in history:
        print "<TR><TD>%s</TD><TD>%s</TD><TD>%s</TD></TR>"%(historyDate,display(body),gotoButton('undo','history.py?undo=%s'%historyId))

    print "</TABLE>"

printFooter()

