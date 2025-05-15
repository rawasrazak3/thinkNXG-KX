import frappe
import requests
import json
from frappe.utils import nowdate
from datetime import datetime
from thinknxg_kx.thinknxg_kx.doctype.karexpert_settings.karexpert_settings import fetch_api_details
billing_type = "OP PHARMACY BILLING"
settings = frappe.get_single("Karexpert Settings")
TOKEN_URL = settings.get("token_url")
BILLING_URL = settings.get("billing_url")
facility_id = settings.get("facility_id")

# Fetch row details based on billing type
billing_row = frappe.get_value("Karexpert Table", {"billing_type": billing_type},
                                ["client_code", "integration_key", "x_api_key"], as_dict=True)


headers_token = fetch_api_details(billing_type)
# TOKEN_URL = "https://metro.kxstage.com/external/api/v1/token"
# BILLING_URL = "https://metro.kxstage.com/external/api/v1/integrate"
# headers_token = {
#     "Content-Type": "application/json",
#     # "clientCode": "METRO_THINKNXG_FI",
#     "clientCode": billing_row["client_code"],
#     # "facilityId": "METRO_THINKNXG",
#     "facilityId": facility_id,
#     "messageType": "request",
#     # "integrationKey": "OP_BILLING",
#     "integrationKey": billing_row["integration_key"],
#     # "x-api-key": "kfhgjfgjf0980gdfgfds"
#     "x-api-key": billing_row["x_api_key"]
# }

def get_jwt_token():
    response = requests.post(TOKEN_URL, headers=headers_token)
    if response.status_code == 200:
        return response.json().get("jwttoken")
    else:
        frappe.throw(f"Failed to fetch JWT token: {response.status_code} - {response.text}")

def fetch_op_billing(jwt_token, from_date, to_date):
    headers_billing = {
        "Content-Type": headers_token["Content-Type"],
        # "clientCode": "METRO_THINKNXG_FI",
        "clientCode": headers_token["clientCode"],
        # "integrationKey": "OP_BILLING",
        "integrationKey": headers_token["integrationKey"],
        "Authorization": f"Bearer {jwt_token}"
    }
    payload = {"requestJson": {"FROM": from_date, "TO": to_date}}
    response = requests.post(BILLING_URL, headers=headers_billing, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        frappe.throw(f"Failed to fetch OP Pharmacy Billing data: {response.status_code} - {response.text}")

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

def get_or_create_patient(patient_name,gender):
    existing_patient = frappe.db.exists("Patient", {"patient_name": patient_name})
    if existing_patient:
        return existing_patient
    
    customer = frappe.get_doc({
        "doctype": "Patient",
        "first_name": patient_name,
        "sex": gender
    })
    customer.insert(ignore_permissions=True)
    frappe.db.commit()
    return customer.name


def get_or_create_cost_center(department, sub_department):
    parent_cost_center_name = f"{department}(G)"
    sub_cost_center_name = f"{sub_department}"

    # Check if parent cost center exists, if not, create it
    existing_parent = frappe.db.exists("Cost Center", {"cost_center_name": parent_cost_center_name})
    if not existing_parent:
        parent_cost_center = frappe.get_doc({
            "doctype": "Cost Center",
            "cost_center_name": parent_cost_center_name,
            "parent_cost_center": "METRO HOSPITALS & POLYCLINCS LLC - MH",  # Root level
            "is_group":1,
            "company": frappe.defaults.get_defaults().get("company")
        })
        parent_cost_center.insert(ignore_permissions=True)
        frappe.db.commit()
        existing_parent = parent_cost_center.name

    # Check if sub cost center exists, if not, create it
    existing_sub = frappe.db.exists("Cost Center", {"cost_center_name": sub_cost_center_name})
    if existing_sub:
        return existing_sub

    sub_cost_center = frappe.get_doc({
        "doctype": "Cost Center",
        "cost_center_name": sub_cost_center_name,
        "parent_cost_center": existing_parent,
        "company": frappe.defaults.get_defaults().get("company")
    })
    sub_cost_center.insert(ignore_permissions=True)
    frappe.db.commit()

    return sub_cost_center.name


def create_sales_invoice(billing_data):
    bill_no = billing_data["bill_no"]
    date = billing_data["g_creation_time"]
    datetimes =  date/1000.0
    dt = datetime.fromtimestamp(datetimes)
    formatted_date = dt.strftime('%Y-%m-%d')
    if frappe.db.exists("Sales Invoice", {"custom_bill_no": bill_no,"docstatus": ["!=", 2]}):
        frappe.log(f"Sales Invoice with bill_no {bill_no} already exists.")
        return
    
    customer_name = billing_data["payer_name"]
    patient_name = billing_data["patient_name"]
    gender = billing_data["patient_gender"]
    customer = get_or_create_customer(customer_name)
    patient = get_or_create_patient(patient_name, gender)
    
    
    
    def get_or_create_item(service_name,service_type,service_code):
        """Check if the item exists; if not, create it."""
        item_code = service_code if service_code else service_name
        existing_item = frappe.db.exists("Item", {"item_code": item_code})
        if existing_item:
            return existing_item
        
        # Check if the item group exists, if not create it
        item_group = frappe.db.get_value("Item Group", {"name": service_type})
        if not item_group:
            item_group_doc = frappe.get_doc({
                "doctype": "Item Group",
                "item_group_name": service_type,
                "parent_item_group": "Services",  # Ensure this exists in ERPNext
                "is_group": 0
            })
            item_group_doc.insert(ignore_permissions=True)
            frappe.db.commit()
            item_group = service_type  # Assign the newly created group

        # Create a new item if it doesn't exist
        item = frappe.get_doc({
            "doctype": "Item",
            "item_code": item_code,
            "item_name": service_name,
            "item_group": item_group,  # Ensure you have this group in ERPNext
            "stock_uom": "Nos",
            "is_stock_item":0,
            "is_service_item": 1
        })
        item.insert(ignore_permissions=True)
        frappe.db.commit()

        return item.name

    # Ensure items and cost centers exist before adding them to Sales Invoice
    items = []
    
    for service in billing_data.get("item_details", []):
        
        item_code = get_or_create_item(service["serviceName"],service["serviceType"],service["serviceCode"])  # Ensure item exists
        cost_center = get_or_create_cost_center(service["serviceType"], service["storeName"])
        items.append({
            "item_code": item_code,
            "qty": 1,
            "rate": service["service_selling_amount"],
            "amount": service["service_selling_amount"],
            # "cost_center": cost_center
        })

    
    discount_amount = billing_data["selling_amount"] - billing_data["total_amount"]
    tax_amount = billing_data["tax"]

    # Tax table entry
    taxes = [{
        "charge_type": "On Net Total",
        "account_head": "2370 - VAT 5% - MH" if tax_amount > 0 else "2360 - VAT 0% - MH",  # Change to your tax account
        # "rate": 0 if tax_amount == 0 else (tax_amount / billing_data["total_amount"]) * 100,
        "tax_amount": 0 if tax_amount == 0 else tax_amount,
        "description": "VAT 5%" if tax_amount > 0 else "VAT 0%"
    }]
    
    sales_invoice = frappe.get_doc({
        "doctype": "Sales Invoice",
        "customer": patient,
        "custom_payer": customer,
        "patient": patient,
        "custom_bill": "PHARMACY",
        "set_posting_time":1,
        "posting_date": formatted_date,
        "due_date": formatted_date,
        "custom_bill_no": bill_no,
        "custom_uh_id": billing_data["uhId"],
        "custom_admission_id_": billing_data["admissionId"],
        "custom_admission_type": billing_data["admissionType"],
        "cost_center":cost_center,
        "items": items,
        "discount_amount": discount_amount,
        "total": billing_data["total_amount"],
        "grand_total": billing_data["total_amount"] + tax_amount,        
        "disable_rounded_total":1,
        "taxes": taxes
    })
    
    try:
        frappe.get_doc(sales_invoice).insert(ignore_permissions=True)
        frappe.db.commit()
        # sales_invoice.submit()
        frappe.log(f"Sales Invoice created successfully with bill_no: {bill_no}")
        create_journal_entry(sales_invoice.name, billing_data)

        # create_payment_entry(sales_invoice.name, customer, billing_data)
    except Exception as e:
        frappe.log_error(f"Failed to create Sales Invoice: {e}")
@frappe.whitelist()
def main():
    try:
        jwt_token = get_jwt_token()
        frappe.log("JWT Token fetched successfully.")

        from_date = 1672531200000  
        to_date = 1966962420000    
        billing_data = fetch_op_billing(jwt_token, from_date, to_date)
        frappe.log("OP Billing data fetched successfully.")

        for billing in billing_data.get("jsonResponse", []):
            create_sales_invoice(billing["pharmacy_billing"])

    except Exception as e:
        frappe.log_error(f"Error: {e}")

if __name__ == "__main__":
    main()

def create_journal_entry(sales_invoice_name, billing_data):
    payment_details = billing_data.get("payment_transaction_details", [])
    customer_name = billing_data["payer_name"]
    patient_name = billing_data["patient_name"]
    uhid = billing_data["uhId"]

    authorized_amount = billing_data.get("authorized_amount", 0)
    payer_amounts = billing_data.get("received_amount", 0)
    payer_amount = authorized_amount + payer_amounts

    # Initialize journal entry rows
    je_entries = []
    je_entries.append({
            "account": "Debtors - MH",
            "party_type": "Customer",
            "party": patient_name,
            "debit_in_account_currency": 0,
            "credit_in_account_currency": payer_amount,
            "reference_type": "Sales Invoice",
            "reference_name":sales_invoice_name
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
                # "reference_type": "Sales Invoice",
                # "reference_name":sales_invoice_name
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
            # "reference_type": "Sales Invoice",
            # "reference_name":sales_invoice_name
        })

    # Create Journal Entry if there are valid transactions
    if je_entries:
        je_doc = frappe.get_doc({
            "doctype": "Journal Entry",
            "posting_date": nowdate(),
            "accounts": je_entries,
            "user_remark": f"Pharmacy Sales Invoice: {sales_invoice_name}, Patient: {patient_name} (UHID: {uhid})"
        })
        je_doc.insert(ignore_permissions=True)
        frappe.db.commit()
        je_doc.submit()

        # Link Journal Entry to Sales Invoice
        # frappe.db.set_value("Sales Invoice", sales_invoice_name, "journal_entry", je_doc.name)
        frappe.msgprint(f"Journal Entry {je_doc.name} created successfully.")
