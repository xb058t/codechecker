<template>
  <v-container fluid>
    <reports
      :bus="bus"
      :run-ids="runIds"
      :report-filter="reportFilter"
    />

    <v-row>
      <v-col>
        <single-line-widget
          icon="mdi-close"
          color="red"
          label="Number of failed files"
          :bus="bus"
          :get-value="getNumberOfFailedFiles"
        >
          <template #help>
            Number of failed files in the current product.<br><br>
            Only the Run filter will affect this value.
          </template>

          <template #value="{ value }">
            <failed-files-dialog>
              <template #default="{ on }">
                <span class="num-of-failed-files" v-on="on">
                  {{ value }}
                </span>
              </template>
            </failed-files-dialog>
          </template>
        </single-line-widget>
      </v-col>

      <v-col>
        <single-line-widget
          icon="mdi-card-account-details"
          color="grey"
          label="Number of checkers reporting faults"
          :bus="bus"
          :get-value="getNumberOfActiveCheckers"
        >
          <template #help>
            Number of checkers which found some report in the current product.<br><br>
            Every filter will affect this value.
          </template>
        </single-line-widget>
      </v-col>
    </v-row>

    <v-row class="my-4">
      <v-col>
        <v-card flat>
          <v-card-title class="justify-center">
            Number of outstanding reports
            <tooltip-help-icon>
              Shows the number of reports which were active in the last <i>x</i> months/days.<br><br>
              The following filters don't affect these values:
              <ul>
                <li><b>Outstanding reports on a given date</b> filter.</li>
                <li>All filters in the <b>COMPARE TO</b> section.</li>
                <li><b>Latest Review Status</b> filter.</li>
                <li><b>Latest Detection Status</b> filter.</li>
              </ul>
            </tooltip-help-icon>
          </v-card-title>

          <v-form ref="form" class="interval-selector">
            <v-text-field
              v-model="interval"
              class="interval align-center"
              type="number"
              hide-details
              dense
              solo
            >
              <template v-slot:prepend>
                Last
              </template>

              <template v-slot:append-outer>
                <v-select
                  v-model="resolution"
                  class="resolution"
                  :items="resolutions"
                  label="Resolution"
                  hide-details
                  dense
                  solo
                />
              </template>
            </v-text-field>

            <div v-if="intervalError" class="red--text">
              {{ intervalError }}
            </div>
          </v-form>

          <outstanding-reports-chart
            :bus="bus"
            :get-statistics-filters="getStatisticsFilters"
            :interval="interval"
            :resolution="resolution"
            :styles="{ height: '400px', position: 'relative' }"
          />
        </v-card>
      </v-col>
    </v-row>

    <v-row>
      <v-col>
        <component-severity-statistics
          :bus="bus"
          :namespace="namespace"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useStore } from 'vuex';
import mitt from 'mitt';
import _ from 'lodash';

import { ccService, handleThriftError } from '@cc-api';
import TooltipHelpIcon from '@/components/TooltipHelpIcon.vue';
import Reports from './Reports.vue';
import ComponentSeverityStatistics from "./ComponentSeverityStatistics/ComponentSeverityStatistics.vue";
import FailedFilesDialog from './FailedFilesDialog.vue';
import OutstandingReportsChart from './OutstandingReportsChart.vue';
import SingleLineWidget from './SingleLineWidget.vue';

const namespace = 'statistics';
const store = useStore();
const route = useRoute();
const router = useRouter();
const bus = mitt();

const runIds = computed(() => store.getters[`${namespace}/getRunIds`]);
const reportFilter = computed(() => store.getters[`${namespace}/getReportFilter`]);

const resolutions = [ 'days', 'weeks', 'months', 'years' ];
const defaultInterval = '7';
const defaultResolution = resolutions[0];

const interval = ref(route.query.interval || defaultInterval);
const resolution = ref(
  resolutions.includes(route.query.resolution) ? route.query.resolution : defaultResolution
);
const intervalError = ref(null);

watch(interval, _.debounce(val => {
  validateAndUpdateInterval(val);
}, 300));

function validateAndUpdateInterval(val) {
  const error = validateIntervalValue(val);
  if (error) {
    intervalError.value = error;
    return;
  }

  intervalError.value = null;
  updateUrl();
}

function validateIntervalValue(val) {
  if (!val || isNaN(parseInt(val))) return 'Number is required!';
  if (parseInt(val) > 31) return 'Interval value should be between 1-31!';
  return null;
}

watch(resolution, updateUrl);

function updateUrl() {
  router.replace({
    query: {
      ...route.query,
      interval: interval.value,
      resolution: resolution.value
    }
  }).catch(() => {});
}

function getNumberOfReports(runIds, reportFilter, cmpData) {
  return new Promise(resolve => {
    ccService.getClient().getRunResultCount(runIds, reportFilter, cmpData,
      handleThriftError(res => resolve(res.toNumber())));
  });
}

function getNumberOfFailedFiles() {
  return new Promise(resolve => {
    ccService.getClient().getFailedFilesCount(runIds.value,
      handleThriftError(res => resolve(res)));
  });
}

function getNumberOfActiveCheckers() {
  const { cmpData } = getStatisticsFilters();
  return new Promise(resolve => {
    ccService.getClient().getCheckerCounts(runIds.value, reportFilter.value, cmpData,
      null, 0, handleThriftError(res => resolve(res.length)));
  });
}

function getStatisticsFilters() {
  return {
    runIds: runIds.value,
    reportFilter: reportFilter.value,
    cmpData: null
  };
}
</script>

<style lang="scss" scoped>
.link {
  text-decoration: none;
  color: inherit;

  &:hover {
    color: var(--v-primary-lighten1);
  }
}

.num-of-failed-files {
  cursor: pointer;
}

.interval-selector {
  position: absolute;
  right: 50px;
  top: 0px;
  z-index: 100;

  .interval {
    width: 250px;
    border: 1px dashed grey;
    padding: 6px;
  }

  .resolution {
    width: 120px;
  }
}
</style>
