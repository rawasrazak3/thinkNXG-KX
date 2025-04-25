import frappe
import requests
import json
from frappe.utils import nowdate
from frappe.utils import getdate


TOKEN_URL = "https://metro.kxstage.com/external/api/v1/token"
BILLING_URL = "https://metro.kxstage.com/external/api/v1/integrate"

headers_token = {
    "Content-Type": "application/json",
    "clientCode": "METRO_THINKNXG_FI",
    "facilityId": "METRO_THINKNXG",
    "messageType": "request",
    "integrationKey": "BILLING_DUE_SETTLEMENT",
    "x-api-key": "KJHhiwndia2yyt"
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
        "integrationKey": "BILLING_DUE_SETTLEMENT",
        "Authorization": f"Bearer {jwt_token}"
    }
    payload = {"requestJson": {"FROM": from_date, "TO": to_date}}
    response = requests.post(BILLING_URL, headers=headers_billing, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        frappe.throw(f"Failed to due settlement data: {response.status_code} - {response.text}")
@frappe.whitelist()
def main():
    try:
        jwt_token = get_jwt_token()
        frappe.log("JWT Token fetched successfully.")

        from_date = 1672531200000  
        to_date = 1966962420000    
        billing_data = fetch_advance_billing(jwt_token, from_date, to_date)
        frappe.log("Due settlement data fetched successfully.")

        for billing in billing_data.get("jsonResponse", []):
            create_journal_entry(billing["due_settlement"])

    except Exception as e:
        frappe.log_error(f"Error: {e}")

if __name__ == "__main__":
    main()

def create_journal_entry(billing_data):
    try:
        bill_no = billing_data["bill_no"]

        # Fetch the 'default_account' from Mode of Payment Account (child table)
        sales_inv = frappe.get_all(
            "Sales Invoice",
            filters={"custom_bill_no": bill_no},
            fields=["name","customer"],
            limit=1
        )

        if not sales_inv:
            return f"Failed: No sales innvoice with bill no {bill_no}"
        payment_details = billing_data.get("payment_transaction_details", [])
        customer_name = sales_inv[0]["customer"]
        sales_inv_name = sales_inv[0]["name"]


        authorized_amount = billing_data.get("authorized_amount", 0)
        payer_amounts = billing_data.get("received_amount", 0)
        payer_amount = authorized_amount + payer_amounts

        # Initialize journal entry rows
        je_entries = []
        je_entries.append({
                "account": "Debtors - MH",
                "party_type": "Customer",
                "party": customer_name,
                "debit_in_account_currency": 0,
                "credit_in_account_currency": payer_amount,
                "reference_type": "Sales Invoice",
                "reference_name":sales_inv_name
            })
        # Handling Credit Payment Mode
        credit_payment = next((p for p in payment_details if p["payment_mode_code"].lower() == "credit"), None)
        if authorized_amount>0:
            je_entries.append({
                "account": "Debtors - MH",  # Replace with actual debtors account
                "party_type": "Customer",
                "party": customer_name,
                "debit_in_account_currency": authorized_amount,
                "credit_in_account_currency": 0,
            })
            

        # Handling Cash Payment Mode
        for payment in payment_details:
            if payment["payment_mode_code"].lower() == "cash":
                je_entries.append({
                    "account": "Cash - MH",  # Replace with actual cash account
                    "debit_in_account_currency": payment["amount"],
                    "credit_in_account_currency": 0,
                    "reference_type": "Sales Invoice",
                    "reference_name":sales_inv_name
                })

        # Handling Other Payment Modes (UPI, Card, etc.)
        bank_payment_total = sum(
            p["amount"] for p in payment_details if p["payment_mode_code"].lower() not in ["cash", "credit","IP ADVANCE"]
        )
        if bank_payment_total > 0:
            je_entries.append({
                "account": "Bank Accounts - MH",  # Replace with actual bank account
                "debit_in_account_currency": bank_payment_total,
                "credit_in_account_currency": 0,
                "reference_type": "Sales Invoice",
                "reference_name":sales_inv_name
            })

        # Create Journal Entry if there are valid transactions
        if je_entries:
            je_doc = frappe.get_doc({
                "doctype": "Journal Entry",
                "posting_date": nowdate(),
                "accounts": je_entries,
                "user_remark": f"Sales Invoice: {sales_inv_name}"
            })
            je_doc.insert(ignore_permissions=True)
            frappe.db.commit()

            # Link Journal Entry to Sales Invoice
            # frappe.db.set_value("Sales Invoice", sales_invoice_name, "journal_entry", je_doc.name)
            frappe.msgprint(f"Journal Entry {je_doc.name} created successfully.")
    
    except Exception as e:
        frappe.log_error(f"Error creating Payment Entry: {str(e)}")
        return f"Failed to create Payment Entry: {str(e)}"

