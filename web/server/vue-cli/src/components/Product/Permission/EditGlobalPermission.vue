<template>
  <v-container fluid>
    <v-alert
      :model-value="success"
      dismissible
      color="success"
      border="left"
      elevation="2"
      colored-border
      icon="mdi-check"
      @update:model-value="success = $event"
    >
      Permission changes saved successfully!
    </v-alert>

    <v-alert
      :model-value="error"
      dismissible
      color="error"
      border="left"
      elevation="2"
      colored-border
      icon="mdi-alert-outline"
      @update:model-value="error = $event"
    >
      Some permission changes could not be saved!
    </v-alert>

    <v-row>
      <v-col>
        <product-user-permission
          :permissions="permissions"
          :auth-rights="userAuthRights"
          :bus="bus"
          :extra-params-json="extraParamsJSON"
          :is-group="false"
          :success="success"
          :error="error"
          @update:success="success = $event"
          @update:error="error = $event"
        />
      </v-col>

      <v-col>
        <product-group-permission
          :permissions="permissions"
          :auth-rights="groupAuthRights"
          :bus="bus"
          :extra-params-json="extraParamsJSON"
          :is-group="true"
          :success="success"
          :error="error"
          @update:success="success = $event"
          @update:error="error = $event"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import PopulatePermissionsMixin from "./PopulatePermissions.mixin";
import ProductUserPermission from "./ProductUserPermission";
import ProductGroupPermission from "./ProductGroupPermission";

export default {
  name: "EditProductPermission",
  components: {
    ProductUserPermission,
    ProductGroupPermission
  },
  mixins: [ PopulatePermissionsMixin ],
  props: {
    bus: {
      type: Object,
      required: true
    }
  },
  emits: [ "update:success", "update:error" ],
  data() {
    return {
      scope: "SYSTEM",
      extraParamsJSON: JSON.stringify({}),
      success: false,
      error: false
    };
  },
  mounted() {
    this.populatePermissions(this.scope, this.extraParamsJSON);
  }
};
</script>
