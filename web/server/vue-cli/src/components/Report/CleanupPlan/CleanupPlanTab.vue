<template>
  <v-container>
    <v-tabs v-model="tab">
      <v-tab
        v-for="item in ['Open', 'Closed']"
        :key="item"
        class="font-weight-bold subtitle-2 text-capitalize"
        :value="item"
      >
        {{ item }}
      </v-tab>
    </v-tabs>

    <v-tabs-window v-model="tab">
      <v-tabs-window-item value="Open">
        <slot name="open" />
      </v-tabs-window-item>

      <v-tabs-window-item value="Closed">
        <slot name="closed" />
      </v-tabs-window-item>
    </v-tabs-window>
  </v-container>
</template>

<script>
export default {
  name: "CleanupPlanTab",
  props: {
    value: { type: String, default: "Open" }
  },
  computed: {
    tab: {
      get() {
        return this.value;
      },
      set(val) {
        this.$emit("input", val);
      }
    }
  }
};
</script>
