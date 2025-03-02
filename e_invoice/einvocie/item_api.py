from base64 import b64encode
import frappe
import requests
import json
from frappe import _
from erpnext import  get_default_company
from datetime import datetime, tzinfo
import pytz
from http.client import HTTPSConnection
import ssl



# url : /api/method/e_invoice.einvocie.item_api.create_item
@frappe.whitelist()
def create_item(item_code,item_name,uom=None,uom_list=None , zero_tax = False):
    if not item_code:
        frappe.local.response['message'] = "Item Code Is required"
        frappe.local.response['http_status_code'] = 400 
        return
    
    if not item_name:
        frappe.local.response['message'] = "Item Name Is required"
        frappe.local.response['http_status_code'] = 400 
        return


    # get default company 
    company_name = get_default_company()
    company = frappe.get_doc("Company",company_name)
    item_egs_code = "EG-"+str(company.tax_id or "")+"-"+item_code
    if not frappe.db.exists("Item" ,{"item_code" : item_code }):
         # create item  
        item = frappe.new_doc("Item")
    if  frappe.db.exists("Item" ,{"item_code" : item_code }):
         # create item  
        item = frappe.get_doc("Item" , item_code)
    item.item_code = item_code
    item.item_name = item_name
    item.item_group = "All Item Groups"
    item.item_type = "EGS"
    item.stock_uom = uom if uom !=None else "EA"
    item.itemcode = item_egs_code
    item.e_invoice_setting =[]
    item.item_zero_tax = zero_tax
    item.append("e_invoice_setting",{
        "company":company_name,
        "item_type":"EGS",
        "item_code":item_egs_code
    })
    if uom_list !=None:
        item.uoms =[]
        for uom in uom_list["data"]:
            if uom.get("uom") and uom.get("conversion_factor"):
                if frappe.db.exists("UOM",uom.get("uom")):
                    item.append("uoms",{
                        "uom":uom.get("uom"),
                        "conversion_factor":uom.get("conversion_factor")
                    })
    try:
        item.save()
        frappe.local.response['message'] = item.name
        frappe.local.response['http_status_code'] = 200 
        return
    except Exception as ex:
        frappe.local.response['message'] = str(ex)
        frappe.local.response['http_status_code'] = 400 
        return




# url : /api/method/e_invoice.einvocie.item_api.upadate_item
@frappe.whitelist()
def upadate_item(item_code,item_name,uom_list=None):
    if not item_code :
        frappe.local.response['message'] = "Item Code Is Required"
        frappe.local.response['http_status_code'] = 400 
        return
    
    if not frappe.db.exists("Item",item_code):
        frappe.local.response['message'] = "Item doests exist"
        frappe.local.response['http_status_code'] = 400 
        return
    # get item 
    item = frappe.get_doc("Item",item_code)
    item.item_group = "All Item Groups"
    item.item_type = "EGS"
    if item_name:
        item.item_name = item_name
    

    if uom_list != None:
        for uom in uom_list["data"]:
            exist = False
            for u in item.uoms:
                if u.get("uom") == uom.get("uom"):
                    u.conversion_factor = uom.get("conversion_factor")
                    exist = True
                    continue
            if exist == False :
                if frappe.db.exists("UOM",uom.get("uom")):
                    item.append("uoms",{
                        "uom"               : uom.get("uom"),
                        "conversion_factor" : uom.get("conversion_factor")
                    })

    try:
        item.save()
        frappe.local.response['message'] = item.name
        frappe.local.response['http_status_code'] = 200 
    except Exception as ex:
        frappe.local.response['message'] = str(ex)
        frappe.local.response['http_status_code'] = 400 










