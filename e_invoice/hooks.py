from . import __version__ as app_version

app_name = "e_invoice"
app_title = "EINVOCIE"
app_publisher = "Beshoy Atef"
app_description = "Electronic Invocie For Tax Auth"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "beshoyatef31@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------
doctype_js = {  "Customer": "einvocie/doctype/customer/customer.js",
				"Sales Invoice": "einvocie/doctype/sales_invoice/slaes_update.js",
				"Item": "einvocie/doctype/item/item.js",
				"Item Tax Template":"einvocie//doctype/item_tax_template/item_tax_template.js"
			 }


doc_events = {
	"Sales Invoice":{
 			#"autoname": "e_invoice.einvocie.doctype.sales_invoice.sales_invoice.autoname",
			"on_cancel": "e_invoice.einvocie.doctype.sales_invoice.sales_invoice_fun.cancel_document",
			# "before_submit": "e_invoice.einvocie.doctype.sales_invoice.sales_invoice.validate_item_stock",
			 "validate":"e_invoice.einvocie.apis.validate_datetime_issue"
             
  }  ,
  "Item" : {
	"validate": "e_invoice.einvocie.doctype.item.item.validate_item_defaults"
  } ,
  "Purchase Invoice" : {
	"validate" :"e_invoice.einvocie.apis.validate_purchase_taxes"
	
  } ,
  "Customer" :{
      "validate" :"e_invoice.einvocie.apis.validate_customer_tex_id"
  }

}
domains = {
	"Tax Portal" : "e_invoice.domains.e_invoice"
}

doctype_list_js = {
	"Sales Invoice" : "einvocie/doctype/sales_invoice/sales_invoice_list.js",
	"UOM" : "public/js/uom_list.js"
	}


scheduler_events = {
	"cron": {
		"0/30 * * * *": [
			"e_invoice.einvocie.doctype.sales_invoice.sales_invoice_fun.get_invoice_status",
		],
	},

}



# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "{doctype_1}",
		"filter_by": "{filter_by}",
		"redact_fields": ["{field_1}", "{field_2}"],
		"partial": 1,
	},
	{
		"doctype": "{doctype_2}",
		"filter_by": "{filter_by}",
		"partial": 1,
	},
	{
		"doctype": "{doctype_3}",
		"strict": False,
	},
	{
		"doctype": "{doctype_4}"
	}
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"e_invoice.auth.validate"
# ]

# Translation
# --------------------------------

# Make link fields search translated document names for these DocTypes
# Recommended only for DocTypes which have limited documents with untranslated names
# For example: Role, Gender, etc.
# translated_search_doctypes = []
