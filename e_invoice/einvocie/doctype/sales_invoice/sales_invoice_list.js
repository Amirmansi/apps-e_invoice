

function socket(action) {
    // var action= { name: "ahmed" }
    console.log("Sockect ")
    var websocket = new WebSocket("ws://127.0.0.1:6789/");
    websocket.onopen = function (evt) {
      
        console.log("Sending")
        websocket.send(action);
      
    };

    
      websocket.onmessage = function (event) {
        message = event.data;
        var data = JSON.parse(message);
        console.log("data ===> ", data);
        if (data.status) {
          frappe.show_alert({ message: data.status, indicator: "blue" });
          message = data.status;
          cur_frm.events.add_post(cur_frm);
          if (data.response) {
            frappe.call({
              method:
                "e_invoice.einvocie.doctype.sales_invoice.sales_invoice_fun.update_invoice_submission_status",
              args: {
                submit_response: data.response,
              },
              callback: function (r) {
                window.location.reload();
              },
            });
          }
    
          return message;
        }
      };
  
 
}

frappe.listview_settings['Sales Invoice'] = {
    add_fields: ["invoice_status"] ,
    get_indicator: function (doc) {
          const status_colors = {
            "Valid": "green",
            "Invalid":"red"
          };
          if(["Valid","Invalid"].includes(doc.invoice_status)){
      return [__(doc.invoice_status), status_colors[doc.invoice_status], "status,=,"+doc.invoice_status];
          }
    } ,
    onload: function(listview) {
        

        var data = { "name": "ahmed" };
        socket(JSON.stringify(data)); 
        //console.log("waths0000000000000000000000")

        var method = "e_invoice.einvocie.doctype.sales_invoice.sales_invoice.send_pulk_selected"
        listview.page.add_menu_item(__("Post"), function() {
		var data = 	listview.get_checked_items()
           
                frappe.call({
                    method:
                      "e_invoice.einvocie.doctype.sales_invoice.sales_invoice_fun.post_sales_invoices",
                      async:false,
                      args: {
                      invoices: data,
                    },
                    callback: function (r) {
                      var data = r.message;
                    console.log(data)
                    socket(JSON.stringify(data));
                    },
                 





            });
		});

    }


}