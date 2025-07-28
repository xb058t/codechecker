<template>
  <filter-toolbar
    :id="id"
    title="Outstanding reports on a given date"
    :panel="panel"
    @clear="clear(true)"
  >
    <template #append-toolbar-title>
      <tooltip-help-icon>
        Filter reports that were <i>DETECTED BEFORE</i> the given date and
        <i>NOT FIXED BEFORE</i> the given date.<br /><br />
        The <i>detection date</i> of a report is the <i>storage date</i> when
        the report was stored to the server for the first time and the
        <i>fix date</i> is the date when the report is <i>dissappeared</i>
        from a storage.
      </tooltip-help-icon>

      <span
        v-if="selectedDateTitle"
        class="selected-items"
        :title="selectedDateTitle"
      >
        ({{ selectedDateTitle }})
      </span>
    </template>

    <template #default>
      <v-card-actions>
        <date-time-picker
          v-model:value="date"
          :input-class="id"
          :dialog-class="id"
          label="Report date"
          @update:value="setDateTime($event)"
        />
      </v-card-actions>
    </template>
  </filter-toolbar>
</template>

<script>
import BaseFilterMixin from "./BaseFilter.mixin";
import DateMixin from "@/mixins/date.mixin";
import FilterToolbar from "./Layout/FilterToolbar.vue";
import DateTimePicker from "@/components/DateTimePicker.vue";
import TooltipHelpIcon from "@/components/TooltipHelpIcon.vue";

export default {
  name: "BaselineOpenReportsDateFilter",
  components: {
    FilterToolbar,
    DateTimePicker,
    TooltipHelpIcon
  },
  mixins: [BaseFilterMixin, DateMixin],
  data() {
    return {
      id: "open-reports-date",
      date: null,
      panel: false
    };
  },
  computed: {
    selectedDateTitle() {
      return this.date ? this.dateTimeToStr(this.date) : null;
    }
  },
  methods: {
    setDateTime(date, updateUrl = true) {
      this.date = date;
      this.updateReportFilter();
      if (updateUrl) {
        this.$emit("update:url");
      }
    },
    updateReportFilter() {
      this.setReportFilter({
        openReportsDate: this.date ? this.getUnixTime(this.date) : null
      });
    },
    getUrlState() {
      return {
        [this.id]: this.date ? this.dateTimeToStr(this.date) : undefined
      };
    },
    initByUrl() {
      const raw = this.$route.query[this.id];
      if (raw) {
        const dt = new Date(raw);
        if (dt.getMilliseconds()) {
          dt.setMilliseconds(1000);
        }
        this.setDateTime(dt, false);
      }
    },
    initPanel() {
      this.panel = this.date !== null;
    },
    clear(updateUrl) {
      this.setDateTime(null, updateUrl);
    }
  },
  created() {
    this.initByUrl();
    this.initPanel();
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
