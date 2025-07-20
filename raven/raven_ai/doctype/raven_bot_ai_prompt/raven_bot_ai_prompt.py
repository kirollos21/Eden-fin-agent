# Copyright (c) 2024, The Commit Company (Algocode Technologies Pvt. Ltd.) and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class RavenBotAIPrompt(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		is_global: DF.Check
		naming_series: DF.Literal["PR-.#####."]
		prompt: DF.SmallText
		raven_bot: DF.Link | None
	# end: auto-generated types

	pass
