var message = "";

function socket(action) {
    var minus = 1,
      plus = 2,
     
      websocket = new WebSocket("ws://127.0.0.1:6789/");
    var run_1 = function (action) {
      try {
        websocket.onopen = function (evt) {
          try {
            websocket.send(action);
          } catch (err) {
            console.log("error");
          }
        };
      } catch (err) {
        frappe.show_alert("No Token", 5);
      }
    };
    function plus() {
      websocket.send(JSON.stringify({ action: "plus" }));
    }
  
    websocket.onmessage = function (event) {
      console.log("Event --- ", event)
      var mesage = event.data;
      var data = JSON.parse(mesage);
      console.log("data ======> Message ", data);
      if (data.status) {
        frappe.show_alert({ message: data.status, indicator: "blue" });
        message = data.status;
        cur_frm.events.add_post(cur_frm);
        console.log("Respond status", data.status)
      }
      if (data.Success) {
        console.log("Respond Success", data.Success)
        frappe.call({
          method:
            "e_invoice.einvocie.doctype.sales_invoice.sales_invoice_fun.update_invoice_submission_status",
          args: {
            submit_response: data.Success
          },
          callback: function (r) {
            // cur_frm.events.get_document_sinv(cur_frm);
            window.location.reload();
          },
        });
      }
  
      return message;
  
    };
    run_1(action);
}


frappe.ui.form.on("Sales Invoice", {
    save(frm) {
      frm.events.add_e_tax_btns(frm);
    },
    on_submit(frm) {
      frm.events.add_e_tax_btns(frm);
    },
    refresh(frm) {
      if(frm.doc.docstatus==0){
        // frm.add_custom_button(__("Json"),function(){
        //    frm.events.invs_json(frm)
        // }, __("View"));
      }
      frm.events.add_e_tax_btns(frm);
      if (frm.is_new()) {
        frm.doc.submission_id = "";
        frm.doc.uuid = "";
        frm.doc.long_id = "";
        frm.doc.error_code = "";
        frm.doc.error_details = "";
        frm.doc.invoice_status = "";
      }
  
      // your code here
  
      frm.events.setDateTimeIssued(frm);
      frm.set_query("branch", () => {
        return {
          filters: [["company", "=", frm.doc.company]],
        };
      });
      var data = { name: "ahmed" };
      socket(JSON.stringify(data));
  
    },
    invs_json(frm){
      console.log('------------')
      frappe.call({
        method:"e_invoice.einvocie.apis.get_invs_json",
        args:{
          sinv_name:frm.doc.name,
        },
        callback:function(r){
          console.log('r-->',r.message)
        }
      })
      

    },
    add_e_tax_btns(frm) {
      // if (frm.doc.docstatus == 1 && frm.doc.is_send == 0) {
      // if (frm.doc.docstatus == 1) {
      let version = ""
      frappe.call({
        "method": "e_invoice.einvocie.apis.get_current_environment",
        async: false,
        callback(r) {
          console.log("r.messager.message", r.message)
          if (r.message) {
            version = r.message
          }
        }
      })
      console.log("version ============> ", version)
      if (message == "Token connecting" || message == "success" || version == "0.9") {
        frm.events.add_post(frm);
      }
      if (frm.doc.docstatus ==1 ){frm.events.add_check_token(frm);}
      
  
      if (frm.doc.uuid) {
        frm.events.add_get_document(frm);
        frm.events.add_print_button(frm)
      }
    },
  
    add_check_token(frm) {
      frm.add_custom_button(
        __("Check Token"),
        function () {
          var data = { name: "ahmed" };
          socket(JSON.stringify(data));
          console.log("message", message)
          // check if v9
  
  
          if (message == "Token connecting" || message == "success") {
            frm.events.add_post(frm);
          } else {
            frappe.show_alert({ message: "no connection", indicator: "red" });
          }
        },
        __("E Tax")
      );
    },
    add_post(frm) {
      if ((["Invalid", ""].includes(frm.doc.invoice_status || "") || frm.doc.uuid == '') && frm.doc.docstatus == 1) {
        frm.add_custom_button(
          __("POST TO TAX"),
          function () {
            frappe.call({
              method:
                "e_invoice.einvocie.doctype.sales_invoice.sales_invoice_fun.post_sales_invoice",
              args: {
                invoice_name: frm.doc.name,
              },
              async: false,
              // freeze:true,
              // freeze_message: __('Sending Please Wait ....'),
              callback: function (r) {
                // console.log(r.message);
                var data = r.message;
                // frappe.dom.unfreeze();
                socket(JSON.stringify(data));
  
                frm.reload_doc();
              },
            });
          },
          "E Tax"
        );
      }
    },
    add_print_button(frm) {
      if (frm.doc.uuid.length > 0) {
        frm.add_custom_button(
          __("Print"),
          function () {
            if (frm.doc.document_version == "0.9") {
              window.open(`https://preprod.invoicing.eta.gov.eg/print/documents/${frm.doc.uuid}`)
            } else {
              window.open(`https://invoicing.eta.gov.eg/print/documents/${frm.doc.uuid}`)
            }
          },
          "E Tax"
        );
      }
    },
    add_get_document(frm) {
      frm.add_custom_button(
        __("Document Status"),
        function () {
          frm.events.get_document_sinv(frm);
        },
        "E Tax"
      );
    },
  
    get_document_sinv(frm) {
      frappe.call({
        method:
          "e_invoice.einvocie.doctype.sales_invoice.sales_invoice_fun.get_document_sales_invoice",
        args: {
          invoice_name: frm.doc.name,
        },
        callback: function (r) {
          window.location.reload();
        },
      });
    },
    // tax_auth(frm) {
    //   //   if (frm.doc.tax_auth) {
    //   let df = frappe.meta.get_docfield(
    //     "Sales Invoice",
    //     "date_issued",
    //     me.frm.doc.name
    //   );
    //   if (df) {
    //     df.reqd = frm.doc.tax_auth == 1;
    //     frm.refresh_field("date_issued");
    //   }
  
    //   //   }
    // },
    date_issued(frm) {
      frm.events.setDateTimeIssued(frm);
    },
    setDateTimeIssued(frm) {
      if (frm.doc.date_issued) {
        frm.doc.datetime_issued = toISOString(
          String(new Date(frm.doc.date_issued))
        );
        var tzoffset = new Date().getTimezoneOffset() * 60000;
        frm.refresh_field("datetime_issued");
      }
    },
    validate(frm) {
      frm.events.calculate_item_taxes(frm);
    },
    play(frm) {
      console.log("Called from Button")
    },
    calculate_item_taxes(frm) {
      if (frm.doc.items) {
        frm.doc.items.forEach((d) => {
          if (d.tax_amount) {
            d.tax_rate = (d.tax_amount / (d.amount || 1)) * 100;
          } else if (d.tax_rate) {
            d.tax_amount = (d.amount * d.tax_rate) / 100;
          } else {
            d.tax_amount = 0;
            d.tax_rate = 0;
          }
        });
      }
      frm.refresh_field("items");
    },
  });
  
  frappe.ui.form.on("Sales Invoice Item", {
    tax_rate(frm, cdt, cdn) {
      var d = locals[cdt][cdn];
      if (d.tax_rate && d.amount) {
        d.tax_amount = (d.amount * d.tax_rate) / 100;
      } else {
        d.tax_amount = 0;
        d.tax_rate = 0;
      }
      frm.refresh_field("items");
    },
    tax_amount(frm, cdt, cdn) {
      var d = locals[cdt][cdn];
      if (d.tax_amount && d.amount) {
        d.tax_rate = (d.tax_amount / (d.amount || 1)) * 100;
      } else {
        d.tax_amount = 0;
        d.tax_rate = 0;
      }
      frm.refresh_field("items");
    },
    rate(frm, cdt, cdn) {
      frm.events.calculate_item_taxes(frm);
    },
    amount(frm, cdt, cdn) {
      frm.events.calculate_item_taxes(frm);
    },
    qty(frm, cdt, cdn) {
      frm.events.calculate_item_taxes(frm);
    },
    item_code(frm, cdt, cdn) {
      frm.events.calculate_item_taxes(frm);
    },
    // item_type(frm, cdt, cdn) {
    //   //   if (frm.doc.tax_auth) {
    //   var d = locals[cdt][cdn];
    //   if (d.item_type == "EGS") {
    //     frappe.call({
    //       method: "frappe.client.get",
    //       args: {
    //         doctype: "Company",
    //         name: frappe.defaults.get_default("company"),
    //       },
    //       callback: function (r) {
    //         if (r.message) {
    //           d.itemcode = `EGS-${r.message.tax_id || ""}-${d.item_code || ""}`;
    //         }
    //         frm.refresh_field("items");
    //       },
    //     });
    //   }
    //   frm.refresh_field("items");
  
    //   //   }
    // },
  });
  
  var toISOString = function (s) {
    let months = {
      jan: "01",
      feb: "02",
      mar: "03",
      apr: "04",
      may: "05",
      jun: "06",
      jul: "07",
      aug: "08",
      sep: "09",
      oct: "10",
      nov: "11",
      dec: "12",
    };
    let b = s.split(" ");
    // alert(b)
    return (
      b[3] +
      "-" +
      months[b[1].toLowerCase()] +
      "-" +
      ("0" + b[2]).slice(-2) +
      "T" +
      b[4] +
      "Z"
    );
  };
  