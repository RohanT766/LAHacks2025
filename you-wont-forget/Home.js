import React, { useState, useRef, useEffect } from 'react';
import { View, Text, ScrollView, Pressable, Image, TextInput, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import styles from './styles'; // shared styling

// Get current date information
const today = new Date();
const currentDay = today.getDay(); // 0-6 (Sunday-Saturday)
const currentDate = today.getDate();

// Format date as "M/D/YYYY"
const formatDate = (date) => {
  const month = date.getMonth() + 1; // getMonth() returns 0-11
  const day = date.getDate();
  const year = date.getFullYear();
  return `${month}/${day}/${year}`;
};

// Generate dates for multiple weeks
const generateDates = () => {
  const days = ['S', 'M', 'T', 'W', 'T', 'F', 'S'];
  const allDates = [];
  
  // Start from 2 weeks before current date
  const startDate = new Date(today);
  startDate.setDate(today.getDate() - 14);
  
  // Generate dates for 5 weeks (2 weeks before, current week, 2 weeks after)
  for (let i = 0; i < 35; i++) {
    const date = new Date(startDate);
    date.setDate(startDate.getDate() + i);
    allDates.push({
      day: days[date.getDay()],
      date: date.getDate(),
      fullDate: new Date(date), // Store the full date object
      isCurrentDay: date.getDate() === currentDate && 
                   date.getMonth() === today.getMonth() && 
                   date.getFullYear() === today.getFullYear()
    });
  }
  
  return allDates;
};

const days = generateDates();

// Helper function to check if a date is today
const isToday = (date) => {
  return date.getDate() === today.getDate() &&
         date.getMonth() === today.getMonth() &&
         date.getFullYear() === today.getFullYear();
};

// Helper function to check if a date is tomorrow
const isTomorrow = (date) => {
  const tomorrow = new Date(today);
  tomorrow.setDate(tomorrow.getDate() + 1);
  return date.getDate() === tomorrow.getDate() &&
         date.getMonth() === tomorrow.getMonth() &&
         date.getFullYear() === tomorrow.getFullYear();
};

const initialTasks = [
  { id: '1', text: 'Feed cat', due: 'today', color: 'red', completed: false },
  { id: '2', text: 'Make my bed', due: 'today', color: 'red', completed: false, photo: true },
  { id: '3', text: 'Take out trash', due: 'tomorrow', color: 'orange', completed: false, photo: true },
  { id: '4', text: 'Shower', due: 'May 19', color: 'green', completed: true },
];

export default function Home({ navigation }) {
  const [tasks, setTasks] = useState(initialTasks);
  const [selectedDate, setSelectedDate] = useState(today);
  const calendarScrollViewRef = useRef(null);

  // Scroll to current date when component mounts
  useEffect(() => {
    const itemWidth = 60;
    const scrollPosition = 14 * itemWidth;
    setTimeout(() => {
      calendarScrollViewRef.current?.scrollTo({
        x: scrollPosition,
        animated: false
      });
    }, 100);
  }, []);

  const toggleTask = (id) => {
    setTasks((prev) =>
      prev.map((task) =>
        task.id === id ? { ...task, completed: !task.completed } : task
      )
    );
  };

  const addTask = (newTask) => {
    setTasks((prev) => [...prev, newTask]);
  };

  // Filter tasks based on selected date
  const getTasksForDate = (date) => {
    // If today is selected, show all tasks
    if (isToday(date)) {
      return {
        todayTasks: tasks.filter(t => t.due === 'today'),
        tomorrowTasks: tasks.filter(t => t.due === 'tomorrow'),
        futureTasks: tasks.filter(t => t.due !== 'today' && t.due !== 'tomorrow')
      };
    }

    // For other dates, filter tasks for that specific date
    const allTasks = tasks.filter(t => {
      if (t.due === 'today') {
        return isToday(date);
      } else if (t.due === 'tomorrow') {
        return isTomorrow(date);
      } else {
        return t.due === formatDate(date);
      }
    });

    // Split tasks into categories
    const todayTasks = allTasks.filter(t => t.due === 'today');
    const tomorrowTasks = allTasks.filter(t => t.due === 'tomorrow');
    const futureTasks = allTasks.filter(t => t.due !== 'today' && t.due !== 'tomorrow');

    return {
      todayTasks,
      tomorrowTasks,
      futureTasks
    };
  };

  const deleteTask = (id) => {
    Alert.alert(
      "Delete Task",
      "Are you sure you want to delete this task?",
      [
        {
          text: "Cancel",
          style: "cancel"
        },
        {
          text: "Delete",
          style: "destructive",
          onPress: () => {
            setTasks(prev => prev.filter(task => task.id !== id));
          }
        }
      ]
    );
  };

  const renderTask = (task) => (
    <View key={task.id}>
      <Pressable
        style={styles.taskContainer}
        onPress={() => {
          if (task.photo) {
            navigation.navigate('Photo', { taskId: task.id });
          } else {
            toggleTask(task.id);
          }
        }}
      >
        <View
          style={[
            styles.checkbox,
            {
              borderColor: task.color,
              backgroundColor: task.completed ? task.color : 'transparent',
            },
          ]}
        >
          {task.completed && (
            <Ionicons name="checkmark" size={16} color="white" />
          )}
        </View>

        <View style={{
          flexDirection: 'row',
          alignItems: 'center',
          justifyContent: 'space-between',
          flex: 1,
          backgroundColor: '#ededed',
          paddingRight: 12,
          borderRadius: 8,
          marginLeft: 8,
        }}>
          <Text style={styles.taskText}>{task.text}</Text>
          <View style={{ flexDirection: 'row', alignItems: 'center' }}>
            {task.photo && (
              <Ionicons
                name="camera"
                size={24}
                color="gray"
                style={{ marginLeft: 8 }}
              />
            )}
            <Pressable
              onPress={() => deleteTask(task.id)}
              style={{ marginLeft: 8 }}
            >
              <Ionicons name="remove-circle" size={20} color="gray" />
            </Pressable>
          </View>
        </View>
      </Pressable>
      {task.due !== 'today' && task.due !== 'tomorrow' && (
        <Text style={styles.deadlineText}>Due: {task.due}</Text>
      )}
    </View>
  );

  const { todayTasks, tomorrowTasks, futureTasks } = getTasksForDate(selectedDate);

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>
          {isToday(selectedDate) ? 'Today' : formatDate(selectedDate)}
        </Text>
        <Text style={styles.subtitle}>Good luck with your habits!</Text>
      </View>

      {/* Horizontal Calendar */}
      <ScrollView 
        ref={calendarScrollViewRef}
        horizontal 
        showsHorizontalScrollIndicator={false} 
        style={styles.calendar}
        contentContainerStyle={styles.calendarContent}
      >
        {days.map((item, index) => (
          <Pressable
            key={index}
            onPress={() => setSelectedDate(item.fullDate)}
          >
            <View style={[
              styles.dayContainer,
              item.isCurrentDay && styles.currentDayContainer,
              selectedDate.getDate() === item.date && 
              selectedDate.getMonth() === item.fullDate.getMonth() &&
              selectedDate.getFullYear() === item.fullDate.getFullYear() && 
              styles.selectedDayContainer
            ]}>
              <Text style={[
                styles.dayText,
                item.isCurrentDay && styles.currentDayText,
                selectedDate.getDate() === item.date && 
                selectedDate.getMonth() === item.fullDate.getMonth() &&
                selectedDate.getFullYear() === item.fullDate.getFullYear() && 
                styles.selectedDayText
              ]}>{item.day}</Text>
              <View style={[
                styles.dateCircle,
                item.isCurrentDay && styles.currentDateCircle,
                selectedDate.getDate() === item.date && 
                selectedDate.getMonth() === item.fullDate.getMonth() &&
                selectedDate.getFullYear() === item.fullDate.getFullYear() && 
                styles.selectedDateCircle
              ]}>
                <Text style={[
                  styles.dateText,
                  item.isCurrentDay && styles.currentDateText,
                  selectedDate.getDate() === item.date && 
                  selectedDate.getMonth() === item.fullDate.getMonth() &&
                  selectedDate.getFullYear() === item.fullDate.getFullYear() && 
                  styles.selectedDateText
                ]}>{item.date}</Text>
              </View>
            </View>
          </Pressable>
        ))}
      </ScrollView>

      {/* Task List */}
      <View style={styles.taskSectionContainer}>
        <ScrollView style={styles.taskSection}>
          {/* Today */}
          {todayTasks.length > 0 && (
            <>
              <Text style={styles.sectionTitle}>Due Today:</Text>
              {todayTasks.map(renderTask)}
            </>
          )}

          {/* Tomorrow */}
          {tomorrowTasks.length > 0 && (
            <>
              <Text style={styles.sectionTitle}>Due Tomorrow:</Text>
              {tomorrowTasks.map(renderTask)}
            </>
          )}

          {/* Future */}
          {futureTasks.length > 0 && (
            <>
              <Text style={styles.sectionTitle}>Future:</Text>
              {futureTasks.map(renderTask)}
            </>
          )}

          {/* No Tasks Message */}
          {todayTasks.length === 0 && tomorrowTasks.length === 0 && futureTasks.length === 0 && (
            <Text style={styles.noTasksText}>No tasks for this day</Text>
          )}
        </ScrollView>
      </View>

      {/* Floating + Button */}
      <Pressable
        style={styles.fab}
        onPress={() => navigation.navigate('NewHabit', { addTask })}
      >
        <View style={{ flexDirection: 'row', alignItems: 'center' }}>
          <Ionicons name="add" size={20} color="white" />
          <Text style={{ marginLeft: 4, fontSize: 16, color: 'white' }}>New habit</Text>
        </View>
      </Pressable>
    </View>
  );
}
