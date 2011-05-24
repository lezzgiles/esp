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
              "<GranularityLevel>Coarse</GranularityLevel>" + \
              "<Pagination>"+\
                 "<EntriesPerPage>%d</EntriesPerPage>"%number+\
                 "<PageNumber>%d</PageNumber>"%pageNo+\
               "</Pagination>"+\
              "</GetSellerList>"
#              "<DetailLevel>ReturnAll</DetailLevel>" + \
#              "<OutputSelector>TotalNumberOfPages</OutputSelector>" + \
#              "<OutputSelector>ItemArray.Item.Quantity</OutputSelector>" + \
#              "<OutputSelector>ItemArray.Item.Title</OutputSelector>" + \
#              "<OutputSelector>ItemArray.Item.SellingStatus.ListingStatus</OutputSelector>" + \
#              "<OutputSelector>ItemArray.Item.SellingStatus.QuantitySold</OutputSelector>" + \

    return requestXml

###########################################################################
def getPage(pageNo,number,itemList):

    connection = httplib.HTTPSConnection(serverUrl)

    # specify a POST with the results of generateHeaders and generateRequest
    connection.request("POST", serverDir, buildRequestXml(pageNo,number), buildHttpHeaders())
    response = connection.getresponse()

    # if response was unsuccessful, output message
    if response.status != 200:
        raise Exception,"Error sending request:" + response.reason
        
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
                raise Exception,errmsg
            
        else: #eBay returned no errors - output results
            totalNumberOfPages = int(getText(response.getElementsByTagName('TotalNumberOfPages')[0].childNodes))
            for item in response.getElementsByTagName('Item'):
                title = getText(item.getElementsByTagName('Title')[0].childNodes)
                itemId = getText(item.getElementsByTagName('ItemID')[0].childNodes)
                quantity = getText(item.getElementsByTagName('Quantity')[0].childNodes)
                listingStatus = getText(item.getElementsByTagName('ListingStatus')[0].childNodes)
                quantitySold = getText(item.getElementsByTagName('QuantitySold')[0].childNodes)
                quantity = int(quantity) - int(quantitySold)
                if listingStatus == 'Active':
                    itemList.append([title,itemId,quantity])

    # force garbage collection of the DOM object
    response.unlink()

    return totalNumberOfPages    

###########################################################################
def ebayFindItem(item):

    connection = httplib.HTTPConnection('svcs.ebay.com')

    # specify a POST with the results of generateHeaders and generateRequest
    connection.request("GET", '/services/search/FindingService/v1?OPERATION-NAME=findItemsByKeywords&SERVICE-VERSION=1.0.0&SECURITY-APPNAME=%s&GLOBAL-ID=EBAY-US&responseencoding=XML&paginationInput.entriesPerPage=1&REST-PAYLOAD&keywords=%s'%(appID,urllib.quote_plus(item)))
    response = connection.getresponse()

    if response.status != 200:
        raise Exception,"Error sending request:" + response.reason
        
    else: #response successful
        # store the response data and close the connection
        data = response.read()
        connection.close()

        # parse the response data into a DOM
        response = parseString(data)
        #searchResults = response.getElementsByTagName('searchResult')
        #count = searchResults[0].getAttribute('count')
        count = response.getElementsByTagName('totalEntries')[0].firstChild.data

    # force garbage collection of the DOM object
    response.unlink()


    return int(count)

###########################################################################
def getText(nodelist):
    rc = ""
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc = rc + node.data
    return rc
