import frappe
from frappe import _
import json

from crm.api.doc import get_fields_meta, get_assigned_users
from crm.fcrm.doctype.crm_form_script.crm_form_script import get_form_script

from frappe.utils import today, add_months,getdate
# from random import random
from datetime import datetime


@frappe.whitelist()
def get_deal(name):
	Deal = frappe.qb.DocType("CRM Deal")

	query = (
		frappe.qb.from_(Deal)
		.select("*")
		.where(Deal.name == name)
		.limit(1)
	)

	deal = query.run(as_dict=True)
	if not len(deal):
		frappe.throw(_("Deal not found"), frappe.DoesNotExistError)
	deal = deal.pop()


	deal["contacts"] = frappe.get_all(
		"CRM Contacts",
		filters={"parenttype": "CRM Deal", "parent": deal.name},
		fields=["contact", "is_primary"],
	)

	deal["doctype"] = "CRM Deal"
	deal["fields_meta"] = get_fields_meta("CRM Deal") 
	deal["_form_script"] = get_form_script('CRM Deal')
	deal["_assign"] = get_assigned_users("CRM Deal", deal.name, deal.owner)
	return deal

@frappe.whitelist()
def get_deal_contacts(name):
	contacts = frappe.get_all(
		"CRM Contacts",
		filters={"parenttype": "CRM Deal", "parent": name},
		fields=["contact", "is_primary"],
	)
	deal_contacts = []
	for contact in contacts:
		is_primary = contact.is_primary
		contact = frappe.get_doc("Contact", contact.contact).as_dict()
		def get_primary_email(contact):
			for email in contact.email_ids:
				if email.is_primary:
					return email.email_id
			return contact.email_ids[0].email_id if contact.email_ids else ""
		def get_primary_mobile_no(contact):
			for phone in contact.phone_nos:
				if phone.is_primary:
					return phone.phone
			return contact.phone_nos[0].phone if contact.phone_nos else ""
		_contact = {
			"name": contact.name,
			"image": contact.image,
			"full_name": contact.full_name,
			"email": get_primary_email(contact),
			"mobile_no": get_primary_mobile_no(contact),
			"is_primary": is_primary,
		}
		deal_contacts.append(_contact)
	return deal_contacts

@frappe.whitelist()
def get_deal_metrics(filters=None):
	"""Get deal metrics for dashboard"""
	if isinstance(filters, str):
		filters = json.loads(filters)

	today = frappe.utils.today()
	week_start = frappe.utils.add_days(today, -7)
	month_start = frappe.utils.add_months(today, -1)

	# Total Deals
	total_deals = frappe.db.count('CRM Deal')

	# Active Deals (not closed or lost)
	active_deals = frappe.db.count('CRM Deal', 
		filters={'status': ['not in', ['Closed (Lost)', 'Closed (Won)']]})

	# Expired Deals (past close date)
	expired_deals = frappe.db.count('CRM Deal',
		filters={'close_date': ['<', today], 'status': ['not in', ['Closed (Lost)', 'Closed (Won)']]})

	# New Conversions (Won deals in last month)
	new_conversions = frappe.db.count('CRM Deal',
		filters={'status': 'Closed (Won)', 'modified': ['>=', month_start]})

	# AMC Renewal Deals
	amc_renewal = frappe.db.count('CRM Deal',
		filters={'deal_type': 'AMC Renewal'})

	# Lost Conversions
	lost_conversion = frappe.db.count('CRM Deal',
		filters={'status': 'Closed (Lost)'})

	# Warranty Conversion
	warranty_conversion = frappe.db.count('CRM Deal',
		filters={'deal_type': 'Warranty'})

	# Status-wise count and value
	status_data = frappe.db.sql("""
		SELECT 
			status,
			COUNT(*) as count,
			COALESCE(SUM(annual_revenue), 0) as value
		FROM `tabCRM Deal`
		WHERE status IS NOT NULL
		GROUP BY status
		ORDER BY count DESC
	""", as_dict=1) or []

	# Calculate total value
	total_value = sum(item.get('value', 0) for item in status_data)

	return {
		'total_deals': total_deals,
		'active_deals': active_deals,
		'expired_deals': expired_deals,
		'new_conversions': new_conversions,
		'amc_renewal': amc_renewal,
		'lost_conversion': lost_conversion,
		'warranty_conversion': warranty_conversion,
		'status_data': status_data,
		'total_value': total_value
	}

@frappe.whitelist()
def get_deal_reports(start_date=None, end_date=None):
    """Get comprehensive deal reports including KPIs, trends, and distributions"""
    if not start_date:
        start_date = frappe.utils.add_days(frappe.utils.today(), -30)
    if not end_date:
        end_date = frappe.utils.today()

    return {
        "kpis": get_deal_kpis(start_date, end_date),
        "pipeline": get_deal_pipeline(),
        "trend": get_deal_trend(start_date, end_date),
        "territory": get_territory_distribution(),
        "deal_types": get_deal_type_distribution()
    }

def get_deal_kpis(start_date, end_date):
    """Get key performance indicators for deals"""
    Deal = frappe.qb.DocType("CRM Deal")
    
    # Total Deal Value
    total_value = frappe.db.get_value(
        "CRM Deal",
        {"creation": ["between", [start_date, end_date]]},
        "sum(deal_value)"
    ) or 0

    # Deal Win Rate
    total_closed = frappe.db.count(
        "CRM Deal",
        {"status": ["in", ["Closed (Won)", "Closed (Lost)"]], "modified": ["between", [start_date, end_date]]}
    )
    won_deals = frappe.db.count(
        "CRM Deal",
        {"status": "Closed (Won)", "modified": ["between", [start_date, end_date]]}
    )
    win_rate = (won_deals / total_closed * 100) if total_closed > 0 else 0

    # Average Deal Size
    avg_deal_size = frappe.db.get_value(
        "CRM Deal",
        {"creation": ["between", [start_date, end_date]]},
        "avg(deal_value)"
    ) or 0

    # Active Deals Count
    active_deals = frappe.db.count(
        "CRM Deal",
        {"status": ["not in", ["Closed (Won)", "Closed (Lost)"]], "modified": ["between", [start_date, end_date]]}
    )

    return [
        {
            "label": "Total Deal Value",
            "value": total_value,
            "format": "currency"
        },
        {
            "label": "Deal Win Rate",
            "value": round(win_rate, 1),
            "format": "percentage"
        },
        {
            "label": "Average Deal Size",
            "value": avg_deal_size,
            "format": "currency"
        },
        {
            "label": "Active Deals",
            "value": active_deals,
            "format": "number"
        }
    ]

def get_deal_pipeline():
    """Get deal pipeline distribution"""
    pipeline_stages = frappe.get_all(
        "CRM Pipeline Stage",
        fields=["name", "stage_name"],
        order_by="creation"
    )

    series = []
    for stage in pipeline_stages:
        value = frappe.db.count("CRM Deal", {"pipeline_stage": stage.name})
        series.append(value)

    return {
        "labels": [stage.stage_name for stage in pipeline_stages],
        "series": [{"name": "Deals", "data": series}]
    }

@frappe.whitelist()
def get_deal_trend(start_date=None, end_date=None):
    """Get deal trend over time"""
    if not start_date:
        start_date = frappe.utils.add_days(frappe.utils.today(), -30)
    if not end_date:
        end_date = frappe.utils.today()

    dates = []
    current = frappe.utils.getdate(start_date)
    end = frappe.utils.getdate(end_date)
    
    while current <= end:
        dates.append(current)
        current = frappe.utils.add_days(current, 1)

    won_series = []
    total_series = []

    for date in dates:
        won = frappe.db.count(
            "CRM Deal",
            {"status": "Closed (Won)", "creation": ["<=", date]}
        )
        total = frappe.db.count(
            "CRM Deal",
            {"creation": ["<=", date]}
        )
        
        won_series.append(won)
        total_series.append(total)

    return {
        "labels": [frappe.utils.formatdate(date) for date in dates],
        "series": [
            {"name": "Won Deals", "data": won_series},
            {"name": "Total Deals", "data": total_series}
        ]
    }

def get_territory_distribution():
    """Get deal distribution by territory"""
    territories = frappe.get_all(
        "Territory",
        fields=["territory_name"]
    )

    labels = []
    series = []

    for territory in territories:
        count = frappe.db.count("CRM Deal", {"territory": territory.territory_name})
        if count > 0:
            labels.append(territory.territory_name)
            series.append(count)

    return {
        "labels": labels,
        "series": series
    }

def get_deal_type_distribution():
    """Get deal distribution by type"""
    deal_types = frappe.get_all(
        "CRM Deal",
        fields=["deal_type"],
        group_by="deal_type"
    )

    labels = []
    series = []

    for deal_type in deal_types:
        if not deal_type.deal_type:
            continue
        count = frappe.db.count("CRM Deal", {"deal_type": deal_type.deal_type})
        labels.append(deal_type.deal_type)
        series.append(count)

    return {
        "labels": labels,
        "series": series
    }


@frappe.whitelist()
def duplicate_deal_service(docname):
    if not docname: 
        print(f"------ not present doc name, required {docname} --------")
        return "docname required"
    
    print(f"------ running duplicate deal service {docname} --------")

    doc = frappe.get_doc("CRM Deal", docname)
    new_doc = frappe.copy_doc(doc)
    count = doc.get("duplicate_count") + 1

    new_doc.set("name", f"{docname}-{count}")
    new_doc.set("opportunity_id", f"{docname}-{count}")
    new_doc.set("duplicate_count", 0)
    new_doc.set("last_duplicate_date", today())
    new_doc.set("deal_category","Service")
    new_doc.set("status","Qualification")
    new_doc.set("duplicate_trigger_date",None)
    # Clear expiry dates from the duplicate
    new_doc.set("amc_expiry_date", None)
    new_doc.set("register_date",None)
    new_doc.set("warranty_expiry_date", None)
    new_doc.set("warranty_amc_status",None)
    new_doc.set("from_duplicate",docname)
    # ✅ Set deal_type based on original document
    if doc.get("warranty_expiry_date"):
        new_doc.set("deal_type", "Warranty Conversion")
    elif doc.get("amc_expiry_date"):
        new_doc.set("deal_type", "AMC Renewal")
    new_doc.insert(ignore_permissions=True)
        # get deal_owner
    deal_owner = new_doc.deal_owner
    if deal_owner:
        notify_deal_owner_system(deal_owner, doc, new_doc)
    new_doc.save()
    frappe.db.commit()
    print(f"---- new doc created {new_doc.name}")

    frappe.msgprint(
        _(f'New Deal created: <a href="/app/crm-deal/{new_doc.name}" target="_blank">{new_doc.name}</a>'),
        title="Deal Created",
        indicator="green"
    )

    frappe.db.set_value("CRM Deal", docname, {"duplicate_count": count, "last_duplicate_date": today()})    
    frappe.db.commit()
    return new_doc.name

@frappe.whitelist()
def auto_duplicate_expired_deals():
    today_date = getdate(today())

    deals = frappe.get_all("CRM Deal",
        filters={"duplicate_trigger_date": today_date},
        fields=["name"]
    )

    for deal in deals:
        try:
            print(f"Creating duplicate for deal: {deal.name}")
            duplicate_deal_service(deal.name)
        except Exception:
            frappe.log_error(frappe.get_traceback(), f"Auto Duplicate Deal Failed for {deal.name}")

def notify_deal_owner_system(user, original_doc, duplicate_doc):
    if not user or not frappe.db.exists("User", user):
        print(f"Invalid or missing user: {user}")
        return

    # Get expiry date from AMC or Warranty
    expiry_date = original_doc.amc_expiry_date or original_doc.warranty_expiry_date

    if not expiry_date:
        print("No expiry date found. Skipping notification.")
        return
    # Build the subject as you want
    subject = (
        f"New Deal {duplicate_doc.name} Created from {original_doc.name} "
        f"expiring on {expiry_date}"
    )

    notification = frappe.new_doc("Notification Log")
    notification.update({
        "subject": subject,
        "email_content": subject,
        "for_user": user,
        "document_type": "CRM Deal",
        "document_name": duplicate_doc.name,
        "type": "Alert",
        "seen": 0
    })
    notification.insert(ignore_permissions=True)

    print(f"Notification sent to user: {user}")

