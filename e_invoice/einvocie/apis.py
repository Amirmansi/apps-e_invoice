from base64 import b64encode
import frappe
import requests
import json
from frappe import _
from erpnext import get_company_currency, get_default_company
from datetime import datetime, tzinfo ,date
import pytz
from http.client import HTTPSConnection
import ssl
from erpnext.controllers.accounts_controller import add_taxes_from_tax_template ,set_child_tax_template_and_map
from collections import Counter
from functools import reduce
from operator import add
DOMAINS = frappe.get_active_domains()



@frappe.whitelist()
def get_company_auth_token(clientID , clientSecret , base_url):
    # base_url = "https://id.preprod.eta.gov.eg"
    method = "/connect/token"
    str_byte = bytes(f"{clientID}:{clientSecret}", 'utf-8')
    auth = b64encode(str_byte).decode("ascii")
   
    headers = { 'Authorization' : f'Basic {auth}',
				 'Content-Type': 'application/x-www-form-urlencoded'}
    body = {"grant_type":"client_credentials"}
    response = requests.post(base_url+method,headers=headers,data=body)
    access_token = response.json().get('access_token')
    if not access_token :
        frappe.throw(_("Invalid Client Tax Auth"))
    return response.json().get('access_token')




@frappe.whitelist()
def submit_invoice_api(json_body,access_token,base_url):
   
    method = "/api/v1.0/documentsubmissions"
    headers = { 'Authorization' : f'Bearer {access_token}',
			 'Content-Type': 'application/json'}
    #body = json_body
    c = HTTPSConnection('api.preprod.invoicing.eta.gov.eg' ,context=ssl._create_unverified_context())
    c.request('POST', '/api/v1.0/documentsubmissions' ,headers=headers , body=json_body )
    res = c.getresponse()
    response = res.read().decode()
    print("Respons Type" , type(response))
    print("Respons ===" , json.loads(response))

    return json.loads(response)


@frappe.whitelist()
def document_invoice_api(uuid,access_token,base_url):
    method = f"/api/v1.0/documents/{uuid}/raw"
    headers = { 'Authorization' : f'Bearer {access_token}',
				 'Content-Type': 'application/json'}
    response = requests.get(base_url+method,headers=headers)
    return response.json()




@frappe.whitelist()
def get_current_environment():
    company     = get_default_company()
    setting_doc = frappe.get_doc('E Invoice Configuration', company)
    return setting_doc.invoice_document_version

@frappe.whitelist()
def get_invs_json(sinv_name):
    sinv_doc =  frappe.get_doc('Sales Invoice',sinv_name)
    obj = {}

    exchangeRate = frappe.db.get_value('Currency Exchange',{'from_currency':sinv_doc.currency,'to_currency':"EGP"},'exchange_rate') if sinv_doc.currency != "EGP" else 1
    obj['Header'] = {
        "receiptNumber":sinv_doc.name,
        "exchangeRate": exchangeRate,
        "currency": sinv_doc.currency
    }

    obj['DocumentType'] = {"receiptType" : "s","typeVersion" : "1.2"}

    customer_doc = frappe.get_doc("Customer",sinv_doc.customer) 
    buyer_name = customer_doc.get('customer_name') if customer_doc.get('customer_type')=='Company' else customer_doc.get('salutation') +' '+customer_doc.get('customer_name')

    obj['Buyer'] = {"type":customer_doc.get('receiver_type'),
    "id":customer_doc.get('receiver_id'),
    "name":buyer_name,"mobileNumber":customer_doc.get('mobile_no'),
    "paymentNumber":123
    }

    # obj['BranchAddress'] = {
    #     "country" : customer_doc.get('country_code'),
    #     "governate" : customer_doc.get('governate'),
    #     "regionCity" : customer_doc.get('regioncity'),
    #     "street" : customer_doc.get('street'),
    #     "buildingNumber" : customer_doc.get('buildingnumber'),
    #     "postalCode" : customer_doc.get('postalCode',''),
    #     "street" : customer_doc.get('street'),
    # }

    e_inv_conf = frappe.get_doc('E Invoice Configuration',sinv_doc.company)
    branch_code = frappe.get_doc('Branches',e_inv_conf.branches[0].get('branch',''))
    obj['Seller'] ={
        "rin":"",
        "companyTradeName":sinv_doc.company,
        "branchCode": branch_code.get('branch_code',''),
        "branchAddress":{
            "country":branch_code.get('country_code',''),
            "governate":branch_code.get('governate',''),
            "regionCity":branch_code.get('region_city',''),
            "street":branch_code.get('street',''),
            "buildingNumber":branch_code.get('building_number',''),
            "activityCode":branch_code.get('activity_code',''),
            "deviceSerialNumber":branch_code.get('deviceSerialNumber',''),
        }
    }

    obj['ItemData'] = []
    for row in sinv_doc.items:
        item_doc = frappe.get_doc('Item',row.item_code)
        row_dict = {
                    "internalCode":row.item_code,
                    "description":row.description,
                    "itemType":item_doc.item_type,
                    "itemCode":item_doc.itemcode,
                    "unitType":row.uom,
                    "quantity":row.qty,
                    "unitPrice":row.price_list_rate,
                    "netSale":(row.price_list_rate - row.discount_amount) * row.qty,
                    "totalSale":row.price_list_rate * row.qty,
                    "total":row.net_amount ,
                    "Discount":{
                        "amount":row.discount_amount,
                        "description":"discount amount"
                    },            
                    }
        obj['ItemData'].append(row_dict)

    obj['totalSales'] = sinv_doc.total

    obj['netAmount'] = sinv_doc.grand_total
    obj['totalAmount'] = sinv_doc.grand_total - sinv_doc.discount_amount
    # obj = json.dump(obj)
    return obj
      
#?check 
'''

totalAmount
paymentNumber,
rin,
deviceSerialNumber,
internalCode
'''



def add(a, b):
    "Same as a + b."
    print(f" ++++++++++++++++++++++++++values {a} , {b} +++++++++++++++++++++++")
    return a + b
def clean_list_sict(li) :
    new_li = []
    #
    for i in li :
             
            st =f"""{i["type"]}*{i["account_head"]}*{i["tax_type"]}*{i["tax_suptype"]}"""
            amount = i['tax_amount']
            new_li.append({st : amount})

    sum_dict = {}
    for d in  new_li :
        for key, value in d.items():
            sum_dict[key] = sum_dict.get(key, 0) + value
        
    data = list(sum_dict.items())
    
    list_response = []
    
    
    for i in data :
        key = i[0].split('*')
        ob = {"type": key[0] ,"account_head":key[1] , "tax_type":key[2] , "tax_suptype":key[3] , "tax_amount" :i[1] }
        list_response.append(ob)
    
    return list_response




def validate_purchase_taxes(doc,*args,**kwargs):
    tax_totals = 0
    taxes = []
    for item in doc.items :
        if item.item_tax_template :
            rate = 0
            amount = 0 
            template = frappe.get_doc("Item Tax Template" ,item.item_tax_template)
            for tax in template.taxes :
                if float(tax.tax_rate or 0) > 0 :
                    amount = float(item.base_amount)  * (float(tax.tax_rate) / 100 )
                  
                if float(tax.tax_rate or 0)< 0 :
                    amount = float(item.base_amount)  * (float(tax.tax_rate) / 100 )
                taxes.append({ "category":"Total" ,"type" : "Actual" , "account_head" : tax.tax_type , "tax_type" :tax.tax_type_invoice ,
                            "tax_suptype" :tax.tax_sub_type ,
                              "tax_amount": amount })

    if len(taxes) > 0 :
        clean_taxes = clean_list_sict(taxes)
        if len(clean_taxes ) > 0 :
            doc.taxes = []
            for t in clean_taxes  :
                raw = doc.append("taxes")
                raw.category = "Total"
                raw.add_deduct_tax = "Add"
                raw.charge_type = t.get('type')
                raw.description =  t.get("tax_type")
                raw.account_head = t.get("account_head")
                raw.tax_type = t.get("tax_type")
                raw.tax_subtype = t.get("tax_suptype")
                raw.tax_amount = float(t.get("tax_amount") or 1)
                raw.tax_amount_after_discount_amount = raw.tax_amount
                raw.total = doc.total + float(t.get("tax_amount") or 1)
                tax_totals = tax_totals + float(t.get("tax_amount") or 1)
            doc.total_taxes_and_charges = tax_totals
            doc.calculate_taxes_and_totals()
            
def validate_datetime_issue(doc,*args,**kwargs):
    if not doc.datetime_issued:
        format_data = "%y-%m-%d %H:%M:%S.%f"
        utc_now_dt = datetime.now(tz=pytz.UTC)
        doc.date_issued = utc_now_dt.strftime(format_data) 
    # Calculate Tax 
    tax_totals = 0
    taxes = []
    for item in doc.items :
        
        if  item.item_tax_template :
            rate = 0
            amount = 0 
            template = frappe.get_doc("Item Tax Template" ,item.item_tax_template)
            for tax in template.taxes :
                # if float(tax.tax_rate or 0) > 0 :
                amount = float(item.base_amount)  * (float(tax.tax_rate) / 100 )
                    # frappe.throw(str(amount))
                # if float(tax.tax_rate or 0)< 0 :
                #     amount = float(tax.amount)
                taxes.append({"type" : "Actual" , "account_head" : tax.tax_type , "tax_type" :tax.tax_type_invoice ,
                            "tax_suptype" :tax.tax_sub_type ,
                              "tax_amount": amount })
    
    if len(taxes) > 0 :
        clean_taxes =clean_list_sict(taxes)
        doc.taxes = []
        if len(clean_taxes ) > 0 :
            
            for t in clean_taxes  :
                raw = doc.append("taxes")
                raw.charge_type = t.get('type')
                raw.description =  t.get("tax_type")
                raw.account_head = t.get("account_head")
                raw.tax_type = t.get("tax_type")
                raw.tax_subtype = t.get("tax_suptype")
                raw.tax_amount = float(t.get("tax_amount"))
                raw.tax_amount_after_discount_amount = raw.tax_amount
                raw.total = doc.total + float(t.get("tax_amount") or 1)
                tax_totals = tax_totals + float(t.get("tax_amount") or 1)
                        #add taxe in sinv
           
            doc.total_taxes_and_charges = tax_totals
            doc.calculate_taxes_and_totals()
        #    set_child_tax_template_and_map()
        #    add_taxes_from_tax_template(item , doc)


# 1 - Item Create APi 
# item required tax table item 
def get_defalute_item_tax():
    #  defaulte
    taxes = frappe.db.sql(""" SELECT name FROM `tabItem Tax Template` WHERE defaulte =1""" ,as_dict =1)
    if taxes and len(taxes) > 0 :
        return taxes[0].get('name')
    return False
def get_defaulte_tax_account(company = False):
    if not company :
        company =frappe.defaults.get_user_default("Company")
    currenct_company = frappe.get_doc("Company" , company)
    tax_account = False
    try :
        tax_account =  currenct_company.tax_defaulte_account 
    except :
        pass
    if not tax_account : 
        print("no Tax Account")
    return tax_account
@frappe.whitelist()
def item_tax( *args , **kwargs) :
    # create item tax 
    # Fields = {
    #  "target" :[Create , Update , Delete] , Required 
    #  "title" : String , Required
    #   taxes :[
    #    {
    #  "tax_type" :"One of tax auth tax types " , 
    #  "tax_sub_type" : "One of Tax subtypes" ,
    #  "tax_rate" : float , 
    #  "amount" : float
    #     ]
    #    }
    # }
   
    method = kwargs.get("target")

    if not tax_tilte :
        frappe.local.response['message'] = "Please Set method to compelet " 
        frappe.local.response['http_status_code'] = 400 
        return 
    tax_tilte = kwargs.get("title")
    if not tax_tilte :
        frappe.local.response['message'] = "Please Set Title For Tax Template" 
        frappe.local.response['http_status_code'] = 400 
        return 
    #tax_type_invoice
    taxes = []
    taxes_request = kwargs.get('taxes')

    

    # set old item tax 
    old_item = False

    # check Exist Tax 
    
    old_tax = frappe.db.sql(f""" SELECT name FROM `tabItem Tax Template` WHERE title ='{tax_tilte}'""" ,as_dict = 1)

    if len(old_tax) > 0 and old_tax[0].get('name'):
        old_item = old_tax[0].get('name')

    if method == "Create" :
        try :
          taxes = json.loads(taxes_request)
        except Exception as E :
            frappe.local.response['message'] = f"Taxes Load Error {E}" 
            frappe.local.response['http_status_code'] = 400 
            return
        if old_item :
            frappe.local.response['message'] = f"Tax Template {old_item} already Exist  " 
            frappe.local.response['http_status_code'] = 400 
            return 
        new_template = frappe.db.new_doc("Item Tax Template")
        new_template.title = tax_tilte
        
        for tax in taxes :
            tax_rate                  = new_template.append("taxes")
            tax_rate.tax_type         = get_defaulte_tax_account()
            tax_rate.tax_type_invoice = tax.tax_type
            tax_rate.tax_sub_type     = tax.tax_sub_type 
            tax_rate.tax_rate         = tax.tax_rate
            tax_rate.amount           = tax.amount
        try :
            new_template.save()
            frappe.local.response['message'] = f"{new_template.name} " 
            frappe.local.response['http_status_code'] = 200 
            return 
        except Exception as E :
            frappe.local.response['message'] = f"{E} " 
            frappe.local.response['http_status_code'] = 400
            return 
        # tax_rate.
    if method in ["update"  , "delete"]:
        if not old_item :
            frappe.local.response['message'] = f"Tax Template {old_item} Not Found  " 
            frappe.local.response['http_status_code'] = 400 
            return 
        if method == "delete" :
            frappe.db.sql(f""" DELETE FROM tabItem Tax Template` WHERE name ='{old_item}' """)
            frappe.db.commit()
            frappe.local.response['message'] = f"Tax Template {tax_tilte} Succefully Deleted " 
            frappe.local.response['http_status_code'] = 200 
            return 
        if method == "update" :
            try :
                 taxes = json.loads(taxes_request)
            except Exception as E :
                frappe.local.response['message'] = f"Taxes Load Error {E}" 
                frappe.local.response['http_status_code'] = 400 
                return
            tax_template = frappe.get_doc("Item Tax Template" , old_item)
            #Clear Child table
            #update with new values
            tax_template.set('taxes', [])
            for tax in taxes :
                tax_rate                  = tax_template.append("taxes")
                tax_rate.tax_type         = get_defaulte_tax_account()
                tax_rate.tax_type_invoice = tax.tax_type
                tax_rate.tax_sub_type     = tax.tax_sub_type 
                tax_rate.tax_rate         = tax.tax_rate
                tax_rate.amount           = tax.amount
            try :
                tax_template.save()
                frappe.local.response['message'] = f"{tax_template.name}  Update Success !" 
                frappe.local.response['http_status_code'] = 200 
                return 
            except Exception as E :
                frappe.local.response['message'] = f"{E} " 
                frappe.local.response['http_status_code'] = 400
                return 
        
        # update sql 
        
@frappe.whitelist()
def create_item(*args , **kwargs) :
    pass



"""
Sales Invocie Refrence 
method = POST
END POINT  = e_invocie.einvocie.apis.sales_invoice
FIELDS :
    "target"  : ["Create" ,"Update" , "Delete"]
    "customer"  : "customer local id  or customer name "
    date_issued = date time iso format like 2021-12-28T10:11:32Z
    items = [
        {
            "item_code"        :  string  #required field item local id 
            "qty"              :  float   #required field 
            "rate"             :  float   #required field 
            "discount_amount"  :  float
            "discount_percent" :  float
            "uom:              :   string # on Of tax auth valid unit of masure   
            "item_tax"         :  string  # item tax template local  id or title
        }
    ]
__________________________________
SUCCESS REPONSE  =  {"status_code" :200 , "message" : invoice Erp name}
ERROR RESPONE = {"status_code" : 400 , "message" :  Error message from erp }
"""

 


# required functions 

# 1 -get Customer With name or Remote id 

def return_customer_obj(customer):
    customer_name = frappe.db.sql(f""" SELECT name From `tabCustomer` WHERE remote_id ='{customer}'""" ,as_dict =1 )
    if not customer_name or len(customer_name) == 0 :
        customer_name = frappe.db.sql(f""" SELECT name From `tabCustomer` WHERE customer_name='{customer}'""" ,as_dict =1 )
    if customer_name and len(customer_name) > 0 :
        return customer_name[0].get('name')
    else :
        return False
def validate_item(code): 
    item =frappe.db.sql(f""" SELECT name FROM `tabItem` WHERE item_code = '{code}' """)
    if item and len(item) > 0 :
        return True
    else :
        return False
@frappe.whitelist()
def sales_invoice( *args , **kwargs) :
    try :
         obj = json.loads(frappe.request.data)
    except Exception as e  :
         frappe.local.response['message'] = f" Error {E}"
         frappe.local.response['http_status_code'] = 400 
         return
    # Check Target
    target =obj.get("target")
    if not target :
         target = "Create"
    
   
    
 
    if not target  or target not in ["Create" ,"Update" , "Delete"] : 

        frappe.local.response['message'] = f"""Errro Accourd Coz You Should Set Target["Create" ,"Update" , "Delete"] """
        frappe.local.response['http_status_code'] = 400 
        return


    #customer shoud be synced 
    customer = obj.get("customer")
    if not customer :
        frappe.local.response['message'] = f"""Errro Accourd customer if required  """
        frappe.local.response['http_status_code'] = 400 
        return          


    #validate customer object 
    customer_obj = return_customer_obj(customer)
    if not customer_obj :
        frappe.local.response['message'] = f"""can not Find Customer {customer} """
        frappe.local.response['http_status_code'] = 400 
        return  


    
    date_issued = obj.get("date_issued")
    if not date_issued :
        frappe.local.response['message'] = f"""Errro Accourd date_issued  if required  """
        frappe.local.response['http_status_code'] = 400 
        return

    invoice = frappe.new_doc("Sales Invoice")
    invoice.customer = customer_obj
    # invoice.posting_date = frappe.utils.nowdate()
    invoice.tax_auth = 1
    invoice.update_stock =1
    date_on = date_issued.split("T")
    invoice.posting_date = date_on[0]
    invoice.due_date = frappe.utils.nowdate()
    #nvoice.date_issued = datetime.strptime(date_issued ,format_data)
    # invoice.branch= "0"
    invoice.datetime_issued =date_issued
    # item table 
    items = obj.get("items")
    invoice_items = []
    #validate item 
    try :
        invoice_items = items
    except Exception as E :
        frappe.local.response['message'] = f"{E}"
        frappe.local.response['http_status_code'] = 400 
        return 

    if len(invoice_items) == 0 :
        frappe.local.response['message'] = f"No Items Has Been found "
        frappe.local.response['http_status_code'] = 400 
        return 
    #validate ITEMS 

    for item in invoice_items :
        raw = invoice.append("items")
        if not frappe.db.exists("Item",item.get("item_code")):
            frappe.local.response['message'] = "Item '%s' doesnt exist"%item.get("item_code")
            frappe.local.response['http_status_code'] = 400
            return 
        item_obj = frappe.get_doc("Item" , item.get("item_code"))
       
        raw.item_code = item.get("item_code")
        raw.qty = item.get("qty")
        raw.price_list_rate = item.get("rate")
        raw.rate = item.get("rate")
        if not raw.item_code :
            frappe.local.response['message'] = f"Please Set Required Fields Item Code "
            frappe.local.response['http_status_code'] = 400 
            return 
        if not item.get("qty") :
            frappe.local.response['message'] = f"Please Set Required Fields Qty For item : {raw.item_code} "
            frappe.local.response['http_status_code'] = 400 
            return 
        if not item.get("rate") :
            frappe.local.response['message'] = f"Please Set Required Fields Rate For item : {raw.item_code} "
            frappe.local.response['http_status_code'] = 400 
            return 
        raw.item_type = "EGS" 
        raw.uom = item.get("uom")
        deiscount_amount  =float( item.get("discount_amount") or 0)
        deiscount_percent  =float( item.get("discount_percentt") or 0)
        if not item_obj.item_zero_tax : 
            raw.item_tax_template = item.get("item_tax") or get_defalute_item_tax()


    
    invoice.save()
    frappe.local.response['message'] = f"{invoice.name}"
    frappe.local.response['http_status_code'] = 200
    return 



def validate_customer_tex_id(doc , *args, **kwargs) :

        #if doc.receiver_type in ["P" , "B" ,"F"] :
        #validate Type type
		
        # if doc.receiver_type == "P" :
        #     if not doc.receiver_id  :
        #         frappe.throw(_("Pleaase Set user Nationsal ID 14 number "))
        #     if len(doc.receiver_id ) != 14 :
        #         frappe.throw(_("Pleaase Set user Nationsal ID 14 number "))
        if doc.receiver_type == "B" :
            if not doc.receiver_id :
                frappe.throw(_("Pleaase Set user Tax number 9 numbers "))
            if len(doc.receiver_id ) != 9 :
                frappe.throw(_("Pleaase Set user Tax number 9 numbers "))
 
