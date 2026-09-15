<template>
  <v-card
    class="ai-explanation-panel d-flex flex-column"
    variant="flat"
    height="100%"
  >
    <v-card-title class="d-flex align-center py-2 px-3">
      <v-icon size="small" color="primary" class="mr-2">
        mdi-lightbulb-on-outline
      </v-icon>

      <span class="text-body-2 font-weight-medium">
        AI explanation
      </span>

      <v-spacer />

      <v-btn
        v-if="explanation || error"
        class="back-btn mr-1"
        size="x-small"
        variant="text"
        title="Choose another model"
        @click="reset"
      >
        <v-icon size="small" class="mr-1">
          mdi-swap-horizontal
        </v-icon>
        Change model
      </v-btn>

      <v-btn
        class="close-btn"
        icon
        size="x-small"
        variant="text"
        title="Close"
        @click="$emit('close')"
      >
        <v-icon size="small">
          mdi-close
        </v-icon>
      </v-btn>
    </v-card-title>

    <v-divider />

    <v-card-text class="ai-explanation-content pa-0 flex-grow-1">
      <!-- Off, or no usable model. -->
      <v-alert
        v-if="unavailable"
        class="ma-3"
        type="info"
        variant="tonal"
        density="compact"
      >
        {{ unavailable }}
      </v-alert>

      <!-- Chooser. -->
      <div v-else-if="!loading && !explanation && !error" class="chooser pa-4">
        <p class="text-body-2 mb-1">
          Which model should explain this report?
        </p>
        <p class="text-caption text-grey mb-4">
          The report, its bug path and the surrounding source are sent to the
          provider you choose.
        </p>

        <div class="d-flex flex-column ga-2">
          <v-btn
            v-for="model in models"
            :key="model.id"
            class="model-choice justify-start"
            variant="outlined"
            size="large"
            @click="explain(model.id)"
          >
            <v-icon size="small" class="mr-2">
              mdi-play-circle-outline
            </v-icon>
            <span class="text-none">{{ model.displayName }}</span>
            <v-spacer />
            <v-chip
              v-if="model.id === lastUsedModel"
              size="x-small"
              variant="tonal"
              class="ml-2"
            >
              last used
            </v-chip>
            <v-chip
              v-else-if="model.isDefault"
              size="x-small"
              variant="tonal"
              class="ml-2"
            >
              default
            </v-chip>
          </v-btn>
        </div>
      </div>

      <!-- Generating. -->
      <div
        v-else-if="loading"
        class="d-flex flex-column align-center justify-center pa-6"
      >
        <v-progress-circular indeterminate color="primary" size="36" />
        <div class="text-body-2 mt-3">
          Asking {{ selectedModelName }}&hellip;
        </div>
        <div class="text-caption text-grey mt-1 text-center">
          This usually takes 10 - 20 seconds.
        </div>
      </div>

      <!-- Failed. -->
      <v-alert
        v-else-if="error"
        class="ma-3"
        type="error"
        variant="tonal"
        density="compact"
      >
        {{ error }}
      </v-alert>

      <!-- Answered. -->
      <div v-else class="pa-3">
        <div class="d-flex align-center flex-wrap ga-2 mb-3">
          <v-chip
            class="verdict-chip"
            :color="verdictColor"
            variant="flat"
            size="small"
          >
            <v-icon start size="small">
              {{ verdictIcon }}
            </v-icon>
            {{ verdictLabel }}
          </v-chip>

          <v-chip size="small" variant="tonal">
            Confidence {{ explanation.confidence }}%
          </v-chip>
        </div>

        <section class="mb-4">
          <h4 class="text-caption text-uppercase text-grey mb-1">
            Background
          </h4>
          <p class="text-body-2 mb-0">
            {{ explanation.background }}
          </p>
        </section>

        <section v-if="explanation.truePositiveCase" class="mb-4">
          <h4 class="text-caption text-uppercase text-grey mb-1">
            <v-icon size="x-small" color="error" class="mr-1">
              mdi-alert-circle-outline
            </v-icon>
            Why this may be a real defect
          </h4>
          <p class="text-body-2 mb-0">
            {{ explanation.truePositiveCase }}
          </p>
        </section>

        <section v-if="explanation.falsePositiveCase" class="mb-4">
          <h4 class="text-caption text-uppercase text-grey mb-1">
            <v-icon size="x-small" color="success" class="mr-1">
              mdi-shield-check-outline
            </v-icon>
            Why this may be a false positive
          </h4>
          <p class="text-body-2 mb-0">
            {{ explanation.falsePositiveCase }}
          </p>
        </section>

        <v-divider class="my-3" />

        <p class="text-caption text-grey mb-0">
          Generated by {{ selectedModelName }}. AI answers can be wrong -
          confirm against the code before setting a review status.
        </p>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { computed, onMounted, ref, watch } from "vue";

import { ccService, handleThriftError } from "@cc-api";
import { AIVerdict } from "@cc/report-server-types";

const props = defineProps({
  reportId: { type: Object, default: null }
});

defineEmits([ "close" ]);

// Kept for the page's lifetime, so a run of reports stays one click.
let rememberedModel = null;

const models = ref([]);
const selectedModel = ref(null);
const lastUsedModel = ref(rememberedModel);
const explanation = ref(null);
const loading = ref(false);
const error = ref(null);
const unavailable = ref(null);

const selectedModelName = computed(() => {
  const model = models.value.find(m => m.id === selectedModel.value);
  return model ? model.displayName : "(none)";
});

const verdictLabel = computed(() => {
  switch (explanation.value?.verdict) {
  case AIVerdict.LIKELY_TRUE_POSITIVE:
    return "Likely a true positive";
  case AIVerdict.LIKELY_FALSE_POSITIVE:
    return "Likely a false positive";
  default:
    return "Uncertain";
  }
});

const verdictColor = computed(() => {
  switch (explanation.value?.verdict) {
  case AIVerdict.LIKELY_TRUE_POSITIVE:
    return "error";
  case AIVerdict.LIKELY_FALSE_POSITIVE:
    return "success";
  default:
    return "grey";
  }
});

const verdictIcon = computed(() => {
  switch (explanation.value?.verdict) {
  case AIVerdict.LIKELY_TRUE_POSITIVE:
    return "mdi-alert-circle-outline";
  case AIVerdict.LIKELY_FALSE_POSITIVE:
    return "mdi-shield-check-outline";
  default:
    return "mdi-help-circle-outline";
  }
});

onMounted(loadModels);

// Never leave an answer next to a different report.
watch(() => props.reportId, reset);

function reset() {
  explanation.value = null;
  error.value = null;
  loading.value = false;
  selectedModel.value = null;
}

function loadModels() {
  ccService.getClient().getAIModels(handleThriftError(availableModels => {
    models.value = availableModels;

    if (!availableModels.length) {
      unavailable.value =
        "AI explanation is not enabled on this server.";
    }
  }, err => {
    unavailable.value = errorMessage(err);
  }));
}

function explain(modelId) {
  if (!props.reportId || !modelId) return;

  selectedModel.value = modelId;
  rememberedModel = modelId;
  lastUsedModel.value = modelId;

  loading.value = true;
  error.value = null;
  explanation.value = null;

  ccService.getClient().getReportExplanation(
    props.reportId,
    modelId,
    handleThriftError(result => {
      explanation.value = result;
      loading.value = false;
    }, err => {
      error.value = errorMessage(err);
      loading.value = false;
    }));
}

function errorMessage(err) {
  return err?.message || "The explanation could not be generated.";
}
</script>

<style lang="scss" scoped>
.ai-explanation-panel {
  border-left: 1px solid rgb(var(--v-border-color), 0.2);
  overflow: hidden;
}

.ai-explanation-content {
  overflow-y: auto;
}

.model-choice {
  width: 100%;
}

section p {
  white-space: pre-wrap;
}
</style>
