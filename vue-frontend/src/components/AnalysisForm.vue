<template>
  <form @submit.prevent="submitForm">
    <div class="mb-4">
      <label for="text_content" class="block text-gray-700 text-sm font-bold mb-2">請輸入您想分析的內容:</label>
      <textarea
        id="text_content"
        v-model="textContent"
        rows="8"
        class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
        placeholder="例如：今天有 30 位顧客來電詢問保健食品，其中 12 位表示近期有胃部不適..."
        required
      ></textarea>
    </div>
    <div v-if="error" class="text-red-500 text-sm mb-4">{{ error }}</div>
    <button
      type="submit"
      :disabled="loading"
      class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline disabled:opacity-50 disabled:cursor-not-allowed"
    >
      {{ loading ? '提交中...' : '提交分析' }}
    </button>
  </form>
</template>

<script setup>
import { ref, defineEmits } from 'vue';

const textContent = ref('');
const loading = ref(false);
const error = ref(null);
const emit = defineEmits(['submit-text']);

const submitForm = async () => {
  loading.value = true;
  error.value = null;
  try {
    await emit('submit-text', textContent.value);
    textContent.value = ''; // Clear input field on success
  } catch (err) {
    error.value = err.message || '提交失敗，請重試。';
  } finally {
    loading.value = false;
  }
};
</script>
