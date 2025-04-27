import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  Pressable,
  Keyboard,
  TouchableWithoutFeedback,
  Linking,
  Alert,
  ActivityIndicator
} from 'react-native';
import { registerUser } from './api'; // Import the API service
const API_BASE_URL = 'http://localhost:8000';  // or wherever your FastAPI is running
import styles from './styles';

// Set global default Text props
if (Text.defaultProps == null) Text.defaultProps = {};
Text.defaultProps.allowFontScaling = false;
Text.defaultProps.style = { fontSize: 18 };

export default function CreateProfile({ navigation }) {
  const [nickname, setNickname] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [phone, setPhone] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSignUp = async () => {
    Keyboard.dismiss();
    setError('');
    
    // Basic validation
    if (!email.trim()) {
      setError('Email is required');
      return;
    }
    if (!password) {
      setError('Password is required');
      return;
    }
    if (!nickname.trim()) {
      setError('Name is required');
      return;
    }
    
    setIsLoading(true);
    
    try {
      const userData = { 
        email: email.trim(), 
        password, 
        nickname: nickname.trim(),
        phone: phone.trim() // Include phone number
      };
      
      const data = await registerUser(userData);
      
      console.log('Registration successful:', data);
      
      Alert.alert('Success', 'Account created!', [
        { text: 'OK', onPress: () => navigation.reset({ index: 0, routes: [{ name: 'Home' }] }) },
      ]);
    } catch (err) {
      console.error('Registration Error:', err);
      
      // Provide user-friendly error messages based on status codes
      if (err.status === 503) {
        setError('Server is temporarily unavailable. Please try again later.');
      } else if (err.status === 400 && err.message.includes('already exists')) {
        setError('This email is already registered. Please try signing in instead.');
      } else if (err.message.includes('Network request failed')) {
        setError('Network error. Please check your internet connection and try again.');
      } else {
        // Limit error message length for UI
        setError(err.message.length > 100 ? err.message.substring(0, 100) + '...' : err.message);
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <TouchableWithoutFeedback onPress={Keyboard.dismiss}>
      <View style={styles.container}>
        <View style={styles.content}>
          <View style={styles.header}>
            <Text style={styles.title}>You Won't Forget</Text>
            <Text style={[styles.subtitle, { marginBottom: 8 }]}>
              Welcome to your last habit tracker! Create an account at your own risk.
            </Text>
            {error ? (
              <Text style={{ color: 'red', marginBottom: 12, textAlign: 'center' }}>
                {error}
              </Text>
            ) : null}
          </View>

          {/* Nickname Input */}
          <View style={styles.inlineRow}>
            <Text style={styles.sectionTitle}>Name</Text>
            <TextInput
              style={[styles.subtitle, styles.input, { width: 160, marginLeft: 'auto' }]}
              value={nickname}
              onChangeText={setNickname}
              placeholder="Lazy bum"
              editable={!isLoading}
            />
          </View>

          {/* Email Input */}
          <View style={styles.inlineRow}>
            <Text style={styles.sectionTitle}>Email</Text>
            <TextInput
              style={[styles.subtitle, styles.input, { width: 200, marginLeft: 'auto' }]}
              value={email}
              onChangeText={setEmail}
              placeholder="you@example.com"
              keyboardType="email-address"
              autoCapitalize="none"
              editable={!isLoading}
            />
          </View>

          {/* Password Input */}
          <View style={styles.inlineRow}>
            <Text style={styles.sectionTitle}>Password</Text>
            <TextInput
              style={[styles.subtitle, styles.input, { width: 200, marginLeft: 'auto' }]}
              value={password}
              onChangeText={setPassword}
              placeholder="••••••••"
              secureTextEntry
              editable={!isLoading}
            />
          </View>

          {/* Phone Input */}
          <View style={styles.inlineRow}>
            <Text style={styles.sectionTitle}>Phone #</Text>
            <TextInput
              style={[styles.subtitle, styles.input, { width: 160, marginLeft: 'auto' }]}
              value={phone}
              onChangeText={setPhone}
              placeholder="1-800-nothing"
              keyboardType="phone-pad"
              editable={!isLoading}
            />
          </View>

          {/* Link Stripe & Twitter (placeholders) */}
          <Pressable
            style={{ backgroundColor: 'black', padding: 12, borderRadius: 8, marginBottom: 16, marginTop: 12 }}
            onPress={() => {
              const clientId = 'placeholder';
              const url = `https://connect.stripe.com/oauth/authorize?response_type=code&client_id=${clientId}&scope=read_write`;
              Linking.openURL(url);
            }}
            disabled={isLoading}
          >
            <Text style={{ color: 'white', textAlign: 'center' }}>Link Stripe account</Text>
          </Pressable>

          <Pressable
            style={{
              backgroundColor: '#1DA1F2',  // Twitter blue
              padding: 12,
              borderRadius: 8,
              marginBottom: 16,
              flexDirection: 'row',
              justifyContent: 'center',
              alignItems: 'center',
            }}
            onPress={() => {
              // This will open your FastAPI redirect endpoint in the device's browser
              Linking.openURL(`${API_BASE_URL}/login/twitter`);
            }}
            disabled={isLoading}
          >
            <Text style={{ color: 'white', fontWeight: '600', textAlign: 'center' }}>
              Log in with Twitter
            </Text>
          </Pressable>


          {/* Navigation */}
          <Pressable
            style={[styles.fixedButton, { bottom: 150, backgroundColor: 'transparent' }]}
            onPress={() => navigation.navigate('Signin')}
            disabled={isLoading}
          >
            <Text style={{ fontSize: 16 }}>I already have an account</Text>
          </Pressable>

          {/* Sign Up Button */}
          <Pressable 
            style={[
              styles.fixedButton, 
              isLoading ? { opacity: 0.7 } : null
            ]} 
            onPress={handleSignUp}
            disabled={isLoading}
          >
            {isLoading ? (
              <ActivityIndicator color="#fff" size="small" />
            ) : (
              <Text style={styles.buttonText}>Sign up</Text>
            )}
          </Pressable>
        </View>
      </View>
    </TouchableWithoutFeedback>
  );
}

