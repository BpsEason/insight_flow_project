<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class AnalysisTask extends Model
{
    use HasFactory;

    protected $fillable = [
        'uuid',
        'user_id',
        'input_data',
        'status',
        'result',
    ];

    protected $casts = [
        'result' => 'array',
    ];
}
