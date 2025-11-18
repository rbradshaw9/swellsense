import React, { useState, useEffect } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { StatusBar } from 'expo-status-bar';
import { View, ActivityIndicator, StyleSheet } from 'react-native';
import { authService } from './services/auth';
import { api } from './services/api';
import type { Session } from '@supabase/supabase-js';

// Import screens (we'll create these next)
import LoginScreen from './screens/LoginScreen';
import HomeScreen from './screens/HomeScreen';
import LogSessionScreen from './screens/LogSessionScreen';
import SessionsScreen from './screens/SessionsScreen';
import ProfileScreen from './screens/ProfileScreen';

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: '#0EA5E9',
        tabBarInactiveTintColor: '#64748B',
      }}
    >
      <Tab.Screen 
        name="Home" 
        component={HomeScreen}
        options={{
          tabBarLabel: 'Home',
          tabBarIcon: ({ color }) => <View style={[styles.icon, { backgroundColor: color }]} />,
        }}
      />
      <Tab.Screen 
        name="LogSession" 
        component={LogSessionScreen}
        options={{
          tabBarLabel: 'Log Session',
          tabBarIcon: ({ color }) => <View style={[styles.icon, { backgroundColor: color }]} />,
        }}
      />
      <Tab.Screen 
        name="Sessions" 
        component={SessionsScreen}
        options={{
          tabBarLabel: 'History',
          tabBarIcon: ({ color }) => <View style={[styles.icon, { backgroundColor: color }]} />,
        }}
      />
      <Tab.Screen 
        name="Profile" 
        component={ProfileScreen}
        options={{
          tabBarLabel: 'Profile',
          tabBarIcon: ({ color }) => <View style={[styles.icon, { backgroundColor: color }]} />,
        }}
      />
    </Tab.Navigator>
  );
}

export default function App() {
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for existing session
    authService.getSession().then((session) => {
      setSession(session);
      if (session?.access_token) {
        api.setToken(session.access_token);
      }
      setLoading(false);
    });

    // Listen for auth changes
    const { data: { subscription } } = authService.onAuthStateChange((session) => {
      setSession(session);
      if (session?.access_token) {
        api.setToken(session.access_token);
      } else {
        api.clearToken();
      }
    });

    return () => {
      subscription?.unsubscribe();
    };
  }, []);

  if (loading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#0EA5E9" />
      </View>
    );
  }

  return (
    <>
      <StatusBar style="auto" />
      <NavigationContainer>
        <Stack.Navigator screenOptions={{ headerShown: false }}>
          {session ? (
            <Stack.Screen name="Main" component={MainTabs} />
          ) : (
            <Stack.Screen name="Login" component={LoginScreen} />
          )}
        </Stack.Navigator>
      </NavigationContainer>
    </>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
  },
  icon: {
    width: 24,
    height: 24,
    borderRadius: 12,
  },
});
