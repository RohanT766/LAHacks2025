// App.js
import React from 'react';
import { Text, View } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { Linking } from 'react-native';

import Home from './Home'; 
import NewHabit from './NewHabit'; 
import Signup from './Signup';
import Signin from './Signin';
import SignupInfo from './SignupInfo';
import Photo from './Photo';
import ImageRight from './ImageRight';
import ImageWrong from './ImageWrong';

const Stack = createStackNavigator();

// Manually declare your custom URL scheme here
const linking = {
  prefixes: ['youwontforget://', 'exp://localhost:19000/--/', 'exp://127.0.0.1:19000/--/'],
  config: {
    screens: {
      Signup: 'signup',
      Signin: 'signin',
      SignupInfo: 'signup-info',
      Home: 'home',
      NewHabit: 'newhabit',
      Photo: 'photo/:taskId',
      ImageRight: 'imageright',
      ImageWrong: 'imagewrong',
      TwitterCallback: {
        path: 'twitter-callback',
        parse: {
          user_id: (user_id) => user_id,
          screen_name: (screen_name) => screen_name,
        },
      },
    },
  },
};

export default function App() {
  return (
    <NavigationContainer linking={linking} fallback={<Text>Loading…</Text>}>
      <Stack.Navigator initialRouteName="Signin">
        <Stack.Screen
          name="Signin"
          component={Signin}
          options={{ title: 'Log in' }}
        />
        <Stack.Screen
          name="Signup"
          component={Signup}
          options={{ title: 'Create account' }}
        />
        <Stack.Screen
          name="SignupInfo"
          component={SignupInfo}
          options={{ title: 'Complete Setup' }}
        />
        <Stack.Screen
          name="Home" 
          component={Home} 
          options={{ title: 'Home' }}
        />
        <Stack.Screen
          name="NewHabit"
          component={NewHabit} 
          options={{ title: 'New habit' }}
        />
        <Stack.Screen
          name="Photo"
          component={Photo} 
          options={{ title: 'Photo' }}
        />
        <Stack.Screen
          name="ImageRight"
          component={ImageRight} 
          options={{ title: 'Verify' }}
        />
        <Stack.Screen
          name="ImageWrong"
          component={ImageWrong} 
          options={{ title: 'Verify' }}
        />

        {/* Deep-link catcher for Twitter OAuth */}
        <Stack.Screen
          name="TwitterCallback"
          component={({ route, navigation }) => {
            const { user_id, screen_name } = route.params || {};
            console.log('Twitter callback received:', { user_id, screen_name });
            
            React.useEffect(() => {
              if (user_id && screen_name) {
                navigation.reset({
                  index: 0,
                  routes: [
                    {
                      name: 'Home',
                      params: {
                        user: {
                          id: user_id,
                          twitter: screen_name
                        }
                      }
                    }
                  ]
                });
              } else {
                console.error('Missing user_id or screen_name in Twitter callback');
                navigation.replace('Signin');
              }
            }, [user_id, screen_name]);

            return (
              <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
                <Text>Signing you in...</Text>
              </View>
            );
          }}
          options={{ title: 'Signing in…' }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
