import frappe
from frappe import _


@frappe.whitelist()
def get_organization_data(name):
    if not frappe.has_permission("Organization", "read", name):
        frappe.throw(_("Not permitted"), frappe.PermissionError)
        
    organization = frappe.get_doc("Organization", name)
    organization = organization.as_dict()
    
    # Get linked warranties
    organization["warranties"] = frappe.get_all(
        "Warranty",
        filters={"organization": name},
        fields=[
            "name", "warranty_owner", "warranty_type", "created_by",
            "expiry_date", "customer_name", "modified"
        ],
        order_by="creation desc"
    )
    
    return organization
    