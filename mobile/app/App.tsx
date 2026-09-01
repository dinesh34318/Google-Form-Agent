import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View, TextInput, Button, ScrollView, ActivityIndicator, Alert } from 'react-native';
import * as Linking from 'expo-linking';
import { analyzeForm, generateAnswers, generatePrefilledUrl } from './src/services/api';

export default function App() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [debugLogs, setDebugLogs] = useState<string[]>([]);
  const [prefilledUrl, setPrefilledUrl] = useState<string | null>(null);

  const addLog = (msg: string) => {
    console.log(msg);
    setDebugLogs(prev => [...prev, msg]);
  };

  useEffect(() => {
    addLog(`[INIT] EXPO_PUBLIC_API_URL: ${process.env.EXPO_PUBLIC_API_URL || 'UNDEFINED'}`);
  }, []);
  
  const handleAutofill = async () => {
    if (!url) {
      Alert.alert('Error', 'Please enter a valid Google Form URL');
      return;
    }
    
    setDebugLogs([]);
    setLoading(true);
    setPrefilledUrl(null);
    addLog(`[START] Button Pressed`);
    addLog(`[CONFIG] EXPO_PUBLIC_API_URL: ${process.env.EXPO_PUBLIC_API_URL}`);
    
    try {
      // 1. Analyze
      addLog(`[API Call] Endpoint: ${process.env.EXPO_PUBLIC_API_URL}/analyze`);
      const analyzeResult = await analyzeForm(url);
      addLog(`[API Response] /analyze Success`);
      
      // 2. Map Profile
      addLog(`[API Call] Endpoint: ${process.env.EXPO_PUBLIC_API_URL}/generate-answers`);
      const ansResult = await generateAnswers(analyzeResult.questions);
      addLog(`[API Response] /generate-answers Success`);
      
      // 3. Generate Link
      addLog(`[API Call] Endpoint: ${process.env.EXPO_PUBLIC_API_URL}/generate-prefilled-url`);
      const generatedUrl = await generatePrefilledUrl(url, analyzeResult.questions, ansResult.answers);
      addLog(`[API Response] /generate-prefilled-url Success`);
      addLog(`[RESULT] Prefilled URL received:\n${generatedUrl}`);
      
      // 4. Update UI to show button
      setPrefilledUrl(generatedUrl);
      setLoading(false);
      
    } catch (e: any) {
      setLoading(false);
      addLog(`[ERROR] Flow failed: ${e.message}`);
      Alert.alert('Error', e.message || 'Failed to process form');
    }
  };

  const openForm = async () => {
    if (!prefilledUrl) return;
    try {
        addLog(`[LINKING] Testing Linking.canOpenURL...`);
        const canOpen = await Linking.canOpenURL(prefilledUrl);
        addLog(`[LINKING] Can open URL: ${canOpen}`);
        
        if (!canOpen) {
            addLog(`[LINKING ERROR] Device claims it cannot open the URL.`);
            Alert.alert('Error', 'Cannot open the URL on this device.');
            return;
        }
        
        addLog(`[LINKING] Calling Linking.openURL()...`);
        await Linking.openURL(prefilledUrl);
        addLog(`[LINKING] Linking.openURL() returned successfully.`);
    } catch (linkError: any) {
        addLog(`[LINKING ERROR] ${linkError.message}`);
        Alert.alert('Linking Error', linkError.message || 'Failed to open URL');
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.scrollContainer} style={styles.container}>
      <Text style={styles.title}>FormAgent Debug</Text>
      
      <TextInput
        style={styles.urlInput}
        value={url}
        onChangeText={setUrl}
        placeholder="https://docs.google.com/forms/..."
        autoCapitalize="none"
      />
      
      <View style={styles.buttonContainer}>
        <Button title="Open & Autofill" onPress={handleAutofill} color="#2196F3" disabled={loading} />
      </View>

      {loading && <ActivityIndicator size="large" color="#0000ff" style={{ marginVertical: 20 }} />}
      
      {prefilledUrl && !loading && (
        <View style={styles.successContainer}>
          <Text style={styles.successText}>Ready to open form!</Text>
          <Button title="Execute Linking.openURL()" onPress={openForm} color="#4CAF50" />
        </View>
      )}

      <View style={styles.logContainer}>
        <Text style={styles.logTitle}>Debug Logs:</Text>
        {debugLogs.map((log, i) => (
          <Text key={i} style={styles.logText}>{log}</Text>
        ))}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  scrollContainer: {
    padding: 20,
    paddingTop: 60,
    alignItems: 'center',
    paddingBottom: 40,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
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
  successContainer: {
    width: '100%',
    marginVertical: 20,
    padding: 15,
    backgroundColor: '#e8f5e9',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#4CAF50',
    alignItems: 'center'
  },
  successText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#2e7d32',
    marginBottom: 15
  },
  logContainer: {
    width: '100%',
    marginTop: 20,
    padding: 10,
    backgroundColor: '#f5f5f5',
    borderRadius: 5,
    borderWidth: 1,
    borderColor: '#ddd',
    minHeight: 200
  },
  logTitle: {
    fontWeight: 'bold',
    marginBottom: 10,
    fontSize: 16
  },
  logText: {
    fontSize: 12,
    fontFamily: 'monospace',
    marginBottom: 5,
    color: '#333'
  }
});
