<script setup lang="ts">
import { computed } from "vue";
import { ErrorMessage, FormControl, Password } from "frappe-ui";
import AppendActionsTable from "./AppendActionsTable.vue";
import type { AccountFormProps } from "./types";

const props = defineProps<AccountFormProps>();

const statusOptions = ["Active", "Inactive"];

const doc = computed(() => props.controller.doc);

const autoReadReceipts = computed({
	get: () => Boolean(doc.value.auto_read_receipts),
	set: (checked: boolean) => {
		doc.value.auto_read_receipts = checked ? 1 : 0;
	},
});

// frappe-ui's `call` puts the server's messages on `messages`; `message` is only the method path.
const errorMessage = computed(() => {
	const error = props.controller.error as { messages?: string[]; message?: string } | null;
	if (!error) return "";
	return error.messages?.length ? error.messages.join("\n") : (error.message ?? String(error));
});
</script>

<template>
	<div class="flex flex-col text-ink-gray-8">
		<div class="flex flex-col gap-4 sm:flex-row">
			<div class="flex min-w-0 flex-1 flex-col gap-4">
				<div>
					<div class="mb-2 text-sm text-ink-gray-5">Account name</div>
					<FormControl
						v-model="doc.account_name"
						type="text"
						placeholder="Enter Account name"
					/>
				</div>
				<div>
					<div class="mb-2 text-sm text-ink-gray-5">Status</div>
					<FormControl v-model="doc.status" type="select" :options="statusOptions" />
				</div>
				<div>
					<div class="mb-2 text-sm text-ink-gray-5">App ID</div>
					<FormControl v-model="doc.app_id" type="text" placeholder="Enter App ID" />
				</div>
			</div>
			<div class="flex min-w-0 flex-1 flex-col gap-4">
				<div>
					<div class="mb-2 text-sm text-ink-gray-5">Business ID</div>
					<FormControl
						v-model="doc.business_id"
						type="text"
						placeholder="Enter Business ID"
					/>
				</div>
				<div>
					<div class="mb-2 text-sm text-ink-gray-5">Phone ID</div>
					<FormControl v-model="doc.phone_id" type="text" placeholder="Enter Phone ID" />
				</div>
				<div>
					<div class="mb-2 text-sm text-ink-gray-5">Access token</div>
					<Password v-model="doc.access_token" placeholder="Enter Access token" />
				</div>
			</div>
		</div>

		<div class="mt-5 border-t border-outline-elevation-2 pt-5">
			<div class="text-lg font-medium text-ink-gray-9">Read Receipts</div>
			<div class="mt-6 flex items-center gap-2">
				<FormControl v-model="autoReadReceipts" type="checkbox" />
				<label
					class="cursor-pointer text-sm text-ink-gray-5"
					@click="autoReadReceipts = !autoReadReceipts"
				>
					Auto Send Read Receipts
				</label>
			</div>
		</div>

		<div class="mt-5 border-t border-outline-elevation-2 pt-5">
			<div class="text-lg font-medium text-ink-gray-9">Append Actions</div>
			<div class="mt-6">
				<div class="mb-2 text-sm text-ink-gray-5">Append Actions</div>
				<AppendActionsTable :controller="controller" />
				<div class="mt-2 text-xs text-ink-gray-5">
					Auto-create documents in linked DocTypes when messages are received or sent
				</div>
			</div>
		</div>

		<ErrorMessage class="mt-4" :message="errorMessage" />
	</div>
</template>
