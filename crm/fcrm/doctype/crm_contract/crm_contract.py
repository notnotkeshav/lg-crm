import frappe
from frappe import _
from datetime import datetime, timedelta
from frappe.utils import today, add_months, add_days, formatdate, getdate
import json
from collections import defaultdict



@frappe.whitelist()
def get_contract_metrics(filters=None):
    """Get contract metrics for dashboard (supports region, branch, and industry filters)"""
    try:
        # Parse filters
        if isinstance(filters, str):
            filters = json.loads(filters)
        filters = filters or {}
        
        frappe.log_error(
            message=f"Parsed filters: {filters}", 
            title="Contract Metrics - Input"
        )

        base_filters = {"docstatus": ["!=", 2]}

        # Handle multi-select industry filter
        if filters.get("industry"):
            industries = filters["industry"]
            if isinstance(industries, str):
                industries = [i.strip() for i in industries.split(',') if i.strip()]
            if industries:
                base_filters["industry"] = ["in", industries]

        # Handle multi-select region filter (DIRECT on CRM Contract)
        if filters.get("region"):
            regions = filters["region"]
            
            # Normalize to list
            if isinstance(regions, str):
                region_list = [r.strip() for r in regions.split(",") if r.strip()]
            else:
                region_list = regions if isinstance(regions, list) else [regions]
            
            if region_list:
                base_filters["region"] = ["in", region_list]
                
                frappe.log_error(
                    message=f"Region filter applied: {region_list}", 
                    title="Contract Metrics - Region Filter"
                )

        # Handle multi-select branch filter (DIRECT on CRM Contract)
        if filters.get("branch"):
            branches = filters["branch"]
            
            # Normalize to list
            if isinstance(branches, str):
                branch_list = [b.strip() for b in branches.split(",") if b.strip()]
            else:
                branch_list = branches if isinstance(branches, list) else [branches]
            
            if branch_list:
                base_filters["branch"] = ["in", branch_list]
                
                frappe.log_error(
                    message=f"Branch filter applied: {branch_list}", 
                    title="Contract Metrics - Branch Filter"
                )

        # Handle multi-select industry filter (DIRECT on CRM Contract)
        if filters.get("industry"):
            industrys = filters["industry"]
            
            # Normalize to list
            if isinstance(industrys, str):
                industry_list = [v.strip() for v in industrys.split(",") if v.strip()]
            else:
                industry_list = industrys if isinstance(industrys, list) else [industrys]
            
            if industry_list:
                base_filters["industry"] = ["in", industry_list]
                
                frappe.log_error(
                    message=f"industry filter applied: {industry_list}", 
                    title="Contract Metrics - industry Filter"
                )

        # Handle date range filters
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

        # Apply date filters to base query
        if from_date_filter and to_date_filter:
            base_filters["creation"] = ["between", [from_date_filter, to_date_filter]]
        elif from_date_filter:
            base_filters["creation"] = [">=", from_date_filter]
        elif to_date_filter:
            base_filters["creation"] = ["<=", to_date_filter]

        frappe.log_error(
            message=f"Final base_filters: {base_filters}", 
            title="Contract Metrics - Query Filters"
        )

        # Get CRM Contracts
        contracts = frappe.get_all(
            "CRM Contract",
            filters=base_filters,
            fields=[
                "name", "docstatus", "amount", "creation",
                "customer", "customer_name", "custom_contract_status",
                "start_date", "expiry_date", "total_usd", "project", 
                "branch", "region", "industry" , "deal_type"
            ]
        )

        frappe.log_error(
            message=f"Contracts found: {len(contracts)}", 
            title="Contract Metrics - Results"
        )
        
        
        

        lost_amc_conversion = 0
        amc_renewal = 0
        warranty_amc_conversion = 0
        lost_warranty_conversion = 0
        
        # Process contract metrics
        current_today_date = getdate(current_today)
        active_contracts = expiring_soon = expired_contracts = renewed_contracts = 0
        total_value = total_usd_value = 0

        for contract in contracts:
            total_value += float(contract.amount or 0)
            total_usd_value += float(contract.total_usd or 0)
            
            
            if contract.deal_type == "Lost AMC Conversion":
                lost_amc_conversion += 1
                
            if contract.deal_type == "AMC Renewal":
                amc_renewal += 1

            if contract.deal_type == "Warranty AMC Conversion":
                warranty_amc_conversion += 1

            if contract.deal_type == "Lost Warranty Conversion":
                lost_warranty_conversion += 1

            # Count renewed contracts (based on project AMC status)
            if contract.project:
                try:
                    project_status = frappe.db.get_value("Project", contract.project, "status")
                    if project_status == "AMC Active":
                        renewed_contracts += 1
                except Exception:
                    pass

            # Contract status handling
            status = contract.custom_contract_status or "Draft"
            if status == "Active":
                active_contracts += 1
            elif status == "Expired":
                expired_contracts += 1
            elif status == "Draft":
                if contract.start_date and contract.expiry_date:
                    start_date = getdate(contract.start_date)
                    expiry_date = getdate(contract.expiry_date)
                    if start_date <= current_today_date <= expiry_date:
                        active_contracts += 1

            # Check if contract is expiring soon (within 60 days)
            if contract.expiry_date:
                try:
                    expiry_date = getdate(contract.expiry_date)
                    days_to_expiry = (expiry_date - current_today_date).days
                    if 0 <= days_to_expiry <= 60:
                        expiring_soon += 1
                except Exception:
                    pass

        total_contracts = len(contracts)
        active_ratio = (active_contracts / total_contracts * 100) if total_contracts else 0

        # Calculate growth compared to previous period
        value_growth = active_ratio_growth = 0
         
        
        if from_date_filter and to_date_filter:
            previous_from_date = previous_to_date = None
            
            if filters.get("date_range") == "Custom":
                from_dt = datetime.strptime(str(from_date_filter), "%Y-%m-%d").date()
                to_dt = datetime.strptime(str(to_date_filter), "%Y-%m-%d").date()
                duration = (to_dt - from_dt).days + 1
                previous_to_date = from_dt - timedelta(days=1)
                previous_from_date = previous_to_date - timedelta(days=duration - 1)
            elif filters.get("date_range") in range_map:
                months = range_map[filters["date_range"]]
                previous_from_date = add_months(current_today, months * 2)
                previous_to_date = add_months(current_today, months)

            if previous_from_date and previous_to_date:
                previous_filters = {"docstatus": ["!=", 2]}
                previous_filters["creation"] = ["between", [str(previous_from_date), str(previous_to_date)]]
                
                # Apply same filtering criteria to previous period
                if base_filters.get("industry"):
                    previous_filters["industry"] = base_filters["industry"]
                if base_filters.get("region"):
                    previous_filters["region"] = base_filters["region"]
                if base_filters.get("branch"):
                    previous_filters["branch"] = base_filters["branch"]
                if base_filters.get("industry"):
                    previous_filters["industry"] = base_filters["industry"]

                previous_contracts = frappe.get_all(
                    "CRM Contract", 
                    filters=previous_filters, 
                    fields=["amount", "custom_contract_status"]
                )
                
                previous_value = sum(float(c.amount or 0) for c in previous_contracts)
                previous_active = len([c for c in previous_contracts if (c.custom_contract_status or "Draft") == "Active"])
                previous_total = len(previous_contracts)
                previous_active_ratio = (previous_active / previous_total * 100) if previous_total else 0
                
                value_growth = ((total_value - previous_value) / previous_value * 100) if previous_value else 0
                # active_ratio_growth = active_ratio - previous_active_ratio
                active_ratio_growth = previous_active
        frappe.log_error(
            message=f"Metrics - Total: {total_contracts}, Active: {active_contracts}, Value: {total_value}, USD: {total_usd_value}", 
            title="Contract Metrics - Final"
        )
        

        return {
            "total_contracts": total_contracts,
            "active_contracts": active_contracts,
            "expiring_soon": expiring_soon,
            "expired_contracts": expired_contracts,
            "renewed_contracts": renewed_contracts,
            "total_value": total_value,
            "total_usd_value": total_usd_value,
            "total_value_growth": round(value_growth, 2),
            "active_ratio": round(active_ratio, 2),
            "active_ratio_growth": round(active_ratio_growth, 2),
            "lost_amc_conversion": lost_amc_conversion,
            "lost_amc_conversion_growth": round(((lost_amc_conversion / total_contracts * 100) if total_contracts else 0), 2),
            
            "amc_renewal": amc_renewal,
            "amc_renewal_growth": round(((amc_renewal / total_contracts * 100) if total_contracts else 0), 2),
            "warranty_amc_conversion": warranty_amc_conversion,
            "warranty_amc_conversion_growth": round(((warranty_amc_conversion / total_contracts * 100) if total_contracts else 0), 2),
            "lost_warranty_conversion": lost_warranty_conversion,
            "lost_warranty_conversion_growth": round(((lost_warranty_conversion / total_contracts * 100) if total_contracts else 0), 2)
            
        }

    except Exception as e:
        frappe.log_error(
            message=f"ERROR: {str(e)}\n\nTraceback:\n{frappe.get_traceback()}", 
            title="Contract Metrics - Exception"
        )
        return _empty_contract_metrics()
def _empty_contract_metrics():
    """Return empty contract metrics structure"""
    return {
        "total_contracts": 0,
        "active_contracts": 0,
        "expiring_soon": 0,
        "expired_contracts": 0,
        "renewed_contracts": 0,
        "total_value": 0,
        "total_usd_value": 0,
        "total_value_growth": 0,
        "active_ratio": 0,
        "active_ratio_growth": 0
    }
