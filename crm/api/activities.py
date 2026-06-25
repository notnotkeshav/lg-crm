import json
from bs4 import BeautifulSoup
import frappe
from frappe import _
from frappe.desk.form.load import get_docinfo

@frappe.whitelist()
def get_activities(name):
	if frappe.db.exists("CRM Contract", name):
		return get_contract_activities(name)
	elif frappe.db.exists("CRM Quotation", name):
		return get_quotation_activities(name)
	else:
		frappe.throw(_("Document not found"), frappe.DoesNotExistError)

def get_contract_activities(name):
	get_docinfo('', "CRM Contract", name)
	docinfo = frappe.response["docinfo"]
	contract_meta = frappe.get_meta("CRM Contract")
	contract_fields = {field.fieldname: {"label": field.label, "options": field.options} for field in contract_meta.fields}
	avoid_fields = [
		"response_by",
		"sla_creation",
		"sla",
		"first_response_time",
		"first_responded_on",
	]

	doc = frappe.db.get_values("CRM Contract", name, ["creation", "owner"])[0]
	activities = [{
		"activity_type": "creation",
		"creation": doc[0],
		"owner": doc[1],
		"data": "created this contract",
		"is_contract": True,
	}]

	docinfo.versions.reverse()

	for version in docinfo.versions:
		data = json.loads(version.data)
		if not data.get("changed"):
			continue

		if change := data.get("changed")[0]:
			field = contract_fields.get(change[0], None)

			if not field or change[0] in avoid_fields or (not change[1] and not change[2]):
				continue

			field_label = field.get("label") or change[0]
			field_option = field.get("options") or None

			activity_type = "changed"
			data = {
				"field": change[0],
				"field_label": field_label,
				"old_value": change[1],
				"value": change[2],
			}

			if not change[1] and change[2]:
				activity_type = "added"
				data = {
					"field": change[0],
					"field_label": field_label,
					"value": change[2],
				}
			elif change[1] and not change[2]:
				activity_type = "removed"
				data = {
					"field": change[0],
					"field_label": field_label,
					"value": change[1],
				}

		activity = {
			"activity_type": activity_type,
			"creation": version.creation,
			"owner": version.owner,
			"data": data,
			"is_contract": True,
			"options": field_option,
		}
		activities.append(activity)

	for comment in docinfo.comments:
		activity = {
			"name": comment.name,
			"activity_type": "comment",
			"creation": comment.creation,
			"owner": comment.owner,
			"content": comment.content,
			"attachments": get_attachments('Comment', comment.name),
			"is_contract": True,
		}
		activities.append(activity)

	for communication in docinfo.communications + docinfo.automated_messages:
			activity = {
				"activity_type": "communication",
				"communication_type": communication.communication_type,
				"creation": communication.creation,
				"data": {
					"subject": communication.subject,
					"content": communication.content,
					"sender_full_name": communication.sender_full_name,
					"sender": communication.sender,
					"recipients": communication.recipients,
					"cc": communication.cc,
					"bcc": communication.bcc,
					"attachments": get_attachments('Communication', communication.name),
					"read_by_recipient": communication.read_by_recipient,
					"delivery_status": communication.delivery_status,
				},
				"is_contract": True,
			}
			activities.append(activity)

	for attachment_log in docinfo.attachment_logs:
		activity = {
			"name": attachment_log.name,
			"activity_type": "attachment_log",
			"creation": attachment_log.creation,
			"owner": attachment_log.owner,
			"data": parse_attachment_log(attachment_log.content, attachment_log.comment_type),
			"is_contract": True,
		}
		activities.append(activity)

	calls = get_linked_calls(name)
	notes = get_linked_notes(name)
	tasks = get_linked_tasks(name)
	attachments = get_attachments('CRM Contract', name)

	activities.sort(key=lambda x: x["creation"], reverse=True)
	activities = handle_multiple_versions(activities)

	return activities, calls, notes, tasks, attachments

def get_quotation_activities(name):
	get_docinfo('', "CRM Quotation", name)
	docinfo = frappe.response["docinfo"]
	quotation_meta = frappe.get_meta("CRM Quotation")
	quotation_fields = {field.fieldname: {"label": field.label, "options": field.options} for field in quotation_meta.fields}
	avoid_fields = [
		"response_by",
		"sla_creation",
		"sla",
		"first_response_time",
		"first_responded_on",
	]

	doc = frappe.db.get_values("CRM Quotation", name, ["creation", "owner"])[0]
	activities = [{
		"activity_type": "creation",
		"creation": doc[0],
		"owner": doc[1],
		"data": "created this quotation",
		"is_quotation": True,
	}]

	docinfo.versions.reverse()

	for version in docinfo.versions:
		data = json.loads(version.data)
		if not data.get("changed"):
			continue

		if change := data.get("changed")[0]:
			field = quotation_fields.get(change[0], None)

			if not field or change[0] in avoid_fields or (not change[1] and not change[2]):
				continue

			field_label = field.get("label") or change[0]
			field_option = field.get("options") or None

			activity_type = "changed"
			data = {
				"field": change[0],
				"field_label": field_label,
				"old_value": change[1],
				"value": change[2],
			}

			if not change[1] and change[2]:
				activity_type = "added"
				data = {
					"field": change[0],
					"field_label": field_label,
					"value": change[2],
				}
			elif change[1] and not change[2]:
				activity_type = "removed"
				data = {
					"field": change[0],
					"field_label": field_label,
					"value": change[1],
				}

		activity = {
			"activity_type": activity_type,
			"creation": version.creation,
			"owner": version.owner,
			"data": data,
			"is_quotation": True,
			"options": field_option,
		}
		activities.append(activity)

	for comment in docinfo.comments:
		activity = {
			"name": comment.name,
			"activity_type": "comment",
			"creation": comment.creation,
			"owner": comment.owner,
			"content": comment.content,
			"attachments": get_attachments('Comment', comment.name),
			"is_quotation": True,
		}
		activities.append(activity)

	for communication in docinfo.communications + docinfo.automated_messages:
		activity = {
			"activity_type": "communication",
			"communication_type": communication.communication_type,
			"creation": communication.creation,
			"data": {
				"subject": communication.subject,
				"content": communication.content,
				"sender_full_name": communication.sender_full_name,
				"sender": communication.sender,
				"recipients": communication.recipients,
				"cc": communication.cc,
				"bcc": communication.bcc,
				"attachments": get_attachments('Communication', communication.name),
				"read_by_recipient": communication.read_by_recipient,
				"delivery_status": communication.delivery_status,
			},
			"is_quotation": True,
		}
		activities.append(activity)

	for attachment_log in docinfo.attachment_logs:
		activity = {
			"name": attachment_log.name,
			"activity_type": "attachment_log",
			"creation": attachment_log.creation,
			"owner": attachment_log.owner,
			"data": parse_attachment_log(attachment_log.content, attachment_log.comment_type),
			"is_quotation": True,
		}
		activities.append(activity)

	calls = get_linked_calls(name)
	notes = get_linked_notes(name)
	tasks = get_linked_tasks(name)
	attachments = get_attachments('CRM Quotation', name)

	activities.sort(key=lambda x: x["creation"], reverse=True)
	activities = handle_multiple_versions(activities)

	return activities, calls, notes, tasks, attachments

def get_linked_calls(name):
	return frappe.get_all(
		"Call Log",
		filters={"reference_name": name},
		fields=["name", "type", "from", "to", "duration", "recording_url", "creation", "owner", "caller", "receiver"],
	)

def get_linked_notes(name):
	return frappe.get_all(
		"Note",
		filters={"reference_name": name},
		fields=["name", "title", "content", "creation", "owner"],
	)

def get_linked_tasks(name):
	return frappe.get_all(
		"Task",
		filters={"reference_name": name},
		fields=["name", "subject", "status", "priority", "creation", "owner"],
	)

def get_attachments(doctype, name):
	return frappe.get_all(
		"File",
		filters={"attached_to_doctype": doctype, "attached_to_name": name},
		fields=["name", "file_name", "file_url", "is_private", "creation", "owner"],
	)

def parse_attachment_log(content, comment_type):
	if not content:
		return ""
	soup = BeautifulSoup(content, "html.parser")
	if comment_type == "Attachment":
		return soup.get_text()
	return content

def handle_multiple_versions(activities):
	activities_by_field = {}
	for activity in activities:
		if activity["activity_type"] not in ["changed", "added", "removed"]:
			continue
		field = activity["data"]["field"]
		if field not in activities_by_field:
			activities_by_field[field] = []
		activities_by_field[field].append(activity)

	for field, field_activities in activities_by_field.items():
		if len(field_activities) > 1:
			latest_activity = field_activities[0]
			latest_activity["other_versions"] = field_activities[1:]
			for activity in field_activities[1:]:
				activities.remove(activity)

	return activities