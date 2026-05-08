<template>
  <span v-html="highlighted" />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { highlightText } from '@/utils/highlight'

const props = defineProps<{
  text: string
  query: string
}>()

const highlighted = computed(() => highlightText(props.text, props.query))
</script>
