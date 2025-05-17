import frappe
import requests
import json
from frappe.utils import nowdate
from frappe.utils import getdate
from datetime import datetime


TOKEN_URL = "https://metro.kxstage.com/external/api/v1/token"
BILLING_URL = "https://metro.kxstage.com/external/api/v1/integrate"

headers_token = {
    "Content-Type": "application/json",
    "clientCode": "METRO_THINKNXG_FI",
    "facilityId": "METRO_THINKNXG",
    "messageType": "request",
    "integrationKey": "ADVANCE_DEPOSIT",
    "x-api-key": "dgshf573bnda75"
}

def get_jwt_token():
    response = requests.post(TOKEN_URL, headers=headers_token)
    if response.status_code == 200:
        return response.json().get("jwttoken")
    else:
        frappe.throw(f"Failed to fetch JWT token: {response.status_code} - {response.text}")

def fetch_advance_billing(jwt_token, from_date, to_date):
    headers_billing = {
        "Content-Type": "application/json",
        "clientCode": "METRO_THINKNXG_FI",
        "integrationKey": "ADVANCE_DEPOSIT",
        "Authorization": f"Bearer {jwt_token}"
    }
    payload = {"requestJson": {"FROM": from_date, "TO": to_date}}
    response = requests.post(BILLING_URL, headers=headers_billing, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        frappe.throw(f"Failed to fetch OP Billing data: {response.status_code} - {response.text}")
@frappe.whitelist()
def main():
    try:
        jwt_token = get_jwt_token()
        frappe.log("JWT Token fetched successfully.")

        from_date = 1672531200000  
        to_date = 1966962420000    
        billing_data = fetch_advance_billing(jwt_token, from_date, to_date)
        frappe.log("Advance Billing data fetched successfully.")

        for billing in billing_data.get("jsonResponse", []):
            create_payment_entry(billing["advance"])

    except Exception as e:
        frappe.log_error(f"Error: {e}")

if __name__ == "__main__":
    main()

def create_payment_entry(billing_data):
    try:
        mode_of_payment = billing_data["payment_transaction_details"][0]["payment_mode_display"]

        # Fetch the 'default_account' from Mode of Payment Account (child table)
        mode_of_payment_accounts = frappe.get_all(
            "Mode of Payment Account",
            filters={"parent": mode_of_payment},
            fields=["default_account"],
            limit=1
        )

        if not mode_of_payment_accounts:
            return f"Failed: No default account found for mode of payment {mode_of_payment}"

        paid_to_account = mode_of_payment_accounts[0]["default_account"]

        # Fetch the account currency
        paid_to_account_currency = frappe.db.get_value("Account", paid_to_account, "account_currency")

        if not paid_to_account_currency:
            return f"Failed: No currency found for account {paid_to_account}"

        # Ensure transaction_date_time exists
        transaction_date_time = billing_data["payment_transaction_details"][0].get("transaction_date_time")
        datetimes =  transaction_date_time/1000.0
        dt = datetime.fromtimestamp(datetimes)
        formatted_date = dt.strftime('%Y-%m-%d')
        print("date----", formatted_date)
        if not transaction_date_time:
            return "Failed: Transaction Date is missing."

        # # Convert JSON timestamp (milliseconds) to datetime
        # reference_date = getdate(transaction_date_time)
        # print ("dt====",reference_date)
        # Ensure Reference No is available
        reference_no = billing_data.get("receipt_no")
        if not reference_no:
            return "Failed: Reference No is missing."

        # Check if a Payment Entry already exists
        existing_payment_entry = frappe.get_value(
            "Payment Entry",
            {"reference_no": reference_no, "reference_date": formatted_date},
            "name"
        )

        if existing_payment_entry:
            return f"Skipped: Payment Entry {existing_payment_entry} already exists."
        customer_name = billing_data.get("patient_name")
        customer = get_or_create_customer(customer_name)
        # Create a new Payment Entry
        payment_entry = frappe.get_doc({
            "doctype": "Payment Entry",
            "payment_type": "Receive",
            "posting_date" : formatted_date,
            "party_type": "Customer",
            "party": customer,
            "mode_of_payment": mode_of_payment,
            "paid_amount": billing_data.get("amount"),
            "received_amount": billing_data.get("amount"),
            "reference_no": reference_no,
            "reference_date": formatted_date,
            "target_exchange_rate": 1,
            "paid_to": paid_to_account,
            "paid_to_account_currency": paid_to_account_currency,
        })

        payment_entry.insert()
        frappe.db.commit()
        payment_entry.submit()
        
        return f"Payment Entry {payment_entry.name} created successfully!"
    
    except Exception as e:
        frappe.log_error(f"Error creating Payment Entry: {str(e)}")
        return f"Failed to create Payment Entry: {str(e)}"

def get_or_create_customer(customer_name):
    existing_customer = frappe.db.exists("Customer", {"customer_name": customer_name})
    if existing_customer:
        return existing_customer
    
    customer = frappe.get_doc({
        "doctype": "Customer",
        "customer_name": customer_name,
        "customer_group": "Individual",
        "territory": "All Territories"
    })
    customer.insert(ignore_permissions=True)
    frappe.db.commit()
    return customer.name