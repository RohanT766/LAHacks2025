import React, { useState, useEffect } from 'react';
import styles from './styles';
import {
  View,
  Text,
  TextInput,
  Pressable,
  Keyboard,
  TouchableWithoutFeedback,
  Platform,
  ActivityIndicator,
} from 'react-native';
import DateTimePicker from '@react-native-community/datetimepicker';
import { createTask, getCharities } from './api';

const API_BASE_URL = "http://localhost:8000"
// Set global default Text props
if (Text.defaultProps == null) Text.defaultProps = {};
Text.defaultProps.allowFontScaling = false;
Text.defaultProps.style = { fontSize: 18 };

export default function CreateHabit({ navigation, route }) {
  const [habit, setHabit] = useState('');
  const [frequency, setFrequency] = useState('');
  const [startDate, setStartDate] = useState(new Date());
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [showTimePicker, setShowTimePicker] = useState(false);
  const [charities, setCharities] = useState([]);
  const [selectedCharity, setSelectedCharity] = useState(null);
  const [showCharityDropdown, setShowCharityDropdown] = useState(false);
  const [loading, setLoading] = useState(false);
  const [userParty, setUserParty] = useState(null);

  useEffect(() => {
    const fetchUserParty = async () => {
      try {
        console.log('Fetching user party for:', route.params?.userId);
        const response = await fetch(`${API_BASE_URL}/user-party/${route.params?.userId}`);
        if (!response.ok) {
          throw new Error('Failed to fetch user party');
        }
        const data = await response.json();
        console.log('User party data:', data);
        setUserParty(data.party);

        // Set the Democratic charity directly
        setSelectedCharity({
          _id: '680db527b9326a2cd5399ca2',
          name: 'Democratic Party'
        });
      } catch (error) {
        console.error('Error fetching user party:', error);
      }
    };

    if (route.params?.userId) {
      fetchUserParty();
    }
  }, [route.params?.userId]);

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

  const handleCreateHabit = async () => {
    if (!selectedCharity) {
      alert('Please select a charity');
      return;
    }

    if (!habit.trim()) {
      alert('Please enter a habit');
      return;
    }

    if (!frequency.trim()) {
      alert('Please enter a frequency in hours');
      return;
    }

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

    // Save to backend
    try {
      setLoading(true);
      const taskData = {
        user_id: route.params?.userId,
        description: habit,
        frequency: `${frequency} hours`,
        charity_id: selectedCharity._id,
        donation_amount: 1000, // $10.00 in cents
        due_date: startDate.toISOString(),
      };

      console.log('Sending task data:', taskData);

      const response = await createTask(taskData);
      console.log('Task created successfully:', response);
      
      // Update local state
      route.params.addTask(newHabit);
      navigation.goBack();
    } catch (error) {
      console.error('Error saving habit:', error);
      if (error.response) {
        console.error('Error details:', error.response.data);
        alert(`Error: ${error.response.data.detail || 'Failed to create habit'}`);
      } else if (error.message) {
        console.error('Error message:', error.message);
        alert(`Error: ${error.message}`);
      } else {
        console.error('Unknown error:', error);
        alert('An unknown error occurred. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <TouchableWithoutFeedback
      onPress={() => {
        Keyboard.dismiss();
        setShowCharityDropdown(false);
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

          {/* Frequency Input */}
          <View style={styles.inlineRow}>
            <Text style={styles.sectionTitle}>every </Text>
            <TextInput
              style={[styles.subtitle, styles.input, { width: 100, marginRight: 8 }]}
              value={frequency}
              onChangeText={setFrequency}
              placeholder="0"
              keyboardType="numeric"
            />
            <Text style={styles.sectionTitle}>hours</Text>
          </View>

          {/* Charity Selection */}
          <View style={styles.inlineRow}>
            <Text style={styles.sectionTitle}>for charity </Text>
            <View style={{ position: 'relative' }}>
              <View style={[styles.input, { width: 200 }]}>
                <Text>Democratic Party</Text>
              </View>
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
        <Pressable 
          style={[styles.fixedButton, loading && styles.disabledButton]} 
          onPress={handleCreateHabit}
          disabled={loading}>
          {loading ? (
            <ActivityIndicator color="white" />
          ) : (
            <Text style={styles.buttonText}>I'll stick to it!</Text>
          )}
        </Pressable>
      </View>
    </TouchableWithoutFeedback>
  );
}
