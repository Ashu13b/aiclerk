import React from 'react';
import { Text, View } from 'react-native';

type Props = { label: string; color: string };

export function Tag({ label, color }: Props) {
  return (
    <View style={{ backgroundColor: color + '22', borderRadius: 99, paddingHorizontal: 8, paddingVertical: 2 }}>
      <Text style={{ fontSize: 10, fontWeight: '700', color, letterSpacing: 0.5 }}>
        {label.toUpperCase()}
      </Text>
    </View>
  );
}
