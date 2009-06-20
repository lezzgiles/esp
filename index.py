#!/python26/python.exe
# -*- coding: UTF-8 -*-

# enable debugging
import cgitb
import sqlite3
from myutils import sql,printHeader,printFooter

cgitb.enable()

printHeader("Stock Management")

print "<p><A HREF=stockList.py>Stock list</A>: Manage stock</p>"
print "<p><A HREF=binList.py>Bin list</A>: List bins and their contents</p>"
print "<p><A HREF=purchases.py>Purchases</A>: List purchases, add new purchases</p>"
print "<p><A HREF=sales.py>Sales</A>: List sales and add new sales</p>"
print "<H2>Admin stuff</H2>"
print "<p><A HREF=bins.py>bins</A>: manage the set of bins</p>"
print "<p><A HREF=items.py>items</A>: manage the item manufacturers and descriptions</p>"
printFooter()