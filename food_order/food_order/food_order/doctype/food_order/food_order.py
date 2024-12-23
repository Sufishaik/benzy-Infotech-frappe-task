# Copyright (c) 2024, Sufiyan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import frappe
import requests
from datetime import datetime

class FoodOrder(Document):
	pass

@frappe.whitelist()
def fetch_food_orders(month=None):
    if not month:
        month = int(month)
    else:
        month = 11
    
    api_url = "http://canteen.benzyinfotech.com/api/v3/customer/report"
    headers = {
        "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiZWRhNWExODU0OTFhYWE0MmY5YzMyZjRhMTU5MDM1ODk4ZjZiMzMxNWUzZjJjNGRiZDA1N2IyNGE3NTAzMDc3NDBlMjFlYjZmNGE4Mjk0MGUiLCJpYXQiOjE3MDQ4MDA4OTAuODc5OTI1OTY2MjYyODE3MzgyODEyNSwibmJmIjoxNzA0ODAwODkwLjg3OTkyOTA2NTcwNDM0NTcwMzEyNSwiZXhwIjoxNzM2NDIzMjkwLjgzNDkxMjA2MTY5MTI4NDE3OTY4NzUsInN1YiI6IjI2NSIsInNjb3BlcyI6W119.CwDEjlHoRtOXdFcaO6KGGxV202AOA7MMtJVPtKzgLqzTFzUUnDLGBd7PNAtHO2--3YOathM9HOG8hYjY8wjktXZIoCGUR9GWIaEVUxLwFq927CrSf05NuqTBTrJcDeBOjXDvKcSBiJ2A994FC2IunPcdkaZ4jpoaWBIaWueYUbHviYSQuLec3tFcAMg4njrImAlaN9k-QKkHetpdrdbUEX1Wzq4X-1QwuOx7W3W2nbbxaoNgFX1gaabxi00ZO7h5MokGvtqy_gCkS9TYoM74VfxmTyAAczjttLcPqDNiAL_ZJdutDMezw32CZj8G8l8PUL46F_BuaxatZDBUZxeClZh4_0Wvo9GX4zqF2XvHdzZHnwdB414vNCl8itaGW9w7QWbdchPOglhnek32ZmkH0MIqeOBhnAyHo5_WbP0uLd_3qmz3w04nvTbTGV25-QebaxPAsVD0-7Za1sVpqB_FD6yEeliaEzdxl_8gA5IH59uowpfPYgUIjom8NVEASuYsAwb0q3f0jhNRfwg2zmXNenoDunh_dN9l2NRjI2gdZueSMwu6IJLQK46jpn01uG2iQ1xx-pFJAGe_bzSceLsho3dbtabym3tMqi0Ac02xUP9Mn50LdkFJGNVU9jiuHQfyjQirDtGUfya3aIvpJlCGx9Cx99s_4P89uDnOiXy3A1Q",
        "Content-Type": "application/json"
    }
    # print("headers////////////////////",headers)
    
    try:
        payload = {"month": month}
        response = requests.post(
            api_url,
            headers=headers,
            json=payload
        )
        print("response////////////////////",response)
        
        if response.status_code == 200:
            data = response.json()
            print("response////////////////////",data)
            
            process_food_orders(data)
            return {"status": "success", "message": "Food orders fetched successfully"}
        else:
            frappe.log_error(f"API Error: {response.text}", "Food Order Fetch Error")
            return {"status": "error", "message": "Failed to fetch food orders"}
            
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Food Order Fetch Error")
        return {"status": "error", "message": str(e)}

def process_food_orders(data):
    user = data.get("user", {})
    reports = data.get("reports", [])
    
    for report in reports:
        date = report.get("date")
        opt_ins = report.get("opt_ins", {})
        
        if not opt_ins:
            continue
            
      
        fine_amount = calculate_fine(opt_ins)
        
       
        create_update_food_order(user, date, opt_ins, fine_amount)

def calculate_fine(opt_ins):
    fine_per_waste = 100
    pending_count = sum(1 for status in opt_ins.values() if status == "Pending")
    return pending_count * fine_per_waste

def create_update_food_order(user, date, opt_ins, fine_amount):
    existing_order = frappe.get_all(
        "Food Order",
        filters={
            "employee_id": user.get("emp_id"),
            "date": date
        },
        limit=1
    )
    
    order_data = {
        "doctype": "Food Order",
        "employee_id": user.get("emp_id"),
        "employee_name": f"{user.get('f_name')} {user.get('l_name')}".strip(),
        "date": date,
        "breakfast": opt_ins.get("breakfast", "Pending"),
        "lunch": opt_ins.get("lunch", "Pending"),
        "dinner": opt_ins.get("dinner", "Pending"),
        "total_fine": fine_amount
    }
    
    if existing_order:
        doc = frappe.get_doc("Food Order", existing_order[0].name)
        doc.update(order_data)
        doc.save()
    else:
        doc = frappe.get_doc(order_data)
        doc.insert()

