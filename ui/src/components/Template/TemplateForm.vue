<script setup lang="ts">
import { computed, provide } from "vue";
import { ErrorMessage } from "frappe-ui";
import { CommitKey, FormLayout, NO_COMMIT } from "@framework/ui/components/FormLayout";
import { templateLayout } from "./templateLayout";
import { serverErrorMessage } from "../../utils/serverError";
import type { TemplateFormProps } from "./types";

const props = defineProps<TemplateFormProps>();

provide(CommitKey, NO_COMMIT);

const layout = computed(() => templateLayout(props.controller));

const errorMessage = computed(() => serverErrorMessage(props.controller.error));
</script>

<template>
	<div class="flex flex-col text-ink-gray-8">
		<FormLayout v-model:doc="controller.doc" :layout="layout" />
		<ErrorMessage class="mt-4" :message="errorMessage" />
	</div>
</template>
