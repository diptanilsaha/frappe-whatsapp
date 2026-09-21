import frappe

from whatsapp.whatsapp.doctype.whatsapp_profile.whatsapp_profile import normalize_phone


def execute():
	"""Store every profile's phone number in one canonical form.

	Meta's webhook wrote `919876543210` while a host sending to `+91 98765 43210`
	made a second profile for the same person. Profiles that collapse onto the same
	number keep the one Meta created (it has a `wa_id`), or else the oldest, and the
	other's messages and links move over before it is deleted.
	"""
	profiles = frappe.get_all(
		"WhatsApp Profile",
		fields=["name", "phone_number", "whatsapp_account", "wa_id", "creation"],
		order_by="creation asc",
	)

	survivors: dict[tuple[str, str], str] = {}
	for profile in profiles:
		normalized = normalize_phone(profile.phone_number)
		if not normalized:
			continue
		key = (profile.whatsapp_account, normalized)
		survivor = survivors.get(key)
		if not survivor:
			survivors[key] = profile.name
			if normalized != profile.phone_number:
				frappe.db.set_value(
					"WhatsApp Profile", profile.name, "phone_number", normalized, update_modified=False
				)
			continue
		if profile.wa_id and not frappe.db.get_value("WhatsApp Profile", survivor, "wa_id"):
			_merge(survivor, into=profile.name)
			survivors[key] = profile.name
			frappe.db.set_value(
				"WhatsApp Profile", profile.name, "phone_number", normalized, update_modified=False
			)
		else:
			_merge(profile.name, into=survivor)


def _merge(loser: str, into: str) -> None:
	frappe.db.set_value("WhatsApp Message", {"to": loser}, "to", into, update_modified=False)

	target = frappe.get_doc("WhatsApp Profile", into)
	existing = {(link.link_doctype, link.link_name) for link in target.links}
	for link in frappe.get_doc("WhatsApp Profile", loser).links:
		if (link.link_doctype, link.link_name) not in existing:
			target.append(
				"links",
				{
					"link_doctype": link.link_doctype,
					"link_name": link.link_name,
					"link_title": link.link_title,
				},
			)
	target.flags.ignore_permissions = True
	target.save(ignore_permissions=True)

	frappe.delete_doc("WhatsApp Profile", loser, ignore_permissions=True, force=True)
