<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\Api\AnalysisController;
use App\Http\Controllers\Api\InternalAnalysisUpdateController; // For internal worker updates

/*
|--------------------------------------------------------------------------
| API Routes
|--------------------------------------------------------------------------
|
| Here is where you can register API routes for your application. These
| routes are loaded by the RouteServiceProvider and all of them will
| be assigned to the "api" middleware group. Make something great!
|
*/

// Public API for frontend
Route::prefix('analysis')->group(function () {
    Route::post('/submit', [AnalysisController::class, 'submitAnalysis']);
    Route::get('/{uuid}/status', [AnalysisController::class, 'getAnalysisStatus']);
});

// Internal API for worker callbacks (should be secured, e.g., with IP whitelisting or shared secret)
Route::prefix('internal/analysis')->group(function () {
    Route::post('/update', [InternalAnalysisUpdateController::class, 'updateStatus']);
});
