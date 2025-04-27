import { createNativeStackNavigator } from '@react-navigation/native-stack';
import Home from '../Home';
import NewHabit from '../NewHabit';
import Signup from '../Signup'; 
import Photo from '../Photo';
import ImageRight from '../ImageRight';
import ImageWrong from '../ImageWrong';
import Signin from '../Signin';
import PoliPick from '../PoliPick';
import PoliDem from '../PoliDem';
import PoliRep from '../PoliRep';


const Stack = createNativeStackNavigator();

export default function MainNavigator() {
  return (
    <Stack.Navigator initialRouteName="Signup" screenOptions={{ headerShown: false }}>
      <Stack.Screen name="Signup" component={Signup}  />
      <Stack.Screen name="Signin" component={Signin} />
      <Stack.Screen name="Home" component={Home} />
      <Stack.Screen name="NewHabit" component={NewHabit} />
      <Stack.Screen name="Photo" component={Photo} />
      <Stack.Screen name="ImageRight" component={ImageRight} />
      <Stack.Screen name="ImageWrong" component={ImageWrong} />
      <Stack.Screen name="PoliPick" component={PoliPick} />
      <Stack.Screen name="PoliDem" component={PoliDem} />
      <Stack.Screen name="PoliRep" component={PoliRep} />

      
    </Stack.Navigator>
  );
}

