<template>
  <confirm-dialog
    v-model="dialog"
    max-width="1000px"
    @confirm="confirmPermissionChange"
  >
    <template v-slot:activator="{ on }">
      <v-btn
        id="edit-global-permissions-btn"
        color="primary"
        class="mr-2"
        v-bind="on"
      >
        <v-icon left>
          mdi-shield-key
        </v-icon>
        Edit global permission
      </v-btn>
    </template>

    <template v-slot:title>
      Global permissions
    </template>

    <template v-slot:content>
      <edit-global-permission
        :bus="bus"
      />
    </template>
  </confirm-dialog>
</template>

<script>
import Vue from "vue";

import ConfirmDialog from "@/components/ConfirmDialog";
import EditGlobalPermission from "./EditGlobalPermission";

import mitt from "mitt";

export default {
  name: "EditGlobalPermissionBtn",
  components: {
    ConfirmDialog,
    EditGlobalPermission
  },

  data() {
    return {
      dialog: false,
      bus: mitt()
    };
  },

  methods: {
    confirmPermissionChange() {
      this.bus.$emit("save");
    }
  }
};
</script>
