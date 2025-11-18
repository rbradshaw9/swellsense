import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  StyleSheet,
  Alert,
} from 'react-native';
import { api, Session } from '../services/api';

export default function LogSessionScreen() {
  const [spotName, setSpotName] = useState('');
  const [rating, setRating] = useState(5);
  const [wavesCaught, setWavesCaught] = useState('');
  const [durationMinutes, setDurationMinutes] = useState('');
  const [waveHeightFt, setWaveHeightFt] = useState('');
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSave = async () => {
    if (!spotName) {
      Alert.alert('Error', 'Please enter a spot name');
      return;
    }

    setLoading(true);
    try {
      const session: Session = {
        spot_name: spotName,
        session_date: new Date().toISOString(),
        rating,
        waves_caught: wavesCaught ? parseInt(wavesCaught) : undefined,
        duration_minutes: durationMinutes ? parseInt(durationMinutes) : undefined,
        wave_height_ft: waveHeightFt ? parseFloat(waveHeightFt) : undefined,
        notes: notes || undefined,
      };

      await api.createSession(session);

      Alert.alert('Success!', 'Session logged successfully', [
        {
          text: 'OK',
          onPress: () => {
            // Reset form
            setSpotName('');
            setRating(5);
            setWavesCaught('');
            setDurationMinutes('');
            setWaveHeightFt('');
            setNotes('');
          },
        },
      ]);
    } catch (error) {
      Alert.alert('Error', error instanceof Error ? error.message : 'Failed to save session');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Log Surf Session</Text>
        <Text style={styles.subtitle}>Track your sessions to get better recommendations</Text>
      </View>

      <View style={styles.form}>
        <Text style={styles.label}>Spot Name *</Text>
        <TextInput
          style={styles.input}
          placeholder="e.g., Tres Palmas, Domes"
          value={spotName}
          onChangeText={setSpotName}
        />

        <Text style={styles.label}>How was it? (1-10)</Text>
        <View style={styles.ratingContainer}>
          {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((num) => (
            <TouchableOpacity
              key={num}
              style={[styles.ratingButton, rating === num && styles.ratingButtonActive]}
              onPress={() => setRating(num)}
            >
              <Text style={[styles.ratingText, rating === num && styles.ratingTextActive]}>
                {num}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        <Text style={styles.label}>Waves Caught</Text>
        <TextInput
          style={styles.input}
          placeholder="12"
          value={wavesCaught}
          onChangeText={setWavesCaught}
          keyboardType="number-pad"
        />

        <Text style={styles.label}>Session Length (minutes)</Text>
        <TextInput
          style={styles.input}
          placeholder="90"
          value={durationMinutes}
          onChangeText={setDurationMinutes}
          keyboardType="number-pad"
        />

        <Text style={styles.label}>Wave Height (ft)</Text>
        <TextInput
          style={styles.input}
          placeholder="4.5"
          value={waveHeightFt}
          onChangeText={setWaveHeightFt}
          keyboardType="decimal-pad"
        />

        <Text style={styles.label}>Notes</Text>
        <TextInput
          style={[styles.input, styles.textArea]}
          placeholder="Clean waves, light crowd, fun lefts..."
          value={notes}
          onChangeText={setNotes}
          multiline
          numberOfLines={4}
          textAlignVertical="top"
        />

        <TouchableOpacity
          style={[styles.saveButton, loading && styles.saveButtonDisabled]}
          onPress={handleSave}
          disabled={loading}
        >
          <Text style={styles.saveButtonText}>
            {loading ? 'Saving...' : 'Save Session'}
          </Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  header: {
    padding: 20,
    paddingTop: 60,
    backgroundColor: '#0EA5E9',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 14,
    color: '#fff',
    opacity: 0.9,
  },
  form: {
    padding: 20,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1E293B',
    marginBottom: 8,
    marginTop: 12,
  },
  input: {
    height: 50,
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#E2E8F0',
    borderRadius: 8,
    paddingHorizontal: 16,
    fontSize: 16,
  },
  textArea: {
    height: 100,
    paddingTop: 12,
  },
  ratingContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  ratingButton: {
    width: 50,
    height: 50,
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#E2E8F0',
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
  },
  ratingButtonActive: {
    backgroundColor: '#0EA5E9',
    borderColor: '#0EA5E9',
  },
  ratingText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#64748B',
  },
  ratingTextActive: {
    color: '#fff',
  },
  saveButton: {
    backgroundColor: '#0EA5E9',
    height: 56,
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 24,
    marginBottom: 40,
  },
  saveButtonDisabled: {
    opacity: 0.6,
  },
  saveButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '600',
  },
});
