import React, { useState } from 'react';
import { View, Text, ScrollView, Pressable, StyleSheet } from 'react-native';
import { Theme, MED } from '../theme';
import { PENDING_PROPOSALS, Proposal } from '../data';
import { Tag } from '../components/Tag';

type Props = { t: Theme };

export function InboxScreen({ t }: Props) {
  const [proposals, setProposals] = useState(PENDING_PROPOSALS);

  function approve(id: string) {
    setProposals(proposals.filter(p => p.id !== id));
  }

  return (
    <ScrollView style={[styles.container, { backgroundColor: t.bg }]} contentContainerStyle={styles.content}>
      <View style={styles.header}>
        <Text style={[styles.title, { color: t.text }]}>Clerk's Inbox</Text>
        <Text style={[styles.subtitle, { color: t.muted }]}>{proposals.length} proposals awaiting your judgement</Text>
      </View>

      {proposals.length === 0 ? (
        <View style={styles.emptyState}>
          <Text style={{ fontSize: 40, marginBottom: 16 }}>✅</Text>
          <Text style={{ color: t.text, fontWeight: '700', fontSize: 16 }}>All caught up!</Text>
          <Text style={{ color: t.muted, fontSize: 13, marginTop: 4 }}>The Clerk is watching your inbox...</Text>
        </View>
      ) : (
        proposals.map(p => (
          <ProposalCard key={p.id} p={p} t={t} onApprove={() => approve(p.id)} />
        ))
      )}
    </ScrollView>
  );
}

function ProposalCard({ p, t, onApprove }: { p: Proposal; t: Theme; onApprove: () => void }) {
  const meta = p.suggested_metadata;
  
  return (
    <View style={[styles.card, { backgroundColor: t.card, borderColor: t.border }]}>
      <View style={styles.cardHeader}>
        <View style={{ flex: 1 }}>
          <Text style={[styles.sourceFile, { color: t.muted }]} numberOfLines={1}>{p.source_file}</Text>
          <Text style={[styles.subject, { color: t.text }]}>{meta.primary_subject}</Text>
        </View>
        <View style={[styles.confBadge, { backgroundColor: MED.cyan + '22' }]}>
          <Text style={{ color: MED.cyan, fontWeight: '800', fontSize: 12 }}>{(p.confidence * 100).toFixed(0)}%</Text>
        </View>
      </View>

      <View style={styles.previewBox}>
        <Text style={[styles.previewText, { color: t.muted }]} numberOfLines={3}>"{p.ocr_excerpt}"</Text>
      </View>

      <View style={styles.details}>
        <DetailRow label="Vault" value={meta.vault_type} t={t} />
        <DetailRow label="Type" value={meta.action_type} t={t} />
        <DetailRow label="Tag" value={meta.naming_tag} t={t} />
        <DetailRow label="Date" value={meta.date} t={t} />
        {meta.location && <DetailRow label="At" value={meta.location} t={t} />}
      </View>

      <View style={styles.actions}>
        <Pressable style={[styles.btn, { backgroundColor: t.border }]}>
          <Text style={{ color: t.text, fontWeight: '700', fontSize: 13 }}>Edit</Text>
        </Pressable>
        <Pressable onPress={onApprove} style={[styles.btn, { backgroundColor: t.accent, flex: 2 }]}>
          <Text style={{ color: '#fff', fontWeight: '700', fontSize: 13 }}>Approve & File</Text>
        </Pressable>
      </View>
    </View>
  );
}

function DetailRow({ label, value, t }: { label: string; value: any; t: Theme }) {
  return (
    <View style={styles.detailRow}>
      <Text style={[styles.detailLabel, { color: t.muted }]}>{label}</Text>
      <Text style={[styles.detailValue, { color: t.text }]}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  content: { padding: 16, paddingTop: 60, paddingBottom: 40 },
  header: { marginBottom: 24 },
  title: { fontSize: 24, fontWeight: '800' },
  subtitle: { fontSize: 13, marginTop: 4 },
  card: { borderRadius: 20, borderWidth: 1, padding: 18, marginBottom: 16 },
  cardHeader: { flexDirection: 'row', alignItems: 'flex-start', gap: 12, marginBottom: 12 },
  sourceFile: { fontSize: 10, textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 2 },
  subject: { fontSize: 17, fontWeight: '700' },
  confBadge: { paddingHorizontal: 8, paddingVertical: 4, borderRadius: 8 },
  previewBox: { padding: 12, borderRadius: 12, backgroundColor: '#00000022', marginBottom: 16 },
  previewText: { fontSize: 12, fontStyle: 'italic', lineHeight: 18 },
  details: { gap: 8, marginBottom: 20 },
  detailRow: { flexDirection: 'row', justifyContent: 'space-between' },
  detailLabel: { fontSize: 12, fontWeight: '600' },
  detailValue: { fontSize: 12, fontWeight: '700' },
  actions: { flexDirection: 'row', gap: 10 },
  btn: { height: 44, borderRadius: 12, alignItems: 'center', justifyContent: 'center', flex: 1 },
  emptyState: { flex: 1, alignItems: 'center', justifyContent: 'center', marginTop: 100 },
});
