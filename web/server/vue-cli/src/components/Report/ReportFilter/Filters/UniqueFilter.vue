<template>
  <div class="d-flex align-center">
    <v-select
      :value="uniqueMode"
      :items="options"
      label="Unique reports"
      dense
      hide-details
      class="ma-0 py-0"
      @change="setUniqueMode"
    />
    <tooltip-help-icon>
      This narrows the report list to unique report types. The same bug may
      appear several times if it is found in different runs or on different
      control paths, i.e. through different function calls. By checking
      <b>Unique reports</b>, a report appears only once even if it is found
      on several paths or in different runs.
    </tooltip-help-icon>
  </div>
</template>

<script>
import TooltipHelpIcon from "@/components/TooltipHelpIcon";
import BaseFilterMixin from "./BaseFilter.mixin";

export default {
  name: "UniqueFilter",
  components: { TooltipHelpIcon },
  mixins: [ BaseFilterMixin ],
  data() {
    return {
      id: "is-unique",
      defaultValue: "off",
      options: [
        { text: "None", value: "off" },
        { text: "By bug hash (old)", value: "hash" },
        { text: "By file & line (new)", value: "fileline" }
      ]
    };
  },

  computed: {
    uniqueMode() {
      return this.$store.state[this.namespace].reportFilter._uniqueMode || "off";
    }
  },

  methods: {
    setUniqueMode(mode, updateUrl=true) {
      const isUnique = mode === "hash" || mode === "fileline";
      this.setReportFilter({ isUnique: isUnique, _uniqueMode: mode });
      if (updateUrl) {
        this.$emit("update:url");
      }
    },

    encodeValue(mode) {
      return mode;
    },

    decodeValue(state) {
      if (state === "on" || state === "hash") return "hash";
      if (state === "fileline") return "fileline";
      return "off";
    },

    getUrlState() {
      return {
        [this.id]: this.encodeValue(this.uniqueMode)
      };
    },

    initByUrl() {
      return new Promise(resolve => {
        const state = this.$route.query[this.id];
        if (state) {
          const mode = this.decodeValue(state);
          this.setUniqueMode(mode, false);
        } else {
          this.setUniqueMode(this.defaultValue, false);
        }
        resolve();
      });
    },

    clear(updateUrl) {
      this.setUniqueMode(this.defaultValue, updateUrl);
    }
  }
};
</script>
