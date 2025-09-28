<template>
  <v-list v-if="value && value.length">
    <template
      v-for="(cleanupPlan, idx) in value"
      :key="cleanupPlan.id.toNumber()"
    >
      <v-list-item :value="cleanupPlan.id.toNumber()">
        <template #prepend>
          <v-icon v-if="isSelected(cleanupPlan.id)">
            mdi-check
          </v-icon>

          <v-icon v-else-if="notAllSelected[cleanupPlan.id]">
            mdi-minus
          </v-icon>
        </template>

        <v-list-item-title class="font-weight-bold">
          {{ cleanupPlan.name }}
        </v-list-item-title>

        <v-list-item-subtitle
          v-if="cleanupPlan.closedAt"
        >
          <v-icon size="small">
            mdi-calendar-blank
          </v-icon>
          Closed on
          {{ fromUnixTime(cleanupPlan.closedAt, "yyyy-MM-dd") }}
        </v-list-item-subtitle>

        <v-list-item-subtitle
          v-else-if="cleanupPlan.dueDate"
        >
          <due-date :value="cleanupPlan.dueDate" />
        </v-list-item-subtitle>

        <v-list-item-subtitle v-else>
          No due date
        </v-list-item-subtitle>
      </v-list-item>

      <v-divider
        v-if="idx < value.length - 1"
        :key="idx"
      />
    </template>
  </v-list>

  <v-list v-else disabled>
    <v-list-item>
      <v-list-item-title>
        No cleanup plan.
      </v-list-item-title>
    </v-list-item>
  </v-list>
</template>

<script>
import { format } from "date-fns";
import DueDate from "./DueDate";

export default {
  name: "CleanupPlanList",
  components: {
    DueDate
  },
  props: {
    value: { type: Array, default: null },
    notAllSelected: { type: Object, default: () => ({}) }
  },
  methods: {
    isSelected(id) {
      return this.$attrs.modelValue?.includes(id);
    },
    fromUnixTime(timestamp, formatStr = "yyyy-MM-dd") {
      const date =
        typeof timestamp === "object" && typeof timestamp.toNumber === "function"
          ? new Date(timestamp.toNumber() * 1000)
          : new Date(timestamp * 1000);
      return format(date, formatStr);
    }
  }
};
</script>
