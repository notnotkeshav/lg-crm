frappe.ui.form.on("CRM Deal", {
	refresh(frm) {
		// frm.add_web_link(`/crm/deals/${frm.doc.name}`, __("Open in Portal"));

		// Add custom buttons only if document is saved
		if (!frm.doc.__islocal) {
			// Add Create Quotation button
			if (frm.doc.deal_category != "Sales") {
				frm.add_custom_button(__('Create Quotation'), function () {
					frappe.model.open_mapped_doc({
						method: "crm.fcrm.doctype.crm_deal.crm_deal.make_crm_quotation",
						frm: frm
					});

					//  changes --- status 
					// Only advance from Qualification; never move a later-stage deal back
					if (frm.doc.status === "Qualification") {
						frm.set_value("status", "Proposal/Quotation")
						frm.save()
					}
				});


			}
			if (frm.doc.deal_category == "Service") {

				const current_user = frappe.session.user;
				const status = frm.doc.status;

				// ===== GET BRANCH HEAD =====
				if (frm.doc.branch && status !== "Lost by AM" && status !== "Lost by RSM" && status !== "Lost") {

					frappe.db.get_value("Region Branches", frm.doc.branch, "branch_head")
						.then(r => {
							if (r.message && r.message.branch_head === current_user) {
								frm.add_custom_button(__('Not Interested'), () => handle_not_interested(frm, "AM"));
							}
						});
				}

				// ===== GET REGION HEAD =====
				if (frm.doc.region && status === "Lost by AM") {

					frappe.db.get_value("Region", frm.doc.region, "region_head")
						.then(r => {
							if (r.message && r.message.region_head === current_user) {
								frm.add_custom_button(__('Interested'), () => handle_interested(frm));
								frm.add_custom_button(__('Not Interested'), () => handle_not_interested(frm, "RSM"));
							}
						});
				}

				// ===== ALOK FINAL LEVEL =====
				if (current_user === "alok.dave@lge.com" && status === "Lost by RSM") {

					frm.add_custom_button(__('Interested'), () => handle_interested(frm));
					frm.add_custom_button(__('Not Interested'), () => handle_not_interested(frm, "Alok"));
				}
			}

			// if (frm.doc.deal_category == "Service") {
			// 	frappe.role_map = frappe.user_roles || [];

			// 	const isAM = frappe.role_map.includes("AM");
			// 	const isRSM = frappe.role_map.includes("RSM");
			// 	const isAlok = frappe.role_map.includes("Alok");
			// 	const status = frm.doc.status;

			// 	// AM logic
			// 	if (isAM && !["Lost by AM", "Lost by RSM", "Lost"].includes(status)) {
			// 		frm.add_custom_button(__('Not Interested'), () => handle_not_interested(frm, "AM"));
			// 	}

			// 	// RSM logic
			// 	if (isRSM && status === "Lost by AM") {
			// 		frm.add_custom_button(__('Interested'), () => handle_interested(frm, "RSM"));
			// 		frm.add_custom_button(__('Not Interested'), () => handle_not_interested(frm, "RSM"));
			// 	}

			// 	// Alok logic
			// 	if (isAlok && status === "Lost by RSM") {
			// 		frm.add_custom_button(__('Interested'), () => handle_interested(frm, "Alok"));
			// 		frm.add_custom_button(__('Not Interested'), () => handle_not_interested(frm, "Alok"));
			// 	}




			// 	// Add Task and Follow Up buttons outside Create dropdown
			// 	if (!["Won/Award"].includes(frm.doc.status)) {

			// 		frm.add_custom_button(__('Add Task'), function () {
			// 			check_pending_activities(frm, 'ToDo').then(has_pending => {
			// 				if (has_pending) {
			// 					frappe.show_alert({
			// 						message: __('Please complete pending tasks before creating a new one'),
			// 						indicator: 'red'
			// 					});
			// 					return;
			// 				}
			// 				show_task_dialog(frm);
			// 			});
			// 		});

			// 		frm.add_custom_button(__('Add Follow Up'), function () {
			// 			check_pending_activities(frm, 'Event').then(has_pending => {
			// 				if (has_pending) {
			// 					frappe.show_alert({
			// 						message: __('Please complete pending follow-ups before creating a new one'),
			// 						indicator: 'red'
			// 					});
			// 					return;
			// 				}
			// 				show_follow_up_dialog(frm);
			// 			});
			// 		});
			// 	}

			// }

		}


		// Add task list in activities tab
		if (frm.doc.name) {
			show_activity_list(frm);
		}
	},
	onload: function (frm) {
		frm.fields.forEach(field => {
			frm.fields_dict[field.df.fieldname]?.$wrapper?.on('change', function () {
				console.log(`🔄 Field changed: ${field.df.fieldname}`);
				console.log(`Value: ${frm.doc[field.df.fieldname]}`);
			});
		});
		if (frm.is_dirty()) {
			console.log('Form has unsaved changes.');
		}
	},
	region: function (frm) {
		// Make sure required fields exist
		console.log("working")

		// Current year
		const year = frappe.datetime.nowdate().split('-')[0];
		console.log("year", year)
		// First 2 characters
		const north_code = frm.doc.branch.trim().toUpperCase().substring(0, 3);
		console.log("north code", north_code)
		const region_code = frm.doc.region.trim().toUpperCase().substring(0, 5);
		console.log("region code", region_code)
		const prefix = `${year}-${region_code}-${north_code}`;

		// Call server to get next counter
		frappe.call({
			method: "crm.fcrm.doctype.crm_deal.crm_deal.get_next_opportunity_counter",
			args: {
				prefix: prefix
			},
			callback: function (r) {
				if (r.message) {
					console.log("r", r)
					frm.set_value(
						'opportunity_id',
						`${prefix}-${r.message}`
					);
				}
			}
		});
	},
	validate: function (frm) {
		console.log("working");

		// Current date
		const today = frappe.datetime.nowdate(); // YYYY-MM-DD
		const [year, month] = today.split('-');

		console.log("year", year);
		console.log("month", month);

		// Branch code (first 3 letters)
		const north_code = frm.doc.branch
			?.trim()
			.toUpperCase()
			.substring(0, 3);

		// Region code (first 5 letters)
		const region_code = frm.doc.region
			?.trim()
			.toUpperCase()
			.substring(0, 5);

		if (!north_code || !region_code) return;

		// Prefix with year + month
		const prefix = `${year}-${month}-${region_code}-${north_code}`;
		console.log("prefix", prefix);

		// Call server to get next counter
		frappe.call({
			method: "crm.fcrm.doctype.crm_deal.crm_deal.get_next_opportunity_counter",
			args: {
				prefix: prefix
			},
			callback: function (r) {
				if (r.message) {
					frm.set_value(
						'opportunity_id',
						`${prefix}-${r.message}`
					);
				}
			}
		});
	}



});

// function handle_not_interested(frm, role) {
// 	const status_map = {
// 		"AM": "Lost by AM",
// 		"RSM": "Lost by RSM",
// 		"Alok": "Lost"
// 	};
// 	const field_map = {
// 		"AM": "lost_by_am",
// 		"RSM": "lost_by_rsm",
// 		"Alok": "lost_by_alok"
// 	};

// 	frappe.prompt([
// 		{
// 			fieldtype: 'Small Text',
// 			label: 'Enter your reason',
// 			fieldname: 'reason',
// 			reqd: 1
// 		}
// 	], function (values) {
// 		const reason_field = field_map[role];
// 		const new_status = status_map[role];

// 		frm.set_value(reason_field, values.reason);
// 		frm.set_value('status', new_status);

// 		if (role === "Alok") {
// 			frm.set_value('probability', 0);
// 		}

// 		frm.save().then(() => {
// 			frm.clear_custom_buttons();

// 			if (role !== "Alok") {
// 				frappe.call({
// 					method: "crm.fcrm.doctype.crm_deal.crm_deal.send_deal_notification_to_next_role",
// 					args: {
// 						deal_name: frm.doc.name,
// 						current_role: role
// 					}
// 				});
// 			}
// 		});
// 	}, 'Reason for Marking Not Interested', 'Submit');
// }

function handle_not_interested(frm, level) {

	const status_map = {
		"AM": "Lost by AM",
		"RSM": "Lost by RSM",
		"Alok": "Lost"
	};

	const field_map = {
		"AM": "lost_by_am",
		"RSM": "lost_by_rsm",
		"Alok": "lost_by_alok"
	};

	frappe.prompt([
		{
			fieldtype: 'Small Text',
			label: 'Enter your reason',
			fieldname: 'reason',
			reqd: 1
		}
	], function (values) {

		const new_status = status_map[level];
		const reason_field = field_map[level];

		frm.set_value(reason_field, values.reason);
		frm.set_value('status', new_status);

		if (level === "Alok") {
			frm.set_value('probability', 0);
		}

		frm.save().then(() => {
			frm.clear_custom_buttons();

			// Send notification to next level
			frappe.call({
				method: "crm.fcrm.doctype.crm_deal.crm_deal.send_deal_notification_to_next_role",
				args: {
					deal_name: frm.doc.name,
					current_level: level
				}
			});
		});

	}, 'Reason for Marking Not Interested', 'Submit');
}




// function handle_interested(frm, role) {
// 	frm.set_value('status', 'Qualification');
// 	frm.save().then(() => {
// 		frm.clear_custom_buttons();
// 	});
// }

function handle_interested(frm) {
	frm.set_value('status', 'Qualification');
	frm.save().then(() => {
		frm.clear_custom_buttons();
	});
}



async function check_pending_activities(frm, doctype) {
	const response = await frappe.call({
		method: 'crm.fcrm.doctype.crm_deal.crm_deal.check_pending_activities',
		args: {
			deal: frm.doc.name,
			doctype: doctype
		}
	});
	return response.message;
}

function show_activity_list(frm) {
	const wrapper = frm.fields_dict.task_list.wrapper;
	wrapper.innerHTML = `
		<div class="activity-list">
			<div class="activity-filters margin-bottom">
				<div class="row">
					<div class="col-md-3">
						<select class="activity-type-filter form-control">
							<option value="all">All Activities</option>
							<option value="ToDo">Tasks</option>
							<option value="Event">Follow Ups</option>
						</select>
					</div>
					<div class="col-md-3">
						<select class="activity-status-filter form-control">
							<option value="all">All Status</option>
							<option value="Open">Open</option>
							<option value="Completed">Completed</option>
						</select>
					</div>
				</div>
			</div>
			<div class="activity-table-wrapper"></div>
		</div>
	`;

	// Add filter change handlers
	wrapper.querySelector('.activity-type-filter').addEventListener('change', function () {
		refresh_activity_list(frm);
	});
	wrapper.querySelector('.activity-status-filter').addEventListener('change', function () {
		refresh_activity_list(frm);
	});

	refresh_activity_list(frm);
}

function refresh_activity_list(frm) {
	const type_filter = frm.fields_dict.task_list.wrapper.querySelector('.activity-type-filter').value;
	const status_filter = frm.fields_dict.task_list.wrapper.querySelector('.activity-status-filter').value;

	// Convert 'all' to null for activity_type to show both types
	const activity_type = type_filter === 'all' ? null : type_filter;

	frappe.call({
		method: "crm.fcrm.doctype.crm_deal.crm_deal.get_deal_activities",
		args: {
			deal: frm.doc.name,
			activity_type: activity_type,
			status: status_filter
		},
		callback: function (r) {
			if (!r.exc) {
				render_activity_list(frm, r.message || []);
			}
		}
	});
}

function render_activity_list(frm, activities) {
	const wrapper = frm.fields_dict.task_list.wrapper.querySelector('.activity-table-wrapper');

	let html = `<div class="table-responsive">
		<table class="table table-bordered">
			<thead>
				<tr>
					<th>ID</th>
					<th>Type</th>
					<th>Description</th>
					<th>Status</th>
					<th>Due Date</th>
					<th>Assigned To</th>
					<th>Actions</th>
				</tr>
			</thead>
			<tbody>`;

	if (activities.length) {
		activities.forEach(activity => {
			html += `<tr>
				<td> 
				<a href="http://10.101.0.165/app/${activity.doctype}/${activity.name}" target="_blank">
					${activity.name}
				</a>
				</td>
				<td>${activity.activity_type}</td>
				<td>${activity.description || ''}</td>
				<td>${activity.status}</td>
				<td>${activity.date ? frappe.datetime.str_to_user(activity.date) : ''}</td>
				<td>${activity.allocated_to || ''}</td>
				<td>`;

			if (activity.status === "Open") {
				html += `<button class="btn btn-xs btn-complete-activity" 
					data-type="${activity.activity_type}"
					data-id="${activity.name}">Complete</button>`;
			}

			html += `</td></tr>`;
		});
	} else {
		html += `<tr><td colspan="6" class="text-center">No activities found</td></tr>`;
	}

	html += `</tbody></table></div>`;

	wrapper.innerHTML = html;

	// Add handlers
	wrapper.querySelectorAll('.btn-complete-activity').forEach(btn => {
		btn.addEventListener('click', function () {
			const type = this.dataset.type;
			const id = this.dataset.id;
			show_complete_activity_dialog(frm, type, id);
		});
	});

	// Add styles
	if (!document.getElementById('activity-list-styles')) {
		const style = document.createElement('style');
		style.id = 'activity-list-styles';
		style.textContent = `
			.activity-list {
				padding: 15px;
			}
			.activity-filters {
				margin-bottom: 15px;
			}
			.activity-filters .row {
				margin: 0 -8px;
			}
			.activity-filters .col-md-3 {
				padding: 0 8px;
			}
			.table-responsive {
				border-radius: 8px;
				overflow: hidden;
				box-shadow: 0 1px 3px rgba(0,0,0,0.1);
			}
			.table thead th {
				background-color: var(--fg-color);
				font-weight: 600;
			}
			.table td, .table th {
				padding: 0.75rem;
				vertical-align: middle;
			}
			.btn-complete-activity {
				background-color: var(--primary);
				color: white;
				border: none;
				padding: 4px 8px;
				border-radius: 4px;
			}
			.btn-complete-activity:hover {
				background-color: var(--primary-dark);
			}
		`;
		document.head.appendChild(style);
	}
}

function show_task_dialog(frm) {
	const d = new frappe.ui.Dialog({
		title: __('Create Task'),
		fields: [
			{
				fieldname: 'description',
				label: __('Description'),
				fieldtype: 'Small Text',
				reqd: 1
			},
			{
				fieldname: 'date',
				label: __('Due Date'),
				fieldtype: 'Datetime',
				reqd: 1
			},
			{
				fieldname: 'assigned_to',
				label: __('Assign To'),
				fieldtype: 'Link',
				options: 'User',
				reqd: 1,
				default: frm.doc.deal_owner || frappe.session.user
			}
		],
		primary_action_label: __('Create'),
		primary_action(values) {
			console.log(({ values }));
			const now = new Date();
			const selectedDate = frappe.datetime.str_to_obj(values.date);

			// Remove time part (set both to midnight)
			now.setHours(0, 0, 0, 0);
			selectedDate.setHours(0, 0, 0, 0);

			if (selectedDate < now) {
				frappe.throw(__('Due Date cannot be in the past'));
				return;
			}



			frappe.call({
				method: 'crm.fcrm.doctype.crm_deal.crm_deal.create_deal_task',
				args: {
					deal: frm.doc.name,
					description: values.description,
					date: values.date,
					assigned_to: values.assigned_to
				},
				callback: function (r) {
					console.log("response", r)
					if (!r.exc) {
						d.hide();
						// ------changes status on add task 

						refresh_activity_list(frm);
						frm.set_value("status", "Qualification")
						frm.save()
						frappe.show_alert({
							message: __('Task created'),
							indicator: 'green'
						});
					}
				}
			});
		}
	});
	d.show();
}

function show_follow_up_dialog(frm) {
	const d = new frappe.ui.Dialog({
		title: __('Create Follow Up'),
		fields: [
			{
				fieldname: 'subject',
				label: __('Subject'),
				fieldtype: 'Data',
				reqd: 1
			},
			{
				fieldname: 'type',
				label: __('Type'),
				fieldtype: 'Select',
				options: ['Meeting', 'Call', 'Event', 'Sent/Received Email', 'Other'],
				reqd: 1
			},
			{
				fieldname: 'date',
				label: __('Date & Time'),
				fieldtype: 'Datetime',
				reqd: 1
			},
			{
				fieldname: 'description',
				label: __('Description'),
				fieldtype: 'Small Text',
				reqd: 1
			},

			{
				fieldname: 'assigned_to',
				label: __('Assign To'),
				fieldtype: 'Link',
				options: 'User',
				reqd: 1,
				default: frm.doc.deal_owner || frappe.session.user
			}
		],
		primary_action_label: __('Create'),


		primary_action(values) {
			console.log({ values });

			const now = new Date();
			const selectedDate = frappe.datetime.str_to_obj(values.date);

			// Remove time part (set both to midnight)
			now.setHours(0, 0, 0, 0);
			selectedDate.setHours(0, 0, 0, 0);

			if (selectedDate < now) {
				frappe.throw(__('Due Date cannot be in the past'));
				return;
			}

			frappe.call({
				method: 'crm.fcrm.doctype.crm_deal.crm_deal.create_follow_up',
				args: {
					deal: frm.doc.name,
					subject: values.subject,
					type: values.type,
					description: values.description,
					date: values.date,
					assigned_to: values.assigned_to
				},
				callback: function (r) {
					if (!r.exc) {
						d.hide();
						refresh_activity_list(frm);
						frappe.show_alert({
							message: __('Follow up created'),
							indicator: 'green'
						});
						// frm.set_value("status", "Negotiation")
						frm.save()
					}
				}
			});
		}
	});
	d.show();
}

function show_complete_activity_dialog(frm, type, id) {
	const d = new frappe.ui.Dialog({
		title: __(`Complete ${type}`),
		fields: [
			{
				fieldname: 'completion_note',
				label: __('Completion Note'),
				fieldtype: 'Small Text',
				reqd: 1,
				description: __('Please provide details about the completion of this activity')
			}
		],
		primary_action_label: __('Complete'),
		primary_action(values) {
			frappe.call({
				method: 'crm.fcrm.doctype.crm_deal.crm_deal.complete_activity',
				args: {
					activity_type: type,
					activity_id: id,
					completion_note: values.completion_note
				},
				callback: function (r) {
					if (!r.exc) {
						d.hide();
						refresh_activity_list(frm);
						frappe.show_alert({
							message: __(`${type} completed`),
							indicator: 'green'
						});
					}
				}
			});
		}
	});
	d.show();
}
