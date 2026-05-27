import React from 'react';
import { View, Text, Pressable } from 'react-native';
import { Theme } from '../theme';

export type Screen = 'home' | 'inbox' | 'fill' | 'search' | 'settings';

type Props = { screen: Screen; setScreen: (s: Screen) => void; t: Theme };

const TABS: { id: Screen; label: string; icon: string }[] = [
  { id: 'home',     label: 'Ledger',  icon: '📊' },
  { id: 'inbox',    label: 'Inbox',   icon: '📥' },
  { id: 'fill',     label: 'Fill',    icon: '✍️' },
  { id: 'search',   label: 'Find',    icon: '🔍' },
  { id: 'settings', label: 'Clerk',   icon: '⚙️' },
];

export function BottomNav({ screen, setScreen, t }: Props) {
  return (
    <View style={{ flexDirection: 'row', backgroundColor: t.card, borderTopWidth: 1, borderTopColor: t.border, paddingBottom: 24, paddingTop: 8 }}>
      {TABS.map(tab => {
        const active = screen === tab.id;
        return (
          <Pressable key={tab.id} onPress={() => setScreen(tab.id)} style={{ flex: 1, alignItems: 'center', gap: 3, paddingTop: 6 }}>
            {active && (
              <View style={{ position: 'absolute', top: 0, left: '22%', right: '22%', height: 2.5, borderRadius: 99, backgroundColor: t.accent }} />
            )}
            <Text style={{ fontSize: 20 }}>{tab.icon}</Text>
            <Text style={{ fontSize: 10, color: active ? t.accent : t.muted, fontWeight: active ? '700' : '400' }}>
              {tab.label}
            </Text>
          </Pressable>
        );
      })}
    </View>
  );
}
