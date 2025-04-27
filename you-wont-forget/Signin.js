import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  Pressable,
  Keyboard,
  TouchableWithoutFeedback,
  Alert,
  Linking,               // ← import Linking
  ActivityIndicator,
} from 'react-native';
import styles from './styles';

const API_BASE_URL = 'http://localhost:8000'; // adjust if needed

export default function LoginScreen({ navigation }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    setLoading(true);
    try {
      const resp = await fetch(`${API_BASE_URL}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      const payload = await resp.json();
      if (!resp.ok) {
        Alert.alert('Login failed', payload.detail || 'Check your credentials');
      } else {
        console.log('Login successful, user data:', payload); // Debug log
        navigation.reset({
          routes: [{ 
            name: 'Home', 
            params: { 
              user: {
                id: payload.user_id,
                email: payload.email,
                nickname: payload.nickname
              }
            } 
          }],
        });
      }
    } catch (error) {
      console.error('Login error:', error);
      Alert.alert('Network error', 'Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleTwitterLogin = async () => {
    try {
      // First, get the Twitter OAuth URL
      const response = await fetch(`${API_BASE_URL}/login/twitter`);
      if (!response.ok) {
        throw new Error('Failed to get Twitter login URL');
      }

      // Open the Twitter login URL in the browser
      const twitterUrl = response.url;
      const supported = await Linking.canOpenURL(twitterUrl);
      
      if (supported) {
        await Linking.openURL(twitterUrl);
      } else {
        Alert.alert('Error', 'Cannot open Twitter login URL');
      }
    } catch (error) {
      console.error('Twitter login error:', error);
      Alert.alert('Error', 'Failed to start Twitter login');
    }
  };

  return (
    <TouchableWithoutFeedback onPress={Keyboard.dismiss}>
      <View style={styles.container}>
        <View style={styles.content}>
          <View style={styles.header}>
            <Text style={styles.title}>Welcome back!</Text>
            <Text style={[styles.subtitle, { marginBottom: 16 }]}>
              You know the stakes.
            </Text>
          </View>

          {/* Email */}
          <View style={styles.inlineRow}>
            <Text style={styles.sectionTitle}>Email</Text>
            <TextInput
              style={[styles.subtitle, styles.input, { width: 200, marginLeft: 'auto' }]}
              value={email}
              onChangeText={setEmail}
              autoCapitalize="none"
              keyboardType="email-address"
              placeholder="you@example.com"
              editable={!loading}
            />
          </View>

          {/* Password */}
          <View style={styles.inlineRow}>
            <Text style={styles.sectionTitle}>Password</Text>
            <TextInput
              style={[styles.subtitle, styles.input, { width: 200, marginLeft: 'auto' }]}
              value={password}
              onChangeText={setPassword}
              secureTextEntry
              placeholder="••••••••"
              editable={!loading}
            />
          </View>

          {/* Sign up link */}
          <Pressable
            style={[styles.fixedButton, { backgroundColor: 'transparent', bottom: 150 }]}
            onPress={() => navigation.reset({ routes: [{ name: 'Signup' }] })}
            disabled={loading}
          >
            <Text style={styles.buttonText}>I need to sign up</Text>
          </Pressable>

          {/* Standard email/password login */}
          <Pressable
            style={styles.fixedButton}
            onPress={handleLogin}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.buttonText}>Log in</Text>
            )}
          </Pressable>

          {/* ——— Divider ——— */}
          <View style={{ marginVertical: 16, alignItems: 'center' }}>
            <Text style={{ color: '#666' }}>or</Text>
          </View>

          {/* Twitter OAuth login */}
          <Pressable
            style={{
              backgroundColor: '#1DA1F2',
              padding: 12,
              borderRadius: 8,
              marginBottom: 16,
              flexDirection: 'row',
              justifyContent: 'center',
              alignItems: 'center',
              opacity: loading ? 0.6 : 1,
            }}
            onPress={handleTwitterLogin}
            disabled={loading}
          >
            <Text style={{ color: 'white', fontWeight: '600' }}>
              Sign in with Twitter
            </Text>
          </Pressable>
        </View>
      </View>
    </TouchableWithoutFeedback>
  );
}
