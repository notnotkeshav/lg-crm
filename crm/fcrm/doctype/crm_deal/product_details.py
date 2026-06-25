@frappe.whitelist()
def import_products(opportunity: str, file_url: str):

    if not opportunity or not file_url:
        frappe.throw("Missing parameters")

    doc = frappe.get_doc("Opportunity", opportunity)

    # Clear existing rows
    doc.set("product_details", [])

    file_doc = frappe.get_doc("File", {"file_url": file_url})
    content = file_doc.get_content()

    wb = openpyxl.load_workbook(BytesIO(content), data_only=True)
    ws = wb.active

    headers = [str(c.value).strip() if c.value else "" for c in ws[1]]

    for row in ws.iter_rows(min_row=2, values_only=True):

        if not any(row):
            continue

        row_dict = dict(zip(headers, row))

        doc.append("product_details", {
            "item_code": row_dict.get("Item Code"),
            "item_name": row_dict.get("Item Name"),
            "qty": row_dict.get("Qty") or 1,
            "rate": row_dict.get("Rate") or 0,
            "uom": row_dict.get("UOM"),
            "description": row_dict.get("Description")
        })

    doc.save(ignore_permissions=True)

    return "Products imported successfully"