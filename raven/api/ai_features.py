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
				
				# Normalize the endpoint - ensure it doesn't end with a slash (Azure OpenAI doesn't want trailing slash)
				normalized_endpoint = endpoint.strip().rstrip('/')
				
				client = AzureOpenAI(
					api_key=api_key,
					api_version=api_version,
					azure_endpoint=normalized_endpoint
				)
				
				# For Azure OpenAI, we can't list models like with standard OpenAI
				# Instead, we test the connection by making a simple completion call to the deployment
				try:
					test_response = client.chat.completions.create(
						model=deployment_name,  # Use deployment name as model
						messages=[{"role": "user", "content": "test"}],
						max_tokens=1
					)
					
					# If we get here, the connection and deployment work
					frappe.logger().info(f"Azure AI test connection successful. Deployment '{deployment_name}' is accessible")
					
					# For Azure, we return the deployment name as the available "model"
					# since that's what the bot will use to make API calls
					return {
						"success": True,
						"message": f"Successfully connected to Azure AI. Deployment '{deployment_name}' is accessible.",
						"models": [{"id": deployment_name}],  # Return deployment name as the model
					}
					
				except Exception as deployment_error:
					# More specific error about deployment access
					error_msg = str(deployment_error)
					if "DeploymentNotFound" in error_msg or "404" in error_msg:
						return {"success": False, "message": f"Deployment '{deployment_name}' not found. Please check your deployment name."}
					elif "Unauthorized" in error_msg or "401" in error_msg:
						return {"success": False, "message": "Authentication failed. Please check your API key."}
					elif "Forbidden" in error_msg or "403" in error_msg:
						return {"success": False, "message": "Access forbidden. Please check your API key permissions."}
					else:
						return {"success": False, "message": f"Deployment test failed: {error_msg}"}
						
			except Exception as client_error:
				# Log the specific error for debugging
				frappe.log_error(f"Azure AI test connection failed: {str(client_error)}", "Azure AI Test Connection Error")
				
				error_msg = str(client_error)
				if "InvalidApiKey" in error_msg or "401" in error_msg:
					return {"success": False, "message": "Invalid API key. Please check your Azure OpenAI API key."}
				elif "endpoint" in error_msg.lower():
					return {"success": False, "message": f"Invalid endpoint. Please check your Azure OpenAI endpoint URL: {normalized_endpoint}"}
				else:
					return {"success": False, "message": f"Azure AI connection failed: {error_msg}"}

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
	Note: Azure OpenAI doesn't support listing models like standard OpenAI.
	Instead, we return the configured deployment name as the available "model".
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
		azure_deployment_name = (raven_settings.azure_deployment_name or "").strip()

		if not azure_api_key:
			frappe.log_error("Azure AI models requested but Azure API key is not configured", "Azure OpenAI Models Error")
			return []
		if not azure_endpoint:
			frappe.log_error("Azure AI models requested but Azure endpoint is not configured", "Azure OpenAI Models Error")
			return []
		if not azure_api_version:
			frappe.log_error("Azure AI models requested but Azure API version is not configured", "Azure OpenAI Models Error")
			return []
		if not azure_deployment_name:
			frappe.log_error("Azure AI models requested but Azure deployment name is not configured", "Azure OpenAI Models Error")
			return []

		# For Azure OpenAI, we can't list models like with standard OpenAI
		# Azure uses deployment names instead of model names
		# We return the configured deployment name as the available "model"
		frappe.logger().info(f"Azure OpenAI: Returning deployment '{azure_deployment_name}' as available model")
		return [azure_deployment_name]
		
	except Exception as e:
		# Log the error for debugging
		frappe.log_error(f"Error fetching Azure OpenAI models: {str(e)}", "Azure OpenAI Models Error")
		# Return empty list if Azure AI is not configured or enabled
		return []
