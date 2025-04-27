import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import Home from './Home'; 
import NewHabit from './NewHabit'; 
import Signup from './Signup';
import Signin from './Signin';
import Photo from './Photo';
import ImageRight from './ImageRight';
import ImageWrong from './ImageWrong';



const Stack = createStackNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator>
        <Stack.Screen
          name="Signup"
          component={Signup}
          options={{ title: 'Create account' }}
        />
        <Stack.Screen
          name="Signin"
          component={Signin}
          options={{ title: 'Log in' }}
        />
        <Stack.Screen
          name="Home" 
          component={Home} 
          options={{ title: 'Home'}}
        />
        <Stack.Screen
          name="NewHabit"
          component={NewHabit} 
          options={{ title: 'New habit'}}
        />
        <Stack.Screen
          name="Photo"
          component={Photo} 
          options={{ title: 'Photo'}}
        />
        <Stack.Screen
          name="ImageRight"
          component={ImageRight} 
          options={{ title: 'Verify'}}
        />
        <Stack.Screen
          name="ImageWrong"
          component={ImageWrong} 
          options={{ title: 'Verify'}}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
