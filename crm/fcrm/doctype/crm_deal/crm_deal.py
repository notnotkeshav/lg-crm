# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
import json

import frappe
from frappe import _
from frappe.desk.form.assign_to import add as assign
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import now_datetime,getdate,add_months

from crm.fcrm.doctype.crm_service_level_agreement.utils import get_sla
from crm.fcrm.doctype.crm_status_change_log.crm_status_change_log import add_status_change_log
from crm.api.dashboard_filter_based_on_role import get_dashboard_scope


class CRMDeal(Document):

    def before_validate(self):
        self.set_sla()

    def validate(self):
        if not self.is_new() and self.has_value_changed("deal_owner") and self.deal_owner:
            self.share_with_agent(self.deal_owner)
            self.assign_agent(self.deal_owner)
        if self.has_value_changed("status"):
            frappe.msgprint("wprkign if not save document")
            add_status_change_log(self)
    

    def after_insert(self):
        if self.deal_owner:
            self.assign_agent(self.deal_owner)

    def before_save(self):
        self.apply_sla()
        

    def set_primary_contact(self, contact=None):
        if not self.contacts:
            return

        if not contact and len(self.contacts) == 1:
            self.contacts[0].is_primary = 1
        elif contact:
            for d in self.contacts:
                if d.contact == contact:
                    d.is_primary = 1
                else:
                    d.is_primary = 0

    def set_primary_email_mobile_no(self):
        if not self.contacts:
            self.email = ""
            self.mobile_no = ""
            self.phone = ""
            return

        if len([contact for contact in self.contacts if contact.is_primary]) > 1:
            frappe.throw(_("Only one {0} can be set as primary.").format(frappe.bold("Contact")))

        primary_contact_exists = False
        for d in self.contacts:
            if d.is_primary == 1:
                primary_contact_exists = True
                self.email = d.email.strip() if d.email else ""
                self.mobile_no = d.mobile_no.strip() if d.mobile_no else ""
                self.phone = d.phone.strip() if d.phone else ""
                break

        if not primary_contact_exists:
            self.email = ""
            self.mobile_no = ""
            self.phone = ""

    def assign_agent(self, agent):
        if not agent:
            return

        assignees = self.get_assigned_users()
        if assignees:
            for assignee in assignees:
                if agent == assignee:
                    # the agent is already set as an assignee
                    return

        assign({"assign_to": [agent], "doctype": "CRM Deal", "name": self.name})

    def share_with_agent(self, agent):
        if not agent:
            return

        docshares = frappe.get_all(
            "DocShare",
            filters={"share_name": self.name, "share_doctype": self.doctype},
            fields=["name", "user"],
        )

        shared_with = [d.user for d in docshares] + [agent]

        for user in shared_with:
            if user == agent and not frappe.db.exists("DocShare", {"user": agent, "share_name": self.name, "share_doctype": self.doctype}):
                frappe.share.add_docshare(
                    self.doctype, self.name, agent, write=1, flags={"ignore_share_permission": True}
                )
            elif user != agent:
                frappe.share.remove(self.doctype, self.name, user)


    def set_sla(self):
        """
        Find an SLA to apply to the deal.
        """
        if self.sla: return

        sla = get_sla(self)
        if not sla:
            self.first_responded_on = None
            self.first_response_time = None
            return
        self.sla = sla.name

    def apply_sla(self):
        """
        Apply SLA if set.
        """
        if not self.sla:
            return
        sla = frappe.get_last_doc("CRM Service Level Agreement", {"name": self.sla})
        if sla:
            sla.apply(self)

    @staticmethod
    def default_list_data():
        columns = [
            {
                'label': 'Organization',
                'type': 'Link',
                'key': 'organization',
                'options': 'CRM Organization',
                'width': '11rem',
            },
            {
                'label': 'Amount',
                'type': 'Currency',
                'key': 'annual_revenue',
                'width': '9rem',
            },
            {
                'label': 'Status',
                'type': 'Select',
                'key': 'status',
                'width': '10rem',
            },
            {
                'label': 'Email',
                'type': 'Data',
                'key': 'email',
                'width': '12rem',
            },
            {
                'label': 'Mobile No',
                'type': 'Data',
                'key': 'mobile_no',
                'width': '11rem',
            },
            {
                'label': 'Assigned To',
                'type': 'Text',
                'key': '_assign',
                'width': '10rem',
            },
            {
                'label': 'Last Modified',
                'type': 'Datetime',
                'key': 'modified',
                'width': '8rem',
            },
        ]
        rows = [
            "name",
            "organization",
            "annual_revenue",
            "status",
            "email",
            "currency",
            "mobile_no",
            "deal_owner",
            "sla_status",
            "response_by",
            "first_response_time",
            "first_responded_on",
            "modified",
            "_assign",
        ]
        return {'columns': columns, 'rows': rows}

    @staticmethod
    def default_kanban_settings():
        return {
            "column_field": "status",
            "title_field": "organization",
            "kanban_fields": '["annual_revenue", "email", "mobile_no", "_assign", "modified"]'
        }

@frappe.whitelist()
def add_contact(deal, contact):
    if not frappe.has_permission("CRM Deal", "write", deal):
        frappe.throw(_("Not allowed to add contact to Deal"), frappe.PermissionError)

    deal = frappe.get_cached_doc("CRM Deal", deal)
    deal.append("contacts", {"contact": contact})
    deal.save()
    return True

@frappe.whitelist()
def remove_contact(deal, contact):
    if not frappe.has_permission("CRM Deal", "write", deal):
        frappe.throw(_("Not allowed to remove contact from Deal"), frappe.PermissionError)

    deal = frappe.get_cached_doc("CRM Deal", deal)
    deal.contacts = [d for d in deal.contacts if d.contact != contact]
    deal.save()
    return True

@frappe.whitelist()
def set_primary_contact(deal, contact):
    if not frappe.has_permission("CRM Deal", "write", deal):
        frappe.throw(_("Not allowed to set primary contact for Deal"), frappe.PermissionError)

    deal = frappe.get_cached_doc("CRM Deal", deal)
    deal.set_primary_contact(contact)
    deal.save()
    return True

def create_organization(doc):
    if not doc.get("organization_name"):
        return

    existing_organization = frappe.db.exists("CRM Organization", {"organization_name": doc.get("organization_name")})
    if existing_organization:
        return existing_organization

    organization = frappe.new_doc("CRM Organization")
    organization.update(
        {
            "organization_name": doc.get("organization_name"),
            "website": doc.get("website"),
            "territory": doc.get("territory"),
            "industry": doc.get("industry"),
            "annual_revenue": doc.get("annual_revenue"),
        }
    )
    organization.insert(ignore_permissions=True)
    return organization.name

def contact_exists(doc):
    email_exist = frappe.db.exists("Contact Email", {"email_id": doc.get("email")})
    mobile_exist = frappe.db.exists("Contact Phone", {"phone": doc.get("mobile_no")})

    doctype = "Contact Email" if email_exist else "Contact Phone"
    name = email_exist or mobile_exist

    if name:
        return frappe.db.get_value(doctype, name, "parent")

    return False

def create_contact(doc):
    existing_contact = contact_exists(doc)
    if existing_contact:
        return existing_contact

    contact = frappe.new_doc("Contact")
    contact.update(
        {
            "first_name": doc.get("first_name"),
            "last_name": doc.get("last_name"),
            "salutation": doc.get("salutation"),
            "company_name": doc.get("organization") or doc.get("organization_name"),
        }
    )

    if doc.get("email"):
        contact.append("email_ids", {"email_id": doc.get("email"), "is_primary": 1})

    if doc.get("mobile_no"):
        contact.append("phone_nos", {"phone": doc.get("mobile_no"), "is_primary_mobile_no": 1})

    contact.insert(ignore_permissions=True)
    contact.reload()  # load changes by hooks on contact

    return contact.name

@frappe.whitelist()
def create_deal(args):
    deal = frappe.new_doc("CRM Deal")

    contact = args.get("contact")
    if not contact and (args.get("first_name") or args.get("last_name") or args.get("email") or args.get("mobile_no")):
        contact = create_contact(args)

    deal.update({
        "organization": args.get("organization") or create_organization(args),
        "contacts": [{"contact": contact, "is_primary": 1}] if contact else [],
    })

    args.pop("organization", None)

    deal.update(args)

    deal.insert(ignore_permissions=True)
    return deal.name

@frappe.whitelist()
def make_crm_quotation(source_name, target_doc=None):
    def set_missing_values(source, target):
        target.date = frappe.utils.nowdate()
        target.valid_till = frappe.utils.add_days(target.date, 30)
        target.status = "Open"
        target.naming_series = "QT.-.YYYY.-"
        target.deal=source.name
        
        # Copy contact details if available
        if source.email:
            target.contact_email = source.email
        # if source.mobile_no:
        #     target.mobile_no = source.mobile_no

    doclist = get_mapped_doc(
        "CRM Deal",
        source_name,
        {
            "CRM Deal": {
                "doctype": "CRM Quotation",
                "field_map": {
                    "customer_name": "customer",
                    "customer_name":"customer_hc",
                    "currency": "currency",
                    "annual_revenue": "amount",
                    "total_hp":"total_hp",
                    "total_tonnes":"total_tonne",
                    "start_date":"start_date_as_per_po",
                    "end_date":"end_date_as_per_po",

                },
                "validation": {
                    "docstatus": ["=", 0]
                }
            },
            "Product Information": {
                "doctype": "Contract Items",
                "field_map": {
                    "serial_no": "serial_no",
                    "product_code": "product_code",
                    "product_name": "product_name",
                    "rate": "rate",
                    "amount": "amount"
                }
            }
        },
        target_doc,
        set_missing_values
    )
    return doclist

@frappe.whitelist()
def make_crm_contract(source_name, target_doc=None):
    def set_missing_values(source, target):
        target.date = frappe.utils.nowdate()
        target.status = "Open"
        # target.series = "CNT-.YYYY.-"
        target.contract_from = "Deal"
        # Set title based on customer name
        if source.organization_name:
            target.title = source.organization_name

    doclist = get_mapped_doc(
        "CRM Deal",
        source_name,
        {
            "CRM Deal": {
                "doctype": "CRM Contract",
                "field_map": {
                    "customer_name": "customer",
                    "currency": "currency",
                    "annual_revenue": "contract_value",
                    "customer_name":"customer_name"
                },
                "validation": {
                    "docstatus": ["=", 0]
                }
            },
            "Product Information": {
                "doctype": "CRM Contract Item",
                "field_map": {
                    "serial_no": "serial_no",
                    "product_code": "product_code",
                    "product_name": "product_name",
                    "rate": "rate",
                    "amount": "amount",
                    "type": "type",
                    "warranty_start_date": "warranty_start_date",
                    "warranty_expiry_date": "warranty_expiry_date"
                }
            }
        },
        target_doc,
        set_missing_values
    )
    return doclist

@frappe.whitelist()
def get_deal_tasks(deal, status=None):
    """Get tasks related to the deal"""
    filters = {
        "reference_type": "CRM Deal",
        "reference_name": deal
    }
    if status and status != "all":
        filters["status"] = status

    tasks = frappe.get_all("ToDo",
        filters=filters,
        fields=["name", "description", "status", "date", "allocated_to"],
        order_by="creation desc"
    )
    return tasks

@frappe.whitelist()
def create_follow_up_task(deal, description, date, assigned_to):
    """Create a follow up task for the deal"""
    if not frappe.has_permission("CRM Deal", "write", deal):
        frappe.throw(_("Not allowed to create tasks for this deal"), frappe.PermissionError)

    task = frappe.get_doc({
        "doctype": "ToDo",
        "description": description,
        "reference_type": "CRM Deal",
        "reference_name": deal,
        "allocated_to": assigned_to,
        "date": date,
        "status": "Open"
    })
    task.insert(ignore_permissions=True)
    return task.name

@frappe.whitelist()
def complete_task(task, completion_note):
    """Complete a task with a completion note"""
    if not frappe.has_permission("ToDo", "write", task):
        frappe.throw(_("Not allowed to complete this task"), frappe.PermissionError)

    todo = frappe.get_doc("ToDo", task)
    todo.status = "Closed"
    todo.description += "\n\nCompletion Note: " + completion_note
    todo.save(ignore_permissions=True)
    return todo.name

@frappe.whitelist()
def check_pending_activities(deal, doctype):
    """Check if there are any pending activities of the specified type"""
    if doctype == "ToDo":
        return bool(frappe.get_all("ToDo",
            filters={
                "reference_type": "CRM Deal",
                "reference_name": deal,
                "status": "Open"
            },
            limit=1
        ))
    elif doctype == "Event":
        return bool(frappe.db.sql("""
            SELECT e.name 
            FROM tabEvent e
            INNER JOIN `tabEvent Participants` ep ON e.name = ep.parent
            WHERE ep.reference_doctype = 'CRM Deal'
            AND ep.reference_docname = %s
            AND e.status = 'Open'
            LIMIT 1
        """, (deal,)))
    return False

@frappe.whitelist()
def get_deal_activities(deal, activity_type=None, status=None):
    """Get all activities (tasks and events) related to the deal"""
    activities = []
    
    # Get tasks
    if not activity_type or activity_type == "ToDo":
        filters = {
            "reference_type": "CRM Deal",
            "reference_name": deal
        }
        # Only add status filter if it's not 'all'
        if status and status.lower() != "all":
            filters["status"] = status
            
        tasks = frappe.get_all("ToDo",
            filters=filters,
            fields=[
                "name",
                "description",
                "status",
                "date",
                "allocated_to",
                "modified",
                "'ToDo' as activity_type"
            ]
        )
        for t in tasks:
            t["doctype"] = "todo"

        activities.extend(tasks)

    # Get events
    if not activity_type or activity_type == "Event":
        event_filters = ""
        # Only add status filter if it's not 'all'
        if status and status.lower() != "all":
            event_filters = f"AND e.status = '{status}'"
            
        events = frappe.db.sql("""
            SELECT 
                e.name,
                e.subject as description,
                e.status,
                e.starts_on as date,
                ep.owner as allocated_to,
                e.modified,
                'Event' as activity_type,
                e.event_category as event_type
            FROM tabEvent e
            INNER JOIN `tabEvent Participants` ep ON e.name = ep.parent
            WHERE ep.reference_doctype = 'CRM Deal'
            AND ep.reference_docname = %s
            {0}
            ORDER BY e.modified DESC
        """.format(event_filters), (deal,), as_dict=1)
        for e in events:
            e["doctype"] = "event"

        activities.extend(events)
    
    # Sort by modified date
    activities.sort(key=lambda x: x.get("modified"), reverse=True)
    return activities

@frappe.whitelist()
def create_deal_task(deal, description, date, assigned_to):
    """Create a task for the deal"""
    if not frappe.has_permission("CRM Deal", "write", deal):
        frappe.throw(_("Not allowed to create tasks for this deal"), frappe.PermissionError)

    task = frappe.get_doc({
        "doctype": "ToDo",
        "description": description,
        "reference_type": "CRM Deal",
        "reference_name": deal,
        "allocated_to": assigned_to,
        "date": date,
        "status": "Open"
    })
    task.insert(ignore_permissions=True)
    return task.name

@frappe.whitelist()
def create_follow_up(deal, subject, type, description, date, assigned_to):
    """Create a follow up event for the deal"""
    if not frappe.has_permission("CRM Deal", "write", deal):
        frappe.throw(_("Not allowed to create follow ups for this deal"), frappe.PermissionError)

    event = frappe.get_doc({
        "doctype": "Event",
        "subject": subject,
        "event_type": "Private",
        "event_category": type,
        "description": description,
        "starts_on": date,
        "status": "Open",
        "reference_type": "CRM Deal",
        "reference_name": deal
    })
    
    event.append("event_participants", {
        "reference_doctype": "CRM Deal",
        "reference_docname": deal,
        "owner": assigned_to
    })
    
    event.insert(ignore_permissions=True)
    
    # Create assignment with proper JSON formatting
    assign({
        "assign_to": [assigned_to],
        "doctype": "Event",
        "name": event.name,
        "description": description
    })
    
    return event.name

@frappe.whitelist()
def complete_activity(activity_type, activity_id, completion_note):
    """Complete a task or event with a completion note"""
    if not frappe.has_permission(activity_type, "write", activity_id):
        frappe.throw(_("Not allowed to complete this activity"), frappe.PermissionError)

    doc = frappe.get_doc(activity_type, activity_id)
    
    # Set appropriate status based on doctype
    if activity_type == "ToDo":
        doc.status = "Closed"
        doc.description += "\n\nCompletion Note: " + completion_note
    else:  # Event
        doc.status = "Completed"
        doc.description = (doc.description or "") + "\n\nCompletion Note: " + completion_note
    
    doc.save(ignore_permissions=True)
    return doc.name


import json
import frappe
from collections import defaultdict



from frappe.utils import today, add_months, formatdate
from datetime import datetime

import frappe

@frappe.whitelist()
def get_next_opportunity_counter(prefix):
    """
    prefix example: 2026-NOR-BRA
    returns: 001, 002 ...
    """
    # Naming Series style string
    series = f"{prefix}-.###"

    return frappe.model.naming.make_autoname(series).split('-')[-1]

@frappe.whitelist()
def get_deal_metrics(filters=None):
	try:
		if isinstance(filters, str):
			filters = json.loads(filters)
		filters = filters or {}

		# Apply dashboard scope
		scope = get_dashboard_scope()
		if scope.get("type") and scope.get("value"):
			if scope["type"] == "region" and not filters.get("region"):
				filters["region"] = scope["value"]
			elif scope["type"] == "branch" and not filters.get("branch"):
				filters["branch"] = scope["value"]

		base_filters = {"docstatus": ["!=", 2]}

		# Handle multi-select industry filter
		if filters.get("industry"):
			industries = filters["industry"]
			if isinstance(industries, str):
				# Split comma-separated values from frontend
				industries = [i.strip() for i in industries.split(",") if i.strip()]
			if industries:
				base_filters["industry"] = ["in", industries]

		# Handle multi-select region filter
		if filters.get("region"):
			regions = filters["region"]
			if isinstance(regions, str):
				# Split comma-separated values from frontend
				regions = [r.strip() for r in regions.split(",") if r.strip()]
			if regions:
				base_filters["region"] = ["in", regions]

		# Handle multi-select branch filter
		if filters.get("branch"):
			branches = filters["branch"]
			if isinstance(branches, str):
				# Split comma-separated values from frontend
				branches = [b.strip() for b in branches.split(",") if b.strip()]
			if branches:
				base_filters["branch"] = ["in", branches]

		# Handle date range filters
		if filters.get("date_range"):
			date_range = filters["date_range"]
			if date_range == "Last Month":
				base_filters["creation"] = [">=", add_months(today(), -1)]
			elif date_range == "Last Quarter":
				base_filters["creation"] = [">=", add_months(today(), -3)]
			elif date_range == "Last 6 Months":
				base_filters["creation"] = [">=", add_months(today(), -6)]
			elif date_range == "Last Year":
				base_filters["creation"] = [">=", add_months(today(), -12)]
		
		# Handle custom date range
		elif filters.get("from_date") or filters.get("to_date"):
			if filters.get("from_date") and filters.get("to_date"):
				base_filters["creation"] = ["between", [filters["from_date"], filters["to_date"]]]
			elif filters.get("from_date"):
				base_filters["creation"] = [">=", filters["from_date"]]
			elif filters.get("to_date"):
				base_filters["creation"] = ["<=", filters["to_date"]]

		frappe.log_error(f"Deal Metrics Filters Applied: {base_filters}", "Debug Deal Metrics")

		# Get deals
		deals = frappe.get_all(
			"CRM Deal",
			filters=base_filters,
			fields=[
				"name", "status", "annual_revenue", "creation", 
				"customer", "customer_name", "industry", "region", 
				"branch", "amc_expiry_date", "warranty_expiry_date",
				"parent_vertical"
			]
		)

		total_value = sum(float(d.annual_revenue or 0) for d in deals)
		total_deals = len(deals)

		# Calculate status counts
		status_counts = {}
		for d in deals:
			status = d.status or "New"
			status_counts[status] = status_counts.get(status, 0) + 1

		# Calculate win rate
		won_deals = len([d for d in deals if d.status == "Won/Award"])
		win_rate = (won_deals / total_deals * 100) if total_deals else 0

		# Generate trend data by month
		trend_map = defaultdict(lambda: {"total_deals": 0, "won_deals": 0, "total_value": 0})
		for d in deals:
			month_label = frappe.utils.formatdate(d.creation, "MMM YYYY")
			trend_map[month_label]["total_deals"] += 1
			trend_map[month_label]["total_value"] += float(d.annual_revenue or 0)
			if d.status == "Won/Award":
				trend_map[month_label]["won_deals"] += 1

		# Sort months chronologically
		month_order = sorted(trend_map.keys(), key=lambda x: frappe.utils.getdate(f"01 {x}"))
		trend_data = [{"month": m, **trend_map[m]} for m in month_order]

		# Calculate value growth compared to previous period
		previous_period_filters = {"docstatus": ["!=", 2]}
		
		# Apply same filters to previous period
		if filters.get("industry"):
			industries = filters["industry"]
			if isinstance(industries, str):
				industries = [i.strip() for i in industries.split(",") if i.strip()]
			if industries:
				previous_period_filters["industry"] = ["in", industries]
		
		if filters.get("region"):
			regions = filters["region"]
			if isinstance(regions, str):
				regions = [r.strip() for r in regions.split(",") if r.strip()]
			if regions:
				previous_period_filters["region"] = ["in", regions]
		
		if filters.get("branch"):
			branches = filters["branch"]
			if isinstance(branches, str):
				branches = [b.strip() for b in branches.split(",") if b.strip()]
			if branches:
				previous_period_filters["branch"] = ["in", branches]

		# Set previous period date range
		if filters.get("date_range"):
			date_range = filters["date_range"]
			if date_range == "Last Month":
				previous_period_filters["creation"] = ["between", [add_months(today(), -2), add_months(today(), -1)]]
			elif date_range == "Last Quarter":
				previous_period_filters["creation"] = ["between", [add_months(today(), -6), add_months(today(), -3)]]
			elif date_range == "Last 6 Months":
				previous_period_filters["creation"] = ["between", [add_months(today(), -12), add_months(today(), -6)]]
			elif date_range == "Last Year":
				previous_period_filters["creation"] = ["between", [add_months(today(), -24), add_months(today(), -12)]]
		else:
			# Default to previous 6 months if no date range specified
			previous_period_filters["creation"] = ["between", [add_months(today(), -12), add_months(today(), -6)]]

		previous_deals = frappe.get_all("CRM Deal", filters=previous_period_filters, fields=["annual_revenue"])
		previous_value = sum(float(d.annual_revenue or 0) for d in previous_deals)
		value_growth = ((total_value - previous_value) / previous_value * 100) if previous_value else 0

		# Calculate upcoming opportunities (deals expiring in next 2 months)
		today_date = datetime.strptime(frappe.utils.today(), "%Y-%m-%d").date()
		two_months_later = add_months(today_date, 2)
		
		upcoming_deals = [
			d for d in deals
			if (
				(d.get("amc_expiry_date") and frappe.utils.getdate(d.amc_expiry_date) <= two_months_later) or
				(d.get("warranty_expiry_date") and frappe.utils.getdate(d.warranty_expiry_date) <= two_months_later)
			)
		]
		upcoming_opportunities = len(upcoming_deals)

		# Calculate win rate growth
		previous_won_deals = len([d for d in previous_deals if d.get("status") == "Won/Award"])
		previous_total_deals = len(previous_deals)
		previous_win_rate = (previous_won_deals / previous_total_deals * 100) if previous_total_deals else 0
		win_rate_growth = win_rate - previous_win_rate

		return {
			"total_deals": total_deals,
			"won_deals": won_deals,
			"new_deals": status_counts.get("New", 0),
			"total_value": total_value,
			"total_value_growth": round(value_growth, 2),
			"status_counts": status_counts,
			"win_rate": round(win_rate, 2),
			"win_rate_growth": round(win_rate_growth, 2),
			"upcoming_opportunities": upcoming_opportunities,
			"status_data": [
				{
					"status": status,
					"count": count,
					"value": sum(float(d.annual_revenue or 0) for d in deals if d.status == status)
				}
				for status, count in status_counts.items()
			],
			"trend_data": trend_data
		}

	except Exception as e:
		frappe.log_error(f"Error in get_deal_metrics: {str(e)}", frappe.get_traceback())
		return {
			"total_deals": 0,
			"won_deals": 0,
			"new_deals": 0,
			"total_value": 0,
			"total_value_growth": 0,
			"status_counts": {},
			"win_rate": 0,
			"win_rate_growth": 0,
			"upcoming_opportunities": 0,
			"status_data": [],
			"trend_data": []
		}


@frappe.whitelist()
def get_deal_trend(filters=None):
    """Get trend data for deals, filtered by region/branch based on user scope."""
    frappe.log_error(f"GET DEAL Trend: filter receied: {filters}", "DEBUG")
    try:
        # Parse filters from string if needed
        if isinstance(filters, str):
            filters = json.loads(filters)
        filters = filters or {}

        # Inject region/branch based on current user scope if not already provided
        scope = get_dashboard_scope()
        if scope.get("type") and scope.get("value"):
            if scope["type"] == "region" and not filters.get("region"):
                filters["region"] = scope["value"]
            if scope["type"] == "branch" and not filters.get("branch_name"):
                filters["branch_name"] = scope["value"]


        # --- NEW IMPORTANT CHANGE FOR CUSTOM DATE RANGE ---
        start_date = None
        end_date = None

        if filters.get('date_range') == 'Custom':
            if filters.get('from_date'):
                start_date = filters['from_date']
            if filters.get('to_date'):
                end_date = filters['to_date']
        else:
            date_range = filters.get('date_range') # Get the date range, default is None
            current_today_str = frappe.utils.today()
            # current_today_dt = datetime.strptime(current_today_str, "%Y-%m-%d").date() # Not used directly in current logic, can be removed

            if date_range == 'Last Month':
                start_date = frappe.utils.add_months(current_today_str, -1)
            elif date_range == 'Last Quarter':
                start_date = frappe.utils.add_months(current_today_str, -3)
            elif date_range == 'Last Year':
                start_date = frappe.utils.add_months(current_today_str, -12)
            else: # Default to Last 6 Months if no or invalid date_range
                start_date = frappe.utils.add_months(current_today_str, -6)
            
            end_date = current_today_str # For predefined ranges, end_date is today
        
        # Ensure dates are set, even if filters didn't provide them (e.g., initial load)
        if not start_date:
            start_date = frappe.utils.add_months(frappe.utils.today(), -6)
        if not end_date:
            end_date = frappe.utils.today()

        # Dynamic filters
        where_clauses = ["creation BETWEEN %s AND %s"]
        values = [start_date, end_date]

        # Ensure status is not null (as per original logic)
        where_clauses.append("status IS NOT NULL")
        # frappe.log_error(f"GET DEAL Trend: full where_clauses: {where_clauses}", "DEBUG")

        # --- NEW IMPORTANT CHANGE FOR MULTI-SELECT INDUSTRY, REGION, BRANCH ---
        if filters.get("industry"):
            industries_param = filters["industry"]
            if isinstance(industries_param, str):
                industry_list = [i.strip() for i in industries_param.split(',') if i.strip()]
            else: # Assume it's already a list
                industry_list = industries_param
            
            if industry_list:
                where_clauses.append("industry IN %s")
                values.append(tuple(industry_list)) # Use tuple for SQL IN clause

        if filters.get("region"):
            regions_param = filters["region"]
            if isinstance(regions_param, str):
                region_list = [r.strip() for r in regions_param.split(',') if r.strip()]
            else: # Assume it's already a list
                region_list = regions_param

            if region_list:
                where_clauses.append("region IN %s")
                values.append(tuple(region_list)) # Use tuple for SQL IN clause

        if filters.get("branch_name"):
            branches_param = filters["branch_name"]
            if isinstance(branches_param, str):
                branch_list = [b.strip() for b in branches_param.split(',') if b.strip()]
            else: # Assume it's already a list
                branch_list = branches_param

            if branch_list:
                where_clauses.append("branch IN %s")
                values.append(tuple(branch_list)) # Use tuple for SQL IN clause
        # --- END NEW IMPORTANT CHANGE ---

        where_sql = " AND ".join(where_clauses)

        # frappe.log_error(f"GET DEAL Trend: full where_clauses: {where_clauses}",  "DEBUG")
        

        # SQL Query
        
        trend_data = frappe.db.sql(f"""
            SELECT 
                DATE_FORMAT(creation, '%%Y-%%m') as month_key,
                COUNT(*) as total_deals,
                SUM(CASE WHEN status = 'Won/Award' THEN 1 ELSE 0 END) as won_deals,
                SUM(CASE WHEN status = 'Qualification' THEN 1 ELSE 0 END) as qualification_deals,
                SUM(CASE WHEN status = 'Needs Analysis' THEN 1 ELSE 0 END) as analysis_deals,
                COALESCE(SUM(annual_revenue), 0) as total_value
            FROM `tabCRM Deal`
            WHERE {where_sql}
            GROUP BY DATE_FORMAT(creation, '%%Y-%%m')
            ORDER BY month_key
        """, tuple(values), as_dict=1) or [] # Pass values as a tuple

        # Fill in missing months and format for display
        final_trend_data = []
        
        # Determine the start and end month for the trend data
        # Convert start_date and end_date to datetime objects for month iteration
        # Ensure start_date and end_date are strings before strptime
        start_month_dt = datetime.strptime(str(start_date), "%Y-%m-%d").replace(day=1)
        end_month_dt = datetime.strptime(str(end_date), "%Y-%m-%d")

        current_month_iter = start_month_dt
        trend_map = {d.month_key: d for d in trend_data} # Map existing data by month_key

        while current_month_iter <= end_month_dt:
            month_key_str = frappe.utils.formatdate(current_month_iter, "YYYY-MM")
            display_month = frappe.utils.formatdate(current_month_iter, "MMM YYYY")

            data_for_month = trend_map.get(month_key_str, {
                "month_key": month_key_str,
                "total_deals": 0,
                "won_deals": 0,
                "qualification_deals": 0,
                "analysis_deals": 0,
                "total_value": 0
            })
            
            # Use display_month for the 'month' key in the final output
            data_for_month['month'] = display_month 
            # Remove the internal month_key for the final output if not needed by frontend
            data_for_month.pop('month_key', None) 

            final_trend_data.append(data_for_month)

            # --- FIX FOR TypeError: add_months() got an unexpected keyword argument 'as_datetime' ---
            # Move to the first day of the next month using direct datetime arithmetic
            year = current_month_iter.year
            month = current_month_iter.month
            
            if month == 12: # If current month is December, next month is January of next year
                next_month_dt = datetime(year + 1, 1, 1)
            else: # Otherwise, just increment the month
                next_month_dt = datetime(year, month + 1, 1)
            
            current_month_iter = next_month_dt # Update for next iteration
            # --- END FIX ---

        return final_trend_data

    except Exception as e:
        frappe.log_error("Error in get_deal_trend", frappe.get_traceback())
        return []


@frappe.whitelist()
def get_deal_funnel(date_range=None):
    """
    Get deal funnel data for visualization
    
    Args:
        date_range (str, optional): Date range filter. Defaults to None.
        
    Returns:
        dict: Dictionary containing funnel data
    """
    try:
        # Define date filters based on date_range
        filters = {}
        if date_range:
            today = frappe.utils.today()
            if date_range == "Last Month":
                start_date = frappe.utils.add_months(today, -1)
            elif date_range == "Last Quarter":
                start_date = frappe.utils.add_months(today, -3)
            elif date_range == "Last 6 Months":
                start_date = frappe.utils.add_months(today, -6)
            elif date_range == "Last Year":
                start_date = frappe.utils.add_months(today, -12)
            else:
                start_date = frappe.utils.add_months(today, -6)  # Default to 6 months
                
            filters["creation"] = [">=", start_date]
        
        # Get all deal statuses
        statuses = frappe.get_all("CRM Status", 
                                 filters={"parent_doctype": "CRM Deal"},
                                 fields=["name", "status_name", "color", "sort_order"],
                                 order_by="sort_order")
        
        # Count deals by status
        result = []
        for status in statuses:
            count = frappe.db.count("CRM Deal", 
                                   filters={**filters, "status": status.status_name})
            
            result.append({
                "status": status.status_name,
                "count": count,
                "color": status.color
            })
        
        # Sort by status order
        result.sort(key=lambda x: next((s.sort_order for s in statuses if s.status_name == x["status"]), 999))
        
        return result
    
    except Exception as e:
        frappe.log_error(f"Error in get_deal_funnel: {str(e)}")
        return []

@frappe.whitelist()
def get_recent_activities():
    """
    Get recent activities related to deals, quotations, and contracts
    
    Returns:
        list: List of recent activities with details
    """
    try:
        # Get activities from the last 7 days
        date_filter = ["modified", ">", frappe.utils.add_days(frappe.utils.nowdate(), -7)]
        
        # Get recent deals
        deals = frappe.get_all(
            "CRM Deal",
            filters=[date_filter],
            fields=["name", "status", "modified", "customer", "annual_revenue"]
        )
        
        # Get recent quotations
        quotations = frappe.get_all(
            "CRM Quotation",
            filters=[date_filter],
            fields=["name", "status", "modified", "customer", "grand_total"]
        )
        
        # Get recent contracts
        contracts = frappe.get_all(
            "CRM Contract",
            filters=[date_filter],
            fields=["name", "status", "modified", "customer", "contract_value"]
        )
        
        # Combine and format activities
        activities = []
        
        for deal in deals:
            activities.append({
                "id": deal.name,
                "type": "deal",
                "description": f"Deal {deal.name} for {deal.customer or 'Unknown'} was updated",
                "date": deal.modified,
                "link": f"/app/crm-deal/{deal.name}"
            })
        
        for quotation in quotations:
            activities.append({
                "id": quotation.name,
                "type": "quotation",
                "description": f"Quotation {quotation.name} for {quotation.customer or 'Unknown'} was updated",
                "date": quotation.modified,
                "link": f"/app/crm-quotation/{quotation.name}"
            })
        
        for contract in contracts:
            activities.append({
                "id": contract.name,
                "type": "contract",
                "description": f"Contract {contract.name} for {contract.customer or 'Unknown'} was updated",
                "date": contract.modified,
                "link": f"/app/crm-contract/{contract.name}"
            })
        
        # Sort by date (newest first) and limit to 10 activities
        activities.sort(key=lambda x: x["date"], reverse=True)
        activities = activities[:10]
        
        return {"activities": activities}
    
    except Exception as e:
        frappe.log_error(f"Error in get_recent_activities: {str(e)}")
        return {"activities": []}

@frappe.whitelist()
def get_performance_metrics():
    """
    Calculate performance metrics for the dashboard
    
    Returns:
        dict: Dictionary containing performance metrics
    """
    try:
        today = frappe.utils.today()
        current_month_start = frappe.utils.get_first_day(today)
        current_month_end = frappe.utils.get_last_day(today)
        last_month_start = frappe.utils.get_first_day(frappe.utils.add_months(today, -1))
        last_month_end = frappe.utils.get_last_day(frappe.utils.add_months(today, -1))
        
        # Deal metrics
        current_month_deals = frappe.db.count("CRM Deal", filters={
            "creation": ["between", [current_month_start, current_month_end]]
        }) or 0
        
        last_month_deals = frappe.db.count("CRM Deal", filters={
            "creation": ["between", [last_month_start, last_month_end]]
        }) or 0
        
        current_month_won_deals = frappe.db.count("CRM Deal", filters={
            "creation": ["between", [current_month_start, current_month_end]],
            "status": "Closed Won"
        }) or 0
        
        last_month_won_deals = frappe.db.count("CRM Deal", filters={
            "creation": ["between", [last_month_start, last_month_end]],
            "status": "Closed Won"
        }) or 0
        
        # Calculate deal win rate
        deal_win_rate = 0
        if current_month_deals > 0:
            deal_win_rate = (current_month_won_deals / current_month_deals) * 100
        
        last_month_win_rate = 0
        if last_month_deals > 0:
            last_month_win_rate = (last_month_won_deals / last_month_deals) * 100
        
        win_rate_trend = deal_win_rate - last_month_win_rate
        
        # Pipeline metrics
        pipeline_value = frappe.db.sql("""
            SELECT SUM(annual_revenue) 
            FROM `tabCRM Deal` 
            WHERE status NOT IN ('Closed Lost', 'Cancelled')
        """)[0][0] or 0
        
        last_month_pipeline = frappe.db.sql("""
            SELECT SUM(annual_revenue) 
            FROM `tabCRM Deal` 
            WHERE modified BETWEEN %s AND %s
            AND status NOT IN ('Closed Lost', 'Cancelled')
        """, [last_month_start, last_month_end])[0][0] or 0
        
        pipeline_trend = ((pipeline_value - last_month_pipeline) / (last_month_pipeline or 1)) * 100
        
        # Quotation metrics
        current_month_quotations = frappe.db.count("CRM Quotation", filters={
            "creation": ["between", [current_month_start, current_month_end]]
        }) or 0
        
        current_month_converted = frappe.db.count("CRM Quotation", filters={
            "creation": ["between", [current_month_start, current_month_end]],
            "status": "Converted"
        }) or 0
        
        last_month_quotations = frappe.db.count("CRM Quotation", filters={
            "creation": ["between", [last_month_start, last_month_end]]
        }) or 0
        
        last_month_converted = frappe.db.count("CRM Quotation", filters={
            "creation": ["between", [last_month_start, last_month_end]],
            "status": "Converted"
        }) or 0
        
        # Calculate quotation conversion rate
        quotation_conversion_rate = 0
        if current_month_quotations > 0:
            quotation_conversion_rate = (current_month_converted / current_month_quotations) * 100
        
        last_month_conversion_rate = 0
        if last_month_quotations > 0:
            last_month_conversion_rate = (last_month_converted / last_month_quotations) * 100
        
        conversion_trend = quotation_conversion_rate - last_month_conversion_rate
        
        # Contract metrics
        active_contracts = frappe.db.count("CRM Contract", filters={"status": "Active"}) or 0
        total_contracts = frappe.db.count("CRM Contract") or 0
        
        contract_renewal_rate = 0
        if total_contracts > 0:
            contract_renewal_rate = (active_contracts / total_contracts) * 100
        
        # Helper function to determine status label
        def get_status_label(value, thresholds):
            if value >= thresholds["good"]:
                return "good"
            elif value >= thresholds["average"]:
                return "average"
            else:
                return "poor"
        
        # Helper function to format currency
        def format_currency(value):
            currency = frappe.db.get_default("currency") or "INR"
            return f"{currency} {frappe.utils.fmt_money(value)}"
        
        # Prepare metrics
        metrics = [
            {
                "id": "deal_win_rate",
                "title": "Deal Win Rate",
                "value": round(deal_win_rate, 1),
                "unit": "%",
                "status": get_status_label(deal_win_rate, {"good": 30, "average": 20}),
                "progress": min(deal_win_rate, 100) / 100,
                "trend": win_rate_trend
            },
            {
                "id": "pipeline_value",
                "title": "Pipeline Value",
                "value": pipeline_value,
                "unit": "currency",
                "status": get_status_label(pipeline_value, {"good": 1000000, "average": 500000}),
                "progress": min(pipeline_value / 2000000, 1),
                "trend": pipeline_trend
            },
            {
                "id": "quotation_conversion",
                "title": "Quotation Conversion",
                "value": round(quotation_conversion_rate, 1),
                "unit": "%",
                "status": get_status_label(quotation_conversion_rate, {"good": 50, "average": 30}),
                "progress": min(quotation_conversion_rate, 100) / 100,
                "trend": conversion_trend
            },
            {
                "id": "contract_renewal",
                "title": "Contract Renewal Rate",
                "value": round(contract_renewal_rate, 1),
                "unit": "%",
                "status": get_status_label(contract_renewal_rate, {"good": 70, "average": 50}),
                "progress": min(contract_renewal_rate, 100) / 100,
                "trend": 0
            }
        ]
        
        return {"metrics": metrics}
    
    except Exception as e:
        frappe.log_error(f"Error in get_performance_metrics: {str(e)}")
        return {"metrics": []}

import json
from frappe.utils import today, add_months
from datetime import datetime, timedelta


@frappe.whitelist()
def get_industry_metrics(filters=None):
    """Get industry-wise metrics for deals, filtered by industry, region, and branch (via Project)."""
    try:
        # Parse filters
        if isinstance(filters, str):
            filters = json.loads(filters)
        filters = filters or {}
        print("🔹 Raw filters:", filters)

        # Apply dashboard scope
        scope = get_dashboard_scope()
        if scope.get("type") and scope.get("value"):
            if scope["type"] == "region" and not filters.get("region"):
                filters["region"] = scope["value"]
            elif scope["type"] == "branch" and not filters.get("branch"):
                filters["branch"] = scope["value"]
        print("🔹 Filters after dashboard scope:", filters)

        # Base filters for Deal
        base_filters = {"docstatus": ["!=", 2]}

        # Industry filter
        if filters.get("industry"):
            industries = filters["industry"]
            if isinstance(industries, str):
                industries = [i.strip() for i in industries.split(",") if i.strip()]
            if industries:
                base_filters["industry"] = ["in", industries]
        print("🔹 Base filters after industry:", base_filters)

        # Region & Branch via Project
        project_names_to_filter = []
        project_filters = {"docstatus": ["!=", 2]}
        if filters.get("region"):
            regions = filters["region"]
            if isinstance(regions, str):
                regions = [r.strip() for r in regions.split(",") if r.strip()]
            if regions:
                project_filters["region"] = ["in", regions]
        if filters.get("branch"):
            branches = filters["branch"]
            if isinstance(branches, str):
                branches = [b.strip() for b in branches.split(",") if b.strip()]
            if branches:
                project_filters["branch"] = ["in", branches]  # <-- corrected fieldname
        print("🔹 Project filters:", project_filters)

        if "region" in project_filters or "branch" in project_filters:
            matching_projects = frappe.get_all("Project", filters=project_filters, fields=["name"])
            project_names_to_filter = [p.name for p in matching_projects]
            print("🔹 Matching projects:", project_names_to_filter)
            if not project_names_to_filter:
                print("⚠️ No matching projects found")
                return []  # No matching projects
            base_filters["project"] = ["in", project_names_to_filter]

        # Branch filter directly on Deal
        if filters.get("branch"):
            branches = filters["branch"]
            if isinstance(branches, str):
                branches = [b.strip() for b in branches.split(",") if b.strip()]
            if branches:
                base_filters["branch"] = ["in", branches]

        # Date range filter
        from_date = to_date = None
        current_today = today()
        range_map = {"Last Month": -1, "Last Quarter": -3, "Last 6 Months": -6, "Last Year": -12}

        if filters.get("date_range") == "Custom":
            from_date = filters.get("from_date")
            to_date = filters.get("to_date")
        elif filters.get("date_range") in range_map:
            months = range_map[filters["date_range"]]
            from_date = add_months(current_today, months)
            to_date = current_today

        if from_date and to_date:
            base_filters["creation"] = ["between", [from_date, to_date]]
        elif from_date:
            base_filters["creation"] = [">=", from_date]
        elif to_date:
            base_filters["creation"] = ["<=", to_date]

        print("🔹 Final base filters for Deals:", base_filters)

        # Fetch deals
        deals = frappe.get_all("CRM Deal", filters=base_filters,
                               fields=["industry", "status", "annual_revenue"])
        print(f"🔹 Fetched {len(deals)} deals")

        if not deals:
            return []

        # Aggregate industry metrics
        industry_data = {}
        for deal in deals:
            if not deal.industry:
                continue  # Skip deals without industry
            industry = deal.industry
            if industry not in industry_data:
                industry_data[industry] = {"deal_count": 0, "won_count": 0, "revenue": 0}
            industry_data[industry]["deal_count"] += 1
            if deal.status == "Won/Award":
                industry_data[industry]["won_count"] += 1
            industry_data[industry]["revenue"] += float(deal.annual_revenue or 0)

        # Convert to list and calculate win rate
        result = []
        for industry, vals in industry_data.items():
            win_rate = round((vals["won_count"] / vals["deal_count"] * 100), 2) if vals["deal_count"] > 0 else 0
            result.append({
                "industry": industry,
                "deal_count": vals["deal_count"],
                "revenue": vals["revenue"],
                "win_rate": win_rate
            })

        # Sort by revenue descending and limit top 10
        result = sorted(result, key=lambda x: x["revenue"], reverse=True)[:10]
        print("🔹 Final result:", result)
        return result

    except Exception as e:
        frappe.log_error(f"Error in get_industry_metrics: {str(e)}\n{frappe.get_traceback()}", "Industry Metrics Error")
        return []




@frappe.whitelist()
def send_deal_notification_to_next_role(deal_name, current_level):

    deal = frappe.get_doc("CRM Deal", deal_name)

    next_user = None

    if current_level == "AM" and deal.region:
        next_user = frappe.db.get_value("Region", deal.region, "region_head")

    elif current_level == "RSM":
        next_user = "alok.dave@lge.com"

    if not next_user:
        return

    doc = frappe.new_doc("Notification Log")
    doc.update({
        "type": "Alert",
        "document_type": "CRM Deal",
        "document_name": deal_name,
        "subject": f"Deal {deal_name} marked Not Interested",
        "for_user": next_user,
        "from_user": frappe.session.user,
        "seen": 0
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()



import frappe
import openpyxl
import io
from datetime import datetime


@frappe.whitelist()
def download_all_opportunities_excel(filters=None):
    """Trigger export (auto background for large data)"""

    if isinstance(filters, str):
        import json
        filters = json.loads(filters)

    total_count = frappe.db.count("CRM Deal", filters=filters or {})

    # Always background if > 10k
    frappe.enqueue(
        "crm.fcrm.doctype.crm_deal.crm_deal.generate_large_excel_export",
        queue="long",
        timeout=7200,
        filters=filters,
        total_count=total_count,
        user=frappe.session.user,
    )

    return {
        "status": "processing",
        "message": f"{total_count} records export started"
    }


    # ---------------------------------------------------------
    # MAIN BACKGROUND EXPORT FUNCTION
    # ---------------------------------------------------------
    def generate_large_excel_export(filters=None, total_count=0, user=None):
        frappe.set_user(user or "Administrator")

        try:
            file_info = generate_excel_file(filters, total_count)

            frappe.publish_realtime(
                "task_export_progress",
                {
                    "percent": 100,
                    "file_url": file_info["file_url"]
                },
                user=user,
            )

        except Exception as e:
            frappe.log_error(str(e), "CRM Export Error")

            frappe.publish_realtime(
                "task_export_progress",
                {"error": str(e)},
                user=user,
            )


    # ---------------------------------------------------------
    # OPTIMIZED EXCEL GENERATOR
    # ---------------------------------------------------------
    def generate_excel_file(filters=None, total_count=0):

        # Write-only workbook → HUGE performance boost
        wb = openpyxl.Workbook(write_only=True)
        ws = wb.create_sheet("CRM Deals")

        # Get fields dynamically
        meta = frappe.get_meta("CRM Deal")

        skip_types = {
            "Section Break",
            "Column Break",
            "Tab Break",
            "HTML",
            "Button",
            "Image",
            "Table",
            "Table MultiSelect"
        }

        fields = ["name"]
        headers = ["ID"]

        for df in meta.fields:
            if df.fieldtype not in skip_types:
                fields.append(df.fieldname)
                headers.append(df.label or df.fieldname)

        ws.append(headers)

        # Batch fetch
        page_size = 5000
        start = 0
        processed = 0

        while True:

            deals = frappe.get_all(
                "CRM Deal",
                filters=filters or {},
                fields=fields,
                start=start,
                page_length=page_size,
                order_by="creation desc",
            )

            if not deals:
                break

            for d in deals:
                row = []
                for f in fields:
                    val = d.get(f)

                    if isinstance(val, datetime):
                        val = val.strftime("%Y-%m-%d %H:%M:%S")

                    row.append(val or "")

                ws.append(row)
                processed += 1

            start += page_size

            # Send realtime progress
            frappe.publish_realtime(
                "task_export_progress",
                {
                    "processed": processed,
                    "total": total_count,
                    "percent": int((processed / total_count) * 100)
                    if total_count else 0,
                },
                user=frappe.session.user,
            )

            if len(deals) < page_size:
                break

        # Save file
        bio = io.BytesIO()
        wb.save(bio)
        bio.seek(0)

        filename = f"crm_deals_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": filename,
            "content": bio.getvalue(),
            "is_private": 1,
        })
        file_doc.save(ignore_permissions=True)

        return {
            "file_url": file_doc.file_url,
            "filename": filename,
        }



##### Scheduler 


def set_warranty_out():
    current_date = getdate(today())

    opportunities = frappe.get_all(
        "CRM Deal",
        filters={
            "warranty_expiry_date": ["<", current_date],
            "warranty_expiry_date": ["is", "set"],
            "warranty_amc_status": ["!=", "OUT Warranty"],
        },
        fields=["name"]
    )

    for opp in opportunities:
        frappe.db.set_value(
            "CRM Deal",
            opp.name,
            "warranty_amc_status",
            "OUT Warranty",
            update_modified=False
        )

    frappe.db.commit()

import frappe
from frappe.utils import add_months, nowdate, getdate

def check_warranty_conversion():
    today = getdate(nowdate())

    # Fetch all Opportunity docs where warranty_expiry_date is set
    opportunities = frappe.get_all(
        "CRM Deal",
        filters={
            "warranty_expiry_date": ["is", "set"],
            "deal_type": ["!=", "Lost Warranty Conversion"]
        },
        fields=["name", "warranty_expiry_date"]
    )

    for opp in opportunities:
        expiry_date = getdate(opp.warranty_expiry_date)

        # Add 3 months to warranty expiry
        expiry_plus_3 = add_months(expiry_date, 3)

        # Check if today is greater than expiry + 3 months
        if today > expiry_plus_3:

            # Check if any Contract exists against this Opportunity
            contract_exists = frappe.db.exists(
                "CRM Contract",
                {"from_deal": opp.name}
            )

            if not contract_exists:
                # Update deal_type to Lost warranty conversion
                frappe.db.set_value(
                    "CRM Deal",
                    opp.name,
                    "deal_type",
                    "Lost Warranty Conversion"
                )

                frappe.db.commit()