import frappe

@frappe.whitelist()
def get_dashboard_scope():
    current_user = frappe.session.user
    user = frappe.get_doc("User", current_user)

    is_admin = user.get("module_profile") == "Admin"

    # Admin: global scope
    if is_admin:
        return {"type": None, "value": None}

    # Branch Head scope (derive from Branch child table)
    branch_rows = frappe.get_all(
        "Branch",
        filters={"branch_head": current_user},
        fields=["branch_id"]
    )

    if branch_rows:
        return {
            "type": "branch",
            "value": list({b.branch_id for b in branch_rows if b.branch_id})
        }

    # Region Head scope
    regions = frappe.get_all(
        "Region Master",
        filters={"region_head": current_user},
        fields=["name"]
    )

    if regions:
        return {
            "type": "region",
            "value": [r.name for r in regions]
        }

    return {"type": None, "value": None}

@frappe.whitelist()
def get_all_branches():
    branches = frappe.get_all(
        "Branch",
        fields=["branch_id"]
    )

    return [
        {"name": b.branch_id}
        for b in branches
        if b.branch_id
    ]



@frappe.whitelist()
def get_branches_by_region(region_name):
    if not region_name:
        return []

    # Validate region exists
    if not frappe.db.exists("Region Master", region_name):
        return []

    child_rows = frappe.get_all(
        "Branch",
        filters={
            "parent": region_name,
            "parenttype": "Region Master",
            "parentfield": "branches"
        },
        fields=["branch_id"]
    )

    return [
        row.branch_id
        for row in child_rows
        if row.branch_id
    ]
