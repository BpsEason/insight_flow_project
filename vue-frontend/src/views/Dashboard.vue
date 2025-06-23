<template>
  <div class="dashboard p-6">
    <h1 class="text-3xl font-bold mb-6">InsightFlow 智慧分析儀表板</h1>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div class="bg-white p-6 rounded-lg shadow">
        <h2 class="text-xl font-semibold mb-4">提交新分析任務</h2>
        <AnalysisForm @submit-text="handleAnalysisSubmit" />
      </div>

      <div class="bg-white p-6 rounded-lg shadow">
        <h2 class="text-xl font-semibold mb-4">我的分析任務</h2>
        <div v-if="analysisStore.loading" class="text-blue-500">處理中...</div>
        <div v-if="analysisStore.error" class="text-red-500">{{ analysisStore.error }}</div>

        <div v-if="analysisStore.tasks.length === 0" class="text-gray-500">
          尚無分析任務，請提交新的內容。
        </div>

        <div v-else>
          <div v-for="task in analysisStore.tasks" :key="task.id" class="mb-4 p-3 border rounded-md">
            <h3 class="font-bold">任務 ID: {{ task.id }}</h3>
            <p>狀態:
              <span :class="{
                'text-yellow-500': task.status === 'pending' || task.status === 'processing' || task.status === 'queued_for_worker',
                'text-green-500': task.status === 'completed',
                'text-red-500': task.status === 'failed' || task.status === 'failed_dispatch'
              }">
                {{ task.status }}
              </span>
              <button v-if="task.status !== 'completed' && task.status !== 'failed' && task.status !== 'failed_dispatch'" @click="pollTaskStatus(task.id)" class="ml-2 text-blue-500 hover:underline">
                刷新狀態
              </button>
            </p>
            <p v-if="task.input_data">輸入內容: {{ task.input_data.substring(0, Math.min(task.input_data.length, 50)) }}...</p>
            <AnalysisResultDisplay v-if="task.status === 'completed' && task.result" :result="task.result.analysis_output" />
            <p v-else-if="task.status === 'failed' || task.status === 'failed_dispatch'" class="text-red-500">處理失敗: {{ task.result?.error?.details || task.result?.error || '未知錯誤' }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue';
import { useAnalysisStore } from '@/stores/analysis';
import AnalysisForm from '@/components/AnalysisForm.vue';
import AnalysisResultDisplay from '@/components/AnalysisResultDisplay.vue';

const analysisStore = useAnalysisStore();
let pollIntervals = {}; // Store intervals per task

const handleAnalysisSubmit = async (textContent) => {
  try {
    const taskId = await analysisStore.submitAnalysis(textContent);
    startPolling(taskId);
  } catch (error) {
    console.error('提交分析失敗:', error);
  }
};

const pollTaskStatus = async (taskId) => {
  await analysisStore.fetchTaskStatus(taskId);
  const task = analysisStore.tasks.find(t => t.id === taskId);
  if (task && (task.status === 'completed' || task.status === 'failed' || task.status === 'failed_dispatch')) {
    clearInterval(pollIntervals[taskId]);
    delete pollIntervals[taskId];
  }
};

const startPolling = (taskId) => {
  if (pollIntervals[taskId]) {
    clearInterval(pollIntervals[taskId]);
  }
  pollIntervals[taskId] = setInterval(() => {
    pollTaskStatus(taskId);
  }, 3000);
};

onUnmounted(() => {
  for (const taskId in pollIntervals) {
    clearInterval(pollIntervals[taskId]);
  }
});
</script>

<style scoped>
/* You'll need to install Tailwind CSS:
   npm install -D tailwindcss postcss autoprefixer
   npx tailwindcss init -p
   Then configure tailwind.config.js to scan .vue files
   And add Tailwind directives to src/assets/main.css
*/
</style>
