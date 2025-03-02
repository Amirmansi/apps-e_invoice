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




# url : /api/method/e_invoice.einvocie.item_api.create_customer
@frappe.whitelist()
def create_customer(*args, **kwargs):
    data = json.loads(frappe.request.data)

    # validaion
    if not data.get("customer_name"):
        frappe.local.response['message'] = "Customer name required"
        frappe.local.response['http_status_code'] = 400 
        return
    if not data.get("remote_id"):
        frappe.local.response['message'] = "remote id required"
        frappe.local.response['http_status_code'] = 400 
        return
    if data.get("receiver_type") == "B" and not data.get("receiver_id"):
        frappe.local.response['message'] = "recive id is required in reciver type B"
        frappe.local.response['http_status_code'] = 400 
        return
    if data.get("country_code"):
        if not frappe.db.exists("Country Code",data.get("country_code")):
            frappe.local.response['message'] = "Country Code doesnt exist"
            frappe.local.response['http_status_code'] = 400 
            return


    # create customer Country Code
    if not frappe.db.exists("Customer",{"remote_id":data.get("remote_id")}):
        customer = frappe.new_doc("Customer")
    if  frappe.db.exists("Customer",{"remote_id":data.get("remote_id")}):    
        customer = frappe.get_doc("Customer",{"remote_id":data.get("remote_id")})
    customer.customer_name = data.get("customer_name")
    customer.customer_group = "All Customer Groups"
    customer.territory = "All Territories"
    customer.receiver_type = data.get("receiver_type") or ""
    customer.receiver_id = data.get("receiver_id") or ""
    customer.country_code = data.get("country_code") or ""
    customer.governate = data.get("governate") or ""
    customer.regioncity = data.get("regioncity") or ""
    customer.street = data.get("street") or ""
    customer.buildingnumber = data.get("buildingnumber") or ""
    customer.branchid = data.get("branchid") or ""
    customer.remote_id = data.get("remote_id")


    try:
        customer.save()
        frappe.local.response['message'] = customer.name
        frappe.local.response['http_status_code'] = 200 
        return
    except Exception as ex:
        frappe.local.response['message'] = str(ex)
        frappe.local.response['http_status_code'] = 400 
        return



# url : /api/method/e_invoice.einvocie.item_api.update_customer
@frappe.whitelist()
def update_customer(*args, **kwargs):
    data = json.loads(frappe.request.data)
    if not data.get("remote_id"):
        frappe.local.response['message'] = "name is required"
        frappe.local.response['http_status_code'] = 400 
        return
    if data.get("country_code"):
        if not frappe.db.exists("Country Code",data.get("country_code")):
            frappe.local.response['message'] = "Country Code doesnt exist"
            frappe.local.response['http_status_code'] = 400 
            return
    if not frappe.db.exists("Customer",{"remote_id":data.get("remote_id")}):
        frappe.local.response['message'] = "invalid remote id"
        frappe.local.response['http_status_code'] = 400 
        return
    customer = frappe.get_doc("Customer",{"remote_id":data.get("remote_id")})
    customer.customer_name = data.get("customer_name") or customer.customer_name
    customer.receiver_type = data.get("receiver_type") or customer.receiver_type
    customer.receiver_id = data.get("receiver_id") or customer.receiver_id
    customer.country_code = data.get("country_code") or customer.country_code
    customer.governate = data.get("governate") or customer.governate
    customer.regioncity = data.get("regioncity") or customer.regioncity
    customer.street = data.get("street") or customer.street
    customer.buildingnumber = data.get("buildingnumber") or customer.buildingnumber
    customer.branchid = data.get("branchid") or customer.branchid

    try:
        customer.save()
        frappe.local.response['message'] = customer.name
        frappe.local.response['http_status_code'] = 200 
        return
    except Exception as ex:
        frappe.local.response['message'] = str(ex)
        frappe.local.response['http_status_code'] = 400 
        return

