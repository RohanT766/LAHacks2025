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
          <Text style={[styles.title, { marginBottom: 12 }]}>Thanks!</Text>

          {/* Frequency and Interval */}
          <View style={styles.inlineRow}>
            <Text>
              We're going to donate to Donald Trump with every habit
              you miss.
            </Text>

            
          </View>
        </View>

        {/* Fixed Button */}
        <Pressable
          style={styles.fixedButton}
          onPress={() => navigation.navigate('Home')}>
          <Text style={styles.buttonText}>Create my first habit</Text>
        </Pressable>
      </View>
    </TouchableWithoutFeedback>
  );
}
