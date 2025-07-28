<template>
  <splitpanes class="default-theme fill-height">
    <pane size="20" :style="{ 'min-width': '300px' }">
      <report-filter
        style="height: 100%"
        :namespace="namespace"
        :report-count="totalItems"
        @refresh="refresh"
      />
    </pane>

    <pane>
      <checker-documentation-dialog
        v-model:value="checkerDocDialog"
        :checker="selectedChecker"
      />

      <v-data-table
        v-model="selected"
        style="height: 100%"
        :headers="tableHeaders"
        :items="formattedReports"
        v-model:options="pagination"
        :loading="loading"
        loading-text="Loading reports..."
        :server-items-length.sync="totalItems"
        :footer-props="footerProps"
        :must-sort="true"
        :expanded.sync="expanded"
        show-expand
        show-select
        :mobile-breakpoint="1100"
        item-key="$id"
        @item-expanded="itemExpanded"
      >
        <template #top>
          <v-toolbar flat class="report-filter-toolbar" dense>
            <v-row>
              <v-col class="pa-0" align="right">
                <set-cleanup-plan-btn :value="selected" />
              </v-col>
            </v-row>
          </v-toolbar>
        </template>

        <template #expanded-item="{ item }">
          <td class="pa-0" :colspan="headers.length">
            <v-list v-if="item.sameReports">
              <v-list-item
                v-for="report in item.sameReports"
                :key="report.reportId.toNumber()"
                dense
              >
                <v-list-item-content>
                  <v-list-item-title>
                    Same report in <kbd>{{ report.$runName }}</kbd> run:
                    <span>
                      <detection-status-icon
                        :status="parseInt(report.detectionStatus)"
                        :title="report.$detectionStatusTitle"
                        :size="18"
                      />
                      <review-status-icon
                        :status="parseInt(report.reviewData.status)"
                        :size="18"
                      />
                      <router-link
                        :to="{ name: 'report-detail', query: {
                          ...$route.query,
                          'report-id': report.reportId,
                          'report-hash': undefined
                        }}"
                      >
                        {{ report.checkedFile }}:{{ report.line }}
                      </router-link>
                    </span>
                  </v-list-item-title>
                </v-list-item-content>
              </v-list-item>
            </v-list>

            <v-card v-else flat tile>
              <v-card-text>
                Loading...
                <v-progress-linear indeterminate class="mb-0" />
              </v-card-text>
            </v-card>
          </td>
        </template>

        <template #item.bugHash="{ item }">
          <span :title="item.bugHash">
            {{ truncate(item.bugHash, 10) }}
          </span>
        </template>

        <template #item.checkedFile="{ item }">
          <router-link
            :to="{ name: 'report-detail', query: {
              ...$route.query,
              'report-id': item.reportId || undefined,
              'report-hash': item.bugHash,
              'report-filepath': reportFilter.isUnique ? `*${item.checkedFile}` : item.checkedFile
            }}"
            class="file-name"
          >
            {{ item.checkedFile }}<span v-if="item.line">@ Line {{ item.line }}</span>
          </router-link>
        </template>

        <template #item.checkerId="{ item }">
          <span class="checker-name primary--text" @click="openCheckerDocDialog(item.checkerId, item.analyzerName)">
            {{ item.checkerId }}
          </span>
        </template>

        <template #item.checkerMsg="{ item }">
          <span class="checker-message">{{ item.checkerMsg }}</span>
        </template>

        <template #item.severity="{ item }">
          <severity-icon :status="item.severity" />
        </template>

        <template #item.bugPathLength="{ item }">
          <v-chip :color="getBugPathLenColor(item.bugPathLength)">
            {{ item.bugPathLength }}
          </v-chip>
        </template>

        <template v-if="reportFilter.isUnique" #item.reviewData="{ item }">
          <review-status-icon
            v-for="status in sameReports[item.bugHash]"
            :key="status"
            :status="parseInt(status)"
            class="pa-1"
          />
        </template>

        <template v-else #item.reviewData="{ item }">
          <review-status-icon :status="parseInt(item.reviewData.status)" />
        </template>

        <template #item.detectionStatus="{ item }">
          <detection-status-icon
            :status="parseInt(item.detectionStatus)"
            :title="item.$detectionStatusTitle"
          />
        </template>
      </v-data-table>
    </pane>
  </splitpanes>
</template>

<script>
import { Pane, Splitpanes } from "splitpanes";
import { mapGetters } from "vuex";
import { ccService, handleThriftError } from "@cc-api";
import { Checker, Order, SortMode, SortType } from "@cc/report-server-types";

import { FillHeight } from "@/directives";
import { BugPathLengthColorMixin, DetectionStatusMixin } from "@/mixins";
import {
  DetectionStatusIcon,
  ReviewStatusIcon,
  SeverityIcon
} from "@/components/Icons";
import CheckerDocumentationDialog from "@/components/CheckerDocumentationDialog";
import { ReportFilter } from "@/components/Report/ReportFilter";
import { SetCleanupPlanBtn } from "@/components/Report/CleanupPlan";

const namespace = "report";

export default {
  name: "Reports",
  components: {
    Splitpanes,
    Pane,
    ReportFilter,
    CheckerDocumentationDialog,
    DetectionStatusIcon,
    ReviewStatusIcon,
    SeverityIcon,
    SetCleanupPlanBtn
  },
  directives: { FillHeight },
  mixins: [BugPathLengthColorMixin, DetectionStatusMixin],

  data() {
    const itemsPerPageOptions = [25, 50, 100];
    const query = this.$route.query;
    const page = parseInt(query["page"]) || 1;
    const itemsPerPage = parseInt(query["items-per-page"]) || itemsPerPageOptions[0];
    const sortBy = query["sort-by"];
    const sortDesc = query["sort-desc"];

    return {
      headers: [
        { text: "", value: "data-table-expand" },
        { text: "Report hash", value: "bugHash", sortable: false },
        { text: "File", value: "checkedFile", sortable: true },
        { text: "Message", value: "checkerMsg", sortable: false },
        { text: "Checker name", value: "checkerId", sortable: true },
        { text: "Analyzer", value: "analyzerName", align: "center", sortable: false },
        { text: "Severity", value: "severity", sortable: true },
        { text: "Bug path length", value: "bugPathLength", align: "center", sortable: true },
        { text: "Latest review status", value: "reviewData", align: "center", sortable: true },
        { text: "Latest detection status", value: "detectionStatus", align: "center", sortable: true },
        { text: "Timestamp", value: "timestamp", align: "center", sortable: true },
        { text: "Chronological order", value: "chronological_order", align: "center", sortable: true },
        { text: "Testcase", value: "testcase", align: "center", sortable: true }
      ],
      reports: [],
      sameReports: {},
      hasTimeStamp: true,
      hasTestCase: true,
      hasChronologicalOrder: true,
      selected: [],
      namespace,
      pagination: {
        page,
        itemsPerPage,
        sortBy: sortBy ? [sortBy] : [],
        sortDesc: sortDesc !== undefined ? [sortDesc === "true"] : []
      },
      footerProps: { itemsPerPageOptions },
      totalItems: 0,
      loading: false,
      initialized: false,
      checkerDocDialog: false,
      selectedChecker: null,
      expanded: []
    };
  },

  computed: {
    ...mapGetters(namespace, {
      runIds: "getRunIds",
      reportFilter: "getReportFilter",
      cmpData: "getCmpData"
    }),

    tableHeaders() {
      return this.headers.filter(header => {
        if (header.value === "detectionStatus") return !this.reportFilter.isUnique;
        if (header.value === "data-table-expand") return this.reportFilter.isUnique;
        if (header.value === "timestamp") return this.hasTimeStamp && !this.reportFilter.isUnique;
        if (header.value === "testcase") return this.hasTestCase && !this.reportFilter.isUnique;
        if (header.value === "chronological_order") return this.hasChronologicalOrder && !this.reportFilter.isUnique;
        return true;
      });
    },

    formattedReports() {
      return this.reports.map(report => {
        const reportId = report.reportId ? report.reportId.toString() : "";
        const id = reportId + report.bugHash;

        const detectionStatus = this.detectionStatusFromCodeToString(report.detectionStatus);
        const detectedAt = report.detectedAt ? this.prettifyDate(report.detectedAt) : null;
        const fixedAt = report.fixedAt ? this.prettifyDate(report.fixedAt) : null;

        const detectionStatusTitle = [
          `Status: ${detectionStatus}`,
          ...(detectedAt ? [`Detected at: ${detectedAt}`] : []),
          ...(fixedAt ? [`Fixed at: ${fixedAt}`] : [])
        ].join("\n");

        return {
          ...report,
          $detectionStatusTitle: detectionStatusTitle,
          $id: id,
          timestamp: report.annotations["timestamp"],
          testcase: report.annotations["testcase"],
          chronological_order: report.annotations["chronological_order"]
        };
      });
    }
  },

  watch: {
    pagination: {
      handler() {
        this.updateUrl();
        if (this.initialized) this.fetchReports();
      },
      deep: true
    },
    formattedReports: {
      handler() {
        this.hasTimeStamp = this.formattedReports.some(r => r.timestamp);
        this.hasTestCase = this.formattedReports.some(r => r.testcase);
        this.hasChronologicalOrder = this.formattedReports.some(r => r["chronological_order"]);
      }
    }
  },

  mounted() {
    this.refresh();
  },

  methods: {
    prettifyDate(timestamp) {
      const date = new Date(timestamp * 1000);
      return date.toLocaleString();
    },

    truncate(text, length) {
      if (!text) return "";
      return text.length <= length ? text : text.substring(0, length) + "…";
    },

    refresh() {
      this.expanded = [];
      ccService.getClient().getRunResultCount(
        this.runIds,
        this.reportFilter,
        this.cmpData,
        handleThriftError(res => {
          this.totalItems = res.toNumber();
        })
      );
      this.fetchReports();
    },

    fetchReports() {
      this.loading = true;
      const limit = this.pagination.itemsPerPage;
      const offset = limit * (this.pagination.page - 1);
      const sortType = this.getSortMode();

      ccService.getClient().getRunResults(
        this.runIds,
        limit,
        offset,
        sortType,
        this.reportFilter,
        this.cmpData,
        false,
        handleThriftError(reports => {
          this.reports = reports;
          this.loading = false;
          this.initialized = true;

          reports.forEach(report => {
            ccService.getSameReports(report.bugHash).then(sameReports => {
              this.sameReports[report.bugHash] = [...new Set(sameReports.map(r => r.reviewData.status))];
            });
          });
        })
      );
    },

    itemExpanded({ item }) {
      if (item.sameReports) return;
      ccService.getSameReports(item.bugHash).then(sr => {
        item.sameReports = sr;
      });
    },

    getSortMode() {
      const sortBy = this.pagination.sortBy?.[0];
      const sortDesc = this.pagination.sortDesc?.[0];
      const ord = sortDesc ? Order.DESC : Order.ASC;

      const type = {
        checkedFile: SortType.FILENAME,
        checkerId: SortType.CHECKER_NAME,
        detectionStatus: SortType.DETECTION_STATUS,
        reviewData: SortType.REVIEW_STATUS,
        bugPathLength: SortType.BUG_PATH_LENGTH,
        timestamp: SortType.TIMESTAMP,
        testcase: SortType.TESTCASE,
        chronological_order: SortType.CHRONOLOGICAL_ORDER
      }[sortBy] || SortType.SEVERITY;

      return [new SortMode({ type, ord })];
    },

    openCheckerDocDialog(checkerId, analyzerName) {
      this.selectedChecker = new Checker({ checkerId, analyzerName });
      this.checkerDocDialog = true;
    },

    updateUrl() {
      const query = {
        ...this.$route.query,
        "items-per-page": this.pagination.itemsPerPage !== this.footerProps.itemsPerPageOptions[0]
          ? this.pagination.itemsPerPage
          : undefined,
        "page": this.pagination.page !== 1
          ? this.pagination.page
          : undefined,
        "sort-by": this.pagination.sortBy?.[0],
        "sort-desc": this.pagination.sortDesc?.[0]
      };

      this.$router.replace({ query }).catch(() => {});
    }
  }
};
</script>

<style lang="scss" scoped>
.splitpanes.default-theme {
  height: calc(100vh - 64px);

  .splitpanes__pane {
    background-color: inherit;
    overflow-y: scroll;
    overflow-x: auto;
    padding: 8px;
  }
}

.v-data-table {
  .file-name,
  .checker-name,
  .checker-message {
    word-break: break-word;
  }

  .checker-name {
    cursor: pointer;
  }

  .v-data-table__wrapper {
    overflow-x: auto;
  }
}

.report-filter-toolbar {
  padding: 0;
}

.v-toolbar.report-filter-toolbar {
  background-color: transparent;
  box-shadow: none;
}

.v-container {
  padding: 0 !important;
}
</style>
