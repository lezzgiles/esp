#!/python26/python.exe

# enable debugging
import sqlite3

c = sqlite3.connect('/temp/example',isolation_level='EXCLUSIVE')
cursor = c.cursor()

def sql(c,sql):
    print '<pre>',sql,'</pre>'
    c.cursor().execute(sql)
    c.commit()

def printHeader(header):
    print "Content-Type: text/html;charset=utf-8"
    print
    print '''
<HTML>
<HEAD>
<TITLE>%s</TITLE>
<link rel="stylesheet" href="/esp-docs/css/esp.css" type="text/css">
<script src="/esp-docs/js/sorttable.js"></script>
<script src="/esp-docs/js/myutils.js"></script>
</HEAD>
<BODY>
<div class=mainbody>
'''%header
    printNavigation()
    print '<H1>%s</H1>'%header

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
    print gotoButton('Ebay Missing','ebayMissing.py')
    print '<br />'
    print gotoButton('Bin management','bins.py')
    print gotoButton('Item type management','items.py')
    print "</div>"

def printOptions(label,field,valueList):
    print '%s: <SELECT NAME=%s>'%(label,field)
    for (thisValue,display) in valueList:
        print '<OPTION VALUE=%s>%s</OPTION>'%(thisValue,display)
    print '</SELECT>'

def centsToDollarString(cents):
    dollars = cents // 100
    cents = cents % 100
    return "$%d.%02d"%(dollars,cents)

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
    
def cell(contents):
    return '<TD>%s</TD>'%contents

def moneyCell(value):
    return '<TD class=money>%s</TD>'%centsToDollarString(value)
                                                         