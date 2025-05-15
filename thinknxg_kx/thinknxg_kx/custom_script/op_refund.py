import frappe
import requests
import json
from frappe.utils import nowdate
from datetime import datetime


TOKEN_URL = "https://metro.kxstage.com/external/api/v1/token"
BILLING_URL = "https://metro.kxstage.com/external/api/v1/integrate"

headers_token = {
    "Content-Type": "application/json",
    "clientCode": "METRO_THINKNXG_FI",
    "facilityId": "METRO_THINKNXG",
    "messageType": "request",
    "integrationKey": "OP_BILLING_REFUND",
    "x-api-key": "vgythmc8745tuyt"
}

def get_jwt_token():
    response = requests.post(TOKEN_URL, headers=headers_token)
    if response.status_code == 200:
        return response.json().get("jwttoken")
    else:
        frappe.throw(f"Failed to fetch JWT token: {response.status_code} - {response.text}")

def fetch_op_billing_refund(jwt_token, from_date, to_date):
    headers_billing = {
        "Content-Type": "application/json",
        "clientCode": "METRO_THINKNXG_FI",
        "integrationKey": "OP_BILLING_REFUND",
        "Authorization": f"Bearer {jwt_token}"
    }
    payload = {"requestJson": {"FROM": from_date, "TO": to_date}}
    response = requests.post(BILLING_URL, headers=headers_billing, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        frappe.throw(f"Failed to fetch OP Refund data: {response.status_code} - {response.text}")

def create_sales_invoice_return(billing_data):
    # op_refund = billing_data.get("op_refund", {})
    
    # Extract required fields from API response
    bill_no = billing_data.get("bill_no")
    patient_refund_amount = billing_data.get("patient_refund_amount", 0.0)
    g_creation_time = billing_data.get("g_modify_time")
    payment_mode = billing_data.get("payment_transaction_details", [{}])[0].get("payment_mode_code", "cash")
    item_details = billing_data.get("item_details", [])

    # Convert Epoch time to readable date
    return_date = datetime.fromtimestamp(g_creation_time / 1000).strftime('%Y-%m-%d')

    # Fetch the Sales Invoice
    sales_invoice = frappe.get_doc("Sales Invoice", {"custom_bill_no": bill_no})
    if not sales_invoice:
        frappe.throw(f"Sales Invoice {bill_no} not found.")

    # Create Sales Invoice Return
    return_invoice = frappe.new_doc("Sales Invoice")
    return_invoice.update({
        "customer": sales_invoice.customer,
        "custom_payer": sales_invoice.custom_payer,
        "posting_date": nowdate(),
        "is_return": 1,
        "return_against": sales_invoice.name,
        "items": [],
        "payment_mode": payment_mode
    })

    # Add refunded items
    for item in item_details:
        service_name = item.get("serviceName")
        service_code = item.get("serviceCode")
        quantity = item.get("quantity", 1)
        rate = item.get("service_mrp", 0.0)

        return_invoice.append("items", {
            "item_code": service_code if service_code else service_name,
            "qty": -quantity,
            "rate": rate,
            "amount": rate * -quantity
        })

    # Set total refund amount
    return_invoice.set("grand_total", -patient_refund_amount)
    return_invoice.set("outstanding_amount", -patient_refund_amount)

    # Save and submit return invoice
    return_invoice.insert()
    # return_invoice.submit()

    return f"Sales Invoice Return {return_invoice.name} created successfully."

def main():
    try:
        jwt_token = get_jwt_token()
        frappe.log("JWT Token fetched successfully.")

        from_date = 1672531200000  
        to_date = 1743013620000    
        billing_data = fetch_op_billing_refund(jwt_token, from_date, to_date)
        frappe.log("OP Billing refund data fetched successfully.")

        for billing in billing_data.get("jsonResponse", []):
            create_sales_invoice_return(billing["op_refund"])

    except Exception as e:
        frappe.log_error(f"Error: {e}")

if __name__ == "__main__":
    main()