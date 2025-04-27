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
} from 'react-native';
import DateTimePicker from '@react-native-community/datetimepicker';

// Set global default Text props
if (Text.defaultProps == null) Text.defaultProps = {};
Text.defaultProps.allowFontScaling = false;
Text.defaultProps.style = { fontSize: 18 };

export default function CreateHabit({ navigation, route }) {
  const [intervalType, setIntervalType] = useState('Pick a party');
  const [showDropdown, setShowDropdown] = useState(false);

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
          style={styles.fixedButton}
          onPress={() => {
            if (intervalType === 'Democrat') {
              navigation.navigate('PoliRep');
            } else if (intervalType === 'Republican') {
              navigation.navigate('PoliDem');
            }
          }}>
          <Text style={styles.buttonText}>Why do you ask?</Text>
        </Pressable>
      </View>
    </TouchableWithoutFeedback>
  );
}
