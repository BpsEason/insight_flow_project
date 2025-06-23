<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class CreateAnalysisRequest extends FormRequest
{
    /**
     * Determine if the user is authorized to make this request.
     */
    public function authorize(): bool
    {
        return true; // Adjust authorization logic as needed
    }

    /**
     * Get the validation rules that apply to the request.
     *
     * @return array<string, \Illuminate\Contracts\Validation\ValidationRule|array<mixed>|string>
     */
    public function rules(): array
    {
        return [
            'text_content' => ['required', 'string', 'min:10', 'max:5000'],
        ];
    }

    /**
     * Get the error messages for the defined validation rules.
     */
    public function messages(): array
    {
        return [
            'text_content.required' => '分析內容不能為空。',
            'text_content.string' => '分析內容必須是文字。',
            'text_content.min' => '分析內容至少需要 :min 個字元。',
            'text_content.max' => '分析內容不能超過 :max 個字元。',
        ];
    }
}
