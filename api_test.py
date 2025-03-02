import requests 
import json
app_secret = "dfe44da42b9032a"
app_key ="d24f54377f0af1b"
headers  =  {
                            'Authorization': "Token dfe44da42b9032a:d24f54377f0af1b"

                 }
end_point = "http://178.18.250.45:2222/api/method/e_invoice.einvocie.apis.sales_invoice"

data = {"customer" :"1210001370", "date_issued" : "2022-03-08T11:11:32Z" ,
       "items" :[ { "item_code" : "21010201" , "qty" : 2 ,"rate":100 ,"uom":"EA"}
       
       ,{ "item_code" : "22010101" , "qty" : 2 ,"rate":100 ,"uom":"CT"}]}


r = requests.post(end_point , headers=headers , data = json.dumps(data))


print (r.text)
