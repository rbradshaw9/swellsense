import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ActivityIndicator } from 'react-native';
import { api, SessionStats } from '../services/api';

export default function HomeScreen() {
  const [stats, setStats] = useState<SessionStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const data = await api.getSessionStats();
      setStats(data);
    } catch (error) {
      console.error('Error loading stats:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#0EA5E9" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Welcome to SwellSense</Text>
        <Text style={styles.subtitle}>Your AI surf coach</Text>
      </View>

      <View style={styles.statsCard}>
        <Text style={styles.statsTitle}>Your Stats</Text>
        <View style={styles.statRow}>
          <Text style={styles.statLabel}>Total Sessions</Text>
          <Text style={styles.statValue}>{stats?.total_sessions || 0}</Text>
        </View>
        <View style={styles.statRow}>
          <Text style={styles.statLabel}>Waves Caught</Text>
          <Text style={styles.statValue}>{stats?.total_waves_caught || 0}</Text>
        </View>
        <View style={styles.statRow}>
          <Text style={styles.statLabel}>Hours Surfing</Text>
          <Text style={styles.statValue}>{stats?.total_hours || 0}</Text>
        </View>
        <View style={styles.statRow}>
          <Text style={styles.statLabel}>Average Rating</Text>
          <Text style={styles.statValue}>{stats?.average_rating?.toFixed(1) || '0.0'}</Text>
        </View>
        {stats?.favorite_spot && (
          <View style={styles.statRow}>
            <Text style={styles.statLabel}>Favorite Spot</Text>
            <Text style={styles.statValue}>{stats.favorite_spot}</Text>
          </View>
        )}
      </View>
    </View>
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
    fontSize: 16,
    color: '#fff',
    opacity: 0.9,
  },
  statsCard: {
    margin: 20,
    padding: 20,
    backgroundColor: '#fff',
    borderRadius: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statsTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: '#1E293B',
    marginBottom: 16,
  },
  statRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F1F5F9',
  },
  statLabel: {
    fontSize: 16,
    color: '#64748B',
  },
  statValue: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1E293B',
  },
});
