import React, { useState } from 'react';
import { StyleSheet, Text, View, TextInput, Button, ActivityIndicator, Alert } from 'react-native';
import * as Linking from 'expo-linking';
import { analyzeForm, generateAnswers, generatePrefilledUrl } from './src/services/api';

export default function App() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingMsg, setLoadingMsg] = useState('');
  const [prefilledUrl, setPrefilledUrl] = useState<string | null>(null);
  
  const handleAutofill = async () => {
    if (!url) {
      Alert.alert('Error', 'Please enter a valid Google Form URL');
      return;
    }
    
    console.log(`[DEBUG] EXPO_PUBLIC_API_URL: ${process.env.EXPO_PUBLIC_API_URL}`);
    setLoading(true);
    setPrefilledUrl(null);
    
    try {
      // 1. Analyze
      setLoadingMsg('Opening form...');
      const analyzeResult = await analyzeForm(url);
      
      // 2. Map Profile
      setLoadingMsg('Reading questions...\nMatching profile...');
      const ansResult = await generateAnswers(analyzeResult.questions);
      
      // 3. Generate Link
      setLoadingMsg('Filling known answers...');
      const generatedUrl = await generatePrefilledUrl(url, analyzeResult.questions, ansResult.answers);
      console.log(`[DEBUG] Received Prefilled URL: ${generatedUrl}`);
      
      // 4. Update UI to show button
      setPrefilledUrl(generatedUrl);
      setLoading(false);
      
    } catch (e: any) {
      setLoading(false);
      console.error(`[DEBUG] Autofill Flow Error: ${e.message}`);
      Alert.alert('Error', e.message || 'Failed to process form');
    }
  };

  const openForm = async () => {
    if (!prefilledUrl) return;
    try {
        const canOpen = await Linking.canOpenURL(prefilledUrl);
        console.log(`[DEBUG] Linking.canOpenURL: ${canOpen}`);
        if (!canOpen) {
            console.error(`[DEBUG] Cannot open URL. Linking.canOpenURL returned false.`);
            Alert.alert('Error', 'Cannot open the URL on this device.');
            return;
        }
        console.log(`[DEBUG] Executing Linking.openURL...`);
        await Linking.openURL(prefilledUrl);
        console.log(`[DEBUG] Linking.openURL succeeded!`);
    } catch (linkError: any) {
        console.error(`[DEBUG] Linking.openURL Error: ${linkError.message}`);
        Alert.alert('Linking Error', linkError.message || 'Failed to open URL');
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

  if (prefilledUrl) {
    return (
      <View style={styles.centerContainer}>
        <Text style={styles.title}>Success!</Text>
        <Text style={styles.loadingText}>We have filled known answers.</Text>
        <Text style={styles.loadingText}>Please review the form, edit if necessary, and click Submit.</Text>
        <View style={{ marginTop: 30, width: '100%' }}>
          <Button title="Open Google Form" onPress={openForm} color="#4CAF50" />
        </View>
        <View style={{ marginTop: 20, width: '100%' }}>
          <Button title="Start Over" onPress={() => setPrefilledUrl(null)} color="#f44336" />
        </View>
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
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    textAlign: 'center',
    lineHeight: 24,
    color: '#666'
  }
});
