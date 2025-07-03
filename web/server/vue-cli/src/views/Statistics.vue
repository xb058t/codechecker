<template>
  <splitpanes class="default-theme">
    <pane size="20" :style="{ 'min-width': '300px' }">
      <report-filter
        v-fill-height
        :namespace="namespace"
        :show-remove-filtered-reports="false"
        :report-count="reportCount"
        :show-diff-type="false"
        :show-compare-to="showCompareTo"
        :refresh-filter="refreshFilterState"
        @refresh="refresh"
        @set-refresh-filter-state="setRefreshFilterState"
      />
    </pane>

    <pane>
      <div v-fill-height>
        <v-tabs v-model="tab">
          <v-tab
            v-for="t in tabs"
            :key="t.name"
            :to="{
              name: t.name,
              params: { endpoint: $route.params.endpoint },
              query: { ...$route.query }
            }"
            exact
          >
            <v-icon class="mr-2">{{ t.icon }}</v-icon>
            {{ t.label }}
          </v-tab>
        </v-tabs>

        <keep-alive>
          <router-view v-slot="{ Component }" :key="$route.fullPath">
            <component
              v-if="Component"
              :is="Component"
              :bus="bus"
              :namespace="namespace"
              @refresh-filter="setRefreshFilterState(true)"
            />
            <v-alert v-else type="error" text class="ma-4">
              ⚠ No component loaded for current route:
              <strong>{{ $route.name }}</strong>
            </v-alert>
          </router-view>
        </keep-alive>
      </div>
    </pane>
  </splitpanes>
</template>

<script>
import mitt from "mitt";
import { Pane, Splitpanes } from "splitpanes";
import "splitpanes/dist/splitpanes.css";
import { mapState } from "vuex";

import { ccService, handleThriftError } from "@cc-api";
import { FillHeight } from "@/directives";
import { ReportFilter } from "@/components/Report/ReportFilter";

const namespace = "statistics";
const bus = mitt();

export default {
  name: "Statistics",
  components: {
    Splitpanes,
    Pane,
    ReportFilter
  },
  directives: { FillHeight },
  data() {
    const tabs = [
      {
        name: "product-overview",
        icon: "mdi-briefcase-outline",
        path: "overview",
        label: "Product Overview",
        showCompareTo: true
      },
      {
        name: "checker-statistics",
        icon: "mdi-card-account-details",
        path: "checker",
        label: "Checker Statistics",
        showCompareTo: true
      },
      {
        name: "severity-statistics",
        icon: "mdi-speedometer",
        path: "severity",
        label: "Severity Statistics",
        showCompareTo: true
      },
      {
        name: "component-statistics",
        icon: "mdi-puzzle-outline",
        path: "component",
        label: "Component Statistics",
        showCompareTo: true
      },
      {
        name: "checker-coverage-statistics",
        icon: "mdi-clipboard-check-outline",
        path: "coverage",
        label: "Checker Coverage",
        showCompareTo: false
      },
      {
        name: "guideline-statistics",
        icon: "mdi-clipboard-text-outline",
        path: "guideline",
        label: "Guideline Statistics",
        showCompareTo: false
      }
    ];

    const refreshTabs = {};
    tabs.forEach(tab => (refreshTabs[tab.name] = false));

    return {
      namespace,
      bus,
      refreshFilterState: false,
      reportCount: 0,
      showCompareTo: true,
      tab: null,
      tabs,
      refreshTabs
    };
  },
  computed: {
    ...mapState({
      runIds(state, getters) {
        return getters[`${this.namespace}/getRunIds`];
      },
      reportFilter(state, getters) {
        return getters[`${this.namespace}/getReportFilter`];
      }
    })
  },
  mounted() {
    console.log("[Statistics] mounted. Current route name:", this.$route.name);
    this.tab = this.$route.name;
  },
  watch: {
    tab(val) {
      console.log("[Statistics] tab changed to:", val);
      if (!val) return;

      const tabData = this.tabs.find(t => t.name === val);
      if (tabData) {
        this.showCompareTo = tabData.showCompareTo;
      }

      if (this.refreshTabs[val]) {
        this.refreshCurrentTab();
      }
    }
  },
  methods: {
    refresh() {
      ccService.getClient().getRunResultCount(
        this.runIds,
        this.reportFilter,
        null,
        handleThriftError(res => {
          this.reportCount = res.toNumber();
        })
      );

      this.tabs.forEach(tab => {
        this.refreshTabs[tab.name] = true;
      });

      this.refreshCurrentTab();
    },
    refreshCurrentTab() {
      this.bus.emit("refresh");
      if (this.tab) {
        this.refreshTabs[this.tab] = false;
      }
    },
    setRefreshFilterState(state) {
      this.refreshFilterState = state;
    }
  }
};
</script>

<style lang="scss" scoped>
.splitpanes.default-theme {
  .splitpanes__pane {
    background-color: inherit;
  }
}
</style>
