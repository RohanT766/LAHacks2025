import React, { useState } from 'react';
import styles from './styles';
import {
  View,
  Text,
  TextInput,
  Pressable,
  Keyboard,
  TouchableWithoutFeedback,
} from 'react-native';
import DateTimePicker, { DateTimePickerEvent } from '@react-native-community/datetimepicker';

// Set global default Text props
if (Text.defaultProps == null) Text.defaultProps = {};
Text.defaultProps.allowFontScaling = false;
Text.defaultProps.style = { fontSize: 18 };

export default function CreateHabit({ navigation, route }) {
  const [habit, setHabit] = useState('');
  const [frequency, setFrequency] = useState('');
  const [intervalType, setIntervalType] = useState('days');
  const [startDate, setStartDate] = useState(new Date());
  const [showDropdown, setShowDropdown] = useState(false);

  const onChangeDate = (event: DateTimePickerEvent, selectedDate?: Date) => {
    if (event.type === 'dismissed') return;
    const currentDate = selectedDate || startDate;
    setStartDate(currentDate);
  };

  function formatDate(date) {
  const options = { month: 'short', day: 'numeric' };
  return date.toLocaleDateString('en-US', options);
}

function isToday(date) {
  const today = new Date();
  return date.toDateString() === today.toDateString();
}

function isTomorrow(date) {
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  return date.toDateString() === tomorrow.toDateString();
}

const handleCreateHabit = () => {
  let dueLabel = formatDate(startDate);
  let color = 'green';

  if (isToday(startDate)) {
    dueLabel = 'today';
    color = 'red';
  } else if (isTomorrow(startDate)) {
    dueLabel = 'tomorrow';
    color = 'orange';
  }

  const newHabit = {
    id: Math.random().toString(),
    text: habit,
    due: dueLabel,
    color: color,
    completed: false,
  };

  route.params.addTask(newHabit);
  navigation.goBack();
};

  return (
    <TouchableWithoutFeedback
      onPress={() => {
        Keyboard.dismiss();
        setShowDropdown(false);
      }}>
      <View style={styles.container}>
        <View style={styles.content}>
          <Text style={[styles.title, { marginBottom: 24 }]}>Create a new habit</Text>

          {/* Habit Input */}
          <View style={styles.inlineRow}>
            <Text style={styles.sectionTitle}>I want to </Text>
            <TextInput
              style={[styles.subtitle, styles.input, { width: 180 }]}
              value={habit}
              onChangeText={setHabit}
              placeholder="habit"
            />
          </View>

          {/* Frequency and Interval */}
          <View style={styles.inlineRow}>
            <Text style={styles.sectionTitle}>every </Text>
            <TextInput
              style={[styles.subtitle, styles.input, { width: 60 }]}
              value={frequency}
              onChangeText={setFrequency}
              placeholder="0"
              keyboardType="numeric"
            />
            <View style={{ position: 'relative' }}>
              <Pressable
                style={[styles.input, { width: 100 }]}
                onPress={() => setShowDropdown(!showDropdown)}>
                <Text>{intervalType}</Text>
              </Pressable>

              {showDropdown && (
                <View style={styles.dropdown}>
                  {['days', 'weeks', 'months'].map((option) => (
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

          {/* Start Date */}
          <View style={styles.inlineRow}>
            <Text style={styles.sectionTitle}>starting from</Text>
            <DateTimePicker
              value={startDate}
              mode="date"
              display="default"
              onChange={onChangeDate}
              style={{ marginTop: 10 }}
              textColor="black"
            />
          </View>
        </View>

        {/* Fixed Button */}
        <Pressable style={styles.fixedButton} onPress={handleCreateHabit}>
          <Text style={styles.buttonText}>I'll stick to it!</Text>
        </Pressable>
      </View>
    </TouchableWithoutFeedback>
  );
}
