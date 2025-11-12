<script>
import { Pie } from "vue-chartjs";
import ChartDataLabels from "chartjs-plugin-datalabels";
import { Severity } from "@cc/report-server-types";
import { SeverityMixin } from "@/mixins";

export default {
  name: "ComponentSeverityStatisticsChart",
  extends: Pie,
  mixins: [ SeverityMixin ],
  props: {
    statistics: { type: Array, required: true },
    loading:    { type: Boolean, required: true }
  },
  data() {
    const severities = [
      Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM,
      Severity.LOW, Severity.STYLE, Severity.UNSPECIFIED
    ];

    const labels = severities.map(s => this.severityFromCodeToString(s));
    const colors = severities.map(s => this.severityFromCodeToColor(s));

    return {
      severities,
      options: {
        legend: { display: true, position: "bottom" },
        responsive: false,
        maintainAspectRatio: false,
        animation: { duration: 0 },
        hover: { animationDuration: 0 },
        responsiveAnimationDuration: 0,
        plugins: { datalabels: { backgroundColor: colors } }
      },
      chartData: {
        labels,
        datasets: [
          {
            data: Array(labels.length).fill(0),
            backgroundColor: colors,
            datalabels: {
              color: "white",
              borderColor: "white",
              borderRadius: 25,
              borderWidth: 2,
              font: { weight: "bold" }
            }
          }
        ]
      }
    };
  },
  watch: {
    loading(val) {
      if (!val) this.applyStatistics();
    },
    statistics() {
      if (!this.loading) this.applyStatistics();
    }
  },

  mounted() {
    this.addPlugin(ChartDataLabels);
    
    this.$nextTick(() => {
      if (!this.$refs?.canvas) return;
      this.renderChart(this.chartData, this.options);
      if (!this.loading) this.applyStatistics();
    });
  },
  methods: {
    applyStatistics() {
      const labels = this.chartData.labels;
      const next = new Array(labels.length).fill(0);

      if (Array.isArray(this.statistics)) {
        for (const row of this.statistics) {
          for (let i = 0; i < labels.length; i++) {
            const key = labels[i].toLowerCase();
            next[i] += row?.[key]?.count ?? 0;
          }
        }
      }

      const cur = this.chartData.datasets[0].data;
      let changed = cur.length !== next.length;
      if (!changed) {
        for (let i = 0; i < cur.length; i++) {
          if (cur[i] !== next[i]) { changed = true; break; }
        }
      }
      if (!changed) return;

      cur.splice(0, cur.length, ...next);

      if (this._chart && this._chart.ctx) {
        try { this._chart.update(0); } catch {}
      }
    }
  }
};
</script>
