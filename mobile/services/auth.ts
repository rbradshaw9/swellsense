/**
 * Supabase Authentication Service
 * Handles login, signup, and session management
 */
import { createClient, Session, User } from '@supabase/supabase-js';
import AsyncStorage from '@react-native-async-storage/async-storage';
import 'react-native-url-polyfill/auto';

const SUPABASE_URL = 'https://mxxlxoizfqsidyyqxqtg.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im14eGx4b2l6ZnFzaWR5eXF4cXRnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjM0NzMzNDQsImV4cCI6MjA3OTA0OTM0NH0.k8HAbhAFhnf11woAhChNoOx9S3uehdO8Z2hgZeB4p7Y';

export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
  auth: {
    storage: AsyncStorage,
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: false,
  },
});

export interface AuthResponse {
  user: User | null;
  session: Session | null;
  error: Error | null;
}

export const authService = {
  /**
   * Sign up with email and password
   */
  async signUp(email: string, password: string): Promise<AuthResponse> {
    try {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
      });
      
      return {
        user: data.user,
        session: data.session,
        error: error ? new Error(error.message) : null,
      };
    } catch (error) {
      return {
        user: null,
        session: null,
        error: error as Error,
      };
    }
  },

  /**
   * Sign in with email and password
   */
  async signIn(email: string, password: string): Promise<AuthResponse> {
    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });
      
      return {
        user: data.user,
        session: data.session,
        error: error ? new Error(error.message) : null,
      };
    } catch (error) {
      return {
        user: null,
        session: null,
        error: error as Error,
      };
    }
  },

  /**
   * Sign out
   */
  async signOut(): Promise<{ error: Error | null }> {
    try {
      const { error } = await supabase.auth.signOut();
      return {
        error: error ? new Error(error.message) : null,
      };
    } catch (error) {
      return {
        error: error as Error,
      };
    }
  },

  /**
   * Get current session
   */
  async getSession(): Promise<Session | null> {
    try {
      const { data } = await supabase.auth.getSession();
      return data.session;
    } catch (error) {
      console.error('Error getting session:', error);
      return null;
    }
  },

  /**
   * Get current user
   */
  async getUser(): Promise<User | null> {
    try {
      const { data } = await supabase.auth.getUser();
      return data.user;
    } catch (error) {
      console.error('Error getting user:', error);
      return null;
    }
  },

  /**
   * Listen to auth state changes
   */
  onAuthStateChange(callback: (session: Session | null) => void) {
    return supabase.auth.onAuthStateChange((_event, session) => {
      callback(session);
    });
  },
};
