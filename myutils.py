#!/python26/python.exe

# enable debugging
import sqlite3

c = sqlite3.connect('/temp/example',isolation_level='EXCLUSIVE')
cursor = c.cursor()

def sql(c,sql):
    print '<pre>',sql,'</pre>'
    c.cursor().execute(sql)
    c.commit()

def printHeader(header):
    print "Content-Type: text/html;charset=utf-8"
    print
    print '''
<HTML>
<HEAD>
<TITLE>%s</TITLE>
<style type="text/css">
body  {
	text-align: center;
	min-width: 840px;
}

p.error {color:red;font-weight:bold}
p.info {font-weight:bold}
td.money {text-align:right}
input.money {text-align:right}
div.mainbody {
    border:5px solid darkblue;
    padding: 10px;
    width:820px;
    background-color:lightblue;
    margin:0 auto;
    width:600px;
    text-align: left;
}
div.navibar {text-align: left}
div.addthing {
    background-color:lightgreen;
    border: 2px groove darkgreen;
    margin: 2px;
}
table.listthings {
    background-color: orange;
    border: 2px groove darkorange;
    margin:20px;
}
</style>
<script language= "JavaScript">
<!--begin script
function moneyFormat(textObj) {
   var newValue = textObj.value;
   var decAmount = "";
   var dolAmount = "";
   var decFlag = false;
   var aChar = "";
   
   // ignore all but digits and decimal points.
   for(i=0; i < newValue.length; i++) {
      aChar = newValue.substring(i,i+1);
      if(aChar >= "0" && aChar <= "9") {
         if(decFlag) {
           decAmount = "" + decAmount + aChar;
         }
         else {
            dolAmount = "" + dolAmount + aChar;
         }
      }
      if(aChar == ".") {
         if(decFlag) {
            dolAmount = "";
            break;
         }
         decFlag=true;
      }
   }
   
   // Ensure that at least a zero appears for the dollar amount.

   if(dolAmount == "") {
      dolAmount = "0";
   }
   // Strip leading zeros.
   if(dolAmount.length > 1) {
      while(dolAmount.length > 1 && dolAmount.substring(0,1) == "0") {
         dolAmount = dolAmount.substring(1,dolAmount.length);
      }
   }
   
   // Round the decimal amount.
   if(decAmount.length > 2) {
      if(decAmount.substring(2,3) > "4") {
         decAmount = parseInt(decAmount.substring(0,2)) + 1;
         if(decAmount < 10) {
            decAmount = "0" + decAmount;
         }
         else {
            decAmount = "" + decAmount;
         }
      }
      else {
         decAmount = decAmount.substring(0,2);
      }
      if (decAmount == 100) {
         decAmount = "00";
         dolAmount = parseInt(dolAmount) + 1;
      }
   }
   
   // Pad right side of decAmount
   if(decAmount.length == 1) {
      decAmount = decAmount + "0";
   }
   if(decAmount.length == 0) {
      decAmount = decAmount + "00";
  }
   
   // Check for negative values and reset textObj
   if(newValue.substring(0,1) != '-' ||
         (dolAmount == "0" && decAmount == "00")) {
      textObj.value = dolAmount + "." + decAmount;

   }
   else{
      textObj.value = '-' + dolAmount + "." + decAmount;
   }
}

function incdec(inc,incMax,dec)
{
    incField = document.getElementById(inc);
    decField = document.getElementById(dec);
    incValue = incField.value;
    decValue = decField.value;
    incValue++;
    if (incMax != 0 && incValue > incMax) return;
    decValue--;
    if (decValue < 0) return;
    incField.value = incValue;
    decField.value = decValue;
}

function incincdec(inc1,incMax,inc2,dec)
{
    incField1 = document.getElementById(inc1);
    incField2 = document.getElementById(inc2);
    decField = document.getElementById(dec);
    incValue1 = incField1.value;
    incValue2 = incField2.value;
    decValue = decField.value;
    incValue1++;
    incValue2++;
    decValue--;
    if (incMax != 0 && incValue1 > incMax) return;
    if (decValue < 0) return;
    incField1.value = incValue1;
    incField2.value = incValue2;
    decField.value = decValue;
}

function decdecinc(dec1,dec2,inc)
{
    decField1 = document.getElementById(dec1);
    decField2 = document.getElementById(dec2);
    incField = document.getElementById(inc);
    decValue1 = decField1.value;
    decValue2 = decField2.value;
    incValue = incField.value;
    decValue1--;
    decValue2--;
    incValue++;
    if (decValue1 < 0 || decValue2 < 0) return;
    decField1.value = decValue1;
    decField2.value = decValue2;
    incField.value = incValue;
}

function incDecField(id,max,otherId)
{
    retval = "<INPUT TYPE=TEXT CLASS=number NAME="+id+" READONLY ID="+id+" VALUE=0 SIZE=2 />";
    retval = retval + "<INPUT TYPE=button onClick='incdec(\\\""+id+"\\\","+max+",\\\""+otherId+"\\\");' VALUE=+>";
    retval = retval + "<INPUT TYPE=button onClick='incdec(\\\""+otherId+"\\\",0,\\\""+id+"\\\");' VALUE=->";
    return retval;
}

function incIncDecField(id,max,inc2,dec)
{
    retval = "<INPUT TYPE=TEXT CLASS=number NAME="+id+" READONLY ID="+id+" VALUE=0 SIZE=2 />";
    retval = retval + "<INPUT TYPE=button onClick='incincdec(\\\""+id+"\\\","+max+",\\\""+inc2+"\\\",\\\""+dec+"\\\");' VALUE=+>";
    retval = retval + "<INPUT TYPE=button onClick='decdecinc(\\\""+id+"\\\",\\\""+inc2+"\\\",\\\""+dec+"\\\");' VALUE=->";
    return retval;
}

function checkField(fieldName,msg)
{
     field = document.getElementById(fieldName);
     if (field.value == "") {
         alert(msg);
         return false;
     }
     return true;
}

// end script-->
</script>
</HEAD>
<BODY>
<div class=mainbody>
'''%header
    printNavigation()
    print '<H1>%s</H1>'%header

def printFooter():
    printNavigation()
    print "</BODY>"
    print "</HTML>"

def gotoButton(name,url):
    return "<INPUT TYPE=button onClick='location.href=\"%s\"' VALUE='%s' />"%(url,name)

def printNavigation():
    print '<div class=navibar>'
    print gotoButton('top','index.py')
    print gotoButton('Purchases','purchases.py')
    print gotoButton('Sales','sales.py')
    print gotoButton('Stock list','stockList.py')
    print gotoButton('Bin list','binList.py')
    print '<br />'
    print gotoButton('Bin management','bins.py')
    print gotoButton('Item type management','items.py')
    print "</div>"

def printOptions(label,field,valueList):
    print '%s: <SELECT NAME=%s>'%(label,field)
    for (thisValue,display) in valueList:
        print '<OPTION VALUE=%s>%s</OPTION>'%(thisValue,display)
    print '</SELECT>'

def centsToDollarString(cents):
    dollars = cents // 100
    cents = cents % 100
    return "$%d.%02d"%(dollars,cents)

def dollarStringToCents(dollarString):
    (dollars,cents) = dollarString.split('.')
    return int(dollars)*100+int(cents)

def getTranType(type,direction):
    if type == 'REAL':
        if direction == 'ADD':
            typeDetail = 'Purchase'
        else:
            typeDetail = 'Sale'
    else:
        if direction == 'ADD':
            typeDetail = 'Reconcile add'
        else:
            typeDetail = 'Reconcile del'
    
    return typeDetail

def getItemName(manufacturer,brand,name):
    manufacturer = manufacturer.replace("'","\\'")
    if brand: brand = brand.replace("'","\\'")
    name = name.replace("'","\\'")
    if not brand: return '%s %s'%(manufacturer,name)
    else: return '%s %s %s'%(manufacturer,brand,name)
    
def cell(contents):
    return '<TD>%s</TD>'%contents

def moneyCell(value):
    return '<TD class=money>%s</TD>'%centsToDollarString(value)
                                                         