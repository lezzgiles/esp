#!/python26/python.exe
# -*- coding: UTF-8 -*-

# enable debugging
import cgitb
import cgi
from myutils import c,cursor,sql, printHeader, printFooter

cgitb.enable()

form = cgi.FieldStorage()

printHeader('Bin Management')

################
# Add form
print "<div class=addthing>"
print "<H2>Add new bin</H2>"
print "<FORM>"
print "<table>"
print "<tr><td align=right>Bin name:</td><td><INPUT TYPE=TEXT NAME=name ID=addBinName></INPUT></td></tr>"
print "<tr><td align=right>Number of slots:</td><td><SELECT name=slots>"
print "<OPTION VALUE=0 DEFAULT>Unlimited</OPTION>"
for i in range(1,7):
    print "<OPTION VALUE=%d>%d</OPTION>"%(i,i)
print "</SELECT><tr><td align=right>"
print "</table>"
print "<INPUT TYPE=hidden NAME=add VALUE=1/>"
print "<INPUT TYPE=SUBMIT VALUE='Add new bin' onClick='return validateForm();' />"
print "</FORM>"
print "</div>"

print '''<SCRIPT LANGUAGE='javascript'>
function validateForm()
{
    return (checkField('addBinName',"You must enter a bin name"));
}

document.getElementById('addBinName').focus();
</SCRIPT>'''

###############
# Handle add
if form.has_key('add'):
    try:    
        sql = "INSERT INTO bin (name,slots) VALUES (?,?)"
        cursor.execute(sql,(form['name'].value,form['slots'].value))
        c.commit()
    except sqlite3.IntegrityError:
        print "<p class=error>Oops - bin %s already exists!</p><br />"%form['name'].value

###############
# Handle delete
if form.has_key('delete'):
    try:
        sql = "DELETE FROM bin WHERE binId = ?"
        cursor.execute(sql,(form['delete'].value,))
        c.commit()
        print "<p class=info>Deleted",form['name'].value,"</p>"   
    except:
        print "<p class=error>Sorry, something went wrong with the deletion.</p>"

##########
# Display list
cursor.execute("SELECT binId,name,slots,COUNT(binItems.itemId) AS number FROM bin LEFT JOIN binItems USING (binId) GROUP BY binId ORDER BY name")

print "<TABLE border=1 class=listthings><TR><TH>Bin name</TH><TH>slots</TH><TH></TH></TR>"
for (binId,name,slots,number) in cursor:
    if not slots:
        slots = "Unlimited"
    print "<TR>"
    print "<TD>%s</TD><TD>%s</TD>"%(name,slots)
    if number:
        print "<TD>Has stock - cannot delete</TD>"
    elif name == 'unstocked':
        print "<TD>Cannot delete</TD>"
    else:
        print "<TD ALIGN=CENTER><INPUT TYPE=SUBMIT VALUE=Delete onClick='location.href=\"bins.py?delete=%s&name=%s\"' /></TD>"%(binId,name)
    print "</TR>"
print "</TABLE>"


printFooter()