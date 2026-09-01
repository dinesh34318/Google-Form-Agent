export interface FormQuestion {
    id: string;
    question: string;
    type: string;
    required: boolean;
    options?: string[];
    entry_id?: string;
}

export interface FormAnalysisResponse {
    form_title: string;
    questions: FormQuestion[];
    session_id: string;
}

export interface AnswerDecision {
    question: string;
    profile_field?: string;
    answer?: any;
    confidence: number;
    fill: boolean;
    reason: string;
}

export interface GenerateAnswersResponse {
    answers: AnswerDecision[];
}

export interface UrlGeneratorResponse {
    prefilled_url: string;
}

export interface UserAnswer {
    id: string; // we can just pass id as question text for now
    question: string;
    answer: any;
}
