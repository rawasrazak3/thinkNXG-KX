// // Copyright (c) 2025, Kreatao - thinkNXG and contributors
// // For license information, please see license.txt

// frappe.ui.form.on("Karexpert Table", {
// 	execute: function(frm, cdt, cdn) {
//         console.log("button clicked");
//         let row = locals[cdt][cdn];
//         if (row.billing_type == "Op billing"){
//             console.log("condition okay");
//             frappe.call({
//                 method: "thinknxg_kx.thinknxg_kx.custom_script.create_sales_invoice.main",
//                 callback: function(r) {
//                     frappe.msgprint('OP Sales Invoice Created ');
//                 }
//             });

//         }

            

//         else if (row.billing_type == "IPD billing")
//             frappe.call({
//                 method: "thinknxg_kx.thinknxg_kx.custom_script.create_si_ip.main",
//                 callback: function(r) {
//                     frappe.msgprint('IP Sales Invoice Created ');
//                 }
//             });

//         else if (row.billing_type == "Advance Deposit")
//             frappe.call({
//                 method: "thinknxg_kx.thinknxg_kx.custom_script.advance_deposit.main",
//                 callback: function(r) {
//                     frappe.msgprint('Advance Deposit Created');
//                 }
//             });

//         else if (row.billing_type == "IP billing")
//             frappe.call({
//                 method: "thinknxg_kx.thinknxg_kx.custom_script.create_si_ip.main",
//                 callback: function(r) {
//                     frappe.msgprint('IP Sales Invoice Created ');
//                 }
//             });
// 	},
// });

frappe.ui.form.on("Karexpert Table", {
	execute: function(frm, cdt, cdn) {
		console.log("Button clicked");
		let row = locals[cdt][cdn];

		let method_map = {
			"OP BILLING": {
				method: "thinknxg_kx.thinknxg_kx.custom_script.create_sales_invoice.main",
				message: "OP Sales Invoice Created"
			},
			"IPD BILLING": {
				method: "thinknxg_kx.thinknxg_kx.custom_script.create_si_ip.main",
				message: "IP Sales Invoice Created"
			},
			"DUE SETTLEMENT": {
				method:"thinknxg_kx.thinknxg_kx.custom_script.due_settlement.main",
				message: "Due settlement Created"
			},
			"ADVANCE DEPOSIT": {
				method: "thinknxg_kx.thinknxg_kx.custom_script.advance_deposit.main",
				message: "Advance Deposit Created"
			},
			"GRN CREATION DETAILS": {
				method: "thinknxg_kx.thinknxg_kx.custom_script.create_purchase_invoice.main",
				message: "Purchase Invoice Created"
			}
		};

		let billing_info = method_map[row.billing_type];

		if (billing_info) {
			frappe.call({
				method: billing_info.method,
				args: { row_data: row },  // Optional: send row data if needed
				callback: function(r) {
					if (!r.exc) {
						frappe.msgprint(billing_info.message);
					} else {
						frappe.msgprint("An error occurred while creating the document.");
					}
				}
			});
		} else {
			frappe.msgprint("Unsupported billing type selected.");
		}
	}
});
