<?php

namespace App\Jobs;

use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;
use Illuminate\Support\Facades\Redis; // Use Laravel's Redis Facade
use App\Models\AnalysisTask;
use Illuminate\Support\Facades\Log;

class ProcessAnalysisTask implements ShouldQueue
{
    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    protected $taskId;
    protected $textContent;

    /**
     * Create a new job instance.
     */
    public function __construct(string $taskId, string $textContent)
    {
        $this->taskId = $taskId;
        $this->textContent = $textContent;
    }

    /**
     * Execute the job.
     * This job dispatches a message to Redis for the FastAPI worker to consume.
     */
    public function handle(): void
    {
        $task = AnalysisTask::where('uuid', $this->taskId)->first();
        if (!$task) {
            Log::error("Task {$this->taskId} not found in database for dispatch to FastAPI worker.");
            return;
        }

        try {
            // Update status to indicate it's now queued for FastAPI worker
            $task->update(['status' => 'queued_for_worker']);
            Log::info("Task {$this->taskId} status updated to queued_for_worker.");

            // Push the task details to a Redis list/queue that FastAPI worker listens to
            // Using `lpush` or `rpush` to push to a list. `fastapi_analysis_queue` should be defined in .env
            Redis::rpush(env('REDIS_QUEUE_NAME_FASTAPI', 'fastapi_analysis_queue'), json_encode([
                'task_id' => $this->taskId,
                'text_content' => $this->textContent,
            ]));

            Log::info("Task {$this->taskId} successfully pushed to FastAPI Redis queue.");

        } catch (\Exception $e) {
            $errorMessage = "Failed to push task {$this->taskId} to FastAPI Redis queue: " . $e->getMessage();
            $task->update([
                'status' => 'failed_dispatch',
                'result' => ['error' => 'Failed to dispatch to worker queue', 'details' => $e->getMessage()],
            ]);
            Log::error($errorMessage, ['exception' => $e]);
        }
    }
}
