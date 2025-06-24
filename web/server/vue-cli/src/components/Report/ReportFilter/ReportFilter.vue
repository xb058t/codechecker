<template>
  <v-expansion-panels multiple class="pa-2">
    <v-expansion-panel>
      <v-expansion-panel-title>
        <v-btn
          color="primary"
          variant="tonal"
          size="small"
          @click="clearAllFilters"
        >
          CLEAR ALL FILTERS
        </v-btn>

        <v-spacer />

        <report-count :value="reportCount" />
      </v-expansion-panel-title>
    </v-expansion-panel>

    <v-list-item>
      <v-checkbox
        v-model="showUnique"
        label="Unique reports"
        @change="updateUrl"
        density="compact"
      />
    </v-list-item>

    <v-expansion-panel>
      <v-expansion-panel-title>
        BASELINE
      </v-expansion-panel-title>
      <v-expansion-panel-text>
        <baseline-run-filter
          ref="filters"
          :namespace="namespace"
          @update:url="updateUrl"
        />
        <baseline-open-reports-date-filter
          ref="filters"
          :namespace="namespace"
          @update:url="updateUrl"
        />
      </v-expansion-panel-text>
    </v-expansion-panel>

    <v-expansion-panel v-if="showCompareTo">
      <v-expansion-panel-title>
        COMPARE TO
      </v-expansion-panel-title>
      <v-expansion-panel-text>
        <compared-to-run-filter
          ref="filters"
          :namespace="namespace"
          @update:url="updateUrl"
        />
        <compared-to-open-reports-date-filter
          ref="filters"
          :namespace="namespace"
          @update:url="updateUrl"
        />
        <compared-to-diff-type-filter
          v-if="showDiffType"
          ref="filters"
          :namespace="namespace"
          @update:url="updateUrl"
        />
      </v-expansion-panel-text>
    </v-expansion-panel>

    <v-expansion-panel>
      <v-expansion-panel-title>
        FILE PATH
      </v-expansion-panel-title>
      <v-expansion-panel-text>
        <file-path-filter
          ref="filters"
          :namespace="namespace"
          @update:url="updateUrl"
        />
      </v-expansion-panel-text>
    </v-expansion-panel>

    <v-expansion-panel>
      <v-expansion-panel-title>
        CHECKER NAME
      </v-expansion-panel-title>
      <v-expansion-panel-text>
        <checker-name-filter
          ref="filters"
          :namespace="namespace"
          @update:url="updateUrl"
        />
      </v-expansion-panel-text>
    </v-expansion-panel>

    <v-expansion-panel>
      <v-expansion-panel-title>
        SEVERITY
      </v-expansion-panel-title>
      <v-expansion-panel-text>
        <severity-filter
          ref="filters"
          :namespace="namespace"
          @update:url="updateUrl"
        />
      </v-expansion-panel-text>
    </v-expansion-panel>

    <v-expansion-panel>
      <v-expansion-panel-title>
        REPORT STATUS
      </v-expansion-panel-title>
      <v-expansion-panel-text>
        <report-status-filter
          ref="filters"
          :namespace="namespace"
          @update:url="updateUrl"
        />
      </v-expansion-panel-text>
    </v-expansion-panel>

    <v-expansion-panel v-if="showReviewStatus">
      <v-expansion-panel-title>
        REVIEW STATUS
      </v-expansion-panel-title>
      <v-expansion-panel-text>
        <review-status-filter
          ref="filters"
          :namespace="namespace"
          @update:url="updateUrl"
        />
      </v-expansion-panel-text>
    </v-expansion-panel>

    <v-expansion-panel>
      <v-expansion-panel-title>
        DETECTION STATUS
      </v-expansion-panel-title>
      <v-expansion-panel-text>
        <detection-status-filter
          ref="filters"
          :namespace="namespace"
          @update:url="updateUrl"
        />
      </v-expansion-panel-text>
    </v-expansion-panel>

    <v-expansion-panel>
      <v-expansion-panel-title>
        OTHER FILTERS
      </v-expansion-panel-title>
      <v-expansion-panel-text>
        <analyzer-name-filter
          ref="filters"
          :namespace="namespace"
          @update:url="updateUrl"
        />
        <source-component-filter
          ref="filters"
          :namespace="namespace"
          @update:url="updateUrl"
        />
        <cleanup-plan-filter
          ref="filters"
          :namespace="namespace"
          @update:url="updateUrl"
        />
        <checker-message-filter
          ref="filters"
          :namespace="namespace"
          @update:url="updateUrl"
        />
        <report-hash-filter
          ref="filters"
          :namespace="namespace"
          @update:url="updateUrl"
        />
        <bug-path-length-filter
          ref="filters"
          :namespace="namespace"
          @update:url="updateUrl"
        />
        <testcase-filter
          ref="filters"
          :namespace="namespace"
          @update:url="updateUrl"
        />
      </v-expansion-panel-text>
    </v-expansion-panel>
  </v-expansion-panels>
</template>

<script>
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
