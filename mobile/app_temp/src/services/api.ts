import { FormAnalysisResponse, GenerateAnswersResponse, UserAnswer, FormQuestion } from '../types';

// Use localhost for Android emulator (10.0.2.2) or actual IP for physical device.
// For local testing on same machine (web), use localhost.
const API_BASE = process.env.EXPO_PUBLIC_API_URL || 'http://10.0.2.2:8000'; 
// Note: 10.0.2.2 is the special IP alias to your host loopback interface in Android emulator.

export const analyzeForm = async (url: string): Promise<FormAnalysisResponse> => {
    const res = await fetch(`${API_BASE}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ form_url: url })
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
};

export const generateAnswers = async (questions: FormQuestion[]): Promise<GenerateAnswersResponse> => {
    const res = await fetch(`${API_BASE}/generate-answers`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ questions })
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
};

export const fillForm = async (url: string, answers: UserAnswer[]): Promise<{status: string, session_id: string, message: string}> => {
    const res = await fetch(`${API_BASE}/fill`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ form_url: url, answers })
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
};
