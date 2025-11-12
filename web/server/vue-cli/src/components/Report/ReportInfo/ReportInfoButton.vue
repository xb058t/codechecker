<template>
  <v-btn
    class="show-report-info-btn"
    color="primary"
    variant="outlined"
    size="small"
    v-bind="$attrs"
  >
    <v-icon size="small" class="me-1">mdi-help-circle-outline</v-icon>
    Report info
  </v-btn>
</template>

<script>
export default {
  name: "ReportInfoButton",
  inheritAttrs: false,
};
</script>
