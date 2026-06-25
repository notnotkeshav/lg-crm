@frappe.whitelist()
def get_opportunity_funnel_data(date_range=None):
    """Get opportunity data for funnel chart based on stages"""
    filters = {}
    if date_range:
        date_filters = get_date_range_filter(date_range)
        if date_filters:
            filters.update(date_filters)

    # Get all deal statuses ordered by position
    statuses = frappe.get_all(
        "CRM Deal Status",
        fields=["name", "position"],
        order_by="position"
    )

    # Get count of opportunities in each status
    data = []
    for status in statuses:
        count = frappe.db.count(
            "Opportunity",
            filters={**filters, "status": status.name}
        )
        data.append({
            "name": status.name,
            "value": count
        })

    return data

def get_date_range_filter(date_range):
    """Get date filters based on selected range"""
    today = frappe.utils.today()
    if date_range == "Last Month":
        return {
            "creation": [">=", frappe.utils.add_months(today, -1)]
        }
    elif date_range == "Last Quarter":
        return {
            "creation": [">=", frappe.utils.add_months(today, -3)]
        }
    elif date_range == "Last 6 Months":
        return {
            "creation": [">=", frappe.utils.add_months(today, -6)]
        }
    elif date_range == "Last Year":
        return {
            "creation": [">=", frappe.utils.add_years(today, -1)]
        }
    return {} 