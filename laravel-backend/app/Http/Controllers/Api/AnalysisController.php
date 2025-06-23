<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\CreateAnalysisRequest;
use App\Jobs\ProcessAnalysisTask;
use App\Models\AnalysisTask;
use Illuminate\Http\Request;
use Illuminate\Support\Str;
use Illuminate\Support\Facades\Log;

class AnalysisController extends Controller
{
    /**
     * 提交新的分析任務。
     */
    public function submitAnalysis(CreateAnalysisRequest $request)
    {
        try {
            $task = AnalysisTask::create([
                'uuid' => (string) Str::uuid(),
                'user_id' => null, // Adjust if you have auth
                'input_data' => $request->input('text_content'),
                'status' => 'pending',
                'result' => null,
            ]);

            // Dispatch job to Redis Queue, which will be consumed by FastAPI worker via its own Redis consumer
            ProcessAnalysisTask::dispatch($task->uuid, $request->input('text_content'));

            Log::info("Analysis task submitted: " . $task->uuid);

            return response()->json([
                'message' => '分析任務已提交，請稍後查詢結果。',
                'task_id' => $task->uuid,
            ], 202);
        } catch (\Exception $e) {
            Log::error("Failed to submit analysis task: " . $e->getMessage());
            return response()->json(['error' => 'Failed to submit task', 'details' => $e->getMessage()], 500);
        }
    }

    /**
     * 查詢分析任務狀態與結果。
     */
    public function getAnalysisStatus(Request $request, $uuid)
    {
        $task = AnalysisTask::where('uuid', $uuid)->first();

        if (!$task) {
            return response()->json(['error' => 'Task not found'], 404);
        }

        return response()->json([
            'task_id' => $task->uuid,
            'status' => $task->status,
            'result' => $task->result,
            'created_at' => $task->created_at,
            'updated_at' => $task->updated_at,
            'input_data' => $task->input_data, // Also return input_data for display on frontend
        ]);
    }
}
