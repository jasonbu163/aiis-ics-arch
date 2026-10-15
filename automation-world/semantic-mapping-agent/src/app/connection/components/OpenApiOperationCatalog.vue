<!--
File Path: /automation-world/semantic-mapping-agent/src/app/connection/components/OpenApiOperationCatalog.vue
Description: Read-only catalog for operations discovered from the current OpenAPI document.
Main Features:
  - Lists each loaded path and standard HTTP method in a compact expandable form
  - Shows type-placeholder application/json request templates without sending business requests
-->
<script setup lang="ts">
import type { LocaleMessages } from "../../../locales";
import type { BackendOpenApiOperation, BackendOpenApiResult } from "../types";

const props = defineProps<{
  labels: LocaleMessages;
  result: BackendOpenApiResult;
}>();

function operationTitle(operation: BackendOpenApiOperation): string {
  return operation.summary || props.labels.openApiOperationUntitled;
}
</script>

<template>
  <section class="panel openapi-catalog">
    <header class="panel-header">
      <div>
        <p class="panel-kicker">{{ props.labels.openApiCatalogKicker }}</p>
        <h2>{{ props.labels.openApiCatalog }}</h2>
      </div>
      <span class="openapi-catalog-count">
        {{ props.result.operationCount }} {{ props.labels.openApiOperations }}
      </span>
    </header>

    <p class="hint">{{ props.labels.openApiCatalogHint }}</p>

    <div v-if="props.result.operations.length" class="openapi-operation-list">
      <details v-for="operation in props.result.operations" :key="`${operation.method}:${operation.path}`" class="openapi-operation">
        <summary>
          <span class="openapi-operation-route">
            <code class="openapi-method" :data-method="operation.method">{{ operation.method }}</code>
            <code class="openapi-path">{{ operation.path }}</code>
          </span>
          <span class="openapi-operation-title">{{ operationTitle(operation) }}</span>
        </summary>
        <div class="openapi-operation-detail">
          <h3>{{ props.labels.openApiJsonParameters }}</h3>
          <pre v-if="operation.jsonTemplate">{{ operation.jsonTemplate }}</pre>
          <p v-else class="hint">{{ props.labels.openApiNoJsonRequestBody }}</p>
        </div>
      </details>
    </div>
    <p v-else class="hint">{{ props.labels.openApiNoOperations }}</p>
  </section>
</template>
