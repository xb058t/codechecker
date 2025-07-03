<template>
  <div>
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script>
import _ from "lodash";
import {
  endOfMonth, endOfToday, endOfWeek, endOfYear, format, subDays, subMonths,
  subWeeks, subYears
} from "date-fns";
import { Chart, LineController, LineElement, PointElement, LinearScale, Title, CategoryScale, Tooltip, Legend } from "chart.js";
import ChartDataLabels from "chartjs-plugin-datalabels";

import { ccService, handleThriftError } from "@cc-api";
import { ReportFilter, Severity } from "@cc/report-server-types";
import { DateMixin, SeverityMixin } from "@/mixins";
import bus from "@/bus";

Chart.register(LineController, LineElement, PointElement, LinearScale, Title, CategoryScale, Tooltip, Legend, ChartDataLabels);

export default {
  name: "OutstandingReportsChart",
  mixins: [DateMixin, SeverityMixin],
  props: {
    getStatisticsFilters: { type: Function, required: true },
    interval: { type: String, required: true },
    resolution: { type: String, required: true }
  },
  data() {
    return {
      dates: [],
      chartInstance: null,
      chartData: {
        labels: [],
        datasets: Object.keys(Severity).reverse().map(s => {
          const severityId = Severity[s];
          const color = this.severityFromCodeToColor(severityId);
          return {
            label: this.severityFromCodeToString(severityId),
            backgroundColor: color,
            borderColor: color,
            borderWidth: 3,
            fill: false,
            pointRadius: 5,
            pointHoverRadius: 10,
            datalabels: {
              backgroundColor: color,
              color: "white",
              borderRadius: 4,
              font: { weight: "bold" }
            },
            data: []
          };
        })
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          mode: "nearest",
          intersect: true
        },
        plugins: {
          legend: { display: true },
          tooltip: {
            mode: "index",
            callbacks: {
              footer: (tooltipItems) => {
                const total = tooltipItems.reduce((acc, curr) => acc + curr.parsed.y, 0);
                return `Total: ${total}`;
              }
            },
            intersect: false
          },
          datalabels: {
            color: "white",
            borderRadius: 4,
            font: { weight: "bold" }
          }
        },
        scales: {
          x: { ticks: { padding: 10 } },
          y: { beginAtZero: true }
        }
      }
    };
  },

  watch: {
    interval: {
      handler: _.debounce(function () {
        const oldSize = this.dates.length;
        const newSize = parseInt(this.interval);
        this.setChartData();
        if (newSize > oldSize) {
          const dates = this.dates.slice(oldSize);
          this.fetchData(dates);
        }
      }, 500)
    },
    resolution() {
      this.setChartData();
      this.fetchData(this.dates);
    }
  },

  created() {
    this.setChartData();
  },

  mounted() {
    const ctx = this.$refs.chartCanvas.getContext("2d");
    this.chartInstance = new Chart(ctx, {
      type: "line",
      data: this.chartData,
      options: this.options,
      plugins: [ChartDataLabels]
    });

    bus.on("refresh", () => this.fetchData(this.dates));
  },

  methods: {
    setChartData() {
      const interval = parseInt(this.interval);
      if (isNaN(interval) || interval <= 0) return;

      let dateFormat = "yyyy. MMM. dd";
      let endFn = endOfToday;
      let subFn = subDays;

      if (this.resolution === "weeks") {
        endFn = () => endOfWeek(new Date(), { weekStartsOn: 1 });
        subFn = subWeeks;
      } else if (this.resolution === "months") {
        endFn = endOfMonth;
        subFn = subMonths;
        dateFormat = "yyyy. MMM";
      } else if (this.resolution === "years") {
        endFn = endOfYear;
        subFn = subYears;
        dateFormat = "yyyy";
      }

      const end = endFn();
      this.dates = Array.from({ length: interval }, (_, i) => subFn(end, i)).reverse();

      this.chartData.labels = this.dates.map((d, idx) => {
        const formatted = format(d, dateFormat);
        return idx === this.dates.length - 1 ? `${formatted} (Current)` : formatted;
      });

      this.chartData.datasets.forEach(dataset => {
        dataset.data = Array(this.dates.length).fill(null);
      });
    },

    async fetchData(datesToUpdate) {
      for (const [idx, d] of this.dates.entries()) {
        if (!datesToUpdate.includes(d)) continue;

        const reportCount = await this.fetchOutstandingReports(d);

        this.chartData.datasets.forEach((dataset, i) => {
          const severityId = Severity[Object.keys(Severity).reverse()[i]];
          dataset.data[idx] = reportCount[severityId]?.toNumber() || 0;
        });
      }

      this.chartInstance.update();
    },

    fetchOutstandingReports(date) {
      const { runIds, reportFilter } = this.getStatisticsFilters();
      const rFilter = new ReportFilter(reportFilter);
      rFilter.openReportsDate = this.getUnixTime(date);
      rFilter.detectionStatus = null;

      return new Promise(resolve => {
        ccService.getClient().getSeverityCounts(runIds, rFilter, null,
          handleThriftError(res => resolve(res)));
      });
    }
  }
};
</script>
