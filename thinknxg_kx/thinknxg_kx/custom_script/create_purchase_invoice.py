import frappe
import requests
import json
from frappe.utils import nowdate

TOKEN_URL = "https://metro.kxstage.com/external/api/v1/token"
BILLING_URL = "https://metro.kxstage.com/external/api/v1/integrate"

headers_token = {
    "Content-Type": "application/json",
    "clientCode": "METRO_THINKNXG_MM",
    "facilityId": "METRO_THINKNXG",
    "messageType": "request",
    "integrationKey": "GRN_CREATION_DETAIL",
    "x-api-key": "lkhiuyu7656gfdg"
}

def get_jwt_token():
    response = requests.post(TOKEN_URL, headers=headers_token)
    if response.status_code == 200:
        return response.json().get("jwttoken")
    else:
        frappe.throw(f"Failed to fetch JWT token: {response.status_code} - {response.text}")

def fetch_op_billing(jwt_token, from_date, to_date):
    headers_billing = {
        "Content-Type": "application/json",
        "clientCode": "METRO_THINKNXG_MM",
        "integrationKey": "GRN_CREATION_DETAIL",
        "Authorization": f"Bearer {jwt_token}"
    }
    payload = {"requestJson": {"FROM": from_date, "TO": to_date}}
    response = requests.post(BILLING_URL, headers=headers_billing, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        frappe.throw(f"Failed to fetch GRN data: {response.status_code} - {response.text}")

def get_or_create_customer(patient_name,supplier_code):
    existing_customer = frappe.db.exists("Supplier", {"supplier_name": patient_name})
    if existing_customer:
        return existing_customer
    
    customer = frappe.get_doc({
        "doctype": "Supplier",
        "supplier_name": patient_name,
        "supplier_type": "Company",
        "custom_supplier_code":supplier_code
    })
    customer.insert(ignore_permissions=True)
    frappe.db.commit()
    return customer.name

def create_purchase_invoice(billing_data):
    bill_no = billing_data["billNo"]
    existing_invoice = frappe.db.exists("Purchase Invoice", {"custom_bill_number": bill_no})
    if existing_invoice:
        frappe.log(f"Purchase Invoice with bill_no {bill_no} already exists.")
        return
    
    customer_name = billing_data["supplierName"]
    supplier_code = billing_data["supplierCode"]
    customer = get_or_create_customer(customer_name,supplier_code)
    
    purchase_invoice = {
        "doctype": "Purchase Invoice",
        "supplier": customer,
        "posting_date": nowdate(),
        "due_date": nowdate(),
        "custom_bill_number": bill_no,
        "cost_center": "METRO HOSPITALS & POLYCLINCS LLC - MH",
        "items": [
            {
                "item_code": "purchase_item",
                "qty": 1,
                "rate": billing_data["billAmount"],
                "amount": billing_data["billAmount"]
            }
        ],
        "total": billing_data["billAmount"],
        "grand_total": billing_data["billAmount"]
    }
    
    try:
        frappe.get_doc(purchase_invoice).insert(ignore_permissions=True)
        frappe.db.commit()
        frappe.log(f"Purchase Invoice created successfully with bill_no: {bill_no}")
    except Exception as e:
        frappe.log_error(f"Failed to create Purchase Invoice: {e}")
@frappe.whitelist()
def main():
    try:
        jwt_token = get_jwt_token()
        frappe.log("JWT Token fetched successfully.")

        from_date = 1672531200000  
        to_date = 1966962420000    
        billing_data = fetch_op_billing(jwt_token, from_date, to_date)
        frappe.log("GRN Billing data fetched successfully.")

        for billing in billing_data.get("jsonResponse", []):
            create_purchase_invoice(billing)

    except Exception as e:
        frappe.log_error(f"Error: {e}")

if __name__ == "__main__":
    main()
