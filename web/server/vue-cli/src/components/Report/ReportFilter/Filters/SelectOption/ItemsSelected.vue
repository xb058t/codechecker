<template>
  <v-list
    v-if="selected.length"
    class="pa-0"
    density="compact"
  >
    <v-item-group
      v-model="selected"
      class="light-blue--text"
      multiple
    >
      <v-list-item
        v-for="item in selected"
        :key="item.id"
        :value="item"
        class="selected-item pa-0 px-1 ma-0 mb-1"
        :disabled="!multiple"
        density="compact"
      >
        <template #prepend>
          <div class="ma-1 mr-2">
            <slot name="icon" :item="item" />
          </div>
        </template>

        <div class="pa-0 flex-grow-1">
          <slot name="title" :item="item">
            <div class="font-weight-medium" :title="item.title">
              {{ item.title }}
            </div>
          </slot>
        </div>

        <v-chip
          class="report-count"
          color="#878d96"
          variant="outlined"
          size="small"
        >
          {{ item.count || item.count === 0 ? item.count : "N/A" }}
        </v-chip>

        <v-icon
          class="remove-btn font-weight-bold"
          color="error"
        >
          mdi-close
        </v-icon>
      </v-list-item>
    </v-item-group>
  </v-list>

  <v-list-item
    v-else
    density="compact"
  >
    <div class="flex-grow-1">
      <div class="font-italic">No filter</div>
    </div>
  </v-list-item>
</template>

<script>
export default {
  name: "ItemsSelected",
  props: {
    selectedItems: { type: Array, required: true },
    multiple: { type: Boolean, default: true }
  },
  computed: {
    selected: {
      get() {
        return this.selectedItems;
      },
      set(value) {
        this.$emit("update:select", value);
      }
    }
  }
};
</script>

<style lang="scss" scoped>
.v-list-item.v-list-item--density-compact {
  min-height: auto;
}

.selected-item {
  border: 1px solid var(--v-grey-lighten2);

  &:before {
    content: "";
    display: block;
    background-color: var(--v-primary-base);
    border-radius: 4px;
  }

  &:hover:before {
    background-color: var(--v-error-base);
  }

  .remove-btn {
    display:none;
  }

  &:hover {
    .report-count {
      display: none;
    }

    .remove-btn {
      display: block;
    }
  }
}
</style>
