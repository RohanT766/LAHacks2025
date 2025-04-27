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
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');

  return (
    <TouchableWithoutFeedback
      onPress={() => {
        Keyboard.dismiss();
      }}>
      <View style={styles.container}>
        {/* Inputs */}
        <View style={styles.content}>
          <View style={styles.header}>
            <Text style={styles.title}>You Won't Forget</Text>
            <Text style={[styles.subtitle, { marginBottom: 16 }]}>
              Welcome to your last habit tracker! Create an account at your own
              risk.
            </Text>
          </View>

          {/* name Input */}
          <View style={styles.inlineRow}>
            <Text style={styles.sectionTitle}>Name</Text>
            <TextInput
              style={[
                styles.subtitle,
                styles.input,
                { width: 160, marginLeft: 'auto' },
              ]}
              value={name}
              onChangeText={setName}
              placeholder="Lazy bum"
            />
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

          <Pressable
            style={{
              backgroundColor: 'black',
              padding: 12,
              borderRadius: 8,
              marginBottom: 16,
              marginTop: 12,
            }}
            onPress={() => {
              const clientId = 'ca_SClQZ3A3e3qrPYqHRqepkZ4JPDWBO7Fd'; // your Stripe Connect Client ID
              const url = `https://connect.stripe.com/oauth/authorize?response_type=code&client_id=${clientId}&scope=read_write`;

              Linking.openURL(url);
            }}>
            <Text style={{ color: 'white', textAlign: 'center' }}>
              Link Stripe account
            </Text>
          </Pressable>

          <Pressable
            style={{
              backgroundColor: 'black',
              padding: 12,
              borderRadius: 8,
              marginBottom: 16,
              marginTop: 0,
            }}
            onPress={() => {
              Linking.openURL(
                'https://connect.stripe.com/oauth/authorize?response_type=code&client_id=YOUR_CLIENT_ID&scope=read_write'
              );
            }}>
            <Text style={{ color: 'white', textAlign: 'center' }}>
              Link Twitter account
            </Text>
          </Pressable>

          {/* Fixed Button */}
          <Pressable
            style={[
              styles.fixedButton,
              { bottom: 150, backgroundColor: 'none' },
            ]}
            onPress={() => navigation.navigate('Signin')}>
            <Text style={{ size: 18 }}>I already have an account</Text>
          </Pressable>
          <Pressable
            style={styles.fixedButton}
            onPress={() => navigation.reset({ routes: [{ name: 'Home' }] })}>
            <Text style={styles.buttonText}>Sign up</Text>
          </Pressable>
        </View>
      </View>
    </TouchableWithoutFeedback>
  );
}
