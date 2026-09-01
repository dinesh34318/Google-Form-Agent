import React, { useState } from 'react';
import { StyleSheet, Text, View, TextInput, Button, ScrollView, ActivityIndicator, Alert } from 'react-native';
import * as Linking from 'expo-linking';
import { analyzeForm, generateAnswers, generatePrefilledUrl } from './src/services/api';
import { FormAnalysisResponse, AnswerDecision, FormQuestion } from './src/types';

export default function App() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingMsg, setLoadingMsg] = useState('');
  
  const handleAutofill = async () => {
    if (!url) {
      Alert.alert('Error', 'Please enter a valid Google Form URL');
      return;
    }
    
    setLoading(true);
    
    try {
      // 1. Analyze
      setLoadingMsg('Opening form...');
      const analyzeResult = await analyzeForm(url);
      
      // 2. Map Profile
      setLoadingMsg('Reading questions...\nMatching profile...');
      const ansResult = await generateAnswers(analyzeResult.questions);
      
      // 3. Generate Link
      setLoadingMsg('Filling known answers...');
      const prefilledUrl = await generatePrefilledUrl(url, analyzeResult.questions, ansResult.answers);
      
      // 4. Open in Phone Browser
      setLoading(false);
      Alert.alert(
        'Form is ready for your review.',
        'We have filled known answers. Please review the form, edit if necessary, and click Submit.',
        [
          { text: 'Cancel', style: 'cancel' },
          { text: 'Open Form', onPress: () => Linking.openURL(prefilledUrl) }
        ]
      );
      
    } catch (e: any) {
      setLoading(false);
      Alert.alert('Error', e.message || 'Failed to process form');
    }
  };

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#0000ff" />
        <Text style={styles.loadingText}>{loadingMsg}</Text>
      </View>
    );
  }

  return (
    <View style={styles.centerContainer}>
      <Text style={styles.title}>FormAgent</Text>
      
      <TextInput
        style={styles.urlInput}
        value={url}
        onChangeText={setUrl}
        placeholder="https://docs.google.com/forms/..."
        autoCapitalize="none"
      />
      
      <View style={styles.buttonContainer}>
        <Button title="Open & Autofill" onPress={handleAutofill} color="#2196F3" />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  centerContainer: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 40,
    color: '#333'
  },
  urlInput: {
    width: '100%',
    height: 50,
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 8,
    paddingHorizontal: 15,
    marginBottom: 20,
    fontSize: 16
  },
  buttonContainer: {
    width: '100%',
    marginVertical: 10,
    borderRadius: 8,
    overflow: 'hidden'
  },
  loadingText: {
    marginTop: 20,
    fontSize: 16,
    textAlign: 'center',
    lineHeight: 24,
    color: '#666'
  }
});
