<template>
  <v-app id="app">
    <TheHeader />

    <v-main>
      <keep-alive :include="keepAliveList">
        <router-view />
      </keep-alive>
      <Errors />
    </v-main>
  </v-app>
</template>

<script setup>
import Errors from "@/components/Errors";
import { TheHeader } from "@/components/Layout";
import { computed, ref, watch } from "vue";
import { useStore } from "vuex";

const store = useStore();
const keepAliveList = ref([]);

const isAuthenticated = computed(() => store.getters.isAuthenticated);

watch(isAuthenticated, newValue => {
  if (newValue) {
    keepAliveList.value.push("Products");
  } else {
    keepAliveList.value = [];
  }
});
</script>

<style lang="scss">

html {
  overflow-y: auto;
}

.v-text-field.v-text-field--solo.small {
  & > .v-input__control {
    min-height: 30px;

    & > .v-input__slot {
      min-height: 30px;

      .v-select__selections {
        font-size: 0.75rem;
      }
    }
  }
}
</style>
