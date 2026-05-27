import React, { useState } from 'react';
import {
  View, Text, ScrollView, Pressable, TextInput, StyleSheet,
} from 'react-native';
import { Theme, MED } from '../theme';
import { FillReport, FillField } from '../data';

type Props = { t: Theme; report: FillReport };

export function FillScreen({ t, report }: Props) {
  const [fields, setFields] = useState<FillField[]>(report.fields);
  const [editing, setEditing] = useState<string | null>(null);
  const [draft, setDraft] = useState('');

  const filled    = fields.filter(f => f.value && f.confidence >= 0.75);
  const uncertain = fields.filter(f => f.value && f.confidence < 0.75);
  const missing   = fields.filter(f => !f.value);

  function commitEdit(label: string) {
    if (draft.trim()) {
      setFields(fields.map(f =>
        f.label === label
          ? { ...f, value: draft.trim(), confidence: 1.0, source: 'user' as const }
          : f
      ));
    }
    setEditing(null);
    setDraft('');
  }

  function startEdit(f: FillField) {
    setEditing(f.label);
    setDraft(f.value ?? '');
  }

  function cancelEdit() {
    setEditing(null);
    setDraft('');
  }

  const date = new Date(report.generated_at);
  const dateStr = date.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });

  return (
    <ScrollView style={[s.root, { backgroundColor: t.bg }]} contentContainerStyle={s.content}>

      {/* Header */}
      <View style={s.header}>
        <Text style={[s.formName, { color: t.text }]} numberOfLines={2}>
          {report.form_name}
        </Text>
        <Text style={[s.meta, { color: t.muted }]}>
          {report.person_name}  ·  {dateStr}
        </Text>
      </View>

      {/* Stats row */}
      <View style={s.statsRow}>
        <StatBadge label="Filled"    count={filled.length}    color={MED.green} t={t} />
        <StatBadge label="Uncertain" count={uncertain.length} color={MED.amber} t={t} />
        <StatBadge label="Missing"   count={missing.length}   color={MED.red}   t={t} />
      </View>

      {/* Missing — show first */}
      {missing.length > 0 && (
        <Section label="Needs Input" color={MED.red} t={t}>
          {missing.map(f => (
            <FieldRow
              key={f.label} f={f} t={t} color={MED.red}
              editing={editing === f.label} draft={draft}
              onTap={() => startEdit(f)}
              onDraftChange={setDraft}
              onCommit={() => commitEdit(f.label)}
              onCancel={cancelEdit}
            />
          ))}
        </Section>
      )}

      {/* Uncertain */}
      {uncertain.length > 0 && (
        <Section label="Verify" color={MED.amber} t={t}>
          {uncertain.map(f => (
            <FieldRow
              key={f.label} f={f} t={t} color={MED.amber}
              editing={editing === f.label} draft={draft}
              onTap={() => startEdit(f)}
              onDraftChange={setDraft}
              onCommit={() => commitEdit(f.label)}
              onCancel={cancelEdit}
            />
          ))}
        </Section>
      )}

      {/* Filled — all editable, visually cued */}
      {filled.length > 0 && (
        <Section label="Filled" color={MED.green} t={t} editHint>
          {filled.map(f => (
            <FieldRow
              key={f.label} f={f} t={t} color={MED.green}
              editing={editing === f.label} draft={draft}
              onTap={() => startEdit(f)}
              onDraftChange={setDraft}
              onCommit={() => commitEdit(f.label)}
              onCancel={cancelEdit}
            />
          ))}
        </Section>
      )}

      <View style={{ height: 40 }} />
    </ScrollView>
  );
}

// ── Sub-components ──────────────────────────────────────────────────────────

function StatBadge({ label, count, color, t }: { label: string; count: number; color: string; t: Theme }) {
  return (
    <View style={[s.badge, { backgroundColor: color + '18', borderColor: color + '44' }]}>
      <Text style={[s.badgeCount, { color }]}>{count}</Text>
      <Text style={[s.badgeLabel, { color: t.muted }]}>{label}</Text>
    </View>
  );
}

function Section({
  label, color, t, children, editHint,
}: {
  label: string; color: string; t: Theme; children: React.ReactNode; editHint?: boolean;
}) {
  return (
    <View style={s.section}>
      <View style={s.sectionHeader}>
        <View style={[s.sectionDot, { backgroundColor: color }]} />
        <Text style={[s.sectionLabel, { color: t.muted }]}>{label}</Text>
        {editHint && (
          <Text style={[s.editHint, { color: t.muted }]}>  tap to correct</Text>
        )}
      </View>
      <View style={[s.sectionBody, { backgroundColor: t.card, borderColor: t.border }]}>
        {children}
      </View>
    </View>
  );
}

type FieldRowProps = {
  f: FillField; t: Theme; color: string;
  editing: boolean; draft: string;
  onTap: () => void;
  onDraftChange: (v: string) => void;
  onCommit: () => void;
  onCancel: () => void;
};

function FieldRow({ f, t, color, editing, draft, onTap, onDraftChange, onCommit, onCancel }: FieldRowProps) {
  const isFilled = !!f.value;

  return (
    <Pressable onPress={onTap}>
      {({ pressed }) => (
        <View style={[
          s.row,
          { borderBottomColor: t.border },
          pressed && { backgroundColor: color + '12' },
        ]}>
          <View style={s.rowLeft}>
            <Text style={[s.rowLabel, { color: t.muted }]}>{f.label}</Text>

            {editing ? (
              <View style={s.inputRow}>
                <TextInput
                  autoFocus
                  value={draft}
                  onChangeText={onDraftChange}
                  placeholder="Type value..."
                  placeholderTextColor={t.muted}
                  style={[s.input, { color: t.text, borderColor: color }]}
                  onSubmitEditing={onCommit}
                />
                <Pressable onPress={onCommit} style={[s.commitBtn, { backgroundColor: color }]}>
                  <Text style={{ color: '#fff', fontWeight: '700', fontSize: 12 }}>OK</Text>
                </Pressable>
                <Pressable onPress={onCancel} style={[s.cancelBtn, { borderColor: t.border }]}>
                  <Text style={{ color: t.muted, fontSize: 12 }}>✕</Text>
                </Pressable>
              </View>
            ) : (
              <View style={s.valueRow}>
                <Text style={[s.rowValue, { color: f.value ? t.text : t.muted, flex: 1 }]}>
                  {f.value ?? 'Tap to fill...'}
                </Text>
                {/* Edit pencil icon for filled fields */}
                {isFilled && (
                  <Text style={[s.pencil, { color: color + '88' }]}>✎</Text>
                )}
              </View>
            )}

            {f.note && !editing && (
              <Text style={[s.rowNote, { color: t.muted }]}>{f.note}</Text>
            )}
          </View>

          <View style={s.rowRight}>
            {f.value && !editing && (
              <View style={[s.confDot, { backgroundColor: color }]} />
            )}
            {f.confidence > 0 && f.confidence < 0.75 && !editing && (
              <Text style={[s.confPct, { color }]}>{Math.round(f.confidence * 100)}%</Text>
            )}
            {f.source === 'user' && !editing && (
              <Text style={[s.sourceBadge, { color: t.muted }]}>you</Text>
            )}
          </View>
        </View>
      )}
    </Pressable>
  );
}

const s = StyleSheet.create({
  root:          { flex: 1 },
  content:       { padding: 16, paddingTop: 60, paddingBottom: 60 },
  header:        { marginBottom: 20 },
  formName:      { fontSize: 20, fontWeight: '800', lineHeight: 26 },
  meta:          { fontSize: 12, marginTop: 4 },
  statsRow:      { flexDirection: 'row', gap: 10, marginBottom: 24 },
  badge:         { flex: 1, borderRadius: 14, borderWidth: 1, paddingVertical: 10, alignItems: 'center' },
  badgeCount:    { fontSize: 22, fontWeight: '800' },
  badgeLabel:    { fontSize: 11, marginTop: 2 },
  section:       { marginBottom: 20 },
  sectionHeader: { flexDirection: 'row', alignItems: 'center', gap: 6, marginBottom: 8, paddingLeft: 4 },
  sectionDot:    { width: 8, height: 8, borderRadius: 99 },
  sectionLabel:  { fontSize: 11, fontWeight: '700', textTransform: 'uppercase', letterSpacing: 0.8 },
  editHint:      { fontSize: 10, fontStyle: 'italic' },
  sectionBody:   { borderRadius: 16, borderWidth: 1, overflow: 'hidden' },
  row:           { paddingHorizontal: 16, paddingVertical: 14, flexDirection: 'row', borderBottomWidth: StyleSheet.hairlineWidth },
  rowLeft:       { flex: 1 },
  rowRight:      { alignItems: 'flex-end', justifyContent: 'center', paddingLeft: 8, gap: 4 },
  rowLabel:      { fontSize: 11, fontWeight: '600', textTransform: 'uppercase', letterSpacing: 0.4, marginBottom: 4 },
  valueRow:      { flexDirection: 'row', alignItems: 'center', gap: 6 },
  rowValue:      { fontSize: 14, fontWeight: '600' },
  pencil:        { fontSize: 14 },
  rowNote:       { fontSize: 11, marginTop: 4, fontStyle: 'italic' },
  confDot:       { width: 8, height: 8, borderRadius: 99 },
  confPct:       { fontSize: 11, fontWeight: '700' },
  sourceBadge:   { fontSize: 9, textTransform: 'uppercase', letterSpacing: 0.5 },
  inputRow:      { flexDirection: 'row', alignItems: 'center', gap: 6, marginTop: 2 },
  input:         { flex: 1, borderWidth: 1, borderRadius: 8, paddingHorizontal: 10, paddingVertical: 6, fontSize: 14 },
  commitBtn:     { paddingHorizontal: 12, paddingVertical: 7, borderRadius: 8 },
  cancelBtn:     { paddingHorizontal: 10, paddingVertical: 7, borderRadius: 8, borderWidth: 1 },
});
