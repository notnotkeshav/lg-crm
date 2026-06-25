import frappe

# @frappe.whitelist()
# def get_dashboard_scope():
#     current_user = frappe.session.user

#     branch = frappe.get_all(
#         "Region Branches",
#         filters={"branch_head": current_user},
#         fields=["name"],
#         limit=1
#     )
#     if branch:
#         return {
#             "type": "branch",
#             "value": branch[0].name
#         }

#     region = frappe.get_all(
#         "Region Master",
#         filters={"region_head": current_user},
#         fields=["region_name"],
#         limit=1
#     )
#     if region:
#         return {
#             "type": "region",
#             "value": region[0].region_name
#         }

#     # Ensure a dict is always returned
#     return {
#         "type": None,
#         "value": None
#     }

@frappe.whitelist()
def get_dashboard_scope():
    current_user = frappe.session.user
    userDetail = frappe.get_doc("User", current_user)
    isAdmin = userDetail.get("module_profile", "User") == "Admin"
    # Branch scope
    if isAdmin:
        branch = frappe.get_all(
            "Region Branches",
            filters={"branch_head": current_user},
            fields=["name"]
        )
    else:
        branch = frappe.get_all(
            "Region Branches",
            filters={"branch_head": current_user},
            fields=["name"]
        )
    if branch:
        return {
            "type": "branch",
            "value": [b.name for b in branch]
        }

    # Region scope
    if isAdmin:
        region = frappe.get_all(
            "Region Master",
            fields=["region_name"]
        )
    else:
        region = frappe.get_all(
            "Region Master",
            filters={"region_head": current_user},
            fields=["region_name"]
        )
    if region:
        return {
            "type": "region",
            "value": [r.region_name for r in region]   # <---- now returns both
        }

    # No scope
    return {
        "type": None,
        "value": None
    }

# @frappe.whitelist()
# def get_all_branches(region):
#     branch = frappe.get_all(
#             "Region Branches",
#             filters={"region": region},
#             fields=["name"]
#         )

@frappe.whitelist()
def get_all_branches():
    branch = frappe.get_all(
            "Region Branches",
            fields=["name"]
        )
    return branch

# @frappe.whitelist()
# def get_branches_by_region(region_name):
#     current_user = frappe.session.user
#     userDetail = frappe.get_doc("User", current_user)
#     isAdmin = userDetail.get("module_profile", "User") == "Admin"
#     # Ensure the user is either a region head or has some appropriate role to view this data
#     if isAdmin:
#         region = frappe.get_all(
#             "Region Master",
#             filters={"region_name": region_name},
#             fields=["region_name"],
#             limit=1
#         )
#     else:
#         region = frappe.get_all(
#             "Region Master",
#             filters={"region_head": current_user, "region_name": region_name},
#             fields=["region_name"],
#             limit=1
#         )
#     print("region",region)
#     if not region:
#         return {"error": "User not authorized to view this region"}

#     # Fetch branch IDs only if the user is authorized
#     child_rows = frappe.get_all(
#         "Branch",
#         filters={"parent": region_name, "parenttype": "Region Master", "parentfield": "branches"},
#         fields=["branch_id"]
#     )

#     print("child row",child_rows)

#     return [row.branch_id for row in child_rows if row.branch_id]
@frappe.whitelist()
def get_branches_by_region(region_name):
    current_user = frappe.session.user
    userDetail = frappe.get_doc("User", current_user)
    isAdmin = userDetail.get("module_profile", "User") == "Admin"

    # Check if user is allowed to see the region
    filters = {"region_name": region_name}
    if not isAdmin:
        filters["region_head"] = current_user

    region = frappe.get_all(
        "Region Master",
        filters=filters,
        fields=["region_name"],
        limit=1
    )

    if not region:
        # Always return a list, even if user is not authorized
        return []

    # Get child branches
    child_rows = frappe.get_all(
        "Branch",
        filters={
            "parent": region_name,
            "parenttype": "Region Master",
            "parentfield": "branches"
        },
        fields=["branch_id"]
    )

    return [row["branch_id"] for row in child_rows if row.get("branch_id")]
