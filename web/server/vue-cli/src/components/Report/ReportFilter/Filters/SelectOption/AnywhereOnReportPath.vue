<template>
  <v-item-group>
    <v-list-item class="my-1">
      <div class="ma-1 mr-5">
        <v-switch :model-value="modelValue" @change="change" />
      </div>
      <span>
        Anywhere on report path
        <tooltip-help-icon>
          In case of file-related filters only reports ending in those files
          are queried. With this option all reports return where the given
          files are involved anywhere on the bugpath.
        </tooltip-help-icon>
      </span>
    </v-list-item>
  </v-item-group>
</template>

<script>
import TooltipHelpIcon from "@/components/TooltipHelpIcon.vue";

export default {
  name: "AnywhereOnReportPath",
  components: { TooltipHelpIcon },
  props: {
    modelValue: { type: Boolean, default: false }
  },
  emits: ["update:modelValue"],
  methods: {
    change(value) {
      this.$emit("update:modelValue", value);
    }
  }
};
</script>