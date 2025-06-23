import { defineStore } from 'pinia';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_APP_API_URL || 'http://localhost:8000/api';

export const useAnalysisStore = defineStore('analysis', {
  state: () => ({
    currentTask: null,
    tasks: [],
    loading: false,
    error: null,
  }),
  actions: {
    async submitAnalysis(textContent) {
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.post(`${API_BASE_URL}/analysis/submit`, { text_content: textContent });
        this.currentTask = {
          id: response.data.task_id,
          status: 'pending', // Initial status set by Laravel
          input_data: textContent,
          result: null,
          createdAt: new Date().toISOString(),
        };
        this.tasks.unshift(this.currentTask);
        this.loading = false;
        return this.currentTask.id;
      } catch (err) {
        this.error = '提交任務失敗: ' + (err.response?.data?.message || err.message);
        this.loading = false;
        throw err;
      }
    },
    async fetchTaskStatus(taskId) {
      if (!taskId) return;
      this.loading = true;
      try {
        const response = await axios.get(`${API_BASE_URL}/analysis/${taskId}/status`);
        const taskIndex = this.tasks.findIndex(t => t.id === taskId);
        if (taskIndex !== -1) {
          this.tasks[taskIndex].status = response.data.status;
          this.tasks[taskIndex].result = response.data.result;
          this.tasks[taskIndex].input_data = response.data.input_data; // Ensure input_data is updated
        } else {
          // If task is not in current list (e.g., page refresh), add it
          this.tasks.unshift({
            id: response.data.task_id,
            status: response.data.status,
            input_data: response.data.input_data || '載入中...',
            result: response.data.result,
            createdAt: response.data.created_at,
          });
        }
        this.loading = false;
        return response.data;
      } catch (err) {
        this.error = '查詢任務狀態失敗: ' + (err.response?.data?.message || err.message);
        this.loading = false;
        throw err;
      }
    },
  },
});
