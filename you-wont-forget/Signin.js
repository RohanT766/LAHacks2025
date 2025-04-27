import React, { useState } from 'react';
import styles from './styles';

import {
  View,
  Text,
  TextInput,
  Pressable,
  Keyboard,
  TouchableWithoutFeedback,
  Linking,
} from 'react-native';

// Set global default Text props
if (Text.defaultProps == null) Text.defaultProps = {};
Text.defaultProps.allowFontScaling = false;
Text.defaultProps.style = { fontSize: 18 };

export default function CreateProfile({ navigation }) {
  const [phone, setPhone] = useState('');
  const [code, setCode] = useState('');

  return (
    <TouchableWithoutFeedback
      onPress={() => {
        Keyboard.dismiss();
      }}>
      <View style={styles.container}>
        {/* Inputs */}
        <View style={styles.content}>
          <View style={styles.header}>
            <Text style={styles.title}>Welcome back!</Text>
            <Text style={[styles.subtitle, { marginBottom: 16 }]}>
              You know the stakes.
            </Text>
          </View>

          <View style={styles.inlineRow}>
            <Text style={styles.sectionTitle}>Phone #</Text>
            <TextInput
              style={[
                styles.subtitle,
                styles.input,
                { width: 160, marginLeft: 'auto' },
              ]}
              value={phone}
              onChangeText={setPhone}
              placeholder="1-800-nothing"
            />
          </View>
          
          {/* password Input */}
          <View style={styles.inlineRow}>
            <Text style={styles.sectionTitle}>Code</Text>
            <TextInput
              style={[
                styles.subtitle,
                styles.input,
                { width: 160, marginLeft: 'auto' },
              ]}
              value={code}
              onChangeText={setCode}
              placeholder="Password"
            />
          </View>

          {/* Fixed Button */}
          <Pressable
            style={[styles.fixedButton, {bottom: 150, backgroundColor: 'none'}]}
            onPress={() => navigation.reset({ routes: [{ name: 'Signup' }] })}>
            <Text style={{size: 18}}>I need to sign up</Text>
          </Pressable>
          <Pressable
            style={styles.fixedButton}
            onPress={() => navigation.reset({ routes: [{ name: 'Home' }] })}>
            <Text style={styles.buttonText}>Log in</Text>
          </Pressable>
        </View>
      </View>
    </TouchableWithoutFeedback>
  );
}
