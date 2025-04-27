import React, { useState } from 'react';
import styles from './styles';
import {
  View,
  Text,
  TextInput,
  Pressable,
  Keyboard,
  TouchableWithoutFeedback,
  Platform,
  Alert,
} from 'react-native';
import DateTimePicker from '@react-native-community/datetimepicker';

const API_BASE_URL = 'http://localhost:8000';

// Set global default Text props
if (Text.defaultProps == null) Text.defaultProps = {};
Text.defaultProps.allowFontScaling = false;
Text.defaultProps.style = { fontSize: 18 };

export default function CreateHabit({ navigation, route }) {
  const [intervalType, setIntervalType] = useState('Pick a party');
  const [showDropdown, setShowDropdown] = useState(false);
  const [loading, setLoading] = useState(false);

  const handlePartySelection = async () => {
    if (intervalType === 'Pick a party') {
      Alert.alert('Error', 'Please select a political party');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/update-party`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: route.params.user.id,
          party: intervalType
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to save party choice');
      }

      // Navigate based on party choice
      if (intervalType === 'Democrat') {
        navigation.navigate('PoliRep', { user: route.params.user });
      } else if (intervalType === 'Republican') {
        navigation.navigate('PoliDem', { user: route.params.user });
      }
    } catch (error) {
      console.error('Error saving party choice:', error);
      Alert.alert('Error', 'Failed to save your party choice. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <TouchableWithoutFeedback
      onPress={() => {
        Keyboard.dismiss();
        setShowDropdown(false);
      }}>
      <View style={styles.container}>
        <View style={styles.content}>
          <Text style={[styles.title, { marginBottom: 12 }]}>
            By the way...
          </Text>

          {/* Frequency and Interval */}
          <View style={styles.inlineRow}>
            <Text style={{ marginBottom: 16, fontSize: 18 }}>
              What most accurately describes your political affiliation?{' '}
            </Text>

            <View style={{ position: 'relative' }}>
              <Pressable
                style={[styles.input, { width: 140 }]}
                onPress={() => setShowDropdown(!showDropdown)}>
                <Text>{intervalType}</Text>
              </Pressable>

              {showDropdown && (
                <View style={[styles.dropdown, { width: 140 }]}>
                  {['Republican', 'Democrat'].map((option) => (
                    <Pressable
                      key={option}
                      style={styles.dropdownItem}
                      onPress={() => {
                        setIntervalType(option);
                        setShowDropdown(false);
                      }}>
                      <Text style={styles.dropdownItemText}>{option}</Text>
                    </Pressable>
                  ))}
                </View>
              )}
            </View>
          </View>
        </View>

        {/* Fixed Button */}
        <Pressable
          style={[styles.fixedButton, loading && styles.disabledButton]}
          onPress={handlePartySelection}
          disabled={loading}>
          <Text style={styles.buttonText}>Why do you ask?</Text>
        </Pressable>
      </View>
    </TouchableWithoutFeedback>
  );
}
