<template>
  <v-tooltip
    v-model="copyInProgress"
    color="black"
    right
  >
    <template v-slot:activator="{}">
      <v-btn icon x-small @click="copy">
        <v-icon v-if="copyInProgress" color="green">
          mdi-check
        </v-icon>

        <v-icon v-else>
          mdi-content-paste
        </v-icon>    
      </v-btn>
    </template>
    Copied!
  </v-tooltip>
</template>

<script>
function writeToClipboard(str) {
  if (navigator.clipboard && window.isSecureContext) {
    return navigator.clipboard.writeText(str).catch(err => {
      console.error("Clipboard write failed:", err);
    });
  } else {
    const el = document.createElement("textarea");
    el.value = str;
    el.style.position = "fixed";
    el.style.left = "-9999px";
    document.body.appendChild(el);
    el.focus();
    el.select();

    try {
      document.execCommand("copy");
    } catch (err) {
      console.error("Fallback clipboard copy failed:", err);
    }

    document.body.removeChild(el);
  }
}

export default {
  name: "CopyBtn",
  props: {
    value: { type: String, required: true }
  },
  data() {
    return {
      copyInProgress: false
    };
  },
  methods: {
    copy() {
      this.copyInProgress = true;

      writeToClipboard(this.value);

      setTimeout(() => this.copyInProgress = false, 1000);
    }
  }
};
</script>
