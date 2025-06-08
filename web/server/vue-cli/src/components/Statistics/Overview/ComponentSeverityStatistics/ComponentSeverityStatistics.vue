<template>
  <component-severity-statistics-table
    :items="statistics"
    :loading="loading"
    :filters="statisticsFilters"
    :total-columns="totalColumns"
  >
    <template v-slot:header.reports.count="{ header }">
      <detection-status-icon
        :status="DetectionStatus.UNRESOLVED"
        :size="16"
        left
      />
      {{ header.text }}
    </template>

    <template v-slot:header.critical.count="{ header }">
      <severity-icon :status="Severity.CRITICAL" :size="16" />
      {{ header.text }}
    </template>

    <template v-slot:header.high.count="{ header }">
      <severity-icon :status="Severity.HIGH" :size="16" />
      {{ header.text }}
    </template>

    <template v-slot:header.medium.count="{ header }">
      <severity-icon :status="Severity.MEDIUM" :size="16" />
      {{ header.text }}
    </template>

    <template v-slot:header.low.count="{ header }">
      <severity-icon :status="Severity.LOW" :size="16" />
      {{ header.text }}
    </template>

    <template v-slot:header.style.count="{ header }">
      <severity-icon :status="Severity.STYLE" :size="16" />
      {{ header.text }}
    </template>

    <template v-slot:header.unspecified.count="{ header }">
      <severity-icon :status="Severity.UNSPECIFIED" :size="16" />
      {{ header.text }}
    </template>

    <template v-slot:item.critical.count="{ item }">
      <span>
        <router-link
          v-if="item.critical.count"
          :to="{
            name: 'reports',
            query: {
              ...$router.currentRoute.query,
              ...(item.$queryParams || {}),
              'source-component': item.component,
              severity: severityFromCodeToString(Severity.CRITICAL)
            }
          }"
        >
          {{ item.critical.count }}
        </router-link>
        <report-diff-count
          :num-of-new-reports="item.critical.new"
          :num-of-resolved-reports="item.critical.resolved"
          :extra-query-params="{
            'source-component': item.component,
            severity: severityFromCodeToString(Severity.CRITICAL)
          }"
        />
      </span>
    </template>

    <template v-slot:item.high.count="{ item }">
      <span>
        <router-link
          v-if="item.high.count"
          :to="{
            name: 'reports',
            query: {
              ...$router.currentRoute.query,
              ...(item.$queryParams || {}),
              'source-component': item.component,
              severity: severityFromCodeToString(Severity.HIGH)
            }
          }"
        >
          {{ item.high.count }}
        </router-link>
        <report-diff-count
          :num-of-new-reports="item.high.new"
          :num-of-resolved-reports="item.high.resolved"
          :extra-query-params="{
            'source-component': item.component,
            severity: severityFromCodeToString(Severity.HIGH)
          }"
        />
      </span>
    </template>

    <template v-slot:item.medium.count="{ item }">
      <span>
        <router-link
          v-if="item.medium.count"
          :to="{
            name: 'reports',
            query: {
              ...$router.currentRoute.query,
              ...(item.$queryParams || {}),
              'source-component': item.component,
              severity: severityFromCodeToString(Severity.MEDIUM)
            }
          }"
        >
          {{ item.medium.count }}
        </router-link>
        <report-diff-count
          :num-of-new-reports="item.medium.new"
          :num-of-resolved-reports="item.medium.resolved"
          :extra-query-params="{
            'source-component': item.component,
            severity: severityFromCodeToString(Severity.MEDIUM)
          }"
        />
      </span>
    </template>

    <template v-slot:item.low.count="{ item }">
      <span>
        <router-link
          v-if="item.low.count"
          :to="{
            name: 'reports',
            query: {
              ...$router.currentRoute.query,
              ...(item.$queryParams || {}),
              'source-component': item.component,
              severity: severityFromCodeToString(Severity.LOW)
            }
          }"
        >
          {{ item.low.count }}
        </router-link>
        <report-diff-count
          :num-of-new-reports="item.low.new"
          :num-of-resolved-reports="item.low.resolved"
          :extra-query-params="{
            'source-component': item.component,
            severity: severityFromCodeToString(Severity.LOW)
          }"
        />
      </span>
    </template>

    <template v-slot:item.style.count="{ item }">
      <span>
        <router-link
          v-if="item.style.count"
          :to="{
            name: 'reports',
            query: {
              ...$router.currentRoute.query,
              ...(item.$queryParams || {}),
              'source-component': item.component,
              severity: severityFromCodeToString(Severity.STYLE)
            }
          }"
        >
          {{ item.style.count }}
        </router-link>
        <report-diff-count
          :num-of-new-reports="item.style.new"
          :num-of-resolved-reports="item.style.resolved"
          :extra-query-params="{
            'source-component': item.component,
            severity: severityFromCodeToString(Severity.STYLE)
          }"
        />
      </span>
    </template>

    <template v-slot:item.unspecified.count="{ item }">
      <span>
        <router-link
          v-if="item.unspecified.count"
          :to="{
            name: 'reports',
            query: {
              ...$router.currentRoute.query,
              ...(item.$queryParams || {}),
              'source-component': item.component,
              severity: severityFromCodeToString(Severity.UNSPECIFIED)
            }
          }"
        >
          {{ item.unspecified.count }}
        </router-link>
        <report-diff-count
          :num-of-new-reports="item.unspecified.new"
          :num-of-resolved-reports="item.unspecified.resolved"
          :extra-query-params="{
            'source-component': item.component,
            severity: severityFromCodeToString(Severity.UNSPECIFIED)
          }"
        />
      </span>
    </template>
  </component-severity-statistics-table>
</template>

<script>
import ComponentSeverityStatisticsTable 
  from "./ComponentSeverityStatisticsTable.vue";
import DetectionStatusIcon from "@/components/Icons/DetectionStatusIcon.vue";
import SeverityIcon from "@/components/Icons/SeverityIcon.vue";
import ReportDiffCount from "@/components/Statistics/ReportDiffCount.vue";
import Severity from "@/util/severity-util";

export default {
  name: "ComponentSeverityStatistics",
  components: {
    ComponentSeverityStatisticsTable,
    DetectionStatusIcon,
    SeverityIcon,
    ReportDiffCount
  },
  props: {
    statistics: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    },
    statisticsFilters: {
      type: Object,
      default: () => ({})
    },
    totalColumns: {
      type: Number,
      default: 0
    }
  },
  
  methods: {
    severityFromCodeToString(code) {
      return Severity.toString(code);
    }
  }
};
</script>