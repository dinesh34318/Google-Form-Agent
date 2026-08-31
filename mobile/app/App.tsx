import React, { useState } from 'react';
import { StyleSheet, Text, View, TextInput, Button, ScrollView, ActivityIndicator, Alert } from 'react-native';
import { analyzeForm, generateAnswers, fillForm } from './src/services/api';
import { FormAnalysisResponse, AnswerDecision, UserAnswer, FormQuestion } from './src/types';

export default function App() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingMsg, setLoadingMsg] = useState('');
  const [analysis, setAnalysis] = useState<FormAnalysisResponse | null>(null);
  const [decisions, setDecisions] = useState<AnswerDecision[]>([]);
  const [userAnswers, setUserAnswers] = useState<Record<string, any>>({});
  
  const handleAnalyze = async () => {
    if (!url) {
      Alert.alert('Error', 'Please enter a valid URL');
      return;
    }
    setLoading(true);
    setLoadingMsg('Analyzing your form...\n✓ Reading questions');
    try {
      const result = await analyzeForm(url);
      setAnalysis(result);
      
      setLoadingMsg('Analyzing your form...\n✓ Understanding questions\n✓ Matching your profile');
      const ansResult = await generateAnswers(result.questions);
      setDecisions(ansResult.answers);
      
      // Pre-fill userAnswers state
      const initialAnswers: Record<string, any> = {};
      ansResult.answers.forEach(d => {
        if (!d.needs_user_input && d.answer !== null) {
          initialAnswers[d.question] = d.answer;
        }
      });
      setUserAnswers(initialAnswers);
      
    } catch (e: any) {
      Alert.alert('Error', e.message || 'Failed to analyze form');
    } finally {
      setLoading(false);
    }
  };
  
  const handleAnswerChange = (question: string, value: string) => {
    setUserAnswers(prev => ({ ...prev, [question]: value }));
  };
  
  const handleFill = async () => {
    setLoading(true);
    setLoadingMsg('Filling form in browser...');
    
    // Prepare answers
    const answersToSubmit: UserAnswer[] = decisions.map(d => ({
      id: d.question, // Using question text as ID
      question: d.question,
      answer: userAnswers[d.question] || ''
    }));
    
    try {
      const res = await fillForm(url, answersToSubmit);
      Alert.alert('Success', res.message);
    } catch (e: any) {
      Alert.alert('Error', e.message || 'Failed to fill form');
    } finally {
      setLoading(false);
    }
  };

  const renderQuestionInput = (q: FormQuestion, decision: AnswerDecision) => {
    const val = userAnswers[q.question] || '';
    
    // For simplicity in MVP, we just render a text input for everything,
    // but we show options if it's multiple choice or dropdown.
    return (
      <View style={styles.questionContainer} key={q.id}>
        <Text style={styles.questionText}>{q.question} {q.required ? '*' : ''}</Text>
        
        {decision.needs_user_input ? (
          <Text style={styles.needsInputLabel}>❓ Your input is required</Text>
        ) : (
          <Text style={styles.aiKnowsLabel}>✓ Answer found in profile (confidence: {Math.round(decision.confidence*100)}%)</Text>
        )}
        
        {q.options && q.options.length > 0 && (
          <Text style={styles.optionsLabel}>Options: {q.options.join(', ')}</Text>
        )}
        
        <TextInput
          style={styles.input}
          value={String(val)}
          onChangeText={(text) => handleAnswerChange(q.question, text)}
          placeholder="Enter your answer"
        />
      </View>
    );
  };

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#0000ff" />
        <Text style={styles.loadingText}>{loadingMsg}</Text>
      </View>
    );
  }

  if (analysis && decisions.length > 0) {
    return (
      <ScrollView style={styles.container} contentContainerStyle={styles.scrollContent}>
        <Text style={styles.title}>{analysis.form_title}</Text>
        <Text style={styles.subtitle}>Review your answers below</Text>
        
        {analysis.questions.map((q) => {
          const decision = decisions.find(d => d.question === q.question) || {
            question: q.question, profile_field: null, answer: null, confidence: 0, needs_user_input: true, reason: ''
          };
          return renderQuestionInput(q, decision);
        })}
        
        <View style={styles.buttonContainer}>
          <Button title="Fill Google Form" onPress={handleFill} color="#2196F3" />
        </View>
        <Text style={styles.warningText}>Note: The form will be filled in the backend browser. You must manually review and submit it.</Text>
      </ScrollView>
    );
  }

  return (
    <View style={styles.centerContainer}>
      <Text style={styles.title}>FormAgent 🤖</Text>
      <Text style={styles.subtitle}>Paste Google Form URL</Text>
      <TextInput
        style={styles.urlInput}
        value={url}
        onChangeText={setUrl}
        placeholder="https://docs.google.com/forms/..."
        autoCapitalize="none"
      />
      <View style={styles.buttonContainer}>
        <Button title="Analyze Form" onPress={handleAnalyze} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  scrollContent: {
    padding: 20,
    paddingTop: 50,
  },
  centerContainer: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 16,
    marginBottom: 20,
    color: '#666',
  },
  urlInput: {
    width: '100%',
    height: 50,
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 8,
    paddingHorizontal: 15,
    marginBottom: 20,
  },
  buttonContainer: {
    width: '100%',
    marginVertical: 10,
  },
  loadingText: {
    marginTop: 20,
    fontSize: 16,
    textAlign: 'center',
    lineHeight: 24,
  },
  questionContainer: {
    marginBottom: 20,
    padding: 15,
    backgroundColor: '#f9f9f9',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#eee',
  },
  questionText: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 5,
  },
  aiKnowsLabel: {
    color: 'green',
    fontSize: 12,
    marginBottom: 5,
  },
  needsInputLabel: {
    color: 'red',
    fontSize: 12,
    marginBottom: 5,
  },
  optionsLabel: {
    color: '#666',
    fontSize: 12,
    marginBottom: 10,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 5,
    padding: 10,
    backgroundColor: '#fff',
  },
  warningText: {
    marginTop: 20,
    color: '#f57c00',
    textAlign: 'center',
    fontSize: 12,
  }
});
