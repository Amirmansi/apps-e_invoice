from __future__ import unicode_literals
import frappe
from frappe.model.naming import make_autoname
from .sales_invoice_fun import post_sales_invoice
import json


def autoname(self,fun=''):
    try :
         naming = frappe.db.get_single_value('EInvoice Setting', 'naming')
    except :
        naming = False
    if naming :
        series = f"{naming}-.######." if getattr(self,'tax_auth' , 0) else self.naming_series
        self.name = make_autoname(series, doctype="Sales Invoice")
    if not naming :
        series = "Inv-DD-.######." if getattr(self,'tax_auth' , 0) else self.naming_series
        self.name = make_autoname(series, doctype="Sales Invoice")
    # frappe.msgprint(self.name)

@frappe.whitelist()
def clear_stock_item(doc):
    invoice = frappe.get_doc("Sales Invoice" , doc)
    for item in invoice.items:
        if float(item.stock_qty)  > float(item.actual_qty) :
            if float((item.actual_qty) or 0 ) ==  0 :
                 invoice.items.remove(item)  
            if float((item.actual_qty) or 0 ) >  0 :
                item.qty = float(item.actual_qty) / float(item.conversion_factor)
                item.stock_qty = float(item.actual_qty)
            # if invoice.items    
            invoice.save()
    return invoice.name
    
@frappe.whitelist()
def validate_item_stock(doc ,*args ,**kwargs):
    invoice = frappe.get_doc("Sales Invoice" , doc)
    un_stock_item = []
    for item in invoice.items :
        if float(item.stock_qty)  > float(item.actual_qty) :
            un_stock_item .append(
                   {"item_code"    : item.item_code ,
                    "required_qty" : item.stock_qty , 
                    "item_stock"   :str( item.actual_qty or "0")
                    }) 

    if len(un_stock_item) > 0 :
        
        return un_stock_item

@frappe.whitelist()
def send_pulk_selected(names, status ):
    names = json.loads(names)
    for name in names :    
        invocie = post_sales_invoice(str(name))
        frappe.msgprint(str(invocie))
        return invocie


@frappe.whitelist()
def make_purchase_invoice(doc ,supplier) :
    invoice = frappe.get_doc("Sales Invoice" , doc)
    new_doc = frappe.new_doc("Purchase Invoice") 
    new_doc.company = invoice.company
    new_doc.posting_date = invoice.posting_date 
    new_doc.supplier = supplier 
    new_doc.update_stock =1
    new_doc.set_warehouse = invoice.set_warehouse
    for item in invoice.items :
        if item.stock_qty >  item.actual_qty :
            new_doc.append("items" , {
                "item_code" : item.item_code , 
                "stock_qty":   item.stock_qty - item.actual_qty  ,
                "qty" : (item.stock_qty - item.actual_qty) /item.conversion_factor,
                "uom":item.uom
            })

    new_doc.save()
    return new_doc.name





