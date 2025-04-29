import React from 'react';
import { View, Image, StyleSheet, Text, Pressable } from 'react-native';
import styles from './styles'; // shared styling


export default function ImageRight({ route, navigation }) {
  const { photoUri, user } = route.params;

  return (
    <View style={styles.container}>
      <View style={styles.content}>
        <View style={styles.header}>
          <Text style={styles.title}>Photo verified ✅</Text>
          <Text style={styles.subtitle}>Fine, I guess you did the task.</Text>
        </View>

        <View style={photoDone.container}>
          <Image source={{ uri: photoUri }} style={photoDone.image} />
        </View>

        <Pressable
          style={styles.fixedButton}
          onPress={() => navigation.reset({ 
            routes: [{ 
              name: 'Home',
              params: { user: user }
            }] 
          })}
        >
          <Text style={styles.buttonText}>Return to tasks</Text>
        </Pressable>

        <Pressable
          style={[styles.fixedButton, { bottom: 52, backgroundColor: 'transparent' }]}
          onPress={() => navigation.reset({ 
            routes: [{ 
              name: 'Photo',
              params: { user: user }
            }] 
          })}
        >
          <Text style={{ fontSize: 16, color: 'black' }}>Retake photo</Text>
        </Pressable>
      </View>
    </View>
  );
}


const photoDone = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  image: {
    width: '80%',
    height: '60%',
    resizeMode: 'cover',
    borderRadius: 12,
    bottom: 60,
  },
});
