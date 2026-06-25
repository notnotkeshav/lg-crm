frappe.ui.form.on("CRM Quotation", {
	refresh(frm) {


		// Add custom button only if document is submitted
		if (frm.doc.docstatus === 1) {
			frm.add_custom_button(__('Create Contract'), function () {
				frappe.model.open_mapped_doc({
					method: "crm.fcrm.doctype.crm_quotation.crm_quotation.make_crm_contract",
					frm: frm
				});
			});
		}
	},
});

