<template>
  <select-option
    :id="id"
    title="File path"
    :bus="baseSelectOptionFilter.bus"
    :fetch-items="fetchItems"
    :selected-items="baseSelectOptionFilter.selectedItems.value"
    :loading="baseSelectOptionFilter.loading.value"
    :limit="baseSelectOptionFilter.defaultLimit.value"
    :panel="baseSelectOptionFilter.panel.value"
    @clear="baseSelectOptionFilter.clear(true)"
    @input="baseSelectOptionFilter.setSelectedItems"
  >
    <template v-slot:icon>
      <v-icon color="grey">
        mdi-file-document-outline
      </v-icon>
    </template>

    <template v-slot:menu-content="{ onApplyFinished }">
      <v-card flat>
        <v-toolbar class="pa-2" density="compact" flat>
          <v-text-field
            v-model="treeFilter"
            hide-details
            prepend-icon="mdi-magnify"
            single-line
            label="Search for files (e.g.: */src/*)..."
            clearable
          />
        </v-toolbar>

        <AnywhereOnReportPath v-model="isAnywhere" />

        <v-divider v-if="treeItems.length > 0" class="my-1" />

        <v-treeview
          v-if="treeItems.length > 0"
          v-model:selected="treeSelection"
          :items="treeItems"
          selectable
          select-strategy="independent"
          item-value="fullPath"
          item-title="name"
          open-on-click
          density="compact"
          class="file-path-tree"
        >
          <template v-slot:prepend="{ item, isOpen }">
            <v-icon v-if="item.children && item.children.length" size="small">
              {{ isOpen ? 'mdi-folder-open' : 'mdi-folder' }}
            </v-icon>
            <v-icon v-else size="small">
              mdi-file
            </v-icon>
          </template>
          <template v-slot:title="{ item }">
            <span
              class="tree-item-label"
              @click.stop="toggleTreeItem(item)"
            >
              {{ item.name }}
            </span>
            <v-chip class="ml-2" size="x-small">
              {{ item.findings }}
            </v-chip>
          </template>
        </v-treeview>

        <v-card-actions>
          <v-spacer />

          <v-btn
            variant="text"
            class="clear-all-btn"
            color="grey"
            prepend-icon="mdi-close-circle-outline"
            @click="clearAll(onApplyFinished)"
          >
            Clear All
          </v-btn>

          <v-btn
            variant="text"
            class="apply-btn"
            color="primary"
            prepend-icon="mdi-check-circle-outline"
            :disabled="treeSelection.length === 0"
            @click="applyTreeSelection(onApplyFinished)"
          >
            Apply
          </v-btn>
        </v-card-actions>
      </v-card>
    </template>
  </select-option>
</template>

<script setup>
import { ccService, handleThriftError } from "@cc-api";
import { ReportFilter } from "@cc/report-server-types";
import { computed, ref, toRef, watch } from "vue";

import {
  useBaseSelectOptionFilter
} from "@/composables/useBaseSelectOptionFilter";
import SelectOption from "./SelectOption/SelectOption";

import { useRoute } from "vue-router";
import AnywhereOnReportPath from "./SelectOption/AnywhereOnReportPath.vue";

const props = defineProps({
  namespace: { type: String, required: true }
});

const emit = defineEmits([ "update:url" ]);

const baseSelectOptionFilter =
  useBaseSelectOptionFilter(toRef(props, "namespace"));

baseSelectOptionFilter.fetchItems.value = fetchItems;
baseSelectOptionFilter.updateReportFilter.value = updateReportFilter;

const id = "filepath";
baseSelectOptionFilter.id.value = id;

const isAnywhere = ref(false);

const anywhereId = "anywhere-filepath";

// Holds the per-file report counts (path -> count) used to build the tree.
const allFileCounts = ref({});
// Selected tree node fullPaths.
const treeSelection = ref([]);
// Wildcard search string applied to the tree.
const treeFilter = ref("");

const route = useRoute();

const filteredFileCounts = computed(() => {
  if (!treeFilter.value) return allFileCounts.value;

  const pattern = treeFilter.value
    .replace(/[.+^${}()|[\]\\]/g, "\\$&")
    .replace(/\*/g, ".*")
    .replace(/\?/g, ".");
  const regex = new RegExp(pattern, "i");
  const filtered = {};
  Object.entries(allFileCounts.value || {}).forEach(([ fp, count ]) => {
    if (regex.test(fp)) {
      filtered[fp] = count;
    }
  });
  return filtered;
});

const treeItems = computed(() => {
  const items = [];

  Object.entries(filteredFileCounts.value || {}).forEach(
    ([ filePath, count ]) => {
      if (!filePath) return;
      const numCount = typeof count === "object" && count.toNumber
        ? count.toNumber() : count;
      const pathParts = filePath.split("/").slice(0, -1);
      let currentLevel = items;
      let currentPath = "";

      pathParts.forEach(part => {
        if (part === "") return;
        currentPath += "/" + part;
        let existingPart = currentLevel.find(item => item.name === part);
        if (!existingPart) {
          existingPart = {
            name: part,
            fullPath: currentPath,
            children: [],
            findings: 0
          };
          currentLevel.push(existingPart);
        }
        currentLevel = existingPart.children;
      });

      const fileName = filePath.split("/").slice(-1)[0];
      if (fileName) {
        const existingFile = currentLevel.find(
          item => item.name === fileName
        );
        if (existingFile) {
          existingFile.findings += numCount;
        } else {
          currentLevel.push({
            name: fileName,
            fullPath: filePath,
            children: [],
            findings: numCount
          });
        }
      }
    });

  function countFindings(node) {
    if (node.children.length === 0) return node.findings;
    node.findings = node.children.reduce(
      (sum, child) => sum + countFindings(child), 0
    );
    return node.findings;
  }
  items.forEach(countFindings);
  return items;
});

baseSelectOptionFilter.bus.on("update:url", () => {
  emit("update:url");
});

watch(isAnywhere, () => {
  // Update the global reportFilter object in baseFilter.
  updateReportFilter();

  // Emit update url trigger to ReportFilter.
  emit("update:url");

  // Fetch items based on the filter set.
  update();
});

function updateReportFilter() {
  baseSelectOptionFilter.setReportFilter({
    filepath: baseSelectOptionFilter.selectedItems.value.map(item => item.id),
    fileMatchesAnyPoint: isAnywhere.value
  });
}

function onReportFilterChange(key) {
  if (key === "filepath") {
    const paths = baseSelectOptionFilter.reportFilter.value?.filepath || [];
    const curIds = baseSelectOptionFilter.selectedItems.value.map(i => i.id);
    const same = paths.length === curIds.length &&
      paths.every((p, i) => p === curIds[i]);

    if (!same) {
      baseSelectOptionFilter.setSelectedItems(
        paths.map(p => ({ id: p, title: p, count: "N/A" })), false);
      baseSelectOptionFilter.panel.value = paths.length > 0;
    }
    return;
  }
  update();
}

// Custom update: refresh the full per-file counts that back the tree, then
// run the base update (which refreshes the selected item counts).
async function update() {
  await fetchAllFileCounts();
  await baseSelectOptionFilter.update();
}

// Fetch the report count for every file (ignoring the file path filter),
// paging through the results so large projects are fully covered.
function fetchAllFileCounts() {
  const reportFilter = new ReportFilter(
    baseSelectOptionFilter.reportFilter.value);
  reportFilter.filepath = null;
  const allCounts = {};

  return new Promise(resolve => {
    const fetchPage = offset => {
      ccService.getClient().getFileCounts(
        baseSelectOptionFilter.runIds.value, reportFilter,
        baseSelectOptionFilter.cmpData.value, 500, offset,
        handleThriftError(res => {
          const keys = Object.keys(res || {});
          keys.forEach(fp => {
            allCounts[fp] = res[fp];
          });
          if (keys.length >= 500) {
            fetchPage(offset + 500);
          } else {
            allFileCounts.value = Object.assign({}, allCounts);
            resolve();
          }
        }));
    };
    fetchPage(0);
  });
}

function clearAll(onApplyFinished) {
  treeSelection.value = [];
  baseSelectOptionFilter.clear(true);
  if (onApplyFinished) onApplyFinished();
}

function applyTreeSelection(onApplyFinished) {
  if (!treeSelection.value.length) return;

  const items = treeSelection.value.map(fp => {
    const isDir = isDirectory(fp);
    const filterId = isDir ? fp + "/*" : fp;
    return { id: filterId, title: filterId, count: "N/A" };
  });
  baseSelectOptionFilter.setSelectedItems(items);
  if (onApplyFinished) onApplyFinished();
}

function isDirectory(fullPath) {
  const find = nodes => {
    for (const n of nodes) {
      if (n.fullPath === fullPath) {
        return n.children.length > 0;
      }
      if (n.children.length) {
        const r = find(n.children);
        if (r !== null) return r;
      }
    }
    return null;
  };
  return !!find(treeItems.value);
}

function toggleTreeItem(item) {
  const idx = treeSelection.value.indexOf(item.fullPath);
  if (idx === -1) {
    treeSelection.value = [ ...treeSelection.value, item.fullPath ];
  } else {
    treeSelection.value = treeSelection.value.filter(
      p => p !== item.fullPath);
  }
}

function getUrlState() {
  const state =
    baseSelectOptionFilter.selectedItems.value.map(
      item => baseSelectOptionFilter.encodeValue.value(item.id)
    );

  return {
    [id]: state.length ? state : undefined,
    [anywhereId]: isAnywhere.value || undefined
  };
}

function initByUrl() {
  isAnywhere.value = !!route.query[anywhereId];
  baseSelectOptionFilter.initByUrl();
}

function fetchItems(opt={}) {
  baseSelectOptionFilter.loading.value = true;

  // Populate the full per-file counts that back the tree view. SelectOption
  // calls fetchItems when its menu opens, so this keeps the tree in sync.
  fetchAllFileCounts();

  const _reportFilter = new ReportFilter(
    baseSelectOptionFilter.reportFilter.value
  );
  _reportFilter.filepath = opt.query;

  const _limit = opt.limit || baseSelectOptionFilter.defaultLimit.value;
  const _offset = 0;

  return new Promise(resolve => {
    ccService.getClient().getFileCounts(
      baseSelectOptionFilter.runIds.value,
      _reportFilter,
      baseSelectOptionFilter.cmpData.value,
      _limit,
      _offset,
      handleThriftError(res => {
      // Order the results alphabetically.
        resolve(Object.keys(res).sort((a, b) => {
          if (a < b) return -1;
          if (a > b) return 1;
          return 0;
        }).map(file => {
          return {
            id : file,
            title: file,
            count: res[file]?.toNumber() || 0
          };
        }));
        baseSelectOptionFilter.loading.value = false;
      }));
  });
}

defineExpose({
  beforeInit: baseSelectOptionFilter.beforeInit,
  afterInit: baseSelectOptionFilter.afterInit,
  clear: baseSelectOptionFilter.clear,
  update,
  registerWatchers: baseSelectOptionFilter.registerWatchers,
  unregisterWatchers: baseSelectOptionFilter.unregisterWatchers,

  id,
  updateReportFilter,
  onReportFilterChange,
  getUrlState,
  initByUrl,
  fetchItems
});
</script>

<style lang="scss" scoped>
.filter-item-title {
  direction: rtl;
  text-align: left;
}

.file-path-tree {
  max-height: 400px;
  overflow-y: auto;
}

.tree-item-label {
  font-size: 0.85em;
}
</style>
