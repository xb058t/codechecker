<template>
  <v-btn
    class="show-report-info-btn"
    color="primary"
    outlined
    small
    v-bind="$attrs"
  >
    <v-icon class="mr-1" small>
      mdi-help-circle-outline
    </v-icon>
    Report info
  </v-btn>
</template>

<script setup>
defineOptions({ name: "ReportInfoButton" });
</script>
