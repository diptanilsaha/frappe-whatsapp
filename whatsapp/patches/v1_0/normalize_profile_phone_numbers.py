import frappe

from whatsapp.whatsapp.doctype.whatsapp_profile.whatsapp_profile import normalize_phone


def execute():
	"""Profiles that normalize onto one number keep the one Meta created (it has a
	`wa_id`), or else the oldest; the other's messages and links move over."""
	profiles = frappe.get_all(
		"WhatsApp Profile",
		fields=["name", "phone_number", "whatsapp_account", "wa_id", "creation"],
		order_by="creation asc",
	)

	survivors: dict[tuple[str, str], str] = {}
	for profile in profiles:
		normalized = _normalize_stored(profile.phone_number)
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
		loser = profile.name
		if profile.wa_id and not frappe.db.get_value("WhatsApp Profile", survivor, "wa_id"):
			survivor, loser = loser, survivor
			survivors[key] = survivor
		_merge(loser, into=survivor, phone_number=normalized)


def _normalize_stored(phone_number: str | None) -> str:
	# A digits-only number was written by Meta's webhook or by the notification channel
	# stripping a plus, so it already carries its country code and must not be read as a
	# national number: Singapore's 6591234567 is also a valid Indian mobile.
	if phone_number and phone_number.strip().isdigit():
		phone_number = f"+{phone_number.strip()}"
	return normalize_phone(phone_number)


def _merge(loser: str, into: str, phone_number: str) -> None:
	frappe.db.set_value("WhatsApp Message", {"to": loser}, "to", into, update_modified=False)
	loser_links = frappe.get_doc("WhatsApp Profile", loser).links
	# deleted before the target is saved, or the target's unique-phone validation finds it
	frappe.delete_doc("WhatsApp Profile", loser, ignore_permissions=True, force=True)

	target = frappe.get_doc("WhatsApp Profile", into)
	target.phone_number = phone_number
	existing = {(link.link_doctype, link.link_name) for link in target.links}
	for link in loser_links:
		if (link.link_doctype, link.link_name) not in existing:
			target.append(
				"links",
				{
					"link_doctype": link.link_doctype,
					"link_name": link.link_name,
					"link_title": link.link_title,
				},
			)
	target.save(ignore_permissions=True)
