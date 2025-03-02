import requests
import urllib, json
import frappe


@frappe.whitelist()
def get_update_country_code():
    url = "https://sdk.invoicing.eta.gov.eg/files/CountryCodes.json"
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())
    for d in data:
        if frappe.db.exists("Country Code",d.get("code")):
            doc = frappe.get_doc("Country Code",d.get("code"))
            doc.english_description = d.get("Desc_en")
            doc.arabic_description = d.get("Desc_ar")
            doc.save()
        else:
            doc = frappe.new_doc("Country Code")
            doc.code = d.get("code")
            doc.english_description = d.get("Desc_en")
            doc.arabic_description = d.get("Desc_ar")
            doc.save()



@frappe.whitelist()
def get_update_tax_types():

    # first get taxable taxes
    url = "https://sdk.invoicing.eta.gov.eg/files/TaxTypes.json"
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())
    for d in data:
        if frappe.db.exists("Tax Types",d.get("Code")):
            doc = frappe.get_doc("Tax Types",d.get("Code"))
            doc.desc_en = d.get("Desc_en")
            doc.desc_ar = d.get("Desc_ar")
            doc.taxable = True
            doc.save()
        else:
            doc = frappe.new_doc("Tax Types")
            doc.code = d.get("Code")
            doc.desc_en = d.get("Desc_en")
            doc.desc_ar = d.get("Desc_ar")
            doc.taxable = True
            doc.save()


    # second get nontaxable taxes
    url = "https://sdk.invoicing.eta.gov.eg/files/NonTaxableTaxTypes.json"
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())
    for d in data:
        if frappe.db.exists("Tax Types",d.get("Code")):
            doc = frappe.get_doc("Tax Types",d.get("Code"))
            #doc.taxtypereference = d.get("Code")
            doc.desc_en = d.get("Desc_en")
            doc.desc_ar = d.get("Desc_ar")
            doc.save()
        else:
            doc = frappe.new_doc("Tax Types")
            doc.code = d.get("Code")
            #doc.taxtypereference = d.get("Code")
            doc.desc_en = d.get("Desc_en")
            doc.desc_ar = d.get("Desc_ar")
            doc.taxable = False
            doc.save()
    
    # third get tax subtypes
    url = "https://sdk.invoicing.eta.gov.eg/files/TaxSubtypes.json"
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())
    for d in data:
        if frappe.db.exists("Tax Types",d.get("Code")):
            doc = frappe.get_doc("Tax Types",d.get("Code"))
            doc.taxtypereference = d.get("TaxtypeReference")
            doc.desc_en = d.get("Desc_en")
            doc.desc_ar = d.get("Desc_ar")
            doc.fixed_amount = "amount" in d.get("Desc_en")
            doc.save()
        else:
            doc = frappe.new_doc("Tax Types")
            doc.code = d.get("Code")
            doc.taxtypereference = d.get("TaxtypeReference")
            doc.desc_en = d.get("Desc_en")
            doc.desc_ar = d.get("Desc_ar")
            doc.fixed_amount = "amount" in d.get("Desc_en")
            doc.save()


@frappe.whitelist()
def get_update_uom():
    url = "https://sdk.invoicing.eta.gov.eg/files/UnitTypes.json"
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())
    for d in data:
        if frappe.db.exists("UOM",d.get("code")):
            doc = frappe.get_doc("UOM",d.get("code"))
            doc.english_description = d.get("desc_en")
            doc.arabic_description = d.get("desc_ar")
            doc.save()
        else:
            doc = frappe.new_doc("UOM")
            doc.uom_name = d.get("code")
            doc.english_description = d.get("desc_en")
            doc.arabic_description = d.get("desc_ar")
            doc.save()