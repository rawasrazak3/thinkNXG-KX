app_name = "thinknxg_kx"
app_title = "thinkNXG KX"
app_publisher = "Kreatao - thinkNXG"
app_description = "thinkNXG KX"
app_email = "sales@kreatao.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "thinknxg_kx",
# 		"logo": "/assets/thinknxg_kx/logo.png",
# 		"title": "thinkNXG KX",
# 		"route": "/thinknxg_kx",
# 		"has_permission": "thinknxg_kx.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------
fixtures = [
    {
        "doctype": "Custom Field",
        "filters": [
            ["name", "in", 
             [
                 "Sales Invoice-custom_payer",
                 "Sales Invoice-custom_bill_no",
                 "Sales Invoice-custom_uh_id",
                 "Sales Invoice-custom_admission_id_",
                 "Sales Invoice-custom_admission_type",
                 "Sales Invoice-custom_bill",
                 "Purchase Invoice-custom_bill_number",
                 "Supplier-custom_supplier_code",
                 "Employee-custom_visa_details",
                 "Employee-custom_civil_id",
                 "Employee-custom_column_break_shl8d",
                 "Employee-custom_residency_expiry_date",
                 "Employee-custom_civil_id_expiry_date",
                 "Employee-custom_document_details",
                 "Employee-custom_residency_id",
                 "Employee-custom_medical_insurance",
                 "Employee-custom_work_permit",
                 "Employee-custom_contract",
                 "Employee-custom_column_break_32lxg",
                 "Employee-custom_medical_insurance_expiry_date",
                 "Employee-custom_work_permit__expiry_date",
                 "Employee-custom_contract___expiry_date",
                 "Customer-custom_uh_id"
             ]
            ]
        ]
    }
]


# include js, css files in header of desk.html
# app_include_css = "/assets/thinknxg_kx/css/thinknxg_kx.css"
# app_include_js = "/assets/thinknxg_kx/js/thinknxg_kx.js"

# include js, css files in header of web template
# web_include_css = "/assets/thinknxg_kx/css/thinknxg_kx.css"
# web_include_js = "/assets/thinknxg_kx/js/thinknxg_kx.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "thinknxg_kx/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "thinknxg_kx/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "thinknxg_kx.utils.jinja_methods",
# 	"filters": "thinknxg_kx.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "thinknxg_kx.install.before_install"
# after_install = "thinknxg_kx.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "thinknxg_kx.uninstall.before_uninstall"
# after_uninstall = "thinknxg_kx.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "thinknxg_kx.utils.before_app_install"
# after_app_install = "thinknxg_kx.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "thinknxg_kx.utils.before_app_uninstall"
# after_app_uninstall = "thinknxg_kx.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "thinknxg_kx.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------
# scheduled_jobs = [
#     {
#         "method": "thinknxg_kx.thinknxg_kx.custom_script.create_sales_invoice.main",
#         "frequency": "cron",
#         "cron": "*/5 * * * *"  # Every 5 minutes
#     }
# ]
scheduler_events = {
    "cron": {
        "*/10 * * * *": [
            "thinknxg_kx.thinknxg_kx.custom_script.create_sales_invoice.main",
            "thinknxg_kx.thinknxg_kx.custom_script.create_si_ip.main",
            # "thinknxg_kx.thinknxg_kx.custom_script.advance_deposit.main",
            "thinknxg_kx.thinknxg_kx.custom_script.due_settlement.main",
            "thinknxg_kx.thinknxg_kx.custom_script.create_purchase_invoice.main",

        ]
    }
}
# scheduler_events = {
# 	"all": [
# 		"thinknxg_kx.tasks.all"
# 	],
# 	"daily": [
# 		"thinknxg_kx.tasks.daily"
# 	],
# 	"hourly": [
# 		"thinknxg_kx.tasks.hourly"
# 	],
# 	"weekly": [
# 		"thinknxg_kx.tasks.weekly"
# 	],
# 	"monthly": [
# 		"thinknxg_kx.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "thinknxg_kx.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "thinknxg_kx.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "thinknxg_kx.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["thinknxg_kx.utils.before_request"]
# after_request = ["thinknxg_kx.utils.after_request"]

# Job Events
# ----------
# before_job = ["thinknxg_kx.utils.before_job"]
# after_job = ["thinknxg_kx.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"thinknxg_kx.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

