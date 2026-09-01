import { Platform } from 'react-native';

const API_BASE = process.env.EXPO_PUBLIC_API_URL;

if (!API_BASE) {
    console.warn("WARNING: EXPO_PUBLIC_API_URL is not set. API requests will fail.");
}

export const generatePrefilledUrl = async (url: string): Promise<string> => {
    const endpoint = `${API_BASE}/generate-prefilled-url`;
    console.log(`[API Call] Endpoint: ${endpoint}`);
    try {
        const res = await fetch(endpoint, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ form_url: url })
        });
        console.log(`[API Response] ${endpoint} - Status: ${res.status}`);
        const text = await res.text();
        console.log(`[API Body] ${text.substring(0, 500)}...`);
        if (!res.ok) throw new Error(`Status ${res.status}: ${text}`);
        const data = JSON.parse(text);
        return data.prefilled_url || url;
    } catch (e) {
        console.error("[API Error] generatePrefilledUrl:", e);
        throw e;
    }
};
