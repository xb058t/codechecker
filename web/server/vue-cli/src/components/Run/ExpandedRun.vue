<template>
  <v-card
    v-if="Object.keys(formattedHistories).length"
    class="mb-2"
    flat
  >
    <v-timeline
      v-for="(group, date) in formattedHistories"
      :key="date"
      density="compact"
      side="end"
    >
      <v-timeline-item
        class="pb-2"
        icon="mdi-calendar-month"
        dot-color="accent"
        size="small"
        fill-dot
      >
        <strong>{{ date }}</strong>
      </v-timeline-item>

      <v-timeline-item
        v-for="history in group"
        :key="history.id.toNumber()"
        class="run-history pb-2"
        icon="mdi-history"
        dot-color="primary"
        size="small"
        fill-dot
      >
        <v-row justify="space-between">
          <v-col class="pa-0 mr-5" cols="auto" align-self="center">
            <router-link
              :to="{ name: 'reports',
                    query: {
                      ...defaultReportFilterValues,
                      run: history.runName,
                      'run-tag': history.id
                    }
              }"
              class="date mr-2"
            >
              <strong>{{ prettifyDate(history.time) }}</strong>
            </router-link>
          </v-col>
          <v-col class="pa-0" align-self="center" cols="auto">
            <v-list-item lines="two">
              <div class="d-flex flex-column">
                <div class="d-flex align-center mb-1">
                  <v-chip
                    color="success"
                    variant="outlined"
                  >
                    <v-icon start>
                      mdi-account
                    </v-icon>
                    {{ history.user }}
                  </v-chip>

                  <version-tag
                    v-if="history.versionTag"
                    :value="history.versionTag"
                  />
                </div>

                <div class="d-flex align-center text-body-2">
                  <show-statistics-btn
                    :extra-queries="{
                      run: history.runName,
                      'run-tag': history.id
                    }"
                  />

                  <v-divider class="mx-2 d-inline" vertical />

                  <analysis-info-btn
                    @click="openAnalysisInfoDialog(
                      run.runId, history.id)"
                  />

                  <v-divider class="mx-2 d-inline" vertical />

                  <span :title="history.codeCheckerVersion">
                    v{{ history.$codeCheckerVersion }}
                  </span>

                  <v-divider class="mx-2 d-inline" vertical />

                  <analyzer-statistics-btn
                    v-if="Object.keys(history.analyzerStatistics).length"
                    :value="history.analyzerStatistics"
                    @click="openAnalyzerStatisticsDialog(null, history)"
                  />
                </div>
              </div>
            </v-list-item>
          </v-col>

          <v-spacer />

          <v-col
            class="compare-events"
            align="right"
            cols="auto"
            width="100px"
            align-self="center"
          >
            <v-container class="py-0">
              <v-row class="flex-nowrap py-0">
                <v-checkbox
                  v-model="baselineTags"
                  :value="history.id.toNumber()"
                  class="ma-0 pa-0"
                  hide-details
                  density="compact"
                />

                <v-checkbox
                  v-model="comparedToTags"
                  :value="history.id.toNumber()"
                  class="ma-0 pa-0"
                  hide-details
                  density="compact"
                />
              </v-row>
            </v-container>
          </v-col>
        </v-row>
      </v-timeline-item>
    </v-timeline>

    <slot />
  </v-card>

  <v-card v-else flat>
    <v-icon>mdi-alert-circle-outline</v-icon>
    <strong>No history events matched your search.</strong>
  </v-card>
</template>

<script>
import { format, parse } from "date-fns";
import { defaultReportFilterValues } from "@/components/Report/ReportFilter";
import AnalysisInfoBtn from "./AnalysisInfoBtn";
import AnalyzerStatisticsBtn from "./AnalyzerStatisticsBtn";
import ShowStatisticsBtn from "./ShowStatisticsBtn";
import VersionTag from "./VersionTag";

export default {
  name: "ExpandedRun",
  components: {
    AnalysisInfoBtn,
    AnalyzerStatisticsBtn,
    ShowStatisticsBtn,
    VersionTag
  },
  props: {
    histories: { type: Array, required: true },
    run: { type: Object, required: true },
    openAnalysisInfoDialog: { type: Function, default: () => {} },
    openAnalyzerStatisticsDialog: { type: Function, default: () => {} },
    selectedBaselineTags: { type: Array, required: true },
    selectedComparedToTags: { type: Array, required: true }
  },
  data() {
    return {
      defaultReportFilterValues
    };
  },
  methods: {
    prettifyDate(value) {
      if (!value) return "";
      const date = new Date(value);
      if (isNaN(date)) return value;
      return date.toLocaleString(undefined, {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit"
      });
    }
  },
  computed: {
    baselineTags: {
      get() {
        return this.selectedBaselineTags;
      },
      set(newVal) {
        this.$emit("update:selected-baseline-tags", newVal);
      }
    },

    comparedToTags: {
      get() {
        return this.selectedComparedToTags;
      },
      set(newVal) {
        this.$emit("update:selected-compared-to-tags", newVal);
      }
    },

    formattedHistories() {
      return this.histories.reduce((acc, curr) => {
        const date =
          parse(curr.time, "yyyy-MM-dd HH:mm:ss.SSSSSS", new Date());

        const group = format(date, "MMMM, yyyy");

        if (!acc[group])
          acc[group] = [];

        acc[group].push(curr);

        return acc;
      }, {});
    }
  }
};
</script>

<style lang="scss" scoped>
.v-timeline-item.run-history:hover {
  background-color: #eeeeee;
}
</style>
