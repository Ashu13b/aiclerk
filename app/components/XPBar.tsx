import React from 'react';
import { View, Text } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Theme, MED } from '../theme';

type Props = { xp: number; max: number; t: Theme };

const XP_PER_LEVEL = 1000;

export function XPBar({ xp, max, t }: Props) {
  const level    = Math.floor(xp / XP_PER_LEVEL);
  const levelXP  = xp % XP_PER_LEVEL;
  const toNext   = XP_PER_LEVEL - levelXP;
  const barPct   = (levelXP / XP_PER_LEVEL) * 100;

  return (
    <View style={{ width: '100%' }}>
      <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 5 }}>
        <View style={{ flexDirection: 'row', alignItems: 'center', gap: 6 }}>
          <View style={{ backgroundColor: MED.green + '22', borderRadius: 6, paddingHorizontal: 7, paddingVertical: 2 }}>
            <Text style={{ fontSize: 11, fontWeight: '800', color: MED.green }}>Lv {level}</Text>
          </View>
          <Text style={{ fontSize: 11, fontWeight: '600', color: MED.green }}>⚡ App Level</Text>
        </View>
        <Text style={{ fontSize: 10, color: t.muted }}>{toNext.toLocaleString()} XP to next</Text>
      </View>
      <View style={{ height: 7, borderRadius: 99, backgroundColor: t.border, overflow: 'hidden' }}>
        <LinearGradient
          colors={[MED.green, MED.cyan]}
          start={{ x: 0, y: 0 }} end={{ x: 1, y: 0 }}
          style={{ width: `${barPct}%`, height: '100%', borderRadius: 99 }}
        />
      </View>
    </View>
  );
}
