# Copyright (c) 2024, Sufiyan and contributors
# For license information, please see license.txt

# import frappe


# def execute(filters=None):
# 	columns, data = [], []
# 	return columns, data

import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {
            "label": _("Employee ID"),
            "fieldname": "employee_id",
            "fieldtype": "Link",
            "options": "Employee",
            "width": 110
        },
        {
            "label": _("Employee Name"),
            "fieldname": "employee_name",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": _("Date"),
            "fieldname": "date",
            "fieldtype": "Date",
            "width": 100
        },
        {
            "label": _("Breakfast"),
            "fieldname": "breakfast",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": _("Lunch"),
            "fieldname": "lunch",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": _("Dinner"),
            "fieldname": "dinner",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": _("Total"),
            "fieldname": "total_fine",
            "fieldtype": "Float",
            "width": 120
        }
    ]

def get_filters(filters):
    conditions = []
    
    if filters.get("from_date"):
        conditions.append(["date", ">=", filters.get("from_date")])
    if filters.get("to_date"):
        conditions.append(["date", "<=", filters.get("to_date")])
    if filters.get("employee"):
        conditions.append(["employee_id", "=", filters.get("employee")])
    
    return conditions

def get_data(filters):
    conditions = get_filters(filters)
    
    data = frappe.get_all(
        "Food Order",
        fields=[
            "employee_id",
            "employee_name",
            "date",
            "breakfast",
            "lunch",
            "dinner",
            "total_fine"
        ],
        filters=conditions,
        order_by="date desc"
    )
    
    # Calculate total fines
    total_fines = frappe.get_all(
        "Food Order",
        fields=[
            
            "sum(total_fine) as grand_total"
        ],
        filters=conditions
    )
    
    # Add summary row
    data.append({
            "employee_id": "<b>Total</b>",
            "employee_name": "",
            "date": "",
            "total_fine": total_fines[0].grand_total
        })
    
    return data
