# The Clerk's Brain: Intelligence Stack

Docclerk is powered by a multi-layered intelligence stack that mimics how a professional administrative clerk thinks. Below are the 8 layers of logic that process every document.

## 1. Environmental Intelligence (Pre-Scan)
Before reading the text, the Clerk scans the file's "surroundings."
- **Logic**: It looks at the parent folder names (e.g., `GMC-Nagaur/`) and the original filename (e.g., `ash-joining.pdf`).
- **Action**: These are used as "Implicit Hints" to increase OCR accuracy and prioritize known institutions.

## 2. Satisficed Reading (Header + Footer)
A human clerk doesn't read every word of a 600-page book to file it.
- **Logic**: The Clerk focus exclusively on the **Header** (Top 50%) to identify the institution/subject and the **Footer** (Bottom 50%) to find the signatory and date.
- **Action**: This saves 90% of processing time and focuses on the "Source of Truth."

## 3. Weighted Priority (Personal Lens)
Documents are viewed through the user's specific perspective.
- **Logic**: The User (Self) has the highest weight, followed by Family, then known Institutions (GMC Nagaur, RajMES), and finally general people.
- **Action**: High-weight documents go to **ServiceRecords**; low-weight ones go to **Insights/KnowledgeBase**.

## 4. Relational Matrix (Persistent Memory)
The Clerk builds a "Web of Associations" over time.
- **Logic**: If it learns that **Ashish** works at **RajMES** and owns a vehicle with ID **RJ23**, it remembers this connection.
- **Action**: It uses this matrix to fix messy OCR (e.g., linking "Athik" to "Ashish" because the document mentions RajMES).

## 5. Materiality Intelligence (The Reality Filter)
Not all documents have the same "Weight of Truth."
- **Logic**: It distinguishes between **Official** documents (Orders, Salary slips) and **Educational** ones (Handwritten notes, diagrams).
- **Action**: Educational materials are automatically demoted to the KnowledgeBase to prevent them from creating logical conflicts in a person's professional career timeline.

## 6. Contextual Essentiality (Smart Naming)
The Clerk decides what information is "Essential" for a file's identity.
- **Logic**: A city is "Essential" for a local posting order, but it is "Noise" for a National Digital ID card.
- **Action**: It automatically strips location data from filenames if the identity is status-based, resulting in cleaner names like `ash_id-digital-doctor.pdf`.

## 7. Administrative Lifecycle (Gap Analysis)
The Clerk understands that professional events happen in sequences.
- **Logic**: It knows that a **Selection** should be followed by a **Joining Report**.
- **Action**: It audits timelines to identify "Gaps" (missing documents) and warns the user if their career history is incomplete.

## 8. Cross-Language Mapping (Hindi/English)
The Clerk is native in both scripts.
- **Logic**: It recognizes that "आशीष" and "Ashish" are the same person and that "जयपुर" and "Jaipur" are the same place.
- **Action**: It normalizes all findings into a single canonical English key for consistent filing and searching.

---
*Last Logic Update: v1.0 Materiality Stabilized*
