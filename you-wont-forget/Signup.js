import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  Pressable,
  Keyboard,
  TouchableWithoutFeedback,
  Alert,
  ActivityIndicator,
} from 'react-native';
import styles from './styles';
import { registerUser } from './api';

const API_BASE_URL = 'http://localhost:8000';

export default function SignupScreen({ navigation }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [nickname, setNickname] = useState('');
  const [phone, setPhone] = useState('');
  const [loading, setLoading] = useState(false);

  const validatePhone = (phoneNumber) => {
    // Basic phone number validation (10 digits)
    const phoneRegex = /^\d{10}$/;
    return phoneRegex.test(phoneNumber.replace(/\D/g, ''));
  };

  const handleSignup = async () => {
    // Validate all required fields
    if (!email || !password || !nickname || !phone) {
      Alert.alert('Error', 'Please fill in all required fields');
      return;
    }

    // Validate phone number format
    if (!validatePhone(phone)) {
      Alert.alert('Error', 'Please enter a valid 10-digit phone number');
      return;
    }

    setLoading(true);
    try {
      const userData = {
        email,
        password,
        nickname,
        phone
      };

      const response = await registerUser(userData);
      console.log('Signup successful:', response);

      // Navigate to Twitter linking screen
      navigation.reset({
        routes: [
          {
            name: 'SignupInfo',
            params: {
              user: {
                id: response.user_id,
                email: email,
                nickname: nickname
              }
            }
          }
        ]
      });
    } catch (error) {
      console.error('Signup error:', error);
      
      // Check if the error is due to email already existing
      if (error.message && error.message.includes('already exists')) {
        Alert.alert(
          'Account Exists',
          'An account with this email already exists. Would you like to log in?',
          [
            {
              text: 'Cancel',
              style: 'cancel'
            },
            {
              text: 'Log In',
              onPress: () => {
                // Navigate to login screen with the email pre-filled
                navigation.reset({
                  routes: [
                    {
                      name: 'Signin',
                      params: { email }
                    }
                  ]
                });
              }
            }
          ]
        );
      } else {
        Alert.alert('Error', error.message || 'Failed to create account');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <TouchableWithoutFeedback onPress={Keyboard.dismiss}>
      <View style={styles.container}>
        <View style={styles.content}>
          <View style={styles.header}>
            <Text style={styles.title}>Create your account</Text>
            <Text style={[styles.subtitle, { marginBottom: 16 }]}>
              Let's get started with your journey
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

          {/* Nickname */}
          <View style={styles.inlineRow}>
            <Text style={styles.sectionTitle}>Nickname</Text>
            <TextInput
              style={[styles.subtitle, styles.input, { width: 200, marginLeft: 'auto' }]}
              value={nickname}
              onChangeText={setNickname}
              placeholder="Your nickname"
              editable={!loading}
            />
          </View>

          {/* Phone */}
          <View style={styles.inlineRow}>
            <Text style={styles.sectionTitle}>Phone</Text>
            <TextInput
              style={[styles.subtitle, styles.input, { width: 200, marginLeft: 'auto' }]}
              value={phone}
              onChangeText={setPhone}
              keyboardType="phone-pad"
              placeholder="1234567890"
              editable={!loading}
            />
          </View>

          {/* Sign in link */}
          <Pressable
            style={[styles.fixedButton, { backgroundColor: 'transparent', bottom: 150 }]}
            onPress={() => navigation.reset({ routes: [{ name: 'Signin' }] })}
            disabled={loading}
          >
            <Text style={styles.buttonText}>I already have an account</Text>
          </Pressable>

          {/* Sign up button */}
          <Pressable
            style={styles.fixedButton}
            onPress={handleSignup}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.buttonText}>Create Account</Text>
            )}
          </Pressable>
        </View>
      </View>
    </TouchableWithoutFeedback>
  );
}

