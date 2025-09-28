<template>
  <confirm-dialog
    v-model="dialog"
    max-width="80%"
    :loading="loading"
    @confirm="save"
  >
    <template #activator="{ props }">
      <v-btn
        class="edit-btn"
        icon
        color="primary"
        v-bind="props"
      >
        <v-icon>mdi-pencil</v-icon>
      </v-btn>
    </template>

    <template #title>
      Edit product
    </template>

    <template #content>
      <v-alert
        v-model="success"
        dismissible
        color="success"
        border="left"
        elevation="2"
        colored-border
        icon="mdi-check"
      >
        Successfully saved.
      </v-alert>

      <v-alert
        v-model="error"
        dismissible
        color="error"
        border="left"
        elevation="2"
        colored-border
        icon="mdi-alert-outline"
      >
        Failed to save product changes.
      </v-alert>

      <v-tabs
        v-model="tab"
         grow
      >
        <v-tab value="edit">
          Edit
        </v-tab>
        <v-tab value="permissions">
          Permissions
        </v-tab>
      </v-tabs>

      <v-tabs-window 
        v-model="tab"
      >
        <v-tabs-window-item value="edit">
          <v-container fluid>
            <product-config-form
              v-model:is-valid="isValid"
              :is-super-user="isSuperUser"
              :product-config="productConfig"
            />
          </v-container>
        </v-tabs-window-item>
        <v-tabs-window-item value="permissions">
          <edit-product-permission
            :product="product"
            :bus="bus"
            v-model:success="success"
            v-model:error="error"
          />
        </v-tabs-window-item>
      </v-tabs-window>
    </template>
  </confirm-dialog>
</template>

<script>
import { handleThriftError, prodService } from "@cc-api";
import { 
  DatabaseConnection,
  ProductConfiguration
} from "@cc/prod-types";

import ConfirmDialog from "@/components/ConfirmDialog";
import EditProductPermission from "./Permission/EditProductPermission";
import ProductConfigForm from "./ProductConfigForm";

import mitt from "mitt";

export default {
  name: "EditProductBtn",
  components: {
    ConfirmDialog,
    EditProductPermission,
    ProductConfigForm
  },
  props: {
    product: { type: Object, required: true },
    isSuperUser: { type: Boolean, default: false }
  },
  data() {
    return {
      dialog: false,
      productConfig: new ProductConfiguration({
        connection: new DatabaseConnection()
      }),
      tab: "edit",
      loading: false,
      isValid: false,
      success: false,
      error: false,
      bus: mitt()
    };
  },
  watch: {
    dialog() {
      if (!this.dialog) return;

      this.loading = true;
      prodService.getClient().getProductConfiguration(this.product.id,
        handleThriftError(config => {
          this.productConfig = config;
          this.loading = false;
        }));
    }
  },

  methods: {
    save() {
      prodService.getClient().editProduct(this.product.id, this.productConfig,
        handleThriftError(success => {
          if (!success) {
            this.error = true;
            return;
          }

          this.success = true;
          this.$emit("on-complete",
            new ProductConfiguration(this.productConfig));
        }));

      // Save permissions.
      this.bus.emit("save");
    }
  }
};
</script>
