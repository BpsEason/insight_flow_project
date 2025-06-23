<?php

namespace Tests\Feature;

use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Foundation\Testing\WithFaker;
use Tests\TestCase;
use App\Models\AnalysisTask;
use Illuminate\Support\Facades\Queue;
use Illuminate\Support\Facades\Redis; // Use Redis Facade for testing queue push
use Illuminate\Support\Str;
use App\Jobs\ProcessAnalysisTask;

class AnalysisApiTest extends TestCase
{
    use RefreshDatabase, WithFaker;

    /**
     * Setup the test environment.
     *
     * @return void
     */
    protected function setUp(): void
    {
        parent::setUp();
        Redis::del(env('REDIS_QUEUE_NAME_FASTAPI', 'fastapi_analysis_queue')); // Clear Redis queue before each test
        Queue::fake(); // Prevent jobs from being run immediately
    }

    /**
     * Test submitting a new analysis task.
     *
     * @return void
     */
    public function test_can_submit_analysis_task()
    {
        $textContent = $this->faker->sentence(20);

        $response = $this->postJson('/api/analysis/submit', [
            'text_content' => $textContent,
        ]);

        $response->assertStatus(202)
                 ->assertJsonStructure(['message', 'task_id']);

        // Assert that the task was created in the database
        $this->assertDatabaseHas('analysis_tasks', [
            'input_data' => $textContent,
            'status' => 'pending', // Initial status before job dispatch
        ]);

        // Assert that the Laravel job was pushed to Laravel's internal queue
        Queue::assertPushed(ProcessAnalysisTask::class, function ($job) use ($textContent) {
            return $job->textContent === $textContent;
        });

        // Test the handle method of the job directly to simulate Redis push
        // This is a more direct way to test what the Job does.
        $task = AnalysisTask::where('input_data', $textContent)->first();
        $job = new ProcessAnalysisTask($task->uuid, $textContent);
        $job->handle();

        // Assert that task status changed in DB
        $this->assertDatabaseHas('analysis_tasks', [
            'uuid' => $task->uuid,
            'status' => 'queued_for_worker',
        ]);

        // Assert that the message was pushed to the FastAPI Redis queue
        $pushedData = json_decode(Redis::rpop(env('REDIS_QUEUE_NAME_FASTAPI', 'fastapi_analysis_queue')), true);
        $this->assertNotNull($pushedData);
        $this->assertEquals($task->uuid, $pushedData['task_id']);
        $this->assertEquals($textContent, $pushedData['text_content']);
    }

    /**
     * Test getting analysis task status.
     *
     * @return void
     */
    public function test_can_get_analysis_task_status()
    {
        $task = AnalysisTask::create([
            'uuid' => (string) Str::uuid(),
            'input_data' => $this->faker->sentence(),
            'status' => 'completed',
            'result' => ['analysis_output' => ['summary' => ['Test Summary'], 'sentiment_score' => ['label' => 'positive', 'score' => 0.9]]],
        ]);

        $response = $this->getJson("/api/analysis/{$task->uuid}/status");

        $response->assertStatus(200)
                 ->assertJson([
                     'task_id' => $task->uuid,
                     'status' => 'completed',
                     'result' => ['analysis_output' => ['summary' => ['Test Summary'], 'sentiment_score' => ['label' => 'positive', 'score' => 0.9]]],
                     'input_data' => $task->input_data,
                 ]);
    }

    /**
     * Test getting status for a non-existent task.
     *
     * @return void
     */
    public function test_cannot_get_status_for_non_existent_task()
    {
        $response = $this->getJson('/api/analysis/' . Str::uuid() . '/status');
        $response->assertStatus(404)
                 ->assertJson(['error' => 'Task not found']);
    }

    /**
     * Test submitting analysis with invalid input.
     *
     * @return void
     */
    public function test_submit_analysis_with_invalid_input()
    {
        $response = $this->postJson('/api/analysis/submit', [
            'text_content' => 'short', // Too short
        ]);
        $response->assertStatus(422)
                 ->assertJsonValidationErrors(['text_content']);

        $response = $this->postJson('/api/analysis/submit', []); // Missing
        $response->assertStatus(422)
                 ->assertJsonValidationErrors(['text_content']);
    }

    /**
     * Test internal update endpoint.
     */
    public function test_internal_update_task_status()
    {
        $task = AnalysisTask::create([
            'uuid' => (string) Str::uuid(),
            'input_data' => 'Some input data',
            'status' => 'queued_for_worker',
            'result' => null,
        ]);

        $updateData = [
            'task_id' => $task->uuid,
            'status' => 'completed',
            'result' => ['analysis_output' => ['summary' => ['Final Summary'], 'sentiment_score' => ['label' => 'positive', 'score' => 0.99]]],
        ];

        $response = $this->postJson('/api/internal/analysis/update', $updateData);

        $response->assertStatus(200)
                 ->assertJson(['message' => 'Task status updated successfully']);

        $this->assertDatabaseHas('analysis_tasks', [
            'uuid' => $task->uuid,
            'status' => 'completed',
            'result' => $updateData['result'],
        ]);
    }

    /**
     * Test internal update with invalid task ID.
     */
    public function test_internal_update_invalid_task_id()
    {
        $updateData = [
            'task_id' => (string) Str::uuid(), // Non-existent UUID
            'status' => 'completed',
            'result' => ['analysis_output' => ['summary' => ['Invalid Task']]],
        ];

        $response = $this->postJson('/api/internal/analysis/update', $updateData);
        $response->assertStatus(404)
                 ->assertJson(['error' => 'Task not found']);
    }

    /**
     * Test internal update with invalid status.
     */
    public function test_internal_update_invalid_status()
    {
        $task = AnalysisTask::create([
            'uuid' => (string) Str::uuid(),
            'input_data' => 'Some input data',
            'status' => 'queued_for_worker',
            'result' => null,
        ]);

        $updateData = [
            'task_id' => $task->uuid,
            'status' => 'invalid_status', // Invalid status
            'result' => ['analysis_output' => ['summary' => ['Invalid Status']]],
        ];

        $response = $this->postJson('/api/internal/analysis/update', $updateData);
        $response->assertStatus(422)
                 ->assertJsonValidationErrors(['status']);
    }
}
