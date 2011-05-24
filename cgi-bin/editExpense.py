#!/python26/python.exe
# -*- coding: UTF-8 -*-

# enable debugging
import cgitb
import cgi
from myutils import c,cursor,sql, printHeader, printFooter, gotoButton,centsToString

cgitb.enable()

form = cgi.FieldStorage()

printHeader('Edit expense')

if not form.has_key('expenseId'):
    print '<p class=error>Sorry, page called with no expense to edit</p>'
else:
    expenseId = form['expenseId'].value

    cursor.execute('SELECT expDate,description,amount FROM expense WHERE expenseId = ?',(expenseId,))
    (expDate,description,amount) = cursor.fetchone()

    print '''
<div class=addthing>
<FORM ACTION=expenses.py>
<H2>Edit expense</H2>
<table>
<tr><td align=right>Date:</td><td><INPUT TYPE=TEXT NAME=date ID=date SIZE=20 VALUE="%s" /> Format: YYYY-MM-DD</td></tr>
<tr><td align=right>Description:</td><td><INPUT TYPE=TEXT NAME=description ID=description SIZE=70 VALUE="%s" /></td></tr>
<tr><td align=right>Amount:</td><td><INPUT TYPE=TEXT NAME=amount ID=amount VALUE="%s" SIZE=5 onBlur='moneyFormat(event.target)'/>Enter negative amount for a credit</td></tr>
<INPUT TYPE=hidden NAME=edit VALUE=%s />
</table>
<INPUT TYPE=SUBMIT VALUE='Submit changes' onClick='return validateForm();' />
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
'''%(expDate,description,centsToString(amount),expenseId)
