import frappe

DOMAINS = frappe.get_active_domains()
def validate_item_defaults(self , *args ,**kwargs) :
    if "Tax Portal" in DOMAINS :
        if not self.stock_uom :
            self.stock_uom = "EA"
        company = frappe.defaults.get_user_default("Company")

        if self.item_type == "EGS" :
            tax_reg = frappe.get_doc("Company" ,company).tax_id

            #add code 
            auto_add = frappe.db.sql(f"""  SELECT auto_name_item from `tabE Invoice Configuration` where company='{company}' """ ,as_dict =1)
          
            if auto_add and len(auto_add) > 0 : 
                if auto_add[0].get("auto_name_item") ==1 :
                      self.itemcode = f"EG-{tax_reg}-{self.item_code}"
        if self.item_type and self.itemcode :
            if not self.e_invoice_setting or len(self.e_invoice_setting) == 0 :
                row = self.append("e_invoice_setting")
                row.company = company
                row.item_type = self.item_type
                row.item_code = self.itemcode