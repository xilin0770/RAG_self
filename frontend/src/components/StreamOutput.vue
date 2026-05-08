<template>
  <div class="stream-output" ref="containerRef">
    <div class="stream-content">{{ text }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'

const props = defineProps<{ text: string }>()
const containerRef = ref<HTMLElement>()

watch(() => props.text, async () => {
  await nextTick()
  if (containerRef.value) {
    containerRef.value.scrollTop = containerRef.value.scrollHeight
  }
})
</script>

<style scoped>
.stream-output {
  min-height: 200px;
  max-height: 400px;
  overflow-y: auto;
  background: #f9fafb;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 14px;
}
.stream-content {
  white-space: pre-wrap;
  line-height: 1.7;
  font-size: 15px;
}
</style>
