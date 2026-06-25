frappe.query_reports["Customer Visit Deatails"] = {
    filters: [
        {
            fieldname: "customer",
            label: "Customer",
            fieldtype: "Link",
            options: "CRM Organization"
        },
        {
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date",
            default: frappe.datetime.get_today()
        },
		 {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date",
            default: frappe.datetime.get_today()
        }
    ]
};