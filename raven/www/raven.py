import json
import re

import frappe
import frappe.sessions
from frappe import _
from frappe.utils.telemetry import capture

no_cache = 1

SCRIPT_TAG_PATTERN = re.compile(r"\<script[^<]*\</script\>")
CLOSING_SCRIPT_TAG_PATTERN = re.compile(r"</script\>")


def get_context(context):
	csrf_token = frappe.sessions.get_csrf_token()
	# Manually commit the CSRF token here
	frappe.db.commit()  # nosemgrep

	if frappe.session.user == "Guest":
		boot = frappe.website.utils.get_boot_data()
	else:
		try:
			boot = frappe.sessions.get()
		except Exception as e:
			raise frappe.SessionBootFailed from e

	boot["push_relay_server_url"] = frappe.conf.get("push_relay_server_url")

	# add server_script_enabled in boot
	if "server_script_enabled" in frappe.conf:
		enabled = frappe.conf.server_script_enabled
	else:
		enabled = True
	boot["server_script_enabled"] = enabled

	boot_json = frappe.as_json(boot, indent=None, separators=(",", ":"))
	boot_json = SCRIPT_TAG_PATTERN.sub("", boot_json)

	boot_json = CLOSING_SCRIPT_TAG_PATTERN.sub("", boot_json)
	boot_json = json.dumps(boot_json)

	context.update(
		{"build_version": frappe.utils.get_build_version(), "boot": boot_json, "csrf_token": csrf_token}
	)

	# Use local hardcoded values instead of website settings
	context["app_name"] = "Eden"

	# Use local favicon paths - pointing to actual local files
	context["icon_96"] = "raven/public/manifest/favicon-96x96.png"
	context["apple_touch_icon"] = "raven/public/manifest/apple-touch-icon.png"
	context["mask_icon"] = "frontend/public/safari-pinned-tab.svg"
	context["favicon_svg"] = "raven/public/manifest/favicon.svg"
	context["favicon_ico"] = "raven/public/manifest/favicon.ico"
	context["sitename"] = boot.get("sitename")

	if frappe.session.user != "Guest":
		capture("active_site", "raven")

		context[
			"preload_links"
		] = """
			<link rel="preload" href="/api/method/frappe.auth.get_logged_user" as="fetch" crossorigin="use-credentials">
			<link rel="preload" href="/api/method/raven.api.workspaces.get_list" as="fetch" crossorigin="use-credentials">
			<link rel="preload" href="/api/method/raven.api.raven_users.get_list" as="fetch" crossorigin="use-credentials">
			<link rel="preload" href="/api/method/raven.api.raven_channel.get_all_channels?hide_archived=false" as="fetch" crossorigin="use-credentials">
			"""
	else:
		context["preload_links"] = ""

	return context


@frappe.whitelist(methods=["POST"], allow_guest=True)
def get_context_for_dev():
	if not frappe.conf.developer_mode:
		frappe.throw(_("This method is only meant for developer mode"))
	return json.loads(get_boot())


def get_boot():
	try:
		boot = frappe.sessions.get()
	except Exception as e:
		raise frappe.SessionBootFailed from e

	boot["push_relay_server_url"] = frappe.conf.get("push_relay_server_url")
	boot_json = frappe.as_json(boot, indent=None, separators=(",", ":"))
	boot_json = SCRIPT_TAG_PATTERN.sub("", boot_json)

	boot_json = CLOSING_SCRIPT_TAG_PATTERN.sub("", boot_json)
	boot_json = json.dumps(boot_json)

	return boot_json
