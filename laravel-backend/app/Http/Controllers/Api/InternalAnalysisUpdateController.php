<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\AnalysisTask;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Log;
use Illuminate\Validation\ValidationException;

class InternalAnalysisUpdateController extends Controller
{
    /**
     * Internal endpoint for the FastAPI worker to update task status.
     * This endpoint should be secured (e.g., IP whitelist, shared secret).
     */
    public function updateStatus(Request $request)
    {
        try {
            $validatedData = $request->validate([
                'task_id' => 'required|uuid|exists:analysis_tasks,uuid',
                'status' => 'required|string|in:processing,completed,failed',
                'result' => 'nullable|array',
            ]);

            $task = AnalysisTask::where('uuid', $validatedData['task_id'])->first();

            if (!$task) {
                Log::warning("Internal update: Task {$validatedData['task_id']} not found.");
                return response()->json(['error' => 'Task not found'], 404);
            }

            $task->status = $validatedData['status'];
            if (isset($validatedData['result'])) {
                $task->result = $validatedData['result'];
            }
            $task->save();

            Log::info("Internal update: Task {$validatedData['task_id']} updated to status: {$validatedData['status']}");

            return response()->json(['message' => 'Task status updated successfully']);

        } catch (ValidationException $e) {
            Log::error("Internal update validation error: " . $e->getMessage(), ['errors' => $e->errors()]);
            return response()->json(['error' => 'Validation failed', 'details' => $e->errors()], 422);
        } catch (\Exception $e) {
            Log::error("Internal update failed: " . $e->getMessage(), ['exception' => $e]);
            return response()->json(['error' => 'Internal server error', 'details' => $e->getMessage()], 500);
        }
    }
}
