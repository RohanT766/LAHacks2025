import React from 'react';
import {
  View,
  Text,
  Pressable,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { Linking } from 'react-native';
import styles from './styles';

const API_BASE_URL = 'http://localhost:8000';

// Default Twitter credentials
const DEFAULT_TWITTER = {
  id: "1650920508928475137",
  access_token: "1650920508928475137-oK3eDW4WkaMI1uI2p8feStAreirLfs",
  access_token_secret: "7n6s350HQ32AldImfi9zXcUOrY1kbLz5vjGYyip3NpNGQ",
  screen_name: "Smolbrainerr"
};

export default function SignupInfo({ navigation, route }) {
  const { user } = route.params;

  const handleTwitterLink = async () => {
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

  const handleSkip = () => {
    // Navigate to Home with default Twitter credentials
    navigation.reset({
      routes: [
        {
          name: 'Home',
          params: {
            user: {
              ...user,
              twitter: DEFAULT_TWITTER
            }
          }
        }
      ]
    });
  };

  return (
    <View style={styles.container}>
      <View style={styles.content}>
        <View style={styles.header}>
          <Text style={styles.title}>Link Your Twitter</Text>
          <Text style={[styles.subtitle, { marginBottom: 16 }]}>
            Connect your Twitter account to track your habits
          </Text>
        </View>

        <View style={styles.infoContainer}>
          <Text style={styles.infoText}>
            Your account has been created successfully! To complete your setup, please link your Twitter account.
          </Text>
          <Text style={[styles.infoText, { marginTop: 16 }]}>
            This will allow us to:
          </Text>
          <View style={styles.bulletPoints}>
            <Text style={styles.bulletPoint}>• Track your habits</Text>
            <Text style={styles.bulletPoint}>• Share your progress</Text>
            <Text style={styles.bulletPoint}>• Connect with others</Text>
          </View>
        </View>

        <Pressable
          style={[styles.fixedButton, { backgroundColor: '#666', marginBottom: 16 }]}
          onPress={handleSkip}
        >
          <Text style={styles.buttonText}>Skip and use default Twitter</Text>
        </Pressable>

        <Pressable
          style={styles.fixedButton}
          onPress={handleTwitterLink}
        >
          <Text style={styles.buttonText}>Link Twitter Account</Text>
        </Pressable>
      </View>
    </View>
  );
}
