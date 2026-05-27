import React from 'react';
import { View, Text, ScrollView, StyleSheet } from 'react-native';
import { Theme, MED } from '../theme';
import { VAULTS, RECENT_DOCUMENTS, KNOWN_PERSONS } from '../data';
import { Tag } from '../components/Tag';

type Props = { t: Theme };

export function DashboardScreen({ t }: Props) {
  return (
    <ScrollView style={[styles.container, { backgroundColor: t.bg }]} contentContainerStyle={styles.content}>
      <View style={styles.header}>
        <Text style={[styles.title, { color: t.text }]}>Clerk's Ledger</Text>
        <Text style={[styles.subtitle, { color: t.muted }]}>Professional Document Orchestrator</Text>
      </View>

      {/* Stats Cards */}
      <View style={styles.statsRow}>
        <StatCard label="Total Vault" value={62} color={t.accent} t={t} />
        <StatCard label="Pending" value={1} color={t.warning} t={t} />
        <StatCard label="Accuracy" value="98%" color={MED.cyan} t={t} />
      </View>

      {/* Vaults Section */}
      <Text style={[styles.sectionTitle, { color: t.text }]}>Active Vaults</Text>
      {VAULTS.map(v => (
        <View key={v.type} style={[styles.vaultCard, { backgroundColor: t.card, borderColor: t.border }]}>
          <View style={[styles.iconBox, { backgroundColor: v.color + '22' }]}>
            <Text style={{ fontSize: 24 }}>{v.icon}</Text>
          </View>
          <View style={{ flex: 1 }}>
            <Text style={[styles.vaultLabel, { color: t.text }]}>{v.label}</Text>
            <Text style={[styles.vaultDesc, { color: t.muted }]}>{v.desc}</Text>
          </View>
          <Text style={[styles.vaultCount, { color: v.color }]}>12 docs</Text>
        </View>
      ))}

      {/* Recent Activity */}
      <Text style={[styles.sectionTitle, { color: t.text }]}>Recent Ingests</Text>
      {RECENT_DOCUMENTS.map(doc => (
        <View key={doc.id} style={[styles.recentCard, { backgroundColor: t.card, borderColor: t.border }]}>
          <View style={{ flex: 1 }}>
            <Text style={[styles.docName, { color: t.text }]} numberOfLines={1}>{doc.filed_as}</Text>
            <View style={styles.tagRow}>
              <Tag label={doc.vault_type} color={t.accent} />
              <Tag label={doc.date} color={t.muted} />
            </View>
          </View>
          <Text style={{ color: MED.cyan, fontWeight: '800' }}>{(doc.confidence * 100).toFixed(0)}%</Text>
        </View>
      ))}
    </ScrollView>
  );
}

function StatCard({ label, value, color, t }: { label: string; value: any; color: string; t: Theme }) {
  return (
    <View style={[styles.statCard, { backgroundColor: t.card, borderColor: t.border }]}>
      <Text style={[styles.statValue, { color }]}>{value}</Text>
      <Text style={[styles.statLabel, { color: t.muted }]}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  content: { padding: 16, paddingTop: 60, paddingBottom: 40 },
  header: { marginBottom: 24 },
  title: { fontSize: 28, fontWeight: '800', letterSpacing: -0.5 },
  subtitle: { fontSize: 13, fontWeight: '600', marginTop: 4 },
  statsRow: { flexDirection: 'row', gap: 12, marginBottom: 24 },
  statCard: { flex: 1, padding: 16, borderRadius: 18, borderWidth: 1, alignItems: 'center' },
  statValue: { fontSize: 20, fontWeight: '800' },
  statLabel: { fontSize: 10, fontWeight: '700', marginTop: 4, textTransform: 'uppercase' },
  sectionTitle: { fontSize: 15, fontWeight: '800', marginBottom: 12, marginTop: 12 },
  vaultCard: { 
    flexDirection: 'row', alignItems: 'center', gap: 16, padding: 16, 
    borderRadius: 18, borderWidth: 1, marginBottom: 12 
  },
  iconBox: { width: 52, height: 52, borderRadius: 14, alignItems: 'center', justifyContent: 'center' },
  vaultLabel: { fontSize: 15, fontWeight: '700' },
  vaultDesc: { fontSize: 11, marginTop: 2 },
  vaultCount: { fontSize: 12, fontWeight: '800' },
  recentCard: { 
    flexDirection: 'row', alignItems: 'center', gap: 12, padding: 14, 
    borderRadius: 16, borderWidth: 1, marginBottom: 10 
  },
  docName: { fontSize: 13, fontWeight: '600', marginBottom: 6 },
  tagRow: { flexDirection: 'row', gap: 6 },
});
