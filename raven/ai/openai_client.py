import frappe
from frappe import _
from openai import OpenAI


def get_open_ai_client():
	"""
	Get the OpenAI client
	"""

	raven_settings = frappe.get_cached_doc("Raven Settings")

	if not raven_settings.enable_ai_integration:
		frappe.throw(_("AI Integration is not enabled"))

	openai_api_key = raven_settings.get_password("openai_api_key")
	openai_organisation_id = (raven_settings.openai_organisation_id or "").strip()
	openai_project_id = (raven_settings.openai_project_id or "").strip()

	client_args = {"api_key": openai_api_key.strip(), "organization": openai_organisation_id}
	if openai_project_id:
		client_args["project"] = openai_project_id

	return OpenAI(**client_args)


def get_azure_openai_client():
	"""
	Get the Azure OpenAI client
	"""

	raven_settings = frappe.get_cached_doc("Raven Settings")

	if not raven_settings.enable_ai_integration:
		frappe.throw(_("AI Integration is not enabled"))

	if not raven_settings.enable_azure_ai:
		frappe.throw(_("Azure AI is not enabled"))

	azure_api_key = raven_settings.get_password("azure_api_key")
	azure_endpoint = (raven_settings.azure_endpoint or "").strip()
	azure_api_version = (raven_settings.azure_api_version or "").strip()

	if not azure_api_key:
		frappe.throw(_("Azure API key is not configured"))
	if not azure_endpoint:
		frappe.throw(_("Azure endpoint is not configured"))
	if not azure_api_version:
		frappe.throw(_("Azure API version is not configured"))

	client_args = {
		"api_key": azure_api_key.strip(),
		"azure_endpoint": azure_endpoint.strip(),
		"api_version": azure_api_version.strip()
	}

	return OpenAI(**client_args)


def get_openai_models():
	"""
	Get the available OpenAI models
	"""
	client = get_open_ai_client()
	return client.models.list()


def get_azure_openai_models():
	"""
	Get the available Azure OpenAI models
	"""
	client = get_azure_openai_client()
	return client.models.list()


code_interpreter_file_types = [
	"pdf",
	"csv",
	"docx",
	"doc",
	"xlsx",
	"pptx",
	"txt",
	"png",
	"jpg",
	"jpeg",
	"md",
	"json",
	"html",
]

file_search_file_types = ["pdf", "doc", "docx", "json", "txt", "md", "html", "pptx"]
