import frappe
from frappe.utils import getdate

def execute(filters=None):
    filters = filters or {}
    user = frappe.session.user # Current logged-in user

    conditions = []
    values = {}
    # Admin/Super user check (Khushi Rai sees everything)
    if user not in ["khushi.rai@lgepartner.com","Administrator"]:
        conditions.append("vis.owner = %(user)s")
        values["user"] = user

    # Customer filter (CRM Organization)
    if filters.get("customer"):
        conditions.append("org.name = %(customer)s")
        values["customer"] = filters.get("customer")


    # Visit Date Range filter
    if filters.get("from_date") and filters.get("to_date"):
        conditions.append("vis.customer_visit_date BETWEEN %(from_date)s AND %(to_date)s")
        values["from_date"] = getdate(filters.get("from_date"))
        values["to_date"] = getdate(filters.get("to_date"))

    elif filters.get("from_date"):
        conditions.append("vis.customer_visit_date >= %(from_date)s")
        values["from_date"] = getdate(filters.get("from_date"))

    elif filters.get("to_date"):
        conditions.append("vis.customer_visit_date <= %(to_date)s")
        values["to_date"] = getdate(filters.get("to_date"))
        
    condition_sql = ""
    if conditions:
        condition_sql = "WHERE " + " AND ".join(conditions)

    data = frappe.db.sql(f"""
        SELECT
            org.organization_name AS customer_name,
            org.branch AS branch,
            org.branch_head AS asm,
            vis.customer_visit_date,
            vis.description,
			vis.visited_by,
            vis.purpose_of_visit,
            vis.accompanied_by
        FROM `tabCustomer Visit Form` vis
        INNER JOIN `tabCRM Organization` org
            ON org.name = vis.parent
        {condition_sql}
        ORDER BY vis.customer_visit_date DESC
    """, values, as_dict=True)

    columns = [
        {"label": "Customer Name", "fieldname": "customer_name", "fieldtype": "Data", "width": 220},
        {"label": "Branch", "fieldname": "branch", "fieldtype": "Data", "width": 120},
        {"label": "ASM", "fieldname": "asm", "fieldtype": "Data", "width": 200},
        {"label": "Visit Date", "fieldname": "customer_visit_date", "fieldtype": "Date", "width": 120},
        {"label": "Remarks", "fieldname": "description", "fieldtype": "Data", "width": 250},
		{"label": "Visited By", "fieldname": "visited_by", "fieldtype": "Data", "width": 250},
        {"label": "Purpose Of Visit", "fieldname": "purpose_of_visit", "fieldtype": "Data", "width": 250},
        {"label": "Accompained By", "fieldname": "accompanied_by", "fieldtype": "Link","options":"User", "width": 250},

    ]

    return columns, data


