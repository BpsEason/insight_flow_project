<template>
  <div class="analysis-result-display mt-4 p-3 bg-gray-50 rounded-md border border-gray-200">
    <h4 class="font-bold text-lg mb-2">分析結果：</h4>
    <div v-if="result">
      <div v-if="result.摘要 && result.摘要.length">
        <p class="font-semibold text-gray-700">摘要：</p>
        <ul class="list-disc pl-5 mb-2 text-gray-600">
          <li v-for="(item, index) in result.摘要" :key="index" v-html="item"></li>
        </ul>
      </div>

      <div v-if="result.推薦 && result.推薦.length">
        <p class="font-semibold text-gray-700">推薦與建議：</p>
        <ul class="list-disc pl-5 mb-2 text-gray-600">
          <li v-for="(item, index) in result.推薦" :key="index" v-html="item"></li>
        </ul>
      </div>

      <div v-if="result.情緒分數">
        <p class="font-semibold text-gray-700">情緒偵測：</p>
        <p class="text-gray-600">標籤: {{ result.情緒分數.label }} (分數: {{ result.情緒分數.score.toFixed(2) }})</p>
      </div>

      <div v-if="result.關鍵字 && result.關鍵字.length">
        <p class="font-semibold text-gray-700">關鍵字：</p>
        <p class="text-gray-600">{{ result.關鍵字.join(', ') }}</p>
      </div>

      <div v-if="result.意圖">
        <p class="font-semibold text-gray-700">意圖辨識：</p>
        <p class="text-gray-600">意圖: {{ result.意圖.intent }}</p>
        <p v-if="result.意圖.product_category" class="text-gray-600">產品類別: {{ result.意圖.product_category }}</p>
      </div>

    </div>
    <div v-else class="text-gray-500">
      沒有可顯示的分析結果。
    </div>
  </div>
</template>

<script setup>
import { defineProps } from 'vue';

const props = defineProps({
  result: {
    type: Object,
    required: true,
  },
});
</script>

<style scoped>
/* Tailwind CSS utilities will apply */
</style>
