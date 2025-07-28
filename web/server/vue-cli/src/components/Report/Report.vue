<template>
  <v-container fluid class="pa-0">
    <analysis-info-dialog
      v-model="analysisInfoDialog"
      :report-id="reportId"
    />

    <v-row class="ma-0">
      <v-col :cols="editorCols" class="py-0">
        <v-container fluid class="pa-0 mb-2">
          <v-row class="ma-0">
            <v-col cols="auto" class="pa-0 mr-2" align-self="center">
              <show-report-info-dialog :value="report">
                <template #default="{ props }">
                  <report-info-button v-bind="props" />
                </template>
              </show-report-info-dialog>
            </v-col>

            <v-col cols="auto" class="pa-0 mr-2" align-self="center">
              <analysis-info-btn @click="openAnalysisInfoDialog" />
            </v-col>

            <v-col cols="auto" class="pa-0 mr-2" align-self="center">
              <set-cleanup-plan-btn :value="report ? [report] : []" />
            </v-col>

            <v-col cols="auto" class="review-status-wrapper pa-0" align-self="center">
              <v-container fluid class="pa-0">
                <v-row class="px-4">
                  <v-col cols="auto" class="pa-0">
                    <select-review-status
                      class="mx-0"
                      :value="reviewData"
                      :report="report"
                      :on-confirm="confirmReviewStatusChange"
                    />
                  </v-col>
                  <v-col cols="auto" class="pa-0">
                    <v-menu
                      v-if="reviewData.comment"
                      content-class="review-status-message-dialog"
                      :close-on-content-click="false"
                      :nudge-width="200"
                      offset-x
                    >
                      <template #activator="{ props }">
                        <v-btn class="review-status-message" icon v-bind="props">
                          <v-icon>mdi-message-text-outline</v-icon>
                        </v-btn>
                      </template>
                      <v-card>
                        <v-list>
                          <v-list-item>
                            <v-list-item-avatar>
                              <user-icon :value="reviewData.author" />
                            </v-list-item-avatar>
                            <v-list-item-content>
                              <v-list-item-title>{{ reviewData.author }}</v-list-item-title>
                              <v-list-item-subtitle>{{ reviewData.date }}</v-list-item-subtitle>
                            </v-list-item-content>
                          </v-list-item>
                        </v-list>
                        <v-divider />
                        <v-list>
                          <v-list-item>
                            <v-list-item-title>{{ reviewData.comment }}</v-list-item-title>
                          </v-list-item>
                        </v-list>
                      </v-card>
                    </v-menu>
                  </v-col>
                </v-row>
              </v-container>
            </v-col>

            <v-col cols="auto" class="pa-0" align-self="center">
              <v-checkbox
                v-model="showArrows"
                class="show-arrows mx-2 my-0 align-center justify-center"
                label="Show arrows"
                dense
                :hide-details="true"
              />
            </v-col>

            <v-spacer />

            <v-col cols="auto" class="py-0 pr-0" align-self="center">
              <toggle-blame-view-btn v-model="enableBlameView" :disabled="!hasBlameInfo" />
            </v-col>

            <v-col cols="auto" class="py-0 pr-0" align-self="center">
              <v-btn
                class="comments-btn mx-2 mr-0"
                color="primary"
                outlined
                small
                :loading="loadNumOfComments"
                @click="showComments = !showComments"
              >
                <v-icon class="mr-1" small>mdi-comment-multiple-outline</v-icon>
                Comments ({{ numOfComments }})
              </v-btn>
            </v-col>
          </v-row>
        </v-container>

        <v-container fluid class="pa-0">
          <v-row id="editor-wrapper" class="ma-0" style="height: 600px; min-height: 600px;">
            <v-progress-linear v-if="loading" indeterminate class="mb-0" />

            <v-col class="pa-0">
              <v-container fluid class="pa-0">
                <v-row class="header pa-1 ma-0" justify="space-between">
                  <v-col v-if="trackingBranch" class="file-path py-0" align-self="center" cols="auto">
                    <span
                      v-if="sourceFile"
                      :title="`Tracking branch: ${trackingBranch}`"
                      class="grey--text text--darken-3"
                    >
                      <v-icon class="mr-0" small>mdi-source-branch</v-icon>
                      ({{ trackingBranch }})
                    </span>
                  </v-col>

                  <v-col v-if="trackingBranch" class="py-1 px-0" cols="auto">
                    <v-divider inset vertical :style="{ display: 'inline' }" />
                  </v-col>

                  <v-col class="file-path py-0 pl-1" align-self="center">
                    <copy-btn v-if="sourceFile" :value="sourceFile.filePath" />
                    <span v-if="sourceFile" class="file-path" :title="sourceFile.filePath">
                      {{ sourceFile.filePath }}
                    </span>
                  </v-col>

                  <v-col cols="auto" class="py-0" align-self="center">
                    <v-row align="center" class="text-no-wrap">
                      Found in:
                      <select-same-report
                        class="select-same-report ml-2"
                        :report="report"
                        @update:report="$emit('update:report', $event)"
                      />
                    </v-row>
                  </v-col>
                </v-row>

                <v-row class="editor ma-0" style="height: 100%;">
                  <textarea ref="editor" />
                </v-row>
              </v-container>
            </v-col>
          </v-row>
        </v-container>
      </v-col>

      <v-col v-if="showComments" class="pa-0" :cols="commentCols">
        <report-comments class="comments" :report="report" />
      </v-col>
    </v-row>
  </v-container>
</template>
<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from "vue";
import { useRoute } from "vue-router";
import mitt from "mitt";
import { createApp } from "vue";

import _ from "lodash";
import { format } from "date-fns";
import CodeMirror from "codemirror";
import "codemirror/lib/codemirror.css";
import "codemirror/mode/clike/clike.js";
import "codemirror/addon/scroll/annotatescrollbar.js";
import "codemirror/addon/search/match-highlighter.js";
import "codemirror/addon/search/matchesonscrollbar.js";
import "codemirror/addon/dialog/dialog.js";
import "codemirror/addon/dialog/dialog.css";
import "codemirror/addon/search/search.js";
import "codemirror/addon/search/searchcursor.js";

import { jsPlumb } from "jsplumb";

import { ccService, handleThriftError } from "@cc-api";
import { Checker, Encoding, ExtendedReportDataType, ReviewData } from "@cc/report-server-types";

import { AnalysisInfoDialog, CopyBtn } from "@/components";
import { UserIcon } from "@/components/Icons";
import { SetCleanupPlanBtn } from "@/components/Report/CleanupPlan";
import { ReportComments } from "@/components/Report/Comment";
import ToggleBlameViewBtn from "@/components/Report/Git/ToggleBlameViewBtn.vue";
import SelectReviewStatus from "@/components/Report/SelectReviewStatus.vue";
import SelectSameReport from "@/components/Report/SelectSameReport.vue";
import { ReportInfoButton, ShowReportInfoDialog } from "@/components/Report/ReportInfo";
import ReportStepMessage from "@/components/Report/ReportStepMessage.vue";
import ReportTreeKind from "@/components/Report/ReportTree/ReportTreeKind.js";
import AnalysisInfoBtn from "@/components/Report/AnalysisInfoBtn.vue";
import { FillHeight } from "@/directives";

const props = defineProps({ treeItem: { type: Object, default: null } });
const emit = defineEmits(["update-review-data"]);
const route = useRoute();
const bus = mitt();

const report = ref(null);
const editor = ref(null);
const sourceFile = ref(null);
const jsPlumbInstance = ref(null);
const lineMarks = ref([]);
const lineWidgets = ref([]);
const showArrows = ref(true);
const numOfComments = ref(null);
const loadNumOfComments = ref(true);
const showComments = ref(false);
const commentCols = ref(3);
const loading = ref(true);
const annotation = ref(null);
const selectedChecker = ref(null);
const analysisInfoDialog = ref(false);
const reportId = ref(null);
const docUrl = ref(null);
const enableBlameView = ref(route.query["view"] === "blame");

const trackingBranch = computed(() => sourceFile.value?.trackingBranch);
const hasBlameInfo = computed(() => sourceFile.value?.hasBlameInfo);
const editorCols = computed(() => showComments.value ? 9 : 12);
const reviewData = computed(() => report.value?.reviewData ?? new ReviewData());

function confirmReviewStatusChange(comment, status, author) {
  ccService.getClient().addReviewStatusRule(report.value.bugHash, status, comment, handleThriftError(() => {
    reviewData.value.comment = comment;
    reviewData.value.status = status;
    reviewData.value.author = author;
    reviewData.value.date = format(new Date(), "yyyy-MM-dd HH:mm:ss");
    emit("update-review-data", reviewData.value, report.value.reportId);
  }));
}

function openAnalysisInfoDialog() {
  reportId.value = report.value.reportId;
  analysisInfoDialog.value = true;
}

function jumpTo(line, column = 0) {
  editor.value.scrollIntoView({ line, ch: column }, 150);
}

function updateAnnotation(line) {
  annotation.value?.update([{ from: { line }, to: { line } }]);
}

function onResize() {
  annotation.value?.redraw();
}

function findText(evt) {
  if (evt.ctrlKey && evt.keyCode === 13)
    editor.value.execCommand("findPersistentNext");
  if (evt.ctrlKey && evt.keyCode === 70) {
    evt.preventDefault();
    editor.value.execCommand("findPersistent");
    setTimeout(() => {
      document.querySelector(".CodeMirror-search-field")?.focus();
    }, 0);
  }
}

onMounted(() => {
  document.addEventListener("keydown", findText);
  window.addEventListener("resize", onResize);

  nextTick(() => {
    const editorEl = document.querySelector("textarea");
     console.log("Editor element size:", editorEl?.offsetWidth, editorEl?.offsetHeight);
    if (!editorEl) return;

    editor.value = CodeMirror.fromTextArea(editorEl, {
      lineNumbers: true,
      readOnly: true,
      mode: "text/x-c++src",
      gutters: ["CodeMirror-linenumbers", "bugInfo"],
      extraKeys: {},
      viewportMargin: 200,
      highlightSelectionMatches: { showToken: /\w/, annotateScrollbar: true }
    });

    editor.value.setSize("100%", "100%");
    editor.value.on("viewportChange", (cm, from, to) => drawLines(from, to));
    annotation.value = editor.value.annotateScrollbar({ className: "scrollbar-bug-annotation" });

    if (props.treeItem) init(props.treeItem);

    bus.on("jpmToPrevReport", attrs => {
      loadReportStep(report.value, attrs);
    });

    bus.on("jpmToNextReport", attrs => {
      loadReportStep(report.value, attrs);
    });

    bus.on("showDocumentation", () => {
      selectedChecker.value = new Checker({
        analyzerName: report.value.analyzerName,
        checkerId: report.value.checkerId
      });
    });
  });
});

onBeforeUnmount(() => {
  document.removeEventListener("keydown", findText);
  window.removeEventListener("resize", onResize);
});

watch(enableBlameView, async () => {
  if (enableBlameView.value) await loadBlameView();
  else await hideBlameView();

  const line = props.treeItem?.step?.startLine?.toNumber() || props.treeItem?.report?.line?.toNumber();
  if (line) jumpTo(line);
});

watch(() => props.treeItem, () => {
  console.log("treeItem updated:", props.treeItem);
  if (props.treeItem) init(props.treeItem);
});

watch(showArrows, () => {
  showArrows.value ? drawBugPath() : clearLines();
});

watch(report, () => {
  loadNumOfComments.value = true;
  ccService.getClient().getCommentCount(report.value.reportId, handleThriftError(count => {
    numOfComments.value = count;
    loadNumOfComments.value = false;
  }));
});

async function init(item) {
  console.log("init start", item);
  if (!item?.report) return;

  loading.value = true;
  clearLines();
  report.value = item.report;

  try {
    console.log(`Source file data loaded: ${item.report.fileId}`);
    await setSourceFileData(item.report.fileId);
  } catch (err) {
    console.error("Failed loading source file", err);
  }

   nextTick(() => {
    try {
      drawBugPath();
      const step = item.step ?? item.report;
      const line = step.startLine?.toNumber() ?? step.line?.toNumber();
      const col = step.startCol?.toNumber() ?? step.column?.toNumber();

      if (line) {
        updateAnnotation(line - 1);
        jumpTo(line - 1, col ? col - 1 : 0);
      }

      console.log("Bug path drawn");
    } catch (e) {
      console.error("Bug path error", e);
    }

    loading.value = false;
    console.log("init done");
  });

  loading.value = false;
}

async function setSourceFileData(fileId) {
  console.log("Fetching source file with ID:", fileId);
  const source = await new Promise(resolve => {
    ccService.getClient().getSourceFileData(fileId, true, Encoding.DEFAULT,
      handleThriftError(data => resolve(data))
    );
  });

  sourceFile.value = source;
  console.log("Set sourceFile:", source);
  editor.value.setValue(source.fileContent || "");

  if (enableBlameView.value) {
    await loadBlameView();
  }
}


async function loadBlameView() {
  const blameInfo = await new Promise(resolve => {
    ccService.getClient().getBlameInfo(sourceFile.value.fileId, handleThriftError(data => resolve(data)));
  });

  if (!blameInfo) return;

  for (const [line, entry] of Object.entries(blameInfo)) {
    const info = `${entry.commitHash} — ${entry.author} — ${entry.date}`;
    editor.value.addLineClass(Number(line), "background", "blame-line");
    editor.value.addLineWidget(Number(line), createLineWidget(info));
  }
}

function createLineWidget(text) {
  const el = document.createElement("div");
  el.className = "blame-widget";
  el.textContent = text;
  return el;
}

function hideBlameView() {
  if (!lineWidgets.value.length) return;

  for (const widget of lineWidgets.value) {
    widget.clear();
  }

  lineWidgets.value = [];
  for (let i = 0; i < editor.value.lineCount(); ++i) {
    editor.value.removeLineClass(i, "background", "blame-line");
  }
}

function drawBugPath() {
  if (!jsPlumbInstance.value) {
    jsPlumbInstance.value = jsPlumb.getInstance({
      Container: document.getElementById("editor-wrapper"),
      PaintStyle: { stroke: "#f00", strokeWidth: 2 },
      EndpointStyle: { fill: "#f00", radius: 4 },
      Connector: ["Straight"]
    });
  }

  const steps = report.value?.bugPathEvents ?? [];
  const lines = steps.map(s => s.startLine?.toNumber() ?? s.line?.toNumber()).filter(Boolean);

  clearLines();

  for (const line of lines) {
    const widget = document.createElement("div");
    widget.className = "bug-path-marker";
    editor.value.setGutterMarker(line - 1, "bugInfo", widget);
    lineMarks.value.push(widget);
  }
}

function clearLines() {
  for (const marker of lineMarks.value) {
    marker?.parentNode?.removeChild(marker);
  }

  lineMarks.value = [];
  jsPlumbInstance.value?.deleteEveryConnection();
}

</script>

<style scoped>
#editor-wrapper {
  height: 600px;
  min-height: 400px;
  position: relative;
}

.editor {
  height: 100%;
  min-height: 100%;
  font-size: 14px;
  background-color: #f9f9f9;
  overflow: auto;
}

.CodeMirror {
  height: 100% !important;
  min-height: 400px;
  width: 100%;
  font-family: monospace;
  font-size: 14px;
}

.bug-path-marker {
  width: 10px;
  height: 10px;
  margin-top: 3px;
  margin-left: 3px;
  border-radius: 50%;
  background-color: red;
}

.blame-line {
  background-color: #f3f3f3 !important;
}

.blame-widget {
  font-size: 12px;
  color: #666;
  padding-left: 10px;
  white-space: nowrap;
}

.scrollbar-bug-annotation {
  background-color: red;
}
</style>
