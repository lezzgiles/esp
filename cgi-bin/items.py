#!/python26/python.exe
# -*- coding: UTF-8 -*-

# enable debugging
import cgitb
import cgi
from myutils import c,cursor,sql, printHeader, printFooter, gotoButton
import sqlite3

cgitb.enable()

form = cgi.FieldStorage()

printHeader('Item Management')

####################
# Add form
print '''
<div class=addthing>
<FORM>
<H2>Add new item type</H2>
<table>
<tr><td align=right>Manufacturer:</td><td><INPUT TYPE=TEXT NAME=manufacturer ID=addItemMfr SIZE=70></INPUT></td></tr>
<tr><td align=right>Brand:</td><td><INPUT TYPE=TEXT NAME=brand ID=brand SIZE=70></INPUT></td></tr>
<tr><td align=right>Name:</td><td><INPUT TYPE=TEXT NAME=name ID=name SIZE=70></INPUT></td></tr>
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
# Handle delete
if form.has_key('delete'):
    deleteId = int(form['delete'].value)
    # First check again that the item is not referenced
    cursor.execute('SELECT COUNT(*) FROM binItems where itemId = ?',(deleteId,))
    (count,) = cursor.fetchone()
    if int(count):
        print '<p class=error>Item is stored in bins - cannot delete</p>'
    else:
        cursor.execute('SELECT COUNT(*) FROM transItem where itemId = ?',(deleteId,))
        (count,) = cursor.fetchone()
        if int(count):
            print '<p class=error>Item is referenced in old transactions - cannot delete</p>'
        else:
            try:
                cursor.execute('DELETE FROM Item WHERE itemId = ?',(deleteId,))
                c.commit()
                print '<p class=info>Deleted item</p>'
            except Exception,e:
                print '<p class=error>Sorry, something went wrong with the deletion</p>',e
        
    
######################
# Handle add
addManufacturer = None
addBrand = None
if form.has_key('add'):
    if form.has_key('brand'): addBrand = form['brand'].value
    else: addBrand = None
    
    if not form.has_key('manufacturer'):
        print "<p class=error>Oops - you must fill in the manufacturer</p>"
    elif not form.has_key('name'):
        print "<p class=error>Oops - you must fill in the name</p>"
    else:
        addManufacturer = form['manufacturer'].value
        try:
            if addBrand:
                details = (addManufacturer,addBrand,form['name'].value)
                sql = "INSERT INTO item (manufacturer,brand,name) VALUES (?,?,?)"
                cursor.execute(sql,details)
                c.commit()
            else:
                details = (addManufacturer,form['name'].value)
                sql = "INSERT INTO item (manufacturer,name) VALUES (?,?)"
                cursor.execute(sql,details)
                c.commit()
        except sqlite3.IntegrityError:
            print "<p class=error>Oops - item %s already exists!</p><br />"%form['name'].value

#######################3
# Handle edit
if form.has_key('edit'):
    try:
        manufacturer = form['manufacturer'].value
        if form.has_key('brand'): brand = form['brand'].value
        else: brand = None
        name = form['name'].value
        itemId = form['edit'].value
        if brand:
            cursor.execute("UPDATE item SET manufacturer = ?, brand = ?, name = ? WHERE itemId = ?",(manufacturer,brand,name,itemId))
        else:
            cursor.execute("UPDATE item SET manufacturer = ?, brand = NULL, name = ? WHERE itemId = ?",(manufacturer,name,itemId))
        c.commit()
        print "<p class=info>Item details updated</p>"
    except Exception,e:
        print "<p class=error>Sorry, something went wrong with the update.</p>",e

###################
# Display list
cursor.execute('''
SELECT itemId,manufacturer,brand,name,SUM(quantity) AS number
FROM
    item
    LEFT JOIN transItem USING (itemId)
GROUP BY itemId
ORDER BY manufacturer,brand,name
''')

print '''
<TABLE BORDER=1 class='listthings sortable'>
<TR>
<TH>Mfr</TH>
<TH>brand</TH>
<TH>name</TH>
<TH></TH>
</TR>
'''
for (itemId,manufacturer,brand,name,number) in cursor:
    if not brand: brand = '-'
    print '<TR>'
    print '<TD>%s</TD>'%manufacturer
    print '<TD>%s</TD>'%brand
    print '<TD>%s</TD>'%name
    print '<TD>'
    print gotoButton('Edit','editItem.py?itemId=%s'%itemId)
    if number:
        print gotoButton('Transactions','singleItem.py?itemId=%s'%itemId)
    else:
        print gotoButton('Delete','items.py?delete=%s'%itemId)
    print '</TD>'
    print '</TR>'
    
print '</TABLE>'


print "<SCRIPT LANGUAGE='javascript'>"
print "var manufacturer = '%s';"%(addManufacturer or '')
print "var brand = '%s';"%(addBrand or '')
print '''
mfgr = document.getElementById('addItemMfr');
if (manufacturer) {
    document.getElementById('addItemMfr').value = manufacturer;
    if (brand) {
        document.getElementById('brand').value = brand;
    }
    document.getElementById('name').focus();
} else {
    document.getElementById('addItemMfr').focus();
    }
</SCRIPT>
'''

printFooter()