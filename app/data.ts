export type VaultType = 'ServiceRecord' | 'ProfessionalOutput' | 'KnowledgeBase';

export interface Document {
  id: string;
  source_file: string;
  filed_as: string;
  vault_type: VaultType;
  primary_subject: string;
  person_key: string;
  scope: number;
  action_type: string;
  naming_tag: string;
  location?: string;
  date: string;
  relevance_intent?: string;
  professional_tags: string[];
  confidence: number;
  ingested_at: string;
}

export interface Person {
  id: string;
  name: string;
  prefix: string;
  tier: number;
  docs_count: number;
  color: string;
}

export const VAULTS: { type: VaultType; label: string; icon: string; color: string; desc: string }[] = [
  { 
    type: 'ServiceRecord', 
    label: 'Service Records', 
    icon: '📜', 
    color: '#3b82f6', 
    desc: 'Career timeline, appointments, and benefits.' 
  },
  { 
    type: 'ProfessionalOutput', 
    label: 'Work Log', 
    icon: '✍️', 
    color: '#10b981', 
    desc: 'Medical opinions, reports, and signed documents.' 
  },
  { 
    type: 'KnowledgeBase', 
    label: 'Insights', 
    icon: '💡', 
    color: '#f59e0b', 
    desc: 'Rules, precedents, and general references.' 
  },
];

export const KNOWN_PERSONS: Person[] = [
  { id: 'ASHISH_YADAV', name: 'Dr. Ashish Yadav', prefix: 'ash', tier: 1, docs_count: 42, color: '#3b82f6' },
  { id: 'SANJEEV_KALER', name: 'Sanjeev Kaler', prefix: 'sanj', tier: 4, docs_count: 12, color: '#10b981' },
  { id: 'JITENDRA_PATAWAT', name: 'Jitendra Patawat', prefix: 'jit', tier: 4, docs_count: 8, color: '#f59e0b' },
];

export const RECENT_DOCUMENTS: Document[] = [
  {
    id: '1',
    source_file: '16 june .pdf',
    filed_as: 'clerk_roster-2025-jln-hospital-nagaur.pdf',
    vault_type: 'ServiceRecord',
    primary_subject: 'General',
    person_key: 'GENERAL',
    scope: 4,
    action_type: 'roster',
    naming_tag: 'roster-jln-hospital-nagaur',
    location: 'JLN Hospital Nagaur',
    date: '2025-06-16',
    professional_tags: ['doctor'],
    confidence: 1.0,
    ingested_at: '2026-05-11T20:50:00',
  },
  {
    id: '2',
    source_file: 'Ashish application for Paternity leave .pdf',
    filed_as: 'ash_paternity-leave-2025.pdf',
    vault_type: 'ServiceRecord',
    primary_subject: 'Dr. Ashish Yadav',
    person_key: 'ASHISH_YADAV',
    scope: 1,
    action_type: 'application',
    naming_tag: 'paternity-leave',
    date: '2025-04-12',
    relevance_intent: 'Paternity leave approval for records',
    professional_tags: ['medical-officer'],
    confidence: 0.69,
    ingested_at: '2026-05-11T20:51:00',
  }
];

export interface Proposal {
  id: string;
  source_file: string;
  ocr_excerpt: string;
  suggested_metadata: Partial<Document>;
  confidence: number;
}

// ── Fill report types ────────────────────────────────────────────────────────

export type FillSource = 'profile' | 'registry' | 'inferred' | 'unknown' | 'user';

export interface FillField {
  label: string;
  value: string | null;
  confidence: number;
  source: FillSource;
  note?: string;
}

export interface FillReport {
  form: string;
  form_name: string;
  person_key: string;
  person_name: string;
  generated_at: string;
  fields: FillField[];
  stats: { filled: number; uncertain: number; missing: number };
}

export const MOCK_FILL_REPORT: FillReport = {
  form: 'inbox/5.1_Declaration_Form_Faculty_Revised_2021-2022.pdf',
  form_name: 'Faculty Declaration Form (NMC/MCI) 2021-22',
  person_key: 'ASHISH_YADAV',
  person_name: 'Dr. Ashish Yadav',
  generated_at: new Date().toISOString(),
  stats: { filled: 8, uncertain: 0, missing: 21 },
  fields: [
    { label: 'Name of Faculty',         value: 'Ashish Yadav',                              confidence: 0.98, source: 'profile' },
    { label: 'Name of College',         value: 'Rajasthan Medical Education Society, Jaipur', confidence: 0.90, source: 'registry' },
    { label: 'Photo ID',                value: 'RJCR201512002054',                           confidence: 0.95, source: 'registry', note: 'Employee ID' },
    { label: 'Issuing Authority',       value: 'Govt. of Rajasthan',                         confidence: 0.82, source: 'inferred' },
    { label: 'College / Institute',     value: 'Rajasthan University of Health Sciences',    confidence: 0.88, source: 'registry' },
    { label: 'City / District',         value: 'Rajgarh (Churu)',                            confidence: 0.85, source: 'registry' },
    { label: 'Appointment',             value: 'Principal Medical Officer SDH, Rajgarh',    confidence: 0.80, source: 'registry' },
    { label: 'Residential Address',     value: 'SDH Rajgarh, Churu, Rajasthan',             confidence: 0.75, source: 'registry' },
    { label: 'Present Designation',     value: null, confidence: 0, source: 'unknown', note: 'Enter: Medical Officer / Asst. Professor' },
    { label: 'Department',              value: null, confidence: 0, source: 'unknown', note: 'Enter: General Medicine' },
    { label: 'Date of Birth',           value: null, confidence: 0, source: 'unknown' },
    { label: 'Age',                     value: null, confidence: 0, source: 'unknown' },
    { label: 'Date of Joining',         value: null, confidence: 0, source: 'unknown' },
    { label: 'Appointment Order',       value: null, confidence: 0, source: 'unknown' },
    { label: 'Contact Details',         value: null, confidence: 0, source: 'unknown' },
    { label: 'Email Address',           value: null, confidence: 0, source: 'unknown' },
    { label: 'Educational Qualifications', value: null, confidence: 0, source: 'unknown' },
    { label: 'MD / MS Subject',         value: null, confidence: 0, source: 'unknown' },
    { label: 'State Medical Council',   value: null, confidence: 0, source: 'unknown' },
    { label: 'Medical Council Reg. No.',value: null, confidence: 0, source: 'unknown' },
    { label: 'Details of Teaching Experience', value: null, confidence: 0, source: 'unknown' },
    { label: 'Assessment Date',         value: null, confidence: 0, source: 'unknown', note: 'Filled by assessor' },
  ],
};

export const PENDING_PROPOSALS: Proposal[] = [
  {
    id: 'p1',
    source_file: 'डॉ आशीष यादव sdh राजगढ़ सैलरी प्रॉब्लम.pdf',
    ocr_excerpt: 'सेवा में, प्रमुख चिकित्सा अधिकारी महोदया, राजकीय उपजिला अस्पताल राजगढ़, चूरु...',
    suggested_metadata: {
      primary_subject: 'Dr. Ashish Yadav',
      vault_type: 'ServiceRecord',
      action_type: 'application',
      naming_tag: 'salary-problem',
      date: '2024-02-20',
      location: 'SDH Rajgarh',
    },
    confidence: 0.69,
  }
];
