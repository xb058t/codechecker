<template>
  <v-container fluid>
    <v-row>
      <v-col>
        <v-card flat>
          <v-card-title class="justify-center">
            Component severity statistics

            <tooltip-help-icon>
              This table shows component statistics per severity
              levels.
              <br><br>
              Each row can be expanded which will show a checker statistics
              for the actual component.
              <br><br>
              The following filters don't affect these values:
              <ul>
                <li><b>Severity</b> filter.</li>
                <li><b>Source component</b> filter.</li>
              </ul>
            </tooltip-help-icon>
          </v-card-title>
          <component-severity-statistics-table
            :items="statistics"
            :loading="loading"
            :filters="statisticsFilters"
            :total-columns="totalColumns"
          >
            <template v-slot:header.critical.count="{ header }">
              <span>
                <severity-icon :status="Severity.CRITICAL" :size="16" />
                {{ header.text }}
              </span>
            </template>

            <template v-slot:header.high.count="{ header }">
              <span>
                <severity-icon :status="Severity.HIGH" :size="16" />
                {{ header.text }}
              </span>
            </template>

            <template v-slot:header.medium.count="{ header }">
              <span>
                <severity-icon :status="Severity.MEDIUM" :size="16" />
                {{ header.text }}
              </span>
            </template>

            <template v-slot:header.low.count="{ header }">
              <span>
                <severity-icon :status="Severity.LOW" :size="16" />
                {{ header.text }}
              </span>
            </template>

            <template v-slot:header.style.count="{ header }">
              <span>
                <severity-icon :status="Severity.STYLE" :size="16" />
                {{ header.text }}
              </span>
            </template>

            <template v-slot:header.unspecified.count="{ header }">
              <span>
                <severity-icon :status="Severity.UNSPECIFIED" :size="16" />
                {{ header.text }}
              </span>
            </template>

            <template #item.critical.count="{ item }">
              <span>
                <router-link
                  v-if="item.critical.count"
                  :to="{ name: 'reports', query: {
                    ...$router.currentRoute.query,
                    ...(item.$queryParams || {}),
                    'source-component': item.component,
                    'severity': severityFromCodeToString(Severity.CRITICAL)
                  }}"
                >
                  {{ item.critical.count }}
                </router-link>

                <report-diff-count
                  :num-of-new-reports="item.critical.new"
                  :num-of-resolved-reports="item.critical.resolved"
                  :extra-query-params="{
                    'source-component': item.component,
                    'severity': severityFromCodeToString(Severity.CRITICAL)
                  }"
                />
              </span>
            </template>

            <template #item.high.count="{ item }">
              <span>
                <router-link
                  v-if="item.high.count"
                  :to="{ name: 'reports', query: {
                    ...$router.currentRoute.query,
                    ...(item.$queryParams || {}),
                    'source-component': item.component,
                    'severity': severityFromCodeToString(Severity.HIGH)
                  }}"
                >
                  {{ item.high.count }}
                </router-link>

                <report-diff-count
                  :num-of-new-reports="item.high.new"
                  :num-of-resolved-reports="item.high.resolved"
                  :extra-query-params="{
                    'source-component': item.component,
                    'severity': severityFromCodeToString(Severity.HIGH)
                  }"
                />
              </span>
            </template>

            <template #item.medium.count="{ item }">
              <span>
                <router-link
                  v-if="item.medium.count"
                  :to="{ name: 'reports', query: {
                    ...$router.currentRoute.query,
                    ...(item.$queryParams || {}),
                    'source-component': item.component,
                    'severity': severityFromCodeToString(Severity.MEDIUM)
                  }}"
                >
                  {{ item.medium.count }}
                </router-link>

                <report-diff-count
                  :num-of-new-reports="item.medium.new"
                  :num-of-resolved-reports="item.medium.resolved"
                  :extra-query-params="{
                    'source-component': item.component,
                    'severity': severityFromCodeToString(Severity.MEDIUM)
                  }"
                />
              </span>
            </template>

            <template #item.low.count="{ item }">
              <span>
                <router-link
                  v-if="item.low.count"
                  :to="{ name: 'reports', query: {
                    ...$router.currentRoute.query,
                    ...(item.$queryParams || {}),
                    'source-component': item.component,
                    'severity': severityFromCodeToString(Severity.LOW)
                  }}"
                >
                  {{ item.low.count }}
                </router-link>

                <report-diff-count
                  :num-of-new-reports="item.low.new"
                  :num-of-resolved-reports="item.low.resolved"
                  :extra-query-params="{
                    'source-component': item.component,
                    'severity': severityFromCodeToString(Severity.LOW)
                  }"
                />
              </span>
            </template>

            <template #item.style.count="{ item }">
              <span>
                <router-link
                  v-if="item.style.count"
                  :to="{ name: 'reports', query: {
                    ...$router.currentRoute.query,
                    ...(item.$queryParams || {}),
                    'source-component': item.component,
                    'severity': severityFromCodeToString(Severity.STYLE)
                  }}"
                >
                  {{ item.style.count }}
                </router-link>

                <report-diff-count
                  :num-of-new-reports="item.style.new"
                  :num-of-resolved-reports="item.style.resolved"
                  :extra-query-params="{
                    'source-component': item.component,
                    'severity': severityFromCodeToString(Severity.STYLE)
                  }"
                />
              </span>
            </template>

            <template #item.unspecified.count="{ item }">
              <span>
                <router-link
                  v-if="item.unspecified.count"
                  :to="{ name: 'reports', query: {
                    ...$router.currentRoute.query,
                    ...(item.$queryParams || {}),
                    'source-component': item.component,
                    'severity': severityFromCodeToString(Severity.UNSPECIFIED)
                  }}"
                >
                  {{ item.unspecified.count }}
                </router-link>

                <report-diff-count
                  :num-of-new-reports="item.unspecified.new"
                  :num-of-resolved-reports="item.unspecified.resolved"
                  :extra-query-params="{
                    'source-component': item.component,
                    'severity': severityFromCodeToString(Severity.UNSPECIFIED)
                  }"
                />
              </span>
            </template>
            <template v-slot:header.reports.count="{ header }">
              <detection-status-icon
                :status="DetectionStatus.UNRESOLVED"
                :size="16"
                left
              />
              {{ header.text }}
            </template>
          </component-severity-statistics-table>
        </v-card>
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <v-card flat>
          <v-card-title class="justify-center">
            Report severities
            <tooltip-help-icon>
              This pie chart shows the checker severity distribution in the
              product.
              <br><br>
              The following filters don't affect these values:
              <ul>
                <li><b>Severity</b> filter.</li>
                <li><b>Source component</b> filter.</li>
              </ul>
            </tooltip-help-icon>
          </v-card-title>
          <v-row justify="center">
            <v-overlay
              :value="loading"
              :absolute="true"
              :opacity="0.2"
            >
              <v-progress-circular
                indeterminate
                size="64"
              />
            </v-overlay>
            <component-severity-statistics-chart
              :loading="loading"
              :statistics="statistics"
            />
          </v-row>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { ccService, handleThriftError } from "@cc-api";
import {
  DetectionStatus,
  ReportFilter,
  Severity
} from "@cc/report-server-types";
import { SeverityMixin } from "@/mixins";
import { DetectionStatusIcon, SeverityIcon } from "@/components/Icons";
import TooltipHelpIcon from "@/components/TooltipHelpIcon";
import {
  ComponentStatistics,
  ReportDiffCount,
  initDiffField
} from "@/components/Statistics";

import ComponentSeverityStatisticsChart from
  "./ComponentSeverityStatisticsChart";
import ComponentSeverityStatisticsTable from
  "./ComponentSeverityStatisticsTable";

export default {
  name: "ComponentSeverityStatistics",
  components: {
    ComponentSeverityStatisticsChart,
    ComponentSeverityStatisticsTable,
    DetectionStatusIcon,
    ReportDiffCount,
    SeverityIcon,
    TooltipHelpIcon
  },
  mixins: [ ComponentStatistics, SeverityMixin ],
  data() {
    const fieldsToUpdate = [ "critical", "high", "medium", "low", "style",
      "unspecified", "reports" ];

    return {
      DetectionStatus,
      Severity,
      totalColumns: fieldsToUpdate,
      fieldsToUpdate: fieldsToUpdate
    };
  },
  methods: {
    getComponentStatistics(component, runIds, reportFilter, cmpData) {
      const filter = new ReportFilter(reportFilter);
      filter["severity"] = null;
      filter["componentNames"] = [ component.name ];

      return new Promise(resolve =>
        ccService.getClient().getSeverityCounts(runIds, filter, cmpData,
          handleThriftError(res => resolve(res))));
    },

    initStatistics(components) {
      this.statistics = components.map(component => ({
        component   : component.name,
        value       : component.value || component.description,
        reports     : initDiffField(undefined),
        critical    : initDiffField(undefined),
        high        : initDiffField(undefined),
        medium      : initDiffField(undefined),
        low         : initDiffField(undefined),
        style       : initDiffField(undefined),
        unspecified : initDiffField(undefined)
      }));
    },

    async getStatistics(component, runIds, reportFilter, cmpData) {
      const res = await this.getComponentStatistics(component, runIds,
        reportFilter, cmpData);

      const reports = Object.keys(res).reduce((acc, curr) => {
        acc += res[curr].toNumber();
        return acc;
      }, 0);

      return {
        component   : component.name,
        value       : component.value || component.description,
        reports     : initDiffField(reports),
        critical    : initDiffField(res[Severity.CRITICAL]),
        high        : initDiffField(res[Severity.HIGH]),
        medium      : initDiffField(res[Severity.MEDIUM]),
        low         : initDiffField(res[Severity.LOW]),
        style       : initDiffField(res[Severity.STYLE]),
        unspecified : initDiffField(res[Severity.UNSPECIFIED])
      };
    },
  }
};
</script>
