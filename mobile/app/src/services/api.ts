import { Platform } from 'react-native';
import { FormAnalysisResponse, GenerateAnswersResponse, FormQuestion, AnswerDecision, UrlGeneratorResponse } from '../types';

const API_BASE = process.env.EXPO_PUBLIC_API_URL;

if (!API_BASE) {
    console.warn("WARNING: EXPO_PUBLIC_API_URL is not set. API requests will fail.");
}

export const analyzeForm = async (url: string): Promise<FormAnalysisResponse> => {
    try {
        const res = await fetch(`${API_BASE}/analyze`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'bypass-tunnel-reminder': 'true',
                'User-Agent': 'FormAgent/1.0'
            },
            body: JSON.stringify({ form_url: url })
        });
        if (!res.ok) throw new Error(await res.text());
        return await res.json();
    } catch (e) {
        console.error("[API Error] analyzeForm:", e);
        throw e;
    }
};

export const generateAnswers = async (questions: FormQuestion[]): Promise<GenerateAnswersResponse> => {
    try {
        const res = await fetch(`${API_BASE}/generate-answers`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'bypass-tunnel-reminder': 'true',
                'User-Agent': 'FormAgent/1.0'
            },
            body: JSON.stringify({ questions })
        });
        if (!res.ok) throw new Error(await res.text());
        return await res.json();
    } catch (e) {
        console.error("[API Error] generateAnswers:", e);
        throw e;
    }
};

export const generatePrefilledUrl = async (url: string, questions: FormQuestion[], answers: AnswerDecision[]): Promise<string> => {
    try {
        const res = await fetch(`${API_BASE}/generate-prefilled-url`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'bypass-tunnel-reminder': 'true',
                'User-Agent': 'FormAgent/1.0'
            },
            body: JSON.stringify({ form_url: url, questions, answers })
        });
        if (!res.ok) throw new Error(await res.text());
        const data: UrlGeneratorResponse = await res.json();
        return data.prefilled_url || url;
    } catch (e) {
        console.error("[API Error] generatePrefilledUrl:", e);
        throw e;
    }
};
