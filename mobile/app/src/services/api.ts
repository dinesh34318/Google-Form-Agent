import { Platform } from 'react-native';
import { FormAnalysisResponse, GenerateAnswersResponse, FormQuestion, AnswerDecision, UrlGeneratorResponse } from '../types';

const API_BASE = process.env.EXPO_PUBLIC_API_URL;

if (!API_BASE) {
    console.warn("WARNING: EXPO_PUBLIC_API_URL is not set. API requests will fail.");
}

export const analyzeForm = async (url: string): Promise<FormAnalysisResponse> => {
    const endpoint = `${API_BASE}/analyze`;
    console.log(`[API Call] Endpoint: ${endpoint}`);
    try {
        const res = await fetch(endpoint, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'bypass-tunnel-reminder': 'true',
                'User-Agent': 'FormAgent/1.0'
            },
            body: JSON.stringify({ form_url: url })
        });
        console.log(`[API Response] ${endpoint} - Status: ${res.status}`);
        const text = await res.text();
        console.log(`[API Body] ${text.substring(0, 500)}...`);
        if (!res.ok) throw new Error(`Status ${res.status}: ${text}`);
        return JSON.parse(text);
    } catch (e) {
        console.error("[API Error] analyzeForm:", e);
        throw e;
    }
};

export const generateAnswers = async (questions: FormQuestion[]): Promise<GenerateAnswersResponse> => {
    const endpoint = `${API_BASE}/generate-answers`;
    console.log(`[API Call] Endpoint: ${endpoint}`);
    try {
        const res = await fetch(endpoint, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'bypass-tunnel-reminder': 'true',
                'User-Agent': 'FormAgent/1.0'
            },
            body: JSON.stringify({ questions })
        });
        console.log(`[API Response] ${endpoint} - Status: ${res.status}`);
        const text = await res.text();
        console.log(`[API Body] ${text.substring(0, 500)}...`);
        if (!res.ok) throw new Error(`Status ${res.status}: ${text}`);
        return JSON.parse(text);
    } catch (e) {
        console.error("[API Error] generateAnswers:", e);
        throw e;
    }
};

export const generatePrefilledUrl = async (url: string, questions: FormQuestion[], answers: AnswerDecision[]): Promise<string> => {
    const endpoint = `${API_BASE}/generate-prefilled-url`;
    console.log(`[API Call] Endpoint: ${endpoint}`);
    try {
        const res = await fetch(endpoint, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'bypass-tunnel-reminder': 'true',
                'User-Agent': 'FormAgent/1.0'
            },
            body: JSON.stringify({ form_url: url, questions, answers })
        });
        console.log(`[API Response] ${endpoint} - Status: ${res.status}`);
        const text = await res.text();
        console.log(`[API Body] ${text.substring(0, 500)}...`);
        if (!res.ok) throw new Error(`Status ${res.status}: ${text}`);
        const data: UrlGeneratorResponse = JSON.parse(text);
        return data.prefilled_url || url;
    } catch (e) {
        console.error("[API Error] generatePrefilledUrl:", e);
        throw e;
    }
};
