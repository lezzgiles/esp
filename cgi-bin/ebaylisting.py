#!/python26/python.exe
# -*- coding: UTF-8 -*-

# enable debugging
import cgitb
import cgi
import sys
import urllib
from myutils import c,cursor,sql, printHeader, printFooter, gotoButton, centsToDollarString, dollarStringToCents, cell, moneyCell, getItemName
from datetime import datetime,timedelta

cgitb.enable()
form = cgi.FieldStorage()

#import the HTTP, DOM and ConfigParser modules needed
import httplib, ConfigParser
from xml.dom.minidom import parse, parseString

# How many items to retrieve at a time
pageSize = 200

# open config file
config = ConfigParser.ConfigParser()
config.read("config.ini")

# specify eBay API dev,app,cert IDs
devID = config.get("Keys", "Developer")
appID = config.get("Keys", "Application")
certID = config.get("Keys", "Certificate")

#get the server details from the config file
serverUrl = config.get("Server", "URL")
serverDir = config.get("Server", "Directory")

# specify eBay token
# note that eBay requires encrypted storage of user data
userToken = config.get("Authentication", "Token")

#eBay Call Variables
#siteID specifies the eBay international site to associate the call with
#0 = US, 2 = Canada, 3 = UK, ....
siteID = "0"
#verb specifies the name of the call
verb = "GetSellerList"
#verb = "GeteBayTimeRequest"
#The API level that the application conforms to
compatabilityLevel = "625"

###########################################################################
# FUNCTION: buildHttpHeaders
# Build together the required headers for the HTTP request to the eBay API
def buildHttpHeaders():
    httpHeaders = {"X-EBAY-API-COMPATIBILITY-LEVEL": compatabilityLevel,
               "X-EBAY-API-DEV-NAME": devID,
               "X-EBAY-API-APP-NAME": appID,
               "X-EBAY-API-CERT-NAME": certID,
               "X-EBAY-API-CALL-NAME": verb,
               "X-EBAY-API-SITEID": siteID,
               "Content-Type": "text/xml"}
    return httpHeaders

###########################################################################
# FUNCTION: buildRequestXml
# Build the body of the call (in XML) incorporating the required parameters to pass
def buildRequestXml(pageNo,number):
    now = datetime.now()
    now = now.replace(microsecond=0)
    nowString = now.isoformat()
    futureString = (now + timedelta(days=120)).isoformat()
    requestXml ="<?xml version='1.0' encoding='utf-8'?>"+\
              "<GetSellerList xmlns=\"urn:ebay:apis:eBLBaseComponents\">"+\
              "<RequesterCredentials><eBayAuthToken>" + userToken + "</eBayAuthToken></RequesterCredentials>" + \
              "<EndTimeFrom>%s</EndTimeFrom>"%nowString + \
              "<EndTimeTo>%s</EndTimeTo>"%futureString + \
              "<DetailLevel>ReturnAll</DetailLevel>" + \
              "<OutputSelector>TotalNumberOfPages</OutputSelector>" + \
              "<OutputSelector>ItemArray.Item.Quantity</OutputSelector>" + \
              "<OutputSelector>ItemArray.Item.Title</OutputSelector>" + \
              "<OutputSelector>ItemArray.Item.SellingStatus.ListingStatus</OutputSelector>" + \
              "<OutputSelector>ItemArray.Item.SellingStatus.QuantitySold</OutputSelector>" + \
              "<Pagination>"+\
                 "<EntriesPerPage>%d</EntriesPerPage>"%number+\
                 "<PageNumber>%d</PageNumber>"%pageNo+\
               "</Pagination>"+\
              "</GetSellerList>"
#    requestXml = "<?xml version='1.0' encoding='utf-8'?>"+\
#              "<GeteBayOfficialTimeRequest xmlns=\"urn:ebay:apis:eBLBaseComponents\">"+\
#              "<RequesterCredentials><eBayAuthToken>" + userToken + "</eBayAuthToken></RequesterCredentials>" + \
#              "</GeteBayOfficialTimeRequest>"

    return requestXml

###########################################################################
def getPage(connection,pageNo,number,itemList):
    # specify a POST with the results of generateHeaders and generateRequest
    connection.request("POST", serverDir, buildRequestXml(pageNo,number), buildHttpHeaders())
    response = connection.getresponse()

    # if response was unsuccessful, output message
    if response.status != 200:
        raise "Error sending request:" + response.reason
        
    else: #response successful
        # store the response data and close the connection
        data = response.read()
        connection.close()
        #print data
        # parse the response data into a DOM
        response = parseString(data)
        
        # check for any Errors
        errorNodes = response.getElementsByTagName('Errors')
        if (errorNodes != []): #there are errors
            print "<P><B>eBay returned the following errors</B>"
            #Go through each error:
            for error in errorNodes:
                errmsg = ''
                #output the error code and short message
                errmsg += "<P>" + ((error.getElementsByTagName('ErrorCode')[0]).childNodes[0]).nodeValue
                errmsg +=  " : " + ((error.getElementsByTagName('ShortMessage')[0]).childNodes[0]).nodeValue.replace("<", "&lt;")
                #output Long Message if it exists (depends on ErrorLevel setting)
                if (error.getElementsByTagName('LongMessage')!= []):
                    errmsg += ((error.getElementsByTagName('LongMessage')[0]).childNodes[0]).nodeValue.replace("<", "&lt;")
                raise errmsg
            
        else: #eBay returned no errors - output results
            totalNumberOfPages = int(getText(response.getElementsByTagName('TotalNumberOfPages')[0].childNodes))
            for item in response.getElementsByTagName('Item'):
                title = getText(item.getElementsByTagName('Title')[0].childNodes)
                quantity = getText(item.getElementsByTagName('Quantity')[0].childNodes)
                listingStatus = getText(item.getElementsByTagName('ListingStatus')[0].childNodes)
                quantitySold = getText(item.getElementsByTagName('QuantitySold')[0].childNodes)
                quantity = int(quantity) - int(quantitySold)
                if listingStatus == 'Active':
                    itemList.append([title,quantity])

    # force garbage collection of the DOM object
    response.unlink()

    return totalNumberOfPages    

###########################################################################
def getText(nodelist):
    rc = ""
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc = rc + node.data
    return rc

###########################################################################
def loadFromEbay():
    # specify the connection to the eBay Sandbox environment
    connection = httplib.HTTPSConnection(serverUrl)

    itemList = []

    # Get first page, which also gets the total number of pages
    totalNumberOfPages = getPage(connection,1,pageSize,itemList)

    # Already got first page, so start at page 2
    for pageNo in (range(2,totalNumberOfPages+1)):
        getPage(connection,pageNo,pageSize,itemList)

    # Clean up the table
    cursor.execute("DELETE FROM ebayList")

    # Add the new data to the table    
    for (title,quantity) in itemList:
        cursor.execute("INSERT INTO ebayList (title,quantity) VALUES (?,?)",(title,quantity))

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

print gotoButton('Import listings from Ebay','ebaylisting.py?import=1')

###########################################################################
# Add link
if form.has_key('link'):
    itemid = form['itemid'].value
    title = urllib.unquote_plus(form['title'].value)
    print "<p>Linking <i>"+title+"<i> to item id "+itemid+"</p>"
    cursor.execute('INSERT INTO ebayList2Item (title,itemid) VALUES (?,?)',(title,itemid))
    c.commit()
    
######################################
# Table
cursor.execute('''
SELECT
    title,ebayList.quantity,Item.manufacturer,Item.brand,Item.name,SUM(BinItems.quantity)
FROM
    ebayList
    LEFT JOIN ebayList2Item USING (title)
    LEFT JOIN BinItems USING (itemId)
    LEFT JOIN Item USING (itemId)
GROUP BY title
ORDER BY
    title''')

print "<TABLE BORDER=1 class='listthings sortable'>"
print "<TR><TH>Ebay Title</TH><TH>Listed<br />Qty</TH><TH>Item</TH><TH>Stock<br />Qty</TH><TH>Dup</TH></TR>"
count = 0
itemsSeen = {}
results = []
duplicates = {}
for (title,listQty,mfr,brand,name,gotQty) in cursor:
    if mfr:
        itemName = getItemName(mfr,brand,name)
        if itemName in itemsSeen:
            duplicates[itemName] = True
        itemsSeen[itemName] = True
    else:
        itemName = None
    results.append((title,listQty,itemName,gotQty))
    
for (title,listQty,itemName,gotQty) in results:
    count += 1
    if not gotQty:
        rowClass = 'CLASS=warning'
    elif listQty > gotQty:
        rowClass = 'CLASS=error'
    elif listQty != gotQty:
        rowClass = 'CLASS=warning'
    else:
        rowClass = ''
    if itemName == None:
        linkCells = '<TD>'+gotoButton('Link item to stock','linkEbay2Stock.py?title=%s'%urllib.quote_plus(title))+'</TD><TD> </TD>'
        seenCell = ''
    else:
        linkCells = '<TD>'+itemName+'</TD><TD>'+str(gotQty)+'</TD>'        
        if itemName in duplicates:
            seenCell = 'X'
        else:
            seenCell = ''
    
    print "<TR %s><TD>%s</TD><TD>%s</TD>%s<TD>%s</TD></TR>"%(rowClass,title,listQty,linkCells,seenCell)
print "</TABLE>"
print "<p><i>%d entries</i></p>"%count
printFooter()