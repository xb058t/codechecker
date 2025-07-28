<template>
  <VExpansionPanels multiple class="pa-2">
    <VExpansionPanel>
      <VExpansionPanelTitle>
        <VBtn
          color="primary"
          variant="tonal"
          size="small"
          @click="clearAllFilters"
        >
          CLEAR ALL FILTERS
        </VBtn>

        <VSpacer />

        <ReportCount :value="reportCount" />
      </VExpansionPanelTitle>
    </VExpansionPanel>

    <VListItem>
      <VCheckbox
        v-model="showUnique"
        label="Unique reports"
        @update:model-value="updateUrl"
        density="compact"
      />
    </VListItem>

    <VExpansionPanel>
      <VExpansionPanelTitle>BASELINE</VExpansionPanelTitle>
      <VExpansionPanelText>
        <BaselineRunFilter
          ref="filters"
          :namespace="namespace"
          @update:url="updateUrl"
        />
        <BaselineOpenReportsDateFilter
          ref="filters"
          :namespace="namespace"
          @update:url="updateUrl"
        />
      </VExpansionPanelText>
    </VExpansionPanel>

    <VExpansionPanel v-if="showCompareTo">
      <VExpansionPanelTitle>COMPARE TO</VExpansionPanelTitle>
      <VExpansionPanelText>
        <ComparedToRunFilter
          ref="filters"
          :namespace="namespace"
          @update:url="updateUrl"
        />
        <ComparedToOpenReportsDateFilter
          ref="filters"
          :namespace="namespace"
          @update:url="updateUrl"
        />
        <ComparedToDiffTypeFilter
          v-if="showDiffType"
          ref="filters"
          :namespace="namespace"
          @update:url="updateUrl"
        />
      </VExpansionPanelText>
    </VExpansionPanel>

    <VExpansionPanel>
      <VExpansionPanelTitle>FILE PATH</VExpansionPanelTitle>
      <VExpansionPanelText>
        <FilePathFilter
          ref="filters"
          :namespace="namespace"
          @update:url="updateUrl"
        />
      </VExpansionPanelText>
    </VExpansionPanel>

    <VExpansionPanel>
      <VExpansionPanelTitle>CHECKER NAME</VExpansionPanelTitle>
      <VExpansionPanelText>
        <CheckerNameFilter
          ref="filters"
          :namespace="namespace"
          @update:url="updateUrl"
        />
      </VExpansionPanelText>
    </VExpansionPanel>

    <VExpansionPanel>
      <VExpansionPanelTitle>SEVERITY</VExpansionPanelTitle>
      <VExpansionPanelText>
        <SeverityFilter
          ref="filters"
          :namespace="namespace"
          @update:url="updateUrl"
        />
      </VExpansionPanelText>
    </VExpansionPanel>

    <VExpansionPanel>
      <VExpansionPanelTitle>REPORT STATUS</VExpansionPanelTitle>
      <VExpansionPanelText>
        <ReportStatusFilter
          ref="filters"
          :namespace="namespace"
          @update:url="updateUrl"
        />
      </VExpansionPanelText>
    </VExpansionPanel>

    <VExpansionPanel v-if="showReviewStatus">
      <VExpansionPanelTitle>REVIEW STATUS</VExpansionPanelTitle>
      <VExpansionPanelText>
        <ReviewStatusFilter
          ref="filters"
          :namespace="namespace"
          @update:url="updateUrl"
        />
      </VExpansionPanelText>
    </VExpansionPanel>

    <VExpansionPanel>
      <VExpansionPanelTitle>DETECTION STATUS</VExpansionPanelTitle>
      <VExpansionPanelText>
        <DetectionStatusFilter
          ref="filters"
          :namespace="namespace"
          @update:url="updateUrl"
        />
      </VExpansionPanelText>
    </VExpansionPanel>

    <VExpansionPanel>
      <VExpansionPanelTitle>OTHER FILTERS</VExpansionPanelTitle>
      <VExpansionPanelText>
        <AnalyzerNameFilter
          ref="filters"
          :namespace="namespace"
          @update:url="updateUrl"
        />
        <SourceComponentFilter
          ref="filters"
          :namespace="namespace"
          @update:url="updateUrl"
        />
        <CleanupPlanFilter
          ref="filters"
          :namespace="namespace"
          @update:url="updateUrl"
        />
        <CheckerMessageFilter
          ref="filters"
          :namespace="namespace"
          @update:url="updateUrl"
        />
        <ReportHashFilter
          ref="filters"
          :namespace="namespace"
          @update:url="updateUrl"
        />
        <BugPathLengthFilter
          ref="filters"
          :namespace="namespace"
          @update:url="updateUrl"
        />
        <TestcaseFilter
          ref="filters"
          :namespace="namespace"
          @update:url="updateUrl"
        />
      </VExpansionPanelText>
    </VExpansionPanel>
  </VExpansionPanels>
</template>

<script>
import {
  VExpansionPanels,
  VExpansionPanel,
  VExpansionPanelTitle,
  VExpansionPanelText,
  VBtn,
  VSpacer,
  VCheckbox,
  VListItem
} from "vuetify/components";

import ClearAllFilters from "./ClearAllFilters.vue";
import ReportCount from "./ReportCount.vue";
import UniqueFilter from "./Filters/UniqueFilter.vue";
import BaselineRunFilter from "./Filters/BaselineRunFilter.vue";
import BaselineOpenReportsDateFilter from "./Filters/BaselineOpenReportsDateFilter.vue";
import ComparedToRunFilter from "./Filters/ComparedToRunFilter.vue";
import ComparedToOpenReportsDateFilter from "./Filters/ComparedToOpenReportsDateFilter.vue";
import ComparedToDiffTypeFilter from "./Filters/ComparedToDiffTypeFilter.vue";
import FilePathFilter from "./Filters/FilePathFilter.vue";
import CheckerNameFilter from "./Filters/CheckerNameFilter.vue";
import SeverityFilter from "./Filters/SeverityFilter.vue";
import ReportStatusFilter from "./Filters/ReportStatusFilter.vue";
import ReviewStatusFilter from "./Filters/ReviewStatusFilter.vue";
import DetectionStatusFilter from "./Filters/DetectionStatusFilter.vue";
import AnalyzerNameFilter from "./Filters/AnalyzerNameFilter.vue";
import SourceComponentFilter from "./Filters/SourceComponentFilter.vue";
import CleanupPlanFilter from "./Filters/CleanupPlanFilter.vue";
import CheckerMessageFilter from "./Filters/CheckerMessageFilter.vue";
import ReportHashFilter from "./Filters/ReportHashFilter.vue";
import BugPathLengthFilter from "./Filters/BugPathLengthFilter.vue";
import TestcaseFilter from "./Filters/TestcaseFilter.vue";

export default {
  name: "ReportFilter",
  components: {
    VExpansionPanels,
    VExpansionPanel,
    VExpansionPanelTitle,
    VExpansionPanelText,
    VBtn,
    VSpacer,
    VCheckbox,
    VListItem,
    ClearAllFilters,
    ReportCount,
    UniqueFilter,
    BaselineRunFilter,
    BaselineOpenReportsDateFilter,
    ComparedToRunFilter,
    ComparedToOpenReportsDateFilter,
    ComparedToDiffTypeFilter,
    FilePathFilter,
    CheckerNameFilter,
    SeverityFilter,
    ReportStatusFilter,
    ReviewStatusFilter,
    DetectionStatusFilter,
    AnalyzerNameFilter,
    SourceComponentFilter,
    CleanupPlanFilter,
    CheckerMessageFilter,
    ReportHashFilter,
    BugPathLengthFilter,
    TestcaseFilter
  },
  props: {
    namespace: { type: String, required: true },
    showCompareTo: { type: Boolean, default: true },
    showReviewStatus: { type: Boolean, default: true },
    showDiffType: { type: Boolean, default: true },
    reportCount: { type: Number, required: true }
  },
  data() {
    return {
      showUnique: false
    };
  },
  methods: {
    updateUrl() {
      this.$emit("update:url");
    },
    clearAllFilters() {
      this.$emit("clear");
    }
  }
};
</script>

<style scoped>
.v-expansion-panel-title {
  font-weight: bold;
  font-size: 0.8rem;
  min-height: 40px;
}

.v-expansion-panel-text {
  padding: 8px;
}

.v-expansion-panel-text * {
  font-size: 0.8rem !important;
}

.v-expansion-panel-text .v-btn,
.v-expansion-panel-text .v-card,
.v-expansion-panel-text .v-list-item,
.v-expansion-panel-text .v-text-field {
  min-height: 36px;
  padding: 4px 8px;
  font-size: 0.8rem !important;
}

.v-expansion-panel-text .v-card {
  background-color: #f5f5f5;
  box-shadow: none;
}

.v-expansion-panel {
  border: 1px solid rgba(0, 0, 0, 0.12);
  border-radius: 4px;
  margin-bottom: 8px;
}

.v-expansion-panels {
  padding: 0 4px;
}
</style>
