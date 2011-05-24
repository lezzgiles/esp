#!/python26/python.exe
# -*- coding: UTF-8 -*-

# enable debugging
import cgitb
import cgi
from myutils import c,cursor,sql, printRedirect, printHeader1,printHeader2, printFooter, gotoButton,centsToDollarString,dollarStringToCents
import sqlite3
import sys

cgitb.enable()

form = cgi.FieldStorage()

printHeader1('Expenses & Fees')

errorString = None

######################
# Handle delete
if form.has_key('deleteId'):
    try:
        deleteId = int(form['deleteId'].value)

        cursor.execute('BEGIN IMMEDIATE TRANSACTION')
        cursor.execute('DELETE FROM expense WHERE expenseId = ?',(deleteId,))
        c.commit()
        printRedirect('Deleted expense','expenses.py',0)
        sys.exit()

    except Exception,e:
        c.rollback()
        errorString = "<p class=error>Problem with database update:</p><pre>%s</pre>"%str(sys.exc_info())

######################
# Handle add
addManufacturer = None
addBrand = None
if form.has_key('add'):
    try:
        addDate = form['date'].value
        addDesc = form['description'].value
        addAmt  = form['amount'].value
        cursor.execute('BEGIN IMMEDIATE TRANSACTION')
        cursor.execute('INSERT INTO Expense (expDate,description,amount) VALUES (?,?,?)',(addDate,addDesc,dollarStringToCents(addAmt)))
        c.commit()
        printRedirect('Added expense','expenses.py',0)
        sys.exit()

    except Exception,e:
        c.rollback()
        errorString = "<p class=error>Problem with database update:</p><pre>%s</pre>"%str(sys.exc_info())

#######################3
# Handle edit
if form.has_key('edit'):
    try:
        editDate = form['date'].value
        editDesc = form['description'].value
        editAmt  = form['amount'].value
        expenseId = form['edit'].value
        cursor.execute('BEGIN IMMEDIATE TRANSACTION')
        cursor.execute('UPDATE Expense SET expDate = ?, description =?, amount = ? WHERE expenseId =?',
                       (editDate,editDesc,dollarStringToCents(editAmt),expenseId))
        c.commit()
        printRedirect('Modified expense','expenses.py',0)
        sys.exit()

    except Exception,e:
        c.rollback()
        errorString = "<p class=error>Problem with database update:</p><pre>%s</pre>"%str(sys.exc_info())

####################

printHeader2('Expenses & Fees',errorString)
    
####################
# Add form
print '''
<div class=addthing>
<FORM>
<H2>Add new fee or expense</H2>
<table>
<tr><td align=right>Date:</td><td><INPUT TYPE=TEXT NAME=date ID=date SIZE=20></INPUT> Format: YYYY-MM-DD</td></tr>
<tr><td align=right>Description:</td><td><INPUT TYPE=TEXT NAME=description ID=description SIZE=70></INPUT></td></tr>
<tr><td align=right>Amount:</td><td><INPUT TYPE=TEXT NAME=amount ID=amount VALUE=0.00 SIZE=5 onBlur='moneyFormat(event.target)'/>Enter negative amount for a credit</td></tr>
<INPUT TYPE=hidden NAME=add VALUE=1/>
</table>
<INPUT TYPE=SUBMIT VALUE='Add new expense or fee' onClick='return validateForm();' />
</FORM>
</div>

<script language=javascript>
function validateForm()
{
    return (
        checkField('date','Fill out the date')  &&
        checkField('description','Fill out the description')
        );
}
</script>
'''

###################
# Display list
cursor.execute('''
SELECT expenseId,expDate,description,amount
FROM
    expense
ORDER BY expDate
''')

print '''
<TABLE BORDER=1 class='listthings sortable'>
<TR>
<TH>Date</TH>
<TH>Description</TH>
<TH>Amount</TH>
<TH></TH>
</TR>
'''
for (expenseId,date,description,amount) in cursor:
    print '<TR>'
    print '<TD>%s</TD>'%date
    print '<TD>%s</TD>'%description
    print '<TD>%s</TD>'%centsToDollarString(amount)
    print '<TD>'
    print gotoButton('Edit','editExpense.py?expenseId=%s'%expenseId)
    print gotoButton('Delete','expenses.py?deleteId=%s'%expenseId)
    print '</TD>'
    print '</TR>'
    
print '</TABLE>'

printFooter()
