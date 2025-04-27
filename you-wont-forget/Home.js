import React, { useState } from 'react';
import { View, Text, ScrollView, Pressable } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import styles from './styles'; // shared styling

const days = [
  { day: 'M', date: 2 },
  { day: 'T', date: 3 },
  { day: 'W', date: 4 },
  { day: 'T', date: 5 },
  { day: 'F', date: 6 },
  { day: 'S', date: 7 },
  { day: 'S', date: 8 },
];

const initialTasks = [
  { id: '1', text: 'Feed cat', due: 'today', color: 'red', completed: false },
  { id: '2', text: 'Make my bed', due: 'today', color: 'red', completed: false, photo: true },
  { id: '3', text: 'Take out trash', due: 'tomorrow', color: 'orange', completed: false, photo: true },
  { id: '4', text: 'Shower', due: 'May 19', color: 'green', completed: true },
];

export default function Home({ navigation }) {
  const [tasks, setTasks] = useState(initialTasks);

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

  const renderTask = (task) => (
    <Pressable
      key={task.id}
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

        {task.photo && (
          <Ionicons
            name="camera"
            size={24}
            color="gray"
            style={{ marginLeft: 8 }}
          />
        )}
      </View>
    </Pressable>
  );

  // ✨ Split tasks into Today, Tomorrow, and Future
  const todayTasks = tasks.filter((t) => t.due === 'today');
  const tomorrowTasks = tasks.filter((t) => t.due === 'tomorrow');
  const futureTasks = tasks.filter((t) => t.due !== 'today' && t.due !== 'tomorrow');

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>Today is 4/26/2025</Text>
        <Text style={styles.subtitle}>Good morning, Olivia!</Text>
      </View>

      {/* Horizontal Calendar */}
      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.calendar}>
        {days.map((item, index) => (
          <View key={index} style={styles.dayContainer}>
            <Text style={styles.dayText}>{item.day}</Text>
            <View style={styles.dateCircle}>
              <Text style={styles.dateText}>{item.date}</Text>
            </View>
          </View>
        ))}
      </ScrollView>

      {/* Task List */}
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
      </ScrollView>

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
