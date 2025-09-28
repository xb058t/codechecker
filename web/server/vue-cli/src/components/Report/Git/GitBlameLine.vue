<template>
  <div
    :class="[
      'blame-line',
      commit ? 'blame-line-full' : undefined
    ]"
  >
    <v-menu
      v-if="commit"
      :close-on-content-click="false"
      :close-delay="200"
      :max-width="400"
      open-on-hover
      location="end"
    >
      <template #activator="{ props }">
        <span
          class="blame-commit-info"
          v-bind="props"
        >
          <span class="git-avatar mx-1">
            <v-avatar
              :color="strToColor(commit.author.name)"
              size="15"
            >
              <span class="white--text">
                {{ avatarLabel }}
              </span>
            </v-avatar>
          </span>

          <div class="git-message" :title="commit.summary">
            {{ commit.summary }}
          </div>

          <div class="git-time" :title="commit.committedDateTime">
            on {{ date }}
          </div>
        </span>
      </template>

      <v-card>
        <v-list lines="three">
          <v-list-item>
            <template #prepend>
              <v-avatar
                :color="strToColor(commit.author.name)"
              >
                <span class="white--text">
                  {{ avatarLabel }}
                </span>
              </v-avatar>
            </template>

            <v-list-item-title class="font-weight-bold">
              {{ commit.summary }}
            </v-list-item-title>

            <v-list-item-subtitle :title="commit.hexsha">
              <a
                :href="remoteCommitUrl"
                target="_blank"
                rel="noopener noreferrer"
              >
                <span class="text-primary font-weight-bold">
                  #{{ hexsha }}
                </span>
              </a>
              <span :title="`Tracking branch: ${trackingBranch}`">
                ({{ truncate(trackingBranch, 20) }})
              </span>
            </v-list-item-subtitle>

            <v-list-item-subtitle>
              <span class="text-primary">
                {{ commit.author.name }}
              </span>
              ({{ commit.author.email }})
            </v-list-item-subtitle>
          </v-list-item>
        </v-list>

        <v-divider />

        <!-- eslint-disable vue/no-v-html -->
        <div class="pa-4" v-html="message" />
      </v-card>
    </v-menu>

    <span
      v-else
      class="blame-commit-info"
    >
      &nbsp;
    </span>

    <span
      class="blame-line-number"
      :style="{'background-color': color }"
    >
      {{ number }}
    </span>
  </div>
</template>

<script>
import { format } from "date-fns";
import { StrToColorMixin } from "@/mixins";

export default {
  name: "BlameLine",
  mixins: [ StrToColorMixin ],
  props: {
    commit: { type: Object, default: null },
    number: { type: Number, required: true },
    color: { type: String, required: true },
    remoteUrl: { type: String, default: null },
    trackingBranch: { type: String, default: null }
  },
  computed: {
    remoteCommitUrl() {
      return this.commit && this.remoteUrl
        ? this.remoteUrl.replace("$commit", this.commit.hexsha)
        : null;
    },
    avatarLabel() {
      return this.commit ? this.commit.author.name.charAt(0).toUpperCase() : "";
    },
    date() {
      return this.commit ? format(this.commit.committedDateTime, "yyyy-MM-dd") : "";
    },
    message() {
      return this.commit
        ? this.commit.message.replace(/(?:\r\n|\r|\n)/g, "<br>")
        : "";
    },
    hexsha() {
      return this.commit ? this.commit.hexsha.substring(0, 8) : "";
    }
  },
  methods: {
    truncate(value, length) {
      if (!value) return "";
      return value.length > length ? value.substring(0, length) + "…" : value;
    }
  }
};
</script>

<style lang="scss" scoped>
.blame-line-full {
  border-top: 1px solid #bdbaba;
}

.blame-line {
  .blame-commit-info {
    display: inline-block;
    width: 330px;
    min-width: 330px;
    max-width: 330px;

    .git-avatar {
      float: left;
      color: white;
    }

    .git-message {
      max-width: 180px;
      text-overflow: ellipsis;
      white-space: nowrap;
      overflow: hidden;
      display: inline-block;
      cursor: pointer;
    }

    .git-time {
      color: #6a737d;
      float: right;
      padding-right: 5px;
    }
  }

  .blame-line-number {
    min-width: 50px;
    text-align: right;
    padding-right: 10px;
    padding-left: 10px;
    color: #4e524e;
    font-weight: bold;
    position: absolute;
    right: 0;
  }
}
</style>