// Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

// frappe.ui.form.on("CRM Organization", {
// 	refresh(frm) {

// 	},
// });


// Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
// frappe.ui.form.on('CRM Organization', {
// 	organization_name: function (frm) {
// 		console.log("Triggered organization_name field");
// 		fetch_address(frm);
// 	},
// 	refresh: function (frm) {
// 		console.log("Triggered refresh");
// 		fetch_address(frm);
// 	}
// });

// function fetch_address(frm) {

// 	// Don’t run if the record is still unsaved
// 	if (!frm.doc.name) return;

// 	frappe.call({
// 		method: 'frappe.client.get_list',
// 		args: {
// 			doctype: 'Address',
// 			filters: [
// 				// 1️⃣  match Dynamic Link back to this CRM Organization
// 				['Dynamic Link', 'link_doctype', '=', 'CRM Organization'],
// 				['Dynamic Link', 'link_name', '=', frm.doc.name],   // <- use doc.name!

// 				// 2️⃣  only take Billing addresses
// 				['Address', 'address_type', '=', 'Billing']
// 			],
// 			fields: [
// 				'name', 'address_line1', 'address_line2',
// 				'city', 'state', 'custom_pin_code', 'country'
// 			]
// 		},
// 		callback({ message: addresses }) {

// 			let html = '';

// 			if (addresses && addresses.length) {
// 				// Show the first Billing address (or loop if you prefer)
// 				const addr = addresses[0];
// 				html = `
//                     <div style="margin-bottom:15px;
//                                 border-bottom:1px solid #ccc;
//                                 padding-bottom:10px;">
//                         <strong>${addr.name}</strong><br>
//                         ${addr.address_line1 || ''}<br>
//                         ${addr.address_line2 || ''}<br>
//                         ${addr.city || ''}, ${addr.state || ''}
//                         - ${addr.custom_pin_code || ''}<br>
//                         ${addr.country || ''}
//                     </div>`;
// 			} else {
// 				html = '<p>No billing address found for this customer.</p>';
// 			}

// 			frm.set_df_property('address_html', 'options', html);
// 			frm.refresh_field('address_html');
// 		}
// 	});
// }


frappe.ui.form.on('CRM Organization', {
	refresh(frm) {
		// Only run if document is saved
		if (frm.doc.name) {
			render_address_card(frm);
		} else {
			frm.set_df_property('address_html', 'options', '<p style="padding: 10px;">Please save the form to view and manage addresses.</p>');
		}
	},
	 setup: function(frm) {
        if (frm.fields_dict.region) {
            frm.fields_dict.region.get_query = function () {
                return {
                    filters: {
                        is_sub_region: 1
                    }
                };
            };
        }
    }
});

function render_address_card(frm) {
	if (!frm.doc.name) return;

	frappe.call({
		method: 'frappe.client.get_list',
		args: {
			doctype: 'Address',
			filters: [
				['Dynamic Link', 'link_doctype', '=', 'CRM Organization'],
				['Dynamic Link', 'link_name', '=', frm.doc.name]
				// ⬆️  we removed the address_type filter so ALL types appear
			],
			fields: [
				'name', 'address_type',
				'address_line1', 'address_line2',
				'city', 'state', 'custom_pin_code',
				'country', 'email_id', 'phone'
			],
			limit_page_length: 20
		},
		callback({ message: addresses }) {
			let html = `
                <style>
                    .address-wrapper{display:flex;flex-wrap:wrap;gap:16px;margin-bottom:10px;}
                    .address-card{flex:1 1 300px;max-width:320px;min-width:260px;
                                  background:#fafafa;border:1px solid #ddd;border-radius:8px;
                                  padding:16px;position:relative;box-shadow:0 1px 5px rgba(0,0,0,.05);}
                    .edit-icon{position:absolute;top:10px;right:10px;cursor:pointer;font-size:14px;color:#888;}
                    .edit-icon:hover{color:#007bff;}
                    .addr-type-pill{position:absolute;top:10px;left:10px;
                                    background:#e6e6e6;padding:2px 6px;border-radius:4px;
                                    font-size:11px;font-weight:600;text-transform:uppercase;}
                    .create-address-btn{background:#f0f0f0;padding:8px 16px;border-radius:6px;
                                        border:1px dashed #ccc;cursor:pointer;display:inline-block;
                                        color:#c94b6f;font-weight:500;margin-top:12px;}
                    .create-address-btn:hover{background:#e0e0e0;}
                </style>
                <div class="address-wrapper">
            `;

			if (addresses && addresses.length) {
				addresses.forEach(a => {
					html += `
        <div class="address-card">
            // <div class="addr-type-pill">${a.address_type || 'N/A'}</div>
            <span class="edit-icon" data-name="${a.name}" title="Edit">✏️</span>

            <div style="margin-top: 28px;">
           <div><strong>${a.name} - ${a.address_type || ''}</strong></div>
                <div>${a.address_line1 || ''}</div>
                <div>${a.address_line2 || ''}</div>
                <div>${a.city || ''}, ${a.state || ''} – ${a.custom_pin_code || ''}</div>
                <div>${a.country || ''}</div>
                ${a.email_id ? `<div style="margin-top:6px;"> ${a.email_id}</div>` : ''}
                ${a.phone ? `<div>${a.phone}</div>` : ''}
            </div>
        </div>
    `;
				});

			} else {
				html += `<p>No address found for this customer.</p>`;
			}

			html += `</div>
                     <div><div class="create-address-btn" id="create_new_addr">
                            ➕ Create Address
                         </div></div>`;

			frm.set_df_property('address_html', 'options', html);
			frm.refresh_field('address_html');

			frappe.after_ajax(() => {
				// edit existing
				$(frm.fields_dict.address_html.$wrapper)
					.find('.edit-icon').off('click').on('click', function () {
						frappe.set_route('Form', 'Address', $(this).data('name'));
					});
				// create new
				$('#create_new_addr').off('click').on('click', () => {
					create_billing_address(frm);   // uses your helper
				});
			});
		}
	});
}


function create_billing_address(frm) {
	frappe.model.with_doctype('Address', () => {
		const doc = frappe.model.get_new_doc('Address');

		doc.address_title = frm.doc.organization_name || frm.doc.name;
		doc.address_type = 'Billing';
		doc.email_id = frm.doc.email;
		doc.phone = frm.doc.phone;
		doc.links = [{
			link_doctype: 'CRM Organization',
			link_name: frm.doc.name
		}];

		frappe.set_route('Form', 'Address', doc.name);
	});
}










// For license information, please see license.txt


frappe.ui.form.on("CRM Organization", {
	refresh(frm) {
		// Add portal link
		frm.add_web_link(`/app/customer/${frm.doc.name}`, __("Open in Portal"));

		// Add custom buttons and setup dashboard only if document is saved
		if (!frm.doc.__islocal) {
			// Add Create Deal button
			frm.add_custom_button(('Create AMC Opportunity'), function () {
				frappe.model.open_mapped_doc({
					method: "crm.fcrm.doctype.crm_organization.crm_organization.make_crm_deal",
					frm: frm
				});
			});

			// frm.add_custom_button(('Project'), function () {
			// 	frappe.model.open_mapped_doc({
			// 		method: "crm.fcrm.doctype.crm_organization.crm_organization.make_project",
			// 		frm: frm
			// 	});
			// }, "Create");

			// Setup dashboard if the field exists
			if (frm.fields_dict.dashboard) {
				setup_dashboard(frm);
			}

			// Setup activity list if the field exists
			if (frm.fields_dict.task_list) {
				show_activity_list(frm);
			}
		}
	},

	// validate(frm) {
	// 	console.log("working")
	// 	return frappe.call({
	// 		method: "frappe.client.get_list",
	// 		args: {
	// 			doctype: "CRM Organization",
	// 			filters: {
	// 				organization_name: frm.doc.organization_name,
	// 				project: frm.doc.project,
	// 				branch:frm.doc.branch,
	// 				name: ["!=", frm.doc.name || ""]
	// 			},
	// 			fields: ["name"],
	// 			limit_page_length: 1
	// 		},
	// 		async: false,   // validate stop karne ke liye sync call
	// 		callback: function (r) {
	// 			console.log("response", r)
	// 			if (r.message && r.message.length > 0) {
	// 				frappe.throw(
	// 					`Customer already exists: ${frm.doc.organization_name}`
	// 				);
	// 			}
	// 		}
	// 	});
	// }

});

async function check_pending_activities(frm, doctype) {
	const response = await frappe.call({
		method: 'crm.fcrm.doctype.crm_organization.crm_organization.check_pending_activities',
		args: {
			deal: frm.doc.name,
			doctype: doctype
		}
	});
	return response.message;
}

function show_activity_list(frm) {
	if (!frm.fields_dict.task_list || !frm.fields_dict.task_list.wrapper) {
		return;
	}

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
	const typeFilter = wrapper.querySelector('.activity-type-filter');
	const statusFilter = wrapper.querySelector('.activity-status-filter');

	if (typeFilter) {
		typeFilter.addEventListener('change', () => refresh_activity_list(frm));
	}
	if (statusFilter) {
		statusFilter.addEventListener('change', () => refresh_activity_list(frm));
	}

	refresh_activity_list(frm);
}

function refresh_activity_list(frm) {
	const type_filter = frm.fields_dict.task_list.wrapper.querySelector('.activity-type-filter').value;
	const status_filter = frm.fields_dict.task_list.wrapper.querySelector('.activity-status-filter').value;

	// Convert 'all' to null for activity_type to show both types
	const activity_type = type_filter === 'all' ? null : type_filter;

	frappe.call({
		method: "crm.fcrm.doctype.crm_organization.crm_organization.get_deal_activities",
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
				default: frappe.session.user
			}
		],
		primary_action_label: __('Create'),
		primary_action(values) {
			frappe.call({
				method: 'crm.fcrm.doctype.crm_organization.crm_organization.create_deal_task',
				args: {
					deal: frm.doc.name,
					description: values.description,
					date: values.date,
					assigned_to: values.assigned_to
				},
				callback: function (r) {
					if (!r.exc) {
						d.hide();
						refresh_activity_list(frm);
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
				options: ['Meeting', 'Call', 'Email'],
				reqd: 1
			},
			{
				fieldname: 'description',
				label: __('Description'),
				fieldtype: 'Small Text',
				reqd: 1
			},
			{
				fieldname: 'date',
				label: __('Date & Time'),
				fieldtype: 'Datetime',
				reqd: 1
			},
			{
				fieldname: 'assigned_to',
				label: __('Assign To'),
				fieldtype: 'Link',
				options: 'User',
				reqd: 1,
				default: frappe.session.user
			}
		],
		primary_action_label: __('Create'),
		primary_action(values) {
			frappe.call({
				method: 'crm.fcrm.doctype.crm_organization.crm_organization.create_follow_up',
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
				method: 'crm.fcrm.doctype.crm_organization.crm_organization.complete_activity',
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

function setup_dashboard(frm) {
	// Fetch dashboard data
	frappe.call({
		method: 'frappe.client.get_list',
		args: {
			doctype: 'CRM Contract',
			filters: {
				'customer': frm.doc.name,
				'docstatus': 1
			},
			fields: ['name', 'docstatus', 'expiry_date']
		},
		callback: function (contracts_r) {
			frappe.call({
				method: 'frappe.client.get_list',
				args: {
					doctype: 'CRM Quotation',
					filters: {
						'customer': frm.doc.name,
						'docstatus': 1
					},
					fields: ['name', 'docstatus']
				},
				callback: function (quotes_r) {
					frappe.call({
						method: 'frappe.client.get_list',
						args: {
							doctype: 'CRM Deal',
							filters: {
								'customer_name': frm.doc.name,
								'docstatus': 1
							},
							fields: ['name', 'docstatus']
						},
						callback: function (deals_r) {
							// Get additional details for each document
							Promise.all([
								get_contract_details(contracts_r.message || []),
								get_quotation_details(quotes_r.message || []),
								get_deal_details(deals_r.message || [])
							]).then(([contracts, quotes, deals]) => {
								render_dashboard(frm, {
									contracts,
									quotes,
									deals
								});
							});
						}
					});
				}
			});
		}
	});
}

// Helper functions to get additional details
async function get_contract_details(contracts) {
	const details = await Promise.all(contracts.map(contract =>
		frappe.db.get_value('CRM Contract', contract.name, ['name', 'docstatus', 'expiry_date'])
	));
	return details.map(d => d.message);
}

async function get_quotation_details(quotes) {
	const details = await Promise.all(quotes.map(quote =>
		frappe.db.get_value('CRM Quotation', quote.name, ['name', 'docstatus'])
	));
	return details.map(d => d.message);
}

async function get_deal_details(deals) {
	const details = await Promise.all(deals.map(deal =>
		frappe.db.get_value('CRM Deal', deal.name, ['name', 'docstatus'])
	));
	return details.map(d => d.message);
}

function render_dashboard(frm, data) {
	const today = frappe.datetime.get_today();

	// Process contracts
	const active_contracts = data.contracts.filter(c =>
		c.docstatus === 1 && (!c.expiry_date || c.expiry_date >= today)
	).length;

	const expired_contracts = data.contracts.filter(c =>
		c.docstatus === 1 && c.expiry_date && c.expiry_date < today
	).length;

	// Process quotations
	const quotes_won = data.quotes.filter(q => q.docstatus === 1).length;
	const quotes_lost = data.quotes.filter(q => q.docstatus === 2).length;

	// Process deals
	const deals_won = data.deals.filter(d => d.docstatus === 1).length;
	const deals_lost = data.deals.filter(d => d.docstatus === 2).length;

	// Render dashboard HTML
	const dashboard_html = `
		<div class="dashboard-section">
			<style>
				.dashboard-section {
					padding: 1rem;
					background: #fff;
				}
				.kpi-grid {
					display: grid;
					grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
					gap: 1rem;
					margin-bottom: 1rem;
				}
				.kpi-card {
					padding: 1.25rem;
					border-radius: 0.5rem;
					color: white;
					display: flex;
					flex-direction: column;
					justify-content: space-between;
					min-height: 120px;
					box-shadow: 0 2px 4px rgba(0,0,0,0.1);
					transition: transform 0.2s;
					cursor: pointer;
				}
				.kpi-card:hover {
					transform: translateY(-2px);
					box-shadow: 0 4px 8px rgba(0,0,0,0.15);
				}
				.kpi-title {
					font-size: 0.875rem;
					font-weight: 500;
					opacity: 0.9;
				}
				.kpi-value {
					font-size: 2rem;
					font-weight: 600;
					margin-top: 0.5rem;
				}
				.section-title {
					font-size: 1rem;
					font-weight: 600;
					color: var(--text-color);
					margin: 1rem 0;
				}
				.kpi-card .hover-hint {
					font-size: 0.75rem;
					opacity: 0;
					transition: opacity 0.2s;
					margin-top: 0.5rem;
				}
				.kpi-card:hover .hover-hint {
					opacity: 0.8;
				}
			</style>
			
			<div class="section-title">Contracts Overview</div>
			<div class="kpi-grid">
				<div class="kpi-card" data-action="show_active_contracts" style="background: linear-gradient(135deg, #4CAF50, #45a049);">
					<div class="kpi-title">Active Contracts</div>
					<div class="kpi-value">${active_contracts}</div>
					<div class="hover-hint">Click to view active contracts</div>
				</div>
				<div class="kpi-card" data-action="show_expired_contracts" style="background: linear-gradient(135deg, #f44336, #e53935);">
					<div class="kpi-title">Expired Contracts</div>
					<div class="kpi-value">${expired_contracts}</div>
					<div class="hover-hint">Click to view expired contracts</div>
				</div>
			</div>

			<div class="section-title">Quotations Overview</div>
			<div class="kpi-grid">
				<div class="kpi-card" data-action="show_won_quotations" style="background: linear-gradient(135deg, #2196F3, #1e88e5);">
					<div class="kpi-title">Quotations Won</div>
					<div class="kpi-value">${quotes_won}</div>
					<div class="hover-hint">Click to view won quotations</div>
				</div>
				<div class="kpi-card" data-action="show_lost_quotations" style="background: linear-gradient(135deg, #FF9800, #fb8c00);">
					<div class="kpi-title">Quotations Lost</div>
					<div class="kpi-value">${quotes_lost}</div>
					<div class="hover-hint">Click to view lost quotations</div>
				</div>
			</div>

			<div class="section-title">Deals Overview</div>
			<div class="kpi-grid">
				<div class="kpi-card" data-action="show_won_deals" style="background: linear-gradient(135deg, #9C27B0, #8e24aa);">
					<div class="kpi-title">Deals Won</div>
					<div class="kpi-value">${deals_won}</div>
					<div class="hover-hint">Click to view won deals</div>
				</div>
				<div class="kpi-card" data-action="show_lost_deals" style="background: linear-gradient(135deg, #607D8B, #546e7a);">
					<div class="kpi-title">Deals Lost</div>
					<div class="kpi-value">${deals_lost}</div>
					<div class="hover-hint">Click to view lost deals</div>
				</div>
			</div>
		</div>
	`;

	const $dashboard = $(frm.fields_dict.dashboard.wrapper).html(dashboard_html);

	// Add click handlers for KPI cards
	$dashboard.find('.kpi-card').on('click', function () {
		const action = $(this).data('action');
		handle_kpi_click(frm, action);
	});
}

function handle_kpi_click(frm, action) {
	const filters = {
		customer: frm.doc.name
	};

	switch (action) {
		case 'show_active_contracts':
			frappe.set_route('List', 'CRM Contract', {
				customer: frm.doc.name,
				docstatus: 1,
				expiry_date: ['>=', frappe.datetime.get_today()]
			});
			break;

		case 'show_expired_contracts':
			frappe.set_route('List', 'CRM Contract', {
				customer: frm.doc.name,
				docstatus: 1,
				expiry_date: ['<', frappe.datetime.get_today()]
			});
			break;

		case 'show_won_quotations':
			frappe.set_route('List', 'CRM Quotation', {
				customer: frm.doc.name,
				docstatus: 1,
				status: 'Ordered'
			});
			break;

		case 'show_lost_quotations':
			frappe.set_route('List', 'CRM Quotation', {
				customer: frm.doc.name,
				docstatus: 2,
				status: 'Lost'
			});
			break;

		case 'show_won_deals':
			frappe.set_route('List', 'CRM Deal', {
				customer_name: frm.doc.name,
				docstatus: 1,
				status: 'Closed (Won)'
			});
			break;

		case 'show_lost_deals':
			frappe.set_route('List', 'CRM Deal', {
				customer_name: frm.doc.name,
				docstatus: 2,
				status: 'Closed (Lost)'
			});
			break;
	}
}



// function get_address_by_org_name(frm) {
// 	if (frm.doc.organization_name) {
// 		frappe.call({
// 			method: 'crm.fcrm.doctype.crm_organization.crm_organization.get_address_by_org_name',
// 			args: {
// 				org_name: frm.doc.organization_name
// 			},
// 			callback: function (response) {
// 				console.log("Address HTML Response: ", response.message);
// 				frm.set_df_property('address_html', 'options', response.message || "<div>No address found</div>");
// 				frm.refresh_field('address_html');
// 			}
// 		});
// 	} else {
// 		frm.set_df_property('address_html', 'options', '');
// 		frm.refresh_field('address_html');
// 	}
// }

// frappe.ui.form.on('CRM Organization', {
// 	organization_name: function (frm) {
// 		get_address_by_org_name(frm);
// 	},
// 	onload: function (frm) {
// 		get_address_by_org_name(frm);
// 	}
// });


