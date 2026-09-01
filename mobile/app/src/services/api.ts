import { Platform } from 'react-native';
import { FormAnalysisResponse, GenerateAnswersResponse, FormQuestion, AnswerDecision, UrlGeneratorResponse } from '../types';

// Use relative path for web so it works automatically when hosted by FastAPI.
const API_BASE = process.env.EXPO_PUBLIC_API_URL || (Platform.OS === 'web' ? '' : 'http://10.0.2.2:8000');

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

export const generatePrefilledUrl = async (url: string, questions: FormQuestion[], answers: AnswerDecision[]): Promise<string> => {
    const res = await fetch(`${API_BASE}/generate-prefilled-url`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ form_url: url, questions, answers })
    });
    if (!res.ok) throw new Error(await res.text());
    const data: UrlGeneratorResponse = await res.json();
    return data.prefilled_url || url;
};
