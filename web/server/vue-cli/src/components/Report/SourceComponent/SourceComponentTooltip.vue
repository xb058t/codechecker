<template>
  <v-tooltip
    location="right"
    color="white"
  >
    <template v-slot:activator="{ props }">
      <slot v-bind="props" />
    </template>

    <v-card
      v-if="value"
      class="mx-auto"
      variant="outlined"
    >
      <v-list-item
        v-for="v in value.split('\n')"
        :key="v"
        :class="[
          v[0] === '+' ? 'include' : v[0] === '-' ? 'exclude': 'other'
        ]"
        density="compact"
      >
        {{ v }}
      </v-list-item>
    </v-card>
  </v-tooltip>
</template>

<script>
export default {
  name: "SourceComponentTooltip",
  props: {
    value: { type: String, required: true }
  }
};
</script>

<style lang="scss" scoped>
.v-overlay__content {
  padding: 0px;

  .v-list-item {
    min-height: auto;
  }

  .include {
    color: green !important;
  }

  .exclude {
    color: red !important;
  }

  .other {
    color: black !important;
  }
}
</style>
