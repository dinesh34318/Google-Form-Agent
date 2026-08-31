# FormAgent 🤖

Your personal AI-powered Google Form filling assistant. 

FormAgent reads Google Forms, understands the questions, matches them to your personal profile using AI, and securely fills out the form on your behalf—always leaving the final submission to you.

## Features
- **Intelligent Question Matching**: Uses AI to understand questions regardless of phrasing.
- **Privacy First**: Keeps your personal data separate from AI models. No training on your data.
- **Review Before Submit**: Automatically fills the form but requires your manual review and submission.
- **Cross-Platform Mobile App**: Built with React Native & Expo.
- **Robust Automation**: Powered by Playwright and Python backend.

## Project Structure
- `/backend`: FastAPI Python server with Playwright & OpenAI integration.
- `/mobile/app`: Expo React Native application.
- `/data`: Local storage for your personal profile.

## Setup Instructions

### 1. Configure Profile
Edit `data/profile.json` with your personal information.

### 2. Backend Setup
```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

pip install -r requirements.txt
playwright install chromium

# Create .env file based on .env.example
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 3. Run Backend
```bash
cd backend
python main.py
# Server runs on http://0.0.0.0:8000
```

### 4. Mobile Setup
```bash
cd mobile/app
npm install
```

### 5. Run Mobile App
```bash
cd mobile/app
# Set backend URL if running on physical device, e.g. EXPO_PUBLIC_API_URL=http://192.168.1.x:8000
npx expo start
```

## How It Works
1. **Analyze Form**: The mobile app sends the Google Form URL to the backend. The backend uses Playwright to open the form and extract questions.
2. **AI Matching**: The backend sends the question text (but not your full profile) to OpenAI. The AI determines which profile field matches the question.
3. **Review**: The mobile app shows you the proposed answers. You can edit any answer or provide missing information.
4. **Fill**: Once confirmed, the backend uses Playwright to fill the browser session with your approved answers.
5. **Submit**: You review the filled form in the Playwright browser window on your computer and manually click Submit.
