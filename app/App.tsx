import React, { useState } from 'react';
import { View } from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { getTheme, MED } from './theme';
import { BottomNav } from './components/BottomNav';
import { DashboardScreen } from './screens/DashboardScreen';
import { InboxScreen } from './screens/InboxScreen';
import { FillScreen } from './screens/FillScreen';
import { MOCK_FILL_REPORT } from './data';

export type Screen = 'home' | 'inbox' | 'fill' | 'search' | 'settings';

export default function App() {
  const [screen, setScreen] = useState<Screen>('home');
  const t = getTheme(MED.green, true);

  function renderScreen() {
    switch (screen) {
      case 'home':     return <DashboardScreen t={t} />;
      case 'inbox':    return <InboxScreen t={t} />;
      case 'fill':     return <FillScreen t={t} report={MOCK_FILL_REPORT} />;
      case 'search':   return <View style={{ flex: 1, backgroundColor: t.bg }} />;
      case 'settings': return <View style={{ flex: 1, backgroundColor: t.bg }} />;
      default:         return <DashboardScreen t={t} />;
    }
  }

  return (
    <View style={{ flex: 1, backgroundColor: t.bg }}>
      <StatusBar style="light" />
      <View style={{ flex: 1 }}>
        {renderScreen()}
      </View>
      <BottomNav screen={screen as any} setScreen={setScreen as any} t={t} />
    </View>
  );
}
