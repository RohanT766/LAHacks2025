import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  Pressable,
  Keyboard,
  TouchableWithoutFeedback,
  Alert,
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
        // Reset stack and go to Home, passing user data
        navigation.reset({
          routes: [{ name: 'Home', params: { user: payload } }],
        });
      }
    } catch (err) {
      Alert.alert('Network error', 'Please try again.');
    } finally {
      setLoading(false);
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

          <View style={styles.inlineRow}>
            <Text style={styles.sectionTitle}>Email</Text>
            <TextInput
              style={[styles.subtitle, styles.input, { width: 200, marginLeft: 'auto' }]}
              value={email}
              onChangeText={setEmail}
              autoCapitalize="none"
              keyboardType="email-address"
              placeholder="you@example.com"
            />
          </View>

          <View style={styles.inlineRow}>
            <Text style={styles.sectionTitle}>Password</Text>
            <TextInput
              style={[styles.subtitle, styles.input, { width: 200, marginLeft: 'auto' }]}
              value={password}
              onChangeText={setPassword}
              secureTextEntry
              placeholder="••••••••"
            />
          </View>

          <Pressable
            style={[styles.fixedButton, { backgroundColor: 'transparent', bottom: 150 }]}
            onPress={() => navigation.reset({ routes: [{ name: 'Signup' }] })}>
            <Text style={styles.buttonText}>I need to sign up</Text>
          </Pressable>

          <Pressable
            style={styles.fixedButton}
            onPress={handleLogin}
            disabled={loading}>
            <Text style={styles.buttonText}>
              {loading ? 'Logging in…' : 'Log in'}
            </Text>
          </Pressable>
        </View>
      </View>
    </TouchableWithoutFeedback>
  );
}
