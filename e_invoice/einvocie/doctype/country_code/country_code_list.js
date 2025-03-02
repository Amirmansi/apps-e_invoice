frappe.listview_settings['Country Code'] = {
    onload: function(listview) {
        listview.page.add_menu_item(__("Update"), function() {
            frappe.call({
				method: "e_invoice.einvocie.mater_data_apis.get_update_country_code",
				freeze: true,
				callback: function (r) {
					cur_list.refresh()
				}
			});

		});

    }


}