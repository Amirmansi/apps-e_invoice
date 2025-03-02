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

# url : /api/method/e_invoice.einvocie.purchase_api.create_item
@frappe.whitelist()
def create_supplier(remote_id=None,supplier_name=None,tax_id=None):
    if not supplier_name:
        frappe.local.response['message'] = "Supplier name is Required"
        frappe.local.response['http_status_code'] = 400
        return 
    

    if not remote_id:
        frappe.local.response['message'] = "remote id is Required"
        frappe.local.response['http_status_code'] = 400
        return 
    
    if not frappe.db.exists("Supplier",{"remote_id":remote_id}):
        supplier = frappe.new_doc("Supplier")
    if frappe.db.exists("Supplier",{"remote_id":remote_id}):
        supplier = frappe.get_doc("Supplier",{"remote_id":remote_id})
    supplier.supplier_name = supplier_name
    supplier.supplier_group = "All Supplier Groups"
    supplier.tax_id  = tax_id or ""
    supplier.remote_id = remote_id or ""
    try:
        supplier.save()
        frappe.local.response['message'] = supplier.name
        frappe.local.response['http_status_code'] = 200
        return
    except Exception as ex:
        frappe.local.response['message'] = str(ex)
        frappe.local.response['http_status_code'] = 400
        return



@frappe.whitelist()
def update_supplier(remote_id=None,supplier_name=None,tax_id=None):
    if not remote_id:
        frappe.local.response['message'] = "remote id is Required"
        frappe.local.response['http_status_code'] = 400
        return
    if not frappe.db.exists("Supplier",{"remote_id":remote_id}):
        frappe.local.response['message'] = "invalid remote id"
        frappe.local.response['http_status_code'] = 400
        return

    doc = frappe.get_doc("Supplier",{"remote_id":remote_id})
    doc.supplier_name = supplier_name or doc.supplier_name
    doc.tax_id  = tax_id or doc.tax_id

    try:
        doc.save()
        frappe.local.response['message'] = doc.name
        frappe.local.response['http_status_code'] = 200
        return 
    except Exception as ex:
        frappe.local.response['message'] = doc.name
        frappe.local.response['http_status_code'] = 400
        return




"""
required fields
supplier 
"""
def get_defalute_item_tax():
    #  defaulte
    taxes = frappe.db.sql(""" SELECT name FROM `tabItem Tax Template` WHERE defaulte =1""" ,as_dict =1)
    if taxes and len(taxes) > 0 :
        return taxes[0].get('name')
    return False
@frappe.whitelist()
def create_purchase_invoice(*args, **kwargs):
    data = json.loads(frappe.request.data)
    if not data.get("supplier"):
        frappe.local.response['message'] = "supplier is required"
        frappe.local.response['http_status_code'] = 400
        return

    if not frappe.db.exists("Supplier",{"remote_id":data.get("supplier")}):
        frappe.local.response['message'] = "Invalid Supplier id"
        frappe.local.response['http_status_code'] = 400
        return

    if not data.get("items"):
        frappe.local.response['message'] = "Invoice items is required"
        frappe.local.response['http_status_code'] = 400
        return 

    supplier = frappe.get_doc("Supplier",{"remote_id":data.get("supplier")})

    # create purchase invoice
    doc = frappe.new_doc("Purchase Invoice")
    doc.supplier = supplier.name
    doc.remote_id = data.get("remote_id") or ""
    doc.update_stock =1
    doc.due_date = frappe.utils.nowdate()
    invoice_lines = data.get("items")
    for line in invoice_lines:
        if not frappe.db.exists("Item",line.get("item_code")):
            frappe.local.response['message'] = "Item '%s' doesnt exist"%line.get("item_code")
            frappe.local.response['http_status_code'] = 400
            return 
        if not frappe.db.exists("UOM",line.get("uom")):
            frappe.local.response['message'] = "Uom '%s' doesnt exist"%line.get("uom")
            frappe.local.response['http_status_code'] = 400
            return 
        item = frappe.get_doc("Item" , line.get("item_code"))
        # set item tax 
        item_has_tax = True
        if item.item_zero_tax == 1 : 
            doc.append("items",{
                "item_code":line.get("item_code"),
                "qty":line.get("qty"),
                "uom":line.get("uom"),
                "rate":line.get("rate") , 
                # "item_tax_template" :None if   item.item_zero_tax ==True  else  get_defalute_item_tax()
            })
        if item.item_zero_tax ==0  : 
            doc.append("items",{
                "item_code":line.get("item_code"),
                "qty":line.get("qty"),
                "uom":line.get("uom"),
                "rate":line.get("rate") , 
                "item_tax_template" : get_defalute_item_tax()
            })
    if float(data.get("has_hold_tax") or 0) == 1 :
        tax_Account = get_defaulte_tax_account()
        if not tax_Account :
            frappe.local.response['message'] = "No Tax Account Found !"
            frappe.local.response['http_status_code'] = 400
            return 
        doc.append("taxes" , {
            "charge_type" : "On Net Total" ,
            "account_head" : tax_Account  ,
            "rate" : -1 , 
            "description" : "With holding tax"
        })
        
    try:
        doc.save()
        frappe.local.response['message'] = doc.name
        frappe.local.response['http_status_code'] = 200
        return 
    except Exception as ex:
        frappe.local.response['message'] = str(ex)
        frappe.local.response['http_status_code'] = 400
        return 