export interface FormQuestion {
    id: string;
    question: string;
    type: string;
    required: boolean;
    options?: string[];
}

export interface FormAnalysisResponse {
    form_title: string;
    questions: FormQuestion[];
}

export interface AnswerDecision {
    question: string;
    profile_field: string | null;
    answer: any | null;
    confidence: number;
    needs_user_input: boolean;
    reason: string;
}

export interface GenerateAnswersResponse {
    answers: AnswerDecision[];
}

export interface UserAnswer {
    id: string; // we can just pass id as question text for now
    question: string;
    answer: any;
}
