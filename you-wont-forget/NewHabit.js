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
  const [habit, setHabit] = useState('');
  const [frequency, setFrequency] = useState('');
  const [intervalType, setIntervalType] = useState('days');
  const [startDate, setStartDate] = useState(new Date());
  const [showDropdown, setShowDropdown] = useState(false);
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [showTimePicker, setShowTimePicker] = useState(false);

  const onChangeDate = (event, selectedDate) => {
    if (Platform.OS === 'android') {
      setShowDatePicker(false);
    }
    if (selectedDate) {
      const newDate = new Date(startDate);
      newDate.setFullYear(selectedDate.getFullYear());
      newDate.setMonth(selectedDate.getMonth());
      newDate.setDate(selectedDate.getDate());
      setStartDate(newDate);
    }
  };

  const onChangeTime = (event, selectedTime) => {
    if (Platform.OS === 'android') {
      setShowTimePicker(false);
    }
    if (selectedTime) {
      const newDate = new Date(startDate);
      newDate.setHours(selectedTime.getHours());
      newDate.setMinutes(selectedTime.getMinutes());
      setStartDate(newDate);
    }
  };

  const handleDatePress = () => {
    setShowTimePicker(false);
    setShowDatePicker(!showDatePicker);
  };

  const handleTimePress = () => {
    setShowDatePicker(false);
    setShowTimePicker(!showTimePicker);
  };

  function formatDate(date) {
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  }

  function formatTime(date) {
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
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
      time: formatTime(startDate),
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
              style={[styles.subtitle, styles.input, { width: 60, marginRight: 8 }]}
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

          {/* Start Date and Time */}
          <View style={styles.inlineRow}>
            <Text style={styles.sectionTitle}>starting from</Text>
            <View style={styles.dateTimeContainer}>
              <Pressable
                style={styles.dateButton}
                onPress={handleDatePress}
              >
                <Text style={styles.dateButtonText}>{formatDate(startDate)}</Text>
              </Pressable>
              <Pressable
                style={styles.timeButton}
                onPress={handleTimePress}
              >
                <Text style={styles.timeButtonText}>{formatTime(startDate)}</Text>
              </Pressable>
            </View>
          </View>

          {showDatePicker && (
            <DateTimePicker
              value={startDate}
              mode="date"
              display={Platform.OS === 'ios' ? 'spinner' : 'default'}
              onChange={onChangeDate}
              textColor="black"
              themeVariant="light"
              style={{ marginLeft: -24 }}
            />
          )}

          {showTimePicker && (
            <DateTimePicker
              value={startDate}
              mode="time"
              display={Platform.OS === 'ios' ? 'spinner' : 'default'}
              onChange={onChangeTime}
              textColor="black"
              themeVariant="light"
              style={{ marginLeft: -24 }}
            />
          )}
        </View>

        {/* Fixed Button */}
        <Pressable style={styles.fixedButton} onPress={handleCreateHabit}>
          <Text style={styles.buttonText}>I'll stick to it!</Text>
        </Pressable>
      </View>
    </TouchableWithoutFeedback>
  );
}
