#!/python26/python.exe
# -*- coding: UTF-8 -*-

# enable debugging
import cgitb
import cgi
import sqlite3
from myutils import sql, printHeader, printFooter, gotoButton

cgitb.enable()

form = cgi.FieldStorage()

c = sqlite3.connect('/temp/example')
cursor = c.cursor()

printHeader('Edit item')

if not form.has_key('itemId'):
    print '<p class=error>Sorry, page called with no item to edit</p>'
else:
    itemId = form['itemId'].value

    cursor.execute('SELECT manufacturer,brand,name FROM item WHERE itemId = ?',(itemId,))
    (manufacturer,brand,name) = cursor.fetchone()
    if not brand: brand = ''

    print '''
<div class=addthing>
<FORM ACTION=items.py>
<H2>Edit item type</H2>
<table>
<tr><td align=right>Manufacturer:</td><td><INPUT TYPE=TEXT NAME=manufacturer ID=mfr SIZE=70 VALUE="%s" /></td></tr>
<tr><td align=right>Brand:</td><td><INPUT TYPE=TEXT NAME=brand ID=brand SIZE=70 VALUE="%s" /></td></tr>
<tr><td align=right>Name:</td><td><INPUT TYPE=TEXT NAME=name ID=name SIZE=70 VALUE="%s" /></td></tr>
<INPUT TYPE=hidden NAME=edit VALUE=%s />
</table>
<INPUT TYPE=SUBMIT VALUE='Submit changes' onClick='return validateForm();' />
</FORM>
</div>

<script language=javascript>
function validateForm()
{
    return (
        checkField('mfr','Fill out the manufacturer name')  &&
        checkField('name','Fill out the product name')
        );
}
</script>
'''%(manufacturer,brand,name,itemId)
