#!/python26/python.exe
# -*- coding: UTF-8 -*-

# enable debugging
import cgitb
import cgi
import sqlite3
from myutils import sql, printHeader, printFooter

cgitb.enable()

form = cgi.FieldStorage()

c = sqlite3.connect('/temp/example')
cursor = c.cursor()

printHeader('Item Management')


####################
# Add form
print '''
<div class=addthing>
<FORM>
<H2>Add new item type</H2>
<table>
<tr><td align=right>Manufacturer:</td><td><INPUT TYPE=TEXT NAME=manufacturer ID=addItemMfr></INPUT></td></tr>
<tr><td align=right>Brand:</td><td><INPUT TYPE=TEXT NAME=brand ID=brand></INPUT></td></tr>
<tr><td align=right>Name:</td><td><INPUT TYPE=TEXT NAME=name ID=name></INPUT></td></tr>
<INPUT TYPE=hidden NAME=add VALUE=1/>
</table>
<INPUT TYPE=SUBMIT VALUE='Add new item type' onClick='return validateForm();' />
</FORM>
</div>

<script language=javascript>
function validateForm()
{
    return (
        checkField('addItemMfr','Fill out the manufacturer name')  &&
        checkField('name','Fill out the product name')
        );
}
</script>
'''

######################
# Handle add
if form.has_key('add'):
    if form.has_key('brand'): brand = form['brand'].value
    else: brand = None
    
    if not form.has_key('manufacturer'):
        print "<p class=error>Oops - you must fill in the manufacturer</p>"
    elif not form.has_key('name'):
        print "<p class=error>Oops - you must fill in the name</p>"
    else:
        try:
            if brand:
                details = (form['manufacturer'].value,brand,form['name'].value)
                sql = "INSERT INTO item (manufacturer,brand,name) VALUES (?,?,?)"
                cursor.execute(sql,details)
                c.commit()
            else:
                details = (form['manufacturer'].value,form['name'].value)
                sql = "INSERT INTO item (manufacturer,name) VALUES (?,?)"
                cursor.execute(sql,details)
                c.commit()
        except sqlite3.IntegrityError:
            print "<p class=error>Oops - item %s already exists!</p><br />"%form['name'].value

#######################3
# Handle delete
# NO DELETE SINCE OLD SALE & PURCHASE RECORDS WILL POINT TO OLD STOCK
#if form.has_key('delete'):
#    print "Got delete"
#    print "<p class=info>Deleting",form['name'].value,"</p>"
#    try:
#        sql = "DELETE FROM item WHERE itemId = ?"
#        cursor.execute(sql,(form['delete'].value,))
#        c.commit()
#        print "Committed"
#    except:
#        print "<p class=error>Sorry, something went wrong with the deletion.</p>"

###################
# Display list
cursor.execute("SELECT itemId,manufacturer,brand,name,COUNT(binItems.binId) AS number FROM item LEFT JOIN binItems USING (itemId) GROUP BY itemId ORDER BY manufacturer,brand,name")

print "<TABLE BORDER=1 class=listthings>"
print "<TR><TH>Mfr</TH><TH>brand</TH><TH>name</TH></TR>"
for (itemId,manufacturer,brand,name,number) in cursor:
    print "<TR>"
    if not brand: brand = '-'
    print "<TD>%s</TD><TD>%s</TD><TD>%s</TD>"%(manufacturer,brand,name)
    print "</TR>"
print "</TABLE>"

print "<SCRIPT LANGUAGE='javascript'>document.getElementById('addItemMfr').focus();</SCRIPT>"

printFooter()