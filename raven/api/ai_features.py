import frappe
import openai

from raven.ai.handler import get_variables_for_instructions


@frappe.whitelist()
def get_instruction_preview(instruction):
	"""
	Function to get the rendered instructions for the bot
	"""
	frappe.has_permission(doctype="Raven Bot", ptype="write", throw=True)

	instructions = frappe.render_templateist(instruction, get_variables_for_instructions())
	return instructions


@frappe.whitelist()
def get_saved_prompts(bot: str = None):
	"""
	API to get the saved prompt for a user/bot/global
	"""
	or_filters = [["is_global", "=", 1], ["owner", "=", frappe.session.user]]

	prompts = frappe.get_list(
		"Raven Bot AI Prompt", or_filters=or_filters, fields=["name", "prompt", "is_global", "raven_bot"]
	)

	# Order by ones with the given bot
	prompts = sorted(prompts, key=lambda x: x.get("raven_bot") == bot, reverse=True)

	return prompts


@frappe.whitelist()
def get_open_ai_version():
	"""
	API to get the version of the OpenAI Python client
	"""
	frappe.has_permission(doctype="Raven Bot", ptype="read", throw=True)
	return openai.__version__


@frappe.whitelist()
def get_openai_available_models():
	"""
	API to get the available OpenAI models for assistants
	"""
	frappe.has_permission(doctype="Raven Bot", ptype="read", throw=True)
	from raven.ai.openai_client import get_openai_models

	models = get_openai_models()

	valid_prefixes = ["gpt-4", "gpt-3.5", "o1", "o3-mini"]

	# Model should not contain these words
	invalid_models = ["realtime", "transcribe", "search", "audio"]

	compatible_models = []

	for model in models:
		if any(model.id.startswith(prefix) for prefix in valid_prefixes):
			if not any(word in model.id for word in invalid_models):
				compatible_models.append(model.id)

	return compatible_models


@frappe.whitelist()
def test_llm_configuration(provider: str = "OpenAI", api_url: str = None, api_key: str = None, endpoint: str = None, api_version: str = None, deployment_name: str = None):
	"""
	Test LLM configuration (OpenAI, Azure AI, or Local LLM)
	"""
	frappe.has_permission(doctype="Raven Settings", ptype="write", throw=True)

	try:
		if provider == "Local LLM" and api_url:
			# Test local LLM endpoint
			import requests

			response = requests.get(f"{api_url}/models", timeout=5)
			if response.status_code == 200:
				models = response.json()
				return {
					"success": True,
					"message": f"Successfully connected to {api_url}",
					"models": models.get("data", []),
				}
			else:
				return {
					"success": False,
					"message": f"Failed to connect to {api_url}. Status: {response.status_code}",
				}

		elif provider == "Azure AI":
			# Test Azure AI configuration with provided parameters using old AzureOpenAI approach
			if not api_key:
				return {"success": False, "message": "Azure API key is required"}
			if not endpoint:
				return {"success": False, "message": "Azure endpoint is required"}
			if not api_version:
				return {"success": False, "message": "Azure API version is required"}
			if not deployment_name:
				return {"success": False, "message": "Azure deployment name is required"}

			# Create client with provided parameters using old AzureOpenAI approach
			from openai import AzureOpenAI
			import time
			
			try:
				# Add a small delay to avoid potential rate limiting issues
				time.sleep(0.1)
				
				# Normalize the endpoint - ensure it ends with a slash
				normalized_endpoint = endpoint.strip()
				if not normalized_endpoint.endswith('/'):
					normalized_endpoint += '/'
				
				client = AzureOpenAI(
					api_key=api_key,
					api_version=api_version,
					azure_endpoint=normalized_endpoint
				)
				
				# Try to list models
				models = client.models.list()
				
				# Log successful connection for debugging
				frappe.logger().info(f"Azure AI test connection successful. Found {len(models.data)} models")
				
				return {
					"success": True,
					"message": "Successfully connected to Azure AI",
					"models": [{"id": m.id} for m in models.data[:5]],  # Return first 5 models
				}
			except Exception as client_error:
				# Log the specific error for debugging
				frappe.log_error(f"Azure AI test connection failed: {str(client_error)}", "Azure AI Test Connection Error")
				return {"success": False, "message": f"Azure AI connection failed: {str(client_error)}"}

		elif provider == "OpenAI":
			# Test OpenAI configuration with provided parameters
			if not api_key:
				return {"success": False, "message": "OpenAI API key is required"}

			# Create client with provided parameters
			from openai import OpenAI
			client = OpenAI(api_key=api_key)
			
			# Try to list models
			models = client.models.list()
			return {
				"success": True,
				"message": "Successfully connected to OpenAI",
				"models": [{"id": m.id} for m in models.data[:5]],  # Return first 5 models
			}

	except Exception as e:
		return {"success": False, "message": f"Connection failed: {str(e)}"}


@frappe.whitelist()
def get_azure_openai_available_models():
	"""
	API to get the available Azure OpenAI models for assistants
	"""
	frappe.has_permission(doctype="Raven Bot", ptype="read", throw=True)
	
	try:
		# Get current Raven Settings
		raven_settings = frappe.get_cached_doc("Raven Settings")
		
		if not raven_settings.enable_ai_integration:
			frappe.log_error("Azure AI models requested but AI integration is not enabled", "Azure OpenAI Models Error")
			return []
			
		if not raven_settings.enable_azure_ai:
			frappe.log_error("Azure AI models requested but Azure AI is not enabled", "Azure OpenAI Models Error")
			return []

		azure_api_key = raven_settings.get_password("azure_api_key")
		azure_endpoint = (raven_settings.azure_endpoint or "").strip()
		azure_api_version = (raven_settings.azure_api_version or "").strip()

		if not azure_api_key:
			frappe.log_error("Azure AI models requested but Azure API key is not configured", "Azure OpenAI Models Error")
			return []
		if not azure_endpoint:
			frappe.log_error("Azure AI models requested but Azure endpoint is not configured", "Azure OpenAI Models Error")
			return []
		if not azure_api_version:
			frappe.log_error("Azure AI models requested but Azure API version is not configured", "Azure OpenAI Models Error")
			return []

		# Create Azure OpenAI client
		from openai import AzureOpenAI
		
		# Normalize the endpoint - ensure it ends with a slash
		normalized_endpoint = azure_endpoint
		if not normalized_endpoint.endswith('/'):
			normalized_endpoint += '/'
		
		client = AzureOpenAI(
			api_key=azure_api_key,
			api_version=azure_api_version,
			azure_endpoint=normalized_endpoint
		)

		# Get all models
		models = client.models.list()
		
		# Return all model IDs without filtering
		# Let the user choose which model they want to use
		model_ids = [model.id for model in models.data]
		
		frappe.logger().info(f"Successfully fetched {len(model_ids)} Azure OpenAI models")
		return model_ids
		
	except Exception as e:
		# Log the error for debugging
		frappe.log_error(f"Error fetching Azure OpenAI models: {str(e)}", "Azure OpenAI Models Error")
		# Return empty list if Azure AI is not configured or enabled
		return []
