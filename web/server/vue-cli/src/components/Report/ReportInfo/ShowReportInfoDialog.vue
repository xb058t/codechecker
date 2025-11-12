<template>
  <v-dialog
    v-model="dialog"
    content-class="report-info-dialog"
    max-width="600px"
  >

    <template #activator="{ props }">
      <v-container fluid class="px-0">
        <v-row>
          <v-col
            cols="auto"
            class="pa-0 mx-4"
          >
            <slot name="default" :props="props" />
          </v-col>
        </v-row>
      </v-container>
    </template>

    <v-card>
      <v-card-title
        class="headline primary white--text"
        primary-title
      >
        Report info

        <v-spacer />

        <v-btn class="close-btn" icon dark @click="dialog = false">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>

      <v-card-text class="pa-0">
        <v-container>
          <report-info :value="value" />
        </v-container>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
import ReportInfo from "./ReportInfo";

export default {
  name: "ShowReportInfoDialog",
  components: { ReportInfo },
  props: {
    value: { type: Object, default: null }
  },
  computed: {
    model: {
      get() { return this.modelValue },
      set(v) { this.$emit("update:value", v) }
    }
  },
  emits: ["update:value"],
  data() {
    return {
      dialog: false
    };
  }
};
</script>
