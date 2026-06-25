from frappe.model.mapper import get_mapped_doc
import frappe
from frappe import _
from datetime import datetime, timedelta
from crm.api.dashboard_filter_based_on_role import get_dashboard_scope



@frappe.whitelist()
def update_annual_revenue(deal_id, amount):
    deal = frappe.get_doc("CRM Deal", deal_id)
    deal.annual_revenue = amount
    deal.save(ignore_permissions=True)
    return "Updated"


@frappe.whitelist()
def make_crm_contract(source_name, target_doc=None):
	def set_missing_values(source, target):
		target.date = frappe.utils.nowdate()
		target.status = "Draft"
		target.naming_series = "CNT-.YYYY.-"





	def update_items(source_doc, target_doc, source_parent):
		target_doc.qty = source_doc.qty
		target_doc.rate = source_doc.rate
		target_doc.amount = source_doc.amount
		target_doc.description = source_doc.description

	doclist = get_mapped_doc(
		"CRM Quotation",
		source_name,
		{
			"CRM Quotation": {
				"doctype": "CRM Contract",
				"field_map": {
					"name": "from_quotation",
					"customer": "customer",
					"currency": "currency",
					"amount": "contract_value",
					"payment_terms": "payment_terms",
					"terms": "terms_and_conditions",
					"deal": "from_deal",
					"customer_name":"customer_name",
					"end_date": "expiry_date",
					"total_hp": "hp",


				},
				"validation": {
					"docstatus": ["=", 1]  # Only allow from submitted quotations
				}
			},
			"CRM Contract Item": {
				"doctype": "CRM Contract Item",
				"field_map": {
					"parent": "quotation",
					"name": "quotation_item"
				},
				"postprocess": update_items,
				"condition": lambda doc: doc.qty > 0
			}
		},
		target_doc,
		set_missing_values
	)
	return doclist 

@frappe.whitelist()
def get_all_quotations(name=None):
    """
    Fetch all CRM Quotations. Optionally filter by name.
    """
    Quotation = frappe.qb.DocType("CRM Quotation")

    # Build the query
    query = frappe.qb.from_(Quotation).select("*")

    if name:
        query = query.where(Quotation.name == name)

    # Execute the query
    quotations = query.run(as_dict=True)

    # If no quotations found, return an empty list
    if not quotations:
        return []

    # Enrich each quotation with additional details
    for quotation in quotations:
        quotation["contacts"] = frappe.get_all(
            "CRM Contacts",
            filters={"parenttype": "CRM Deal", "parent": quotation.get("name")},
            fields=["contact", "is_primary"],
        )
        quotation["doctype"] = "CRM Quotation"
        quotation["fields_meta"] = get_fields_meta("CRM Deal")
        quotation["_form_script"] = get_form_script("CRM Deal")
        quotation["_assign"] = get_assigned_users(
            "CRM Deal", quotation.get("name"), quotation.get("owner")
        )

    return quotations


from crm.api.dashboard_filter_based_on_role import get_dashboard_scope



import frappe
from frappe.utils import today, add_months, formatdate, get_first_day, get_last_day
import json
from collections import defaultdict



# Latest code


@frappe.whitelist()
def get_quotation_metrics(filters=None):
    """Get quotation metrics for dashboard (filters: date_range, industry, region, branch)"""
    try:
        import json
        from datetime import datetime, timedelta
        from frappe.utils import today, add_months

        # Parse filters from JSON string if provided
        if isinstance(filters, str):
            filters = json.loads(filters)
        filters = filters or {}

        # Apply dashboard scope if not explicitly overridden by filter
        scope = get_dashboard_scope()
        if scope.get("type") and scope.get("value"):
            if scope["type"] == "region" and not filters.get("region"):
                filters["region"] = scope["value"]
            elif scope["type"] == "branch" and not filters.get("branch"):
                filters["branch"] = scope["value"]

        base_filters = {"docstatus": ["!=", 2]}  # Not cancelled

        # --- APPLY FILTERS DIRECTLY ON QUOTATION FIELDS LIKE CONTRACT METRICS ---

        # Branch filter (direct on quotation)
        if filters.get("branch"):
            branches = filters["branch"]
            if isinstance(branches, str):
                branch_list = [b.strip() for b in branches.split(",") if b.strip()]
            else:
                branch_list = branches if isinstance(branches, list) else [branches]
            if branch_list:
                base_filters["branch"] = ["in", branch_list]

        # Region filter (direct on quotation)
        if filters.get("region"):
            regions = filters["region"]
            if isinstance(regions, str):
                region_list = [r.strip() for r in regions.split(",") if r.strip()]
            else:
                region_list = regions if isinstance(regions, list) else [regions]
            if region_list:
                base_filters["region"] = ["in", region_list]

        # Industry filter
        if filters.get("industry"):
            industries = filters["industry"]
            if isinstance(industries, str):
                industry_list = [i.strip() for i in industries.split(',') if i.strip()]
            else:
                industry_list = industries if isinstance(industries, list) else [industries]
            if industry_list:
                base_filters["industry"] = ["in", industry_list]

        # Date range filter
        from_date_filter = to_date_filter = None
        current_today = today()
        range_map = {
            "Last Month": -1,
            "Last Quarter": -3,
            "Last 6 Months": -6,
            "Last Year": -12
        }

        if filters.get("date_range") == "Custom":
            from_date_filter = filters.get("from_date")
            to_date_filter = filters.get("to_date")
        elif filters.get("date_range") in range_map:
            months = range_map[filters["date_range"]]
            from_date_filter = add_months(current_today, months)
            to_date_filter = current_today

        # Apply date filters
        if from_date_filter and to_date_filter:
            base_filters["creation"] = ["between", [from_date_filter, to_date_filter]]
        elif from_date_filter:
            base_filters["creation"] = [">=", from_date_filter]
        elif to_date_filter:
            base_filters["creation"] = ["<=", to_date_filter]

        # Fetch quotations
        quotations = frappe.get_all(
            "CRM Quotation",
            filters=base_filters,
            fields=[
                "name", "docstatus", "amount", "creation", "branch",
                "customer", "customer_name", "status", "workflow_state",
                "region"
            ]
        )

        # Calculate metrics
        total_value = 0
        status_counts = {}

        for q in quotations:
            total_value += float(q.amount or 0)
            status = q.status or "Open"
            status_counts[status] = status_counts.get(status, 0) + 1

        total_quotations = len(quotations)
        won_count = status_counts.get("Quote Won", 0)
        conversion_rate = (won_count / total_quotations * 100) if total_quotations > 0 else 0

        # Calculate growth compared to previous period
        previous_filters = {"docstatus": ["!=", 2]}
        if filters.get("industry"):
            previous_filters["industry"] = base_filters["industry"]
        if filters.get("branch"):
            previous_filters["branch"] = base_filters["branch"]
        if filters.get("region"):
            previous_filters["region"] = base_filters["region"]

        # Previous period dates
        if from_date_filter and to_date_filter:
            current_start = datetime.strptime(from_date_filter, "%Y-%m-%d").date()
            current_end = datetime.strptime(to_date_filter, "%Y-%m-%d").date()
            duration = (current_end - current_start).days + 1
            previous_end = current_start - timedelta(days=1)
            previous_start = previous_end - timedelta(days=duration - 1)
            previous_filters["creation"] = ["between", [str(previous_start), str(previous_end)]]
        else:
            previous_from = add_months(today(), -12)
            previous_to = add_months(today(), -6)
            previous_filters["creation"] = ["between", [previous_from, previous_to]]

        previous_quotations = frappe.get_all(
            "CRM Quotation",
            filters=previous_filters,
            fields=["amount", "status"]
        )
        previous_value = sum(float(q.amount or 0) for q in previous_quotations)
        value_growth = ((total_value - previous_value) / previous_value * 100) if previous_value > 0 else 0

        previous_won = len([q for q in previous_quotations if (q.status or "") == "Quote Won"])
        previous_total = len(previous_quotations)
        previous_conversion_rate = (previous_won / previous_total * 100) if previous_total > 0 else 0
        conversion_rate_growth = conversion_rate - previous_conversion_rate

        # Generate trend data
        trend_data = []
        if from_date_filter and to_date_filter:
            start_date = datetime.strptime(from_date_filter, "%Y-%m-%d").date().replace(day=1)
            end_date = datetime.strptime(to_date_filter, "%Y-%m-%d").date()
            current_month = start_date
            while current_month <= end_date:
                month_end = min(
                    (current_month.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1),
                    end_date
                )
                month_quotations = [q for q in quotations if current_month <= q.creation.date() <= month_end]
                month_data = {
                    "month": current_month.strftime("%b %Y"),
                    "open_value": sum(float(q.amount or 0) for q in month_quotations if (q.status or "Open") == "Open"),
                    "approved_value": sum(float(q.amount or 0) for q in month_quotations if (q.status or "") in ["Approved", "Quote Approved", "PO Pending"]),
                    "won_value": sum(float(q.amount or 0) for q in month_quotations if (q.status or "") == "Quote Won")
                }
                trend_data.append(month_data)
                current_month = (current_month.replace(day=28) + timedelta(days=4)).replace(day=1)

        return {
            "total_value": total_value,
            "total_value_growth": round(value_growth, 2),
            "conversion_rate": round(conversion_rate, 2),
            "conversion_rate_growth": round(conversion_rate_growth, 2),
            "status_counts": [{"status": status, "count": count} for status, count in status_counts.items()],
            "trend_data": trend_data
        }

    except Exception as e:
        frappe.log_error("Error in get_quotation_metrics", frappe.get_traceback())
        return default_metrics()

def default_metrics():
    return {
        "total_value": 0,
        "total_value_growth": 0,
        "conversion_rate": 0,
        "status_counts": [],
        "trend_data": []
    }

@frappe.whitelist()
def get_all_crm_industries():
    return frappe.get_all("CRM Industry", fields=["name"])

# Path: crm/api/region.py or in crm.region_master.region_master

@frappe.whitelist()
def get_all_regions():
    return frappe.get_all("Region Master", fields=["name"])


