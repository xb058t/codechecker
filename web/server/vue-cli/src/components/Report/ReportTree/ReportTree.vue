<template>
  <v-treeview
    :items="items"
    :opened="openedItems"
    @update:opened="val => openedItems = val"
    :activated="activeItems"
    @update:activated="onClick"
    :load-children="getChildren"
    :return-object="true"
    activatable
    item-value="id"
    open-on-click
    density="compact"
    v-model:selection="tree"
  >
    <template #prepend="{ item }">
      <span
        v-for="i in item.level"
        :key="i"
        class="v-treeview-node__level"
        style="display: inline-block"
      >
        &nbsp;
      </span>

      <report-tree-icon :item="item" />

      <review-status-icon
        v-if="item.kind === ReportTreeKind.REPORT"
        :status="parseInt(item.report.reviewData.status)"
      />
    </template>

    <template #label="{ item }">
      <report-tree-label
        :item="item"
        :style="{ backgroundColor: item.bgColor, display: 'inline-block' }"
      />
    </template>
  </v-treeview>
</template>

<script setup>
import { ref, watch, nextTick, onMounted } from "vue";
import { ccService, handleThriftError } from "@cc-api";
import {
  DetectionStatus,
  MAX_QUERY_SIZE,
  ReportFilter,
  ReviewStatus
} from "@cc/report-server-types";

import { ReviewStatusIcon } from "@/components/Icons";
import ReportTreeIcon from "./ReportTreeIcon.vue";
import ReportTreeLabel from "./ReportTreeLabel.vue";
import ReportTreeKind from "./ReportTreeKind";
import ReportTreeRootItem from "./ReportTreeRootItem";
import formatReportDetails from "./ReportDetailFormatter";

const props = defineProps({
  report: { type: Object, default: null },
  reviewStatus: { type: Number, default: null }
});

const emit = defineEmits(["click"]);

const ReportTreeKindConst = ReportTreeKind;

const tree = ref([]);
const items = ref([]);
const openedItems = ref([]);
const activeItems = ref([]);
const runId = ref(null);
const fileId = ref(null);

watch(() => props.report, () => {
  if (isTheReportFileChanged()) fetchReports();
});
watch(() => props.reviewStatus, () => {
  if (!isTheReportFileChanged()) fetchReports();
});

onMounted(() => {
  if (props.report) fetchReports();
});

function isTheReportFileChanged() {
  return !(
    runId.value?.equals(props.report.runId) &&
    fileId.value?.equals(props.report.fileId)
  );
}

function removeEmptyRootElements() {
  if (items.value.length) {
    let i = items.value.length;
    while (i--) {
      let j = items.value[i].children.length;
      while (j--) {
        if (!items.value[i].children[j].children.length) {
          items.value[i].children.splice(j, 1);
        }
      }
      if (!items.value[i].children.length) {
        items.value.splice(i, 1);
      }
    }
  }
}

function fetchReports() {
  runId.value = props.report.runId;
  fileId.value = props.report.fileId;

  items.value = JSON.parse(JSON.stringify(ReportTreeRootItem));

  const reportFilter = new ReportFilter({
    filepath: [props.report.checkedFile]
  });

  ccService.getClient().getRunResults(
    [props.report.runId], null, null, null,
    reportFilter, null, false,
    handleThriftError(reports => {
      if (reports.length === MAX_QUERY_SIZE) {
        const current = reports.find(r => r.reportId.equals(props.report.reportId));
        if (!current) reports.push(props.report);
      }

      reports.sort((a, b) => a.line - b.line).forEach(report => {
        const isResolved = report.detectionStatus === DetectionStatus.RESOLVED;

        const status = !(
          isResolved ||
          report.detectionStatus === DetectionStatus.OFF ||
          report.detectionStatus === DetectionStatus.UNAVAILABLE ||
          report.reviewData.status === ReviewStatus.FALSE_POSITIVE ||
          report.reviewData.status === ReviewStatus.INTENTIONAL
        )
          ? items.value.find(item => item.isOutstanding)
          : items.value.find(item => !item.isOutstanding);

        const parent = status.children.find(item => {
          return isResolved
            ? item.detectionStatus === DetectionStatus.RESOLVED
            : item.severity === report.severity;
        });

        if (parent) {
          parent.children.push({
            id: ReportTreeKind.getId(ReportTreeKind.REPORT, report),
            name: report.checkerId,
            kind: ReportTreeKind.REPORT,
            report,
            children: [],
            itemChildren: [],
            isLoading: false,
            getChildren: item => {
              return new Promise(resolve => {
                ccService.getClient().getReportDetails(report.reportId,
                  handleThriftError(details => {
                    item.children = formatReportDetails(report, details);
                    resolve();

                    if (props.report.reportId.equals(item.report.reportId)) {
                      const bugItem = item.children.find(c =>
                        c.id === `${report.reportId}_${ReportTreeKind.BUG}`
                      );
                      if (bugItem) activeItems.value.push(bugItem);
                    }
                  }));
              });
            }
          });
        }
      });

      openReportItems();
      removeEmptyRootElements();
    })
  );
}

function getChildren(item) {
  if (item.getChildren && !item.isLoading) {
    item.isLoading = true;
    return item.getChildren(item);
  }
  return item.children;
}

function openReportItems() {
  const isResolved = props.report.detectionStatus === DetectionStatus.RESOLVED;

  const status = !(
    isResolved ||
    props.report.detectionStatus === DetectionStatus.OFF ||
    props.report.detectionStatus === DetectionStatus.UNAVAILABLE ||
    props.report.reviewData.status === ReviewStatus.FALSE_POSITIVE ||
    props.report.reviewData.status === ReviewStatus.INTENTIONAL
  )
    ? items.value.find(item => item.isOutstanding)
    : items.value.find(item => !item.isOutstanding);

  openedItems.value.push(status);

  const rootNode = status.children.find(item => {
    return isResolved
      ? item.detectionStatus === DetectionStatus.RESOLVED
      : item.severity === props.report.severity;
  });

  if (rootNode) {
    openedItems.value.push(rootNode);

    nextTick(() => {
      const reportNode = rootNode.children.find(item =>
        item.id === props.report.reportId.toString()
      );
      if (reportNode) openedItems.value.push(reportNode);
    });
  }
}

function onClick(val) {
  emit("click", val[0]);
}
</script>

<style scoped lang="scss">
.v-treeview--density-compact :deep(.v-treeview-node__root) {
  min-height: 25px;
}

:deep(.v-treeview-node__level) {
  width: 18px;
}
</style>
