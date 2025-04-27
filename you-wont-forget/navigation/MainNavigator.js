import { createNativeStackNavigator } from '@react-navigation/native-stack';
import Home from '../Home';
import NewHabit from '../NewHabit';
import Signup from '../Signup'; 
import SignupInfo from '../SignupInfo'; 
import Photo from '../Photo';
import ImageRight from '../ImageRight';
import ImageWrong from '../ImageWrong';
import Signin from '../Signin';


const Stack = createNativeStackNavigator();

export default function MainNavigator() {
  return (
    <Stack.Navigator initialRouteName="Signup" screenOptions={{ headerShown: false }}>
      <Stack.Screen name="Signup" component={Signup}  />
      <Stack.Screen name="Signin" component={Signin} />
      <Stack.Screen name="SignupInfo" component={SignupInfo} />
      <Stack.Screen name="Home" component={Home} />
      <Stack.Screen name="NewHabit" component={NewHabit} />
      <Stack.Screen name="Photo" component={Photo} />
      <Stack.Screen name="ImageRight" component={ImageRight} />
      <Stack.Screen name="ImageWrong" component={ImageWrong} />
      
    </Stack.Navigator>
  );
}

