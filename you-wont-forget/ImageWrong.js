import React from 'react';
import { View, Image, StyleSheet, Text, Pressable } from 'react-native';
import styles from './styles'; // shared styling


export default function ImageWrong({ route, navigation }) {
  const { photoUri } = route.params;

  return (
    <View style={styles.container}>
      <View style={styles.content}>
        <View style={styles.header}>
          <Text style={styles.title}>Photo not verified ❌</Text>
          <Text style={styles.subtitle}>Geez you're not only lazy you're also a liar</Text>
        </View>

        <View style={photoDone.container}>
          <Image source={{ uri: photoUri }} style={photoDone.image} />
        </View>

        <Pressable
          style={styles.fixedButton}
          onPress={() => navigation.reset({ routes: [{ name: 'Home' }] })}
        >
          <Text style={styles.buttonText}>Return to tasks</Text>
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
