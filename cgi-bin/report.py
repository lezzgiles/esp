#!/python26/python.exe

# enable debugging
import cgitb
import cgi
from myutils import c,cursor,sql, printHeader, printFooter, printOptions, centsToDollarString, getItemName, gotoButton, db_removeFromBin, db_addToBin
import sys

cgitb.enable()

form = cgi.FieldStorage()

printHeader('Monthly Report')

###############################################################################
# Get the earliest transaction date
cursor.execute('SELECT tranDate FROM trans ORDER BY trandate LIMIT 1')
(earliest,) = cursor.fetchone()
(earliestYear,earliestMonth,earliestDay) = earliest.split('-')
earliestYear = int(earliestYear)
earliestMonth = int(earliestMonth)

# Get the latest transaction date
cursor.execute('SELECT tranDate FROM trans ORDER BY trandate DESC LIMIT 1')
(latest,) = cursor.fetchone()
(latestYear,latestMonth,latestDay) = latest.split('-')
latestYear = int(latestYear)
latestMonth = int(latestMonth)

# Generate the list of year/date starting & ending points
year = earliestYear
month = earliestMonth
dates = []
while True:
    if month == 12:
        endYear = year+1
        endMonth = 1
    else:
        endYear = year
        endMonth = month+1

    dates.append(["%02d-%02d-01"%(year,month),"%02d-%02d-01"%(endYear,endMonth)])

    if year == latestYear and month == latestMonth: break

    year = endYear
    month = endMonth

dates.reverse()

boughtQuery = "SELECT SUM(quantity) FROM trans LEFT JOIN transItem USING (tranId) WHERE tranDate >= ? AND tranDate < ? AND direction = 'ADD'"
soldQuery = "SELECT SUM(quantity) FROM trans LEFT JOIN transItem USING (tranId) WHERE tranDate >= ? AND tranDate < ? AND direction = 'DEL'"

print "<TABLE BORDER=1>"
print "<TR><TH>Month beginning</TH><TH>Bought</TH><TH>Sold</TH><TH>Delta</TH></TR>"
for (start,end) in dates:
    cursor.execute(boughtQuery,(start,end))
    (bought,) = cursor.fetchone() ; bought = int(bought)
    cursor.execute(soldQuery,(start,end))
    (sold,) = cursor.fetchone() ; sold = int(sold)
    print "<TR>"
    print "<TD>%s</TD>"%start
    print "<TD>%d</TD>"%bought
    print "<TD>%d</TD>"%sold
    print "<TD>%d</TD>"%(bought-sold,)
    print "</TR>"
print "</TABLE>"

printFooter()
