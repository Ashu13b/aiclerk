import json
import re
import shlex
import shutil
import subprocess
import tempfile
import time
from datetime import datetime
from pathlib import Path

import click

from .config import (
    ANCHOR_INSTITUTIONS,
    ARCHIVE_DIR,
    CONFIDENCE_THRESHOLD,
    COURSES_DIR,
    FILL_REPORTS_DIR,
    OUTPUT_DIR,
    REGISTRY_FILE,
    USER_NAME,
)
from .core import (
    RelationalMatrix,
    _is_course_folder,
    _move_course,
    build_final_name,
    build_person_profile,
    extract_json,
    file_document,
    file_hash,
    get_safe_year,
    normalize_text,
    run_ai_cmd,
    slugify,
)
from .data import (
    add_to_review_queue,
    append_registry_entry,
    load_form_codes,
    load_known_persons,
    load_profile,
    load_registry,
    load_review_queue,
    save_form_codes,
    save_json,
    save_known_persons,
    save_profile,
    save_review_queue,
)


@click.group()
def cli():
    """AiClerk: Your Intelligent Interactive Document Clerk."""
    pass


# ── INGEST ────────────────────────────────────────────────────────────────────

@cli.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--no-interactive", is_flag=True, help="Skip prompts; low-confidence items go to review queue.")
def ingest(file_path, no_interactive):
    """Ingest a document: OCR → classify → name → file."""
    file_path = Path(file_path)
    click.secho(f"\n[*] Opening '{file_path.name}'...", fg="cyan", bold=True)

    known_persons = load_known_persons()
    rm = RelationalMatrix()
    tmp_files: list[Path] = []

    try:
        # 1. Glance OCR (header + footer strip)
        click.echo("[*] Glance OCR...")
        stem_safe = re.sub(r"[^a-zA-Z0-9]", "_", file_path.stem)
        ocr_text = ""

        if file_path.suffix.lower() == ".pdf":
            h_pfx = f"tmp_glance_{stem_safe}_h"
            f_pfx = f"tmp_glance_{stem_safe}_f"
            subprocess.run(f"pdftoppm -f 1 -l 1 -jpeg -y 0   -H 500 {shlex.quote(str(file_path))} {shlex.quote(h_pfx)}", shell=True, capture_output=True)
            subprocess.run(f"pdftoppm -f 1 -l 1 -jpeg -y 500         {shlex.quote(str(file_path))} {shlex.quote(f_pfx)}", shell=True, capture_output=True)
            gen_h = sorted(Path(".").glob(f"{h_pfx}*.jpg"))
            gen_f = sorted(Path(".").glob(f"{f_pfx}*.jpg"))
            tmp_files = gen_h + gen_f
            if gen_h:
                ocr_text += normalize_text(run_ai_cmd(f"ai ocr {shlex.quote(str(gen_h[0]))}"))
            if gen_f:
                ocr_text += "\n--- FOOTER ---\n" + normalize_text(run_ai_cmd(f"ai ocr {shlex.quote(str(gen_f[0]))}"))
        else:
            img_tmp = Path(f"tmp_{stem_safe}{file_path.suffix}")
            shutil.copy2(file_path, img_tmp)
            tmp_files = [img_tmp]
            ocr_text = normalize_text(run_ai_cmd(f"ai ocr {shlex.quote(str(img_tmp))}"))

        ocr_text = normalize_text(ocr_text)

        if not ocr_text.strip():
            click.secho("[!] OCR returned empty. Aborting.", fg="red")
            return

        # 2. Pre-inference: resolve owner before asking the AI

        # 2a. Folder path prior — parent folder names are strong implicit signals
        folder_prior_key = None
        for parent in file_path.parents:
            if parent.name in (".", "..", "inbox", "samples", "tmp_reingest"):
                continue
            folder_lower = parent.name.lower()
            for key, pdata in known_persons.items():
                stored_name = pdata.get("name") or key.replace("_", " ").title()
                name_words = [
                    w.lower() for w in re.sub(r"dr\.?", "", stored_name, flags=re.IGNORECASE).split()
                    if len(w) > 3
                ]
                if any(w in folder_lower for w in name_words):
                    folder_prior_key = key
                    break
            if folder_prior_key:
                break

        # 2b. Filename → known person name match
        filename_lower = file_path.stem.lower()
        filename_prior_key = None
        for key, pdata in known_persons.items():
            stored_name = pdata.get("name") or key.replace("_", " ").title()
            name_words = [
                w.lower() for w in re.sub(r"dr\.?", "", stored_name, flags=re.IGNORECASE).split()
                if len(w) > 3
            ]
            if any(w in filename_lower for w in name_words):
                filename_prior_key = key
                break

        # 2c. Filename/path → known vehicle/asset match
        v_match = re.search(r"[A-Z]{2}\d{2}[A-Z]{1,2}\d{4}", file_path.name) or \
                  re.search(r"[A-Z]{2}\d{2}[A-Z]{1,2}\d{4}", ocr_text)
        asset_prior_key = None
        if v_match:
            for p_key, p_data in rm.matrix.items():
                if v_match.group(0) in p_data.get("assets", []):
                    asset_prior_key = p_key
                    break

        prior_lines = []
        if asset_prior_key:
            aname = known_persons.get(asset_prior_key, {}).get("name", asset_prior_key)
            prior_lines.append(
                f"ASSET PRIOR (definitive): vehicle/asset {v_match.group(0)} belongs to {aname}. "
                f"Set primary_subject={aname} and scope=2."
            )
        elif folder_prior_key:
            fname = known_persons.get(folder_prior_key, {}).get("name", folder_prior_key)
            prior_lines.append(
                f"FOLDER PRIOR (definitive): file is in a folder named after '{fname}'. "
                f"Set primary_subject={fname}."
            )
        elif filename_prior_key:
            fname = known_persons.get(filename_prior_key, {}).get("name", filename_prior_key)
            prior_lines.append(
                f"FILENAME PRIOR (definitive): filename contains '{fname}'. "
                f"Set primary_subject={fname} unless OCR names a clearly different owner."
            )
        prior_block = "\n".join(prior_lines) if prior_lines else "None."

        # 3. Deep Inference
        matrix_context = "\n".join(
            f"- {k}: institutions={v.get('institutions', [])}, assets={v.get('assets', [])}"
            for k, v in rm.matrix.items()
        )
        prompt = f"""Return valid JSON only. No markdown fences. All fields required.

PRIORS (resolve these first, before reading OCR):
{prior_block}

FIELDS:
primary_subject: full person name in English
vault_type: ServiceRecord | ProfessionalOutput | KnowledgeBase
scope: 1=Self({USER_NAME}), 2=Family/Assets, 3=AnchorOrg, 4=General, 5=Unrelated
action_type: application | office-order | certificate | receipt | roster | report | guideline
form_code: extract ONLY a standardized government form designation — e.g. "GA 55", "GA 55A", "Form 16", "Form 12BB", "Form 26AS", "D.O. Letter". NOT reference numbers, file numbers, order numbers, vehicle numbers, policy numbers, or roll numbers. Return empty string if no official form type is present.
naming_tag: SHORT human-readable slug for what this document actually IS — its purpose, not its form number. Examples: salary-arrear, paternity-leave, appointment-order, insurance-certificate, selection-list, heatstroke-guideline. Never put a form code here.
include_location: true only if location is essential to this document's identity
location: institution name if include_location is true, else empty string
date: YYYY-MM-DD from body/footer. Linguistic date preferred (e.g. "दिनांक 19.1.26" → 2026-01-19). Empty string if not found.
is_list: true only if document is a multi-row table of multiple people
professional_tags: domain tags array
subject_ids: IDs, reg numbers, account numbers, or codes that belong SPECIFICALLY to primary_subject (employee ID, GPF, PAN, vehicle plate, HPR number, etc.). EXCLUDE IDs belonging to any other person in the document (dependants, witnesses, patients, third parties). Must appear verbatim in OCR text. Return empty array if none.
assets: vehicle registration plates ONLY (e.g. "RJ23CF9025"). Empty array if none.
metadata: {{reference_number: string, date: string}}
confidence: float 0.0–1.0

RELATIONAL MATRIX (identity resolution only — do not echo assets back):
{matrix_context}

OCR TEXT:
{ocr_text[:4500]}"""

        click.echo("[*] Deep Inference...")
        meta_raw = run_ai_cmd(f"ai chat {shlex.quote(prompt)}")
        data = extract_json(meta_raw)

        if not data:
            retry = f"Extract JSON. Fields: primary_subject, vault_type, scope, naming_tag, date, confidence. TEXT: {ocr_text[:1000]}"
            meta_raw = run_ai_cmd(f"ai chat -s 'Output raw JSON only.' {shlex.quote(retry)}")
            data = extract_json(meta_raw)

        if not data:
            click.secho("[!] Intelligence failure — could not parse classification.", fg="red")
            return

        confidence = float(data.get("confidence") or 0.5)

        # 4. Subject + form-code resolution: priors override AI response
        subject = data.get("primary_subject", "General")
        subject_key = slugify(subject).upper().replace("-", "_")
        if asset_prior_key:
            subject_key = asset_prior_key
            confidence = max(confidence, 0.90)
        elif folder_prior_key:
            subject_key = folder_prior_key
            confidence = max(confidence, 0.90)
        elif filename_prior_key:
            subject_key = filename_prior_key
            confidence = max(confidence, 0.80)

        raw_form_code = (data.get("form_code") or "").strip()
        if raw_form_code:
            form_codes = load_form_codes()
            if raw_form_code in form_codes:
                stored = form_codes[raw_form_code]
                data["naming_tag"] = stored["naming_tag"]
                click.echo(f"     [✓] Known form '{raw_form_code}' → {stored['naming_tag']} ({stored['description']})")
                confidence = max(confidence, 0.90)
            elif not no_interactive:
                click.secho(f"\n [?] New form code detected: '{raw_form_code}'", fg="cyan")
                click.echo(f"     AI says this document is: {data.get('naming_tag', '?')}")
                description = click.prompt("     What is this form? (short description)", default="")
                if description:
                    proposed = f"{slugify(raw_form_code)}-{slugify(description)}"
                    naming_tag = click.prompt("     Naming tag for this form type", default=proposed)
                    form_codes[raw_form_code] = {"naming_tag": naming_tag, "description": description}
                    save_form_codes(form_codes)
                    data["naming_tag"] = naming_tag
                    click.secho(f"     [✓] Learned: '{raw_form_code}' → {naming_tag}", fg="green")
            else:
                click.secho(f"     [~] Unknown form code '{raw_form_code}' — using AI description, queuing for review", fg="yellow")
                confidence = min(confidence, CONFIDENCE_THRESHOLD - 0.01)

        scope = 4
        try:
            scope = int(data.get("scope", 4))
        except (TypeError, ValueError):
            pass

        # Person Discovery (Loop 2: user → schema)
        if not no_interactive and subject_key not in known_persons and scope <= 3:
            click.echo(f"\n [?] Found new person: '{subject}'  (confidence: {confidence:.0%})")
            if click.confirm("     Track them?"):
                choice = click.prompt("     Canonical name", default=subject)
                subject_key = slugify(choice).upper().replace("-", "_")
                if subject_key not in known_persons:
                    pfx = click.prompt("     Short prefix (3 chars)", default=choice[:3].lower())
                    known_persons[subject_key] = {"prefix": pfx, "tier": scope, "name": choice}
                    save_known_persons(known_persons)

        # Relevance Intent — distilling user's reason for saving (scope 1–2 only)
        relevance_intent = ""
        if not no_interactive and scope <= 2:
            relevance_intent = click.prompt(
                "\n [?] Why are you saving this? (your context — press Enter to skip)",
                default="", show_default=False
            )

        # List intelligence
        naming_key = subject_key
        if data.get("is_list") and file_path.suffix.lower() == ".pdf":
            click.echo("     [*] List detected — reading preamble (page 1 full)...")
            preamble_pfx = f"tmp_preamble_{stem_safe}"
            subprocess.run(
                f"pdftoppm -f 1 -l 1 -jpeg -r 150 {shlex.quote(str(file_path))} {shlex.quote(preamble_pfx)}",
                shell=True, capture_output=True
            )
            preamble_imgs = sorted(Path(".").glob(f"{preamble_pfx}*.jpg"))
            tmp_files += preamble_imgs
            if preamble_imgs:
                preamble_text = run_ai_cmd(f"ai ocr {shlex.quote(str(preamble_imgs[0]))}")
                if preamble_text.strip():
                    enriched_prompt = f"""A list/roster document. The PREAMBLE below the heading describes its purpose and subject.
Extract: what is this list for? who does it concern? what institution issued it?
Return JSON: {{preamble_summary: string, subject_in_list: string, list_purpose: string}}
PREAMBLE TEXT:
{preamble_text[:2000]}"""
                    preamble_meta_raw = run_ai_cmd(f"ai chat {shlex.quote(enriched_prompt)}")
                    preamble_meta = extract_json(preamble_meta_raw)
                    if preamble_meta:
                        click.echo(f"     [>] List purpose: {preamble_meta.get('list_purpose', '?')}")
                        click.echo(f"     [>] Subject in list: {preamble_meta.get('subject_in_list', '?')}")
                        subject_in_list = preamble_meta.get("subject_in_list", "")
                        if subject_in_list and not filename_prior_key:
                            candidate = slugify(subject_in_list).upper().replace("-", "_")
                            if candidate in known_persons:
                                naming_key = candidate
                        if preamble_meta.get("list_purpose") and not data.get("naming_tag"):
                            data["naming_tag"] = slugify(preamble_meta["list_purpose"])[:30]

        if data.get("is_list") and not no_interactive:
            if click.confirm("\n [?] This looks like a multi-person list. Index a specific entry?"):
                page = click.prompt("     Page number", type=int)
                sno  = click.prompt("     Serial/Index number", type=int)
                person_name = click.prompt("     Person name in this list", default=subject)
                naming_key = slugify(person_name).upper().replace("-", "_")

                click.echo(f"     [*] Verifying page {page}...")
                pg_pfx = f"tmp_verify_{stem_safe}_p{page}"
                subprocess.run(f"pdftoppm -f {page} -l {page} -jpeg {shlex.quote(str(file_path))} {shlex.quote(pg_pfx)}", shell=True, capture_output=True)
                pg_imgs = sorted(Path(".").glob(f"{pg_pfx}*.jpg"))
                tmp_files += pg_imgs
                if pg_imgs:
                    pg_text = run_ai_cmd(f"ai ocr {shlex.quote(str(pg_imgs[0]))}")
                    last_name = person_name.split()[-1].lower()
                    if last_name not in pg_text.lower():
                        click.secho(f"     [!] Warning: '{person_name}' not found on page {page}. Verify manually.", fg="yellow")
                    else:
                        click.secho(f"     [✓] Confirmed '{person_name}' on page {page}.", fg="green")
                data["list_details"] = {"page": page, "sno": sno, "person": person_name}

        # Build name and file
        prefix = known_persons.get(naming_key, {"prefix": "clerk"})["prefix"]
        subject_display = known_persons.get(naming_key, {}).get("name", subject)
        vehicle_no = v_match.group(0) if v_match else ""
        final_name = build_final_name(data, prefix, file_path, vehicle_no)

        if confidence < CONFIDENCE_THRESHOLD:
            click.secho(f"\n [~] Low confidence ({confidence:.0%}) — filing and queuing for review.", fg="yellow")
            add_to_review_queue({
                "filed_as":    final_name,
                "source_file": str(file_path),
                "data":        data,
                "ocr_excerpt": ocr_text[:600],
                "queued_at":   datetime.now().isoformat(),
            })

        actual_name = file_document(data, file_path, final_name, naming_key, subject_display)
        if actual_name is None:
            click.secho(f"[=] Duplicate — already filed as {final_name}", fg="yellow")
            return

        # Write registry entry
        registry_entry = {
            "source_file":       file_path.name,
            "filed_as":          actual_name,
            "vault_type":        data.get("vault_type", "KnowledgeBase"),
            "primary_subject":   subject,
            "person_key":        naming_key,
            "prefix":            prefix,
            "scope":             scope,
            "action_type":       data.get("action_type", ""),
            "naming_tag":        data.get("naming_tag", ""),
            "location":          data.get("location", ""),
            "date":              data.get("date") or (data.get("metadata") or {}).get("date", ""),
            "relevance_intent":  relevance_intent,
            "professional_tags": data.get("professional_tags", []),
            "subject_ids":       [s for s in data.get("subject_ids", []) if s and isinstance(s, str)],
            "assets":            data.get("assets", []),
            "metadata":          data.get("metadata", {}),
            "confidence":        confidence,
            "ingested_at":       datetime.now().isoformat(),
        }
        append_registry_entry(registry_entry)

        # Update relational matrix — only write IDs that belong to primary_subject
        if naming_key in known_persons:
            subject_ids = [s for s in data.get("subject_ids", []) if s and isinstance(s, str)]
            rm.update_matrix(
                naming_key,
                [data.get("location", "")],
                data.get("professional_tags", []),
                subject_ids,
                assets=[v_match.group(0)] if v_match else data.get("assets", []),
            )

        click.secho(f"\n[✓] Filed: {actual_name}", fg="green", bold=True)
        click.echo(f"    Vault: {data.get('vault_type', '?')}  |  Confidence: {confidence:.0%}")
        if relevance_intent:
            click.echo(f"    Intent: {relevance_intent}")

    finally:
        for t in tmp_files:
            if t.exists():
                t.unlink()


# ── REVIEW ────────────────────────────────────────────────────────────────────

@cli.command()
def review():
    """Process the low-confidence review queue."""
    queue = load_review_queue()
    if not queue:
        click.secho("[✓] Review queue is empty.", fg="green")
        return

    click.secho(f"\n[*] {len(queue)} item(s) in review queue.", fg="cyan", bold=True)
    remaining = []

    for i, item in enumerate(queue, 1):
        d = item["data"]
        click.echo(f"\n{'─'*50}")
        click.echo(f"[{i}/{len(queue)}]  {item['filed_as']}")
        click.echo(f"  Subject:    {d.get('primary_subject', '?')}")
        click.echo(f"  Vault:      {d.get('vault_type', '?')}")
        click.echo(f"  Tag:        {d.get('naming_tag', '?')}")
        click.echo(f"  Date:       {d.get('date', '?')}")
        click.echo(f"  Confidence: {float(d.get('confidence', 0)):.0%}")
        click.echo(f"  OCR:        {item.get('ocr_excerpt', '')[:200]}...")

        choice = click.prompt("\n  [a]ccept / [c]orrect / [s]kip", default="s")
        if choice == "a":
            append_registry_entry({**d, "filed_as": item["filed_as"], "source_file": item["source_file"], "reviewed": True})
            click.secho("  [✓] Accepted.", fg="green")
        elif choice == "c":
            d["primary_subject"] = click.prompt("  Subject",  default=d.get("primary_subject", ""))
            d["vault_type"]      = click.prompt("  Vault (ServiceRecord/ProfessionalOutput/KnowledgeBase)", default=d.get("vault_type", "KnowledgeBase"))
            d["naming_tag"]      = click.prompt("  Naming tag", default=d.get("naming_tag", ""))
            d["date"]            = click.prompt("  Date (YYYY-MM-DD)", default=d.get("date", ""))
            d["relevance_intent"]= click.prompt("  Why saved", default=d.get("relevance_intent", ""))
            append_registry_entry({**d, "filed_as": item["filed_as"], "source_file": item["source_file"], "reviewed": True, "corrected": True})
            click.secho("  [✓] Corrected and accepted.", fg="green")
        else:
            remaining.append(item)

    save_review_queue(remaining)
    click.secho(f"\n[*] {len(remaining)} item(s) still pending.", fg="cyan")


# ── CORRECT ───────────────────────────────────────────────────────────────────

@cli.command()
@click.argument("filed_name")
def correct(filed_name):
    """Interactively correct a filed document's classification in the registry."""
    registry = load_registry()
    entry = next((e for e in registry if e.get("filed_as") == filed_name), None)
    if not entry:
        click.secho(f"[!] '{filed_name}' not found in registry.", fg="red")
        return

    click.secho(f"\nCorrecting: {filed_name}", bold=True)
    for field in ("primary_subject", "vault_type", "naming_tag", "date", "location", "relevance_intent"):
        click.echo(f"  {field}: {entry.get(field, '')}")

    click.echo("")
    entry["primary_subject"]  = click.prompt("  Subject",     default=entry.get("primary_subject", ""))
    entry["vault_type"]       = click.prompt("  Vault",       default=entry.get("vault_type", "KnowledgeBase"))
    entry["naming_tag"]       = click.prompt("  Tag",         default=entry.get("naming_tag", ""))
    entry["date"]             = click.prompt("  Date",        default=entry.get("date", ""))
    entry["relevance_intent"] = click.prompt("  Intent",      default=entry.get("relevance_intent", ""))
    entry["corrected"] = True

    updated = [e if e.get("filed_as") != filed_name else entry for e in load_registry()]
    save_json(REGISTRY_FILE, updated)

    rm = RelationalMatrix()
    person_key = entry.get("person_key", "")
    if person_key:
        rm.update_matrix(person_key, [entry.get("location", "")], entry.get("professional_tags", []), [])

    click.secho(f"\n[✓] Registry updated for {filed_name}", fg="green")


# ── TIMELINE ──────────────────────────────────────────────────────────────────

@cli.command()
@click.argument("person_prefix")
@click.option("--out", default=None, help="Write to file instead of stdout.")
def timeline(person_prefix, out):
    """Generate a chronological service book for a person."""
    registry = load_registry()
    known_persons = load_known_persons()

    target_key = next(
        (k for k, v in known_persons.items() if v.get("prefix") == person_prefix or k == person_prefix.upper()),
        None
    )
    if not target_key:
        known = [f"{v['prefix']} ({k})" for k, v in known_persons.items()]
        click.secho(f"[!] Unknown person '{person_prefix}'. Known: {', '.join(known)}", fg="red")
        return

    person_name = known_persons[target_key].get("name", target_key)
    entries = [e for e in registry if e.get("person_key") == target_key]

    if not entries:
        click.secho(f"[!] No documents found for '{person_name}'.", fg="yellow")
        return

    entries.sort(key=lambda e: e.get("date") or "9999")
    lines = [f"# Service Record: {person_name}\n", f"Generated: {datetime.now().strftime('%Y-%m-%d')}\n"]
    current_year = None

    for e in entries:
        year = get_safe_year(e.get("date", "")) or "Undated"
        if year != current_year:
            current_year = year
            lines.append(f"\n## {year}\n")

        tag    = e.get("naming_tag") or e.get("action_type") or "document"
        vault  = e.get("vault_type", "")
        loc    = e.get("location", "")
        intent = e.get("relevance_intent", "")
        filed  = e.get("filed_as", "")
        conf   = float(e.get("confidence", 1.0))
        flag   = " ⚠" if conf < CONFIDENCE_THRESHOLD else ""

        parts = [f"**{tag}**"]
        if loc:
            parts.append(loc)
        if vault:
            parts.append(f"_{vault}_")
        if intent:
            parts.append(f"— _{intent}_")
        parts.append(f"`{filed}`{flag}")
        lines.append(f"- {' — '.join(parts)}\n")

    output = "".join(lines)
    if out:
        Path(out).write_text(output)
        click.secho(f"[✓] Timeline written to {out}", fg="green")
    else:
        click.echo(output)


# ── LIST ──────────────────────────────────────────────────────────────────────

@cli.command("list")
@click.argument("person_prefix", required=False)
def list_vault(person_prefix):
    """Show vault status. Pass a prefix to drill into one person."""
    registry      = load_registry()
    known_persons = load_known_persons()
    queue         = load_review_queue()

    def vault_breakdown(entries):
        by_vault: dict = {}
        for e in entries:
            v = e.get("vault_type", "Unknown")
            by_vault[v] = by_vault.get(v, 0) + 1
        return by_vault

    if person_prefix:
        target_key = next((k for k, v in known_persons.items() if v.get("prefix") == person_prefix), None)
        if not target_key:
            click.secho(f"[!] Unknown prefix '{person_prefix}'.", fg="red")
            return
        entries = [e for e in registry if e.get("person_key") == target_key]
        name = known_persons[target_key].get("name", target_key)
        click.secho(f"\n{name} ({person_prefix}) — {len(entries)} documents", bold=True)
        for vault, count in sorted(vault_breakdown(entries).items()):
            click.echo(f"  {vault:28s} {count}")
        return

    click.secho("\nVault Status", bold=True)
    click.echo("=" * 42)
    for key, pdata in known_persons.items():
        pfx  = pdata.get("prefix", "?")
        name = pdata.get("name", key)
        entries = [e for e in registry if e.get("person_key") == key]
        if not entries:
            continue
        click.secho(f"\n{name} ({pfx})  —  {len(entries)} documents", bold=True)
        for vault, count in sorted(vault_breakdown(entries).items()):
            click.echo(f"  {vault:28s} {count}")

    click.echo(f"\n{'─'*42}")
    click.echo(f"Total registry : {len(registry)}")
    click.echo(f"Review queue   : {len(queue)} pending")


# ── GAPS ──────────────────────────────────────────────────────────────────────

@cli.command()
@click.argument("person_prefix")
def gaps(person_prefix):
    """Surface potential gaps in a person's service record."""
    registry      = load_registry()
    known_persons = load_known_persons()

    target_key = next((k for k, v in known_persons.items() if v.get("prefix") == person_prefix), None)
    if not target_key:
        click.secho(f"[!] Unknown prefix '{person_prefix}'.", fg="red")
        return

    person_name = known_persons[target_key].get("name", target_key)
    entries = [e for e in registry if e.get("person_key") == target_key and e.get("vault_type") == "ServiceRecord"]

    if not entries:
        click.secho(f"[!] No ServiceRecord documents found for '{person_name}'.", fg="yellow")
        return

    tags = {(e.get("naming_tag") or "").lower() for e in entries}
    years = sorted({get_safe_year(e.get("date", "")) for e in entries if get_safe_year(e.get("date", ""))})

    click.secho(f"\nGap Analysis: {person_name}", bold=True)
    click.echo(f"  Documents: {len(entries)}  |  Span: {years[0] if years else '?'} – {years[-1] if years else '?'}")

    expected = {
        "appointment/joining": ["appoint", "join"],
        "promotion":           ["promot", "senior", "upgrad"],
        "salary / GA55":       ["ga55", "salary", "pay"],
        "leave":               ["leave", "casual", "earned"],
        "transfer":            ["transfer", "reliev", "posting"],
    }

    click.echo("\n  Expected document types:")
    for label, keywords in expected.items():
        found = any(any(kw in tag for kw in keywords) for tag in tags)
        mark = click.style("[✓]", fg="green") if found else click.style("[?]", fg="yellow")
        click.echo(f"    {mark}  {label}")

    if len(years) >= 2:
        click.echo("\n  Year gaps (>2 years with no documents):")
        any_gap = False
        for i in range(len(years) - 1):
            gap = int(years[i + 1]) - int(years[i])
            if gap > 2:
                click.secho(f"    [!] {years[i]} → {years[i+1]}  ({gap} year gap)", fg="yellow")
                any_gap = True
        if not any_gap:
            click.secho("    [✓] No significant year gaps.", fg="green")


# ── CLEAN ─────────────────────────────────────────────────────────────────────

@cli.command()
def clean():
    """Drop registry entries whose file no longer exists in archive."""
    registry = load_registry()
    before = len(registry)
    live = [e for e in registry if (ARCHIVE_DIR / e.get("filed_as", "")).exists()]
    save_json(REGISTRY_FILE, live)
    click.secho(f"[✓] Removed {before - len(live)} stale entries. {len(live)} remain.", fg="green")


# ── AUTO ──────────────────────────────────────────────────────────────────────

@cli.command()
@click.argument("directory", type=click.Path(exists=True, file_okay=False))
def auto(directory):
    """Batch-ingest all files in a directory with no interactive prompts."""
    dir_path = Path(directory)

    is_course, kind, sig = _is_course_folder(dir_path)
    if is_course:
        click.secho(
            f"[!] '{dir_path.name}' looks like a {kind} course "
            f"({sig['total']} files, {sig['videos']} video, {sig['sequential']} sequential).",
            fg="yellow", bold=True,
        )
        click.secho("    Use 'aiclerk courses <parent-dir> --move' to relocate it instead.", fg="yellow")
        return

    course_subs = []
    for sub in sorted(dir_path.iterdir()):
        if not sub.is_dir():
            continue
        is_c, k, s = _is_course_folder(sub)
        if is_c:
            course_subs.append((sub, k, s))

    if course_subs:
        click.secho(f"\n[*] Found {len(course_subs)} course subfolder(s) — moving to {COURSES_DIR}/", fg="cyan")
        for sub, k, s in course_subs:
            dest = _move_course(sub, k)
            click.secho(f"    [✓] {sub.name}  [{k}]  → {dest}", fg="green")

    SUPPORTED = {".pdf", ".jpg", ".jpeg", ".png"}
    files = sorted(f for f in dir_path.iterdir() if f.is_file() and f.suffix.lower() in SUPPORTED)

    if not files:
        click.secho(f"[!] No supported files in {directory}", fg="yellow")
        return

    registry = load_registry()
    already_filed = {e.get("source_file") for e in registry}
    pending = [f for f in files if f.name not in already_filed]
    skipped = len(files) - len(pending)

    click.secho(f"\n[*] Auto mode — {len(pending)} to process, {skipped} already filed", fg="cyan", bold=True)
    filed, failed = [], []

    for i, f in enumerate(pending, 1):
        click.secho(f"\n{'─'*52}", fg="cyan")
        click.secho(f"[{i}/{len(pending)}]  {f.name}", fg="cyan", bold=True)
        result = subprocess.run(["aiclerk", "ingest", "--no-interactive", str(f)])
        (filed if result.returncode == 0 else failed).append(f.name)

    click.secho(f"\n{'='*52}", bold=True)
    click.secho(f"Auto complete: {len(filed)} filed, {len(failed)} failed", bold=True)
    if failed:
        click.secho("\nFailed files:", fg="red")
        for name in failed:
            click.echo(f"  {name}")


# ── COURSES ───────────────────────────────────────────────────────────────────

@cli.command()
@click.argument("directory", type=click.Path(exists=True, file_okay=False))
@click.option("--move", is_flag=True, help="Actually move detected course folders (default: dry-run).")
def courses(directory, move):
    """Detect course folders in a directory. Dry-run by default; --move to relocate."""
    dir_path = Path(directory)

    is_course, kind, sig = _is_course_folder(dir_path)
    if is_course:
        click.secho(
            f"[!] '{dir_path.name}' itself looks like a {kind} course "
            f"({sig['total']} files, {sig['videos']} video, {sig['pdfs']} PDF, {sig['sequential']} sequential).",
            fg="yellow", bold=True,
        )
        click.secho("    Pass its parent directory to relocate it.", fg="yellow")
        return

    found: list[tuple[Path, str, dict]] = []
    for sub in sorted(dir_path.iterdir()):
        if not sub.is_dir():
            continue
        is_c, k, s = _is_course_folder(sub)
        if is_c:
            found.append((sub, k, s))

    if not found:
        click.secho("[✓] No course folders detected.", fg="green")
        return

    click.secho(f"\n[*] Found {len(found)} course folder(s):", fg="cyan", bold=True)
    for sub, k, s in found:
        click.echo(
            f"  {sub.name:<40} [{k}]  "
            f"{s['total']} files  ({s['videos']} video, {s['pdfs']} PDF, {s['sequential']} sequential)"
        )

    if not move:
        click.secho(f"\n[~] Dry-run. Use --move to relocate to {COURSES_DIR}/", fg="yellow")
        return

    click.echo("")
    for sub, k, s in found:
        dest = _move_course(sub, k)
        click.secho(f"[✓] Moved: {sub.name} → {dest}", fg="green")


# ── SYNC ──────────────────────────────────────────────────────────────────────

@cli.command()
@click.argument("directory", type=click.Path(exists=True, file_okay=False), default="inbox")
@click.option("--interval", "-i", type=int, default=0, help="Continuous loop interval in seconds (0 = run once).")
def sync(directory, interval):
    """Reconcile a directory with the registry. Only new files are processed."""
    dir_path = Path(directory)

    def run_pass():
        click.secho(f"\n[*] Syncing '{directory}' at {datetime.now().strftime('%H:%M:%S')}...", fg="cyan")

        is_course, kind, sig = _is_course_folder(dir_path)
        if is_course:
            click.secho(f" [!] '{directory}' is a course. Use 'aiclerk courses' to move.", fg="yellow")
            return

        SUPPORTED = {".pdf", ".jpg", ".jpeg", ".png"}
        files = sorted(f for f in dir_path.iterdir() if f.is_file() and f.suffix.lower() in SUPPORTED)

        if not files:
            click.echo(" [✓] Inbox is empty.")
            return

        registry = load_registry()
        already_filed = {e.get("source_file") for e in registry}
        pending = [f for f in files if f.name not in already_filed]

        if not pending:
            click.echo(f" [✓] All {len(files)} files are already indexed.")
            return

        click.secho(f" [*] Found {len(pending)} new file(s) to ingest.", bold=True)
        for i, f in enumerate(pending, 1):
            click.echo(f"     [{i}/{len(pending)}] Ingesting {f.name}...")
            subprocess.run(["aiclerk", "ingest", "--no-interactive", str(f)])

    try:
        if interval > 0:
            click.secho(f"[*] Starting Sync Agent (Interval: {interval}s). Press Ctrl+C to stop.", fg="green", bold=True)
            while True:
                run_pass()
                time.sleep(interval)
        else:
            run_pass()
    except KeyboardInterrupt:
        click.secho("\n[*] Sync Agent stopped.", fg="yellow")


# ── FILL ──────────────────────────────────────────────────────────────────────

@cli.command()
@click.argument("form_path", type=click.Path(exists=True))
@click.option("--person", "-p", default="ash", help="Person prefix or CANONICAL_KEY.")
def fill(form_path, person):
    """Pre-fill a blank form using the person's profile and filed documents."""
    form_path = Path(form_path)

    known = load_known_persons()
    person_key = next(
        (k for k, v in known.items() if v.get("prefix") == person or k == person.upper()),
        None,
    )
    if not person_key:
        click.secho(f"Unknown person: {person}. Known prefixes: {[v.get('prefix') for v in known.values()]}", fg="red")
        return

    person_name = known[person_key].get("name", person_key)
    click.secho(f"Filling form for: {person_name}", fg="cyan", bold=True)

    # --- Full-page OCR ---
    ocr_text = ""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        ext = form_path.suffix.lower()

        if ext == ".pdf":
            result = subprocess.run(
                f"pdfinfo {shlex.quote(str(form_path))} 2>/dev/null",
                shell=True, capture_output=True, text=True
            )
            n_pages = 1
            for line in result.stdout.splitlines():
                if line.startswith("Pages:"):
                    try:
                        n_pages = int(line.split(":")[1].strip())
                    except ValueError:
                        pass

            click.secho(f"OCR: {n_pages} page(s)...", fg="cyan")
            for page_num in range(1, n_pages + 1):
                pfx = str(tmp / f"p{page_num}")
                subprocess.run(
                    f"pdftoppm -f {page_num} -l {page_num} -jpeg -r 200 "
                    f"{shlex.quote(str(form_path))} {shlex.quote(pfx)}",
                    shell=True, capture_output=True,
                )
                imgs = sorted(tmp.glob(f"p{page_num}*.jpg"))
                if imgs:
                    page_text = normalize_text(run_ai_cmd(f"ai ocr {shlex.quote(str(imgs[0]))}"))
                    ocr_text += f"\n--- PAGE {page_num} ---\n{page_text}"
        else:
            ocr_text = normalize_text(run_ai_cmd(f"ai ocr {shlex.quote(str(form_path))}"))

    if not ocr_text.strip():
        click.secho("OCR returned no text. Cannot continue.", fg="red")
        return

    # --- Build person profile ---
    profile = build_person_profile(person_key)
    profile_lines = [f"Name: {profile['name']}"]
    if profile.get("employee_id"):
        profile_lines.append(f"Employee ID / GPF No.: {profile['employee_id']}")
    if profile.get("vehicle_no"):
        profile_lines.append(f"Vehicle No.: {profile['vehicle_no']}")
    if profile.get("known_locations"):
        profile_lines.append(f"Known postings / offices: {'; '.join(profile['known_locations'][:6])}")
    if profile.get("institutions"):
        clean_inst = [i for i in profile["institutions"] if len(i) > 4][:8]
        profile_lines.append(f"Known institutions: {'; '.join(clean_inst)}")
    if profile.get("keywords"):
        profile_lines.append(f"Other known IDs/codes: {', '.join(profile['keywords'][:10])}")
    # User-supplied profile fields (DOB, address, email, etc.)
    for k, v in profile.get("profile", {}).items():
        profile_lines.append(f"{k}: {v}")
    if profile.get("document_excerpts"):
        profile_lines.append("\nOCR data from filed documents:")
        for exc in profile["document_excerpts"]:
            profile_lines.append(f"  {exc}")
    profile_str = "\n".join(profile_lines)

    # --- Step 1: extract blank field labels ---
    label_prompt = (
        f"Here is an OCR scan of an official form or application.\n\n"
        f"FORM TEXT:\n{ocr_text[:4000]}\n\n"
        "List every blank field or line that the applicant must fill in. "
        "Only list field labels, not printed instructions, headings, or already-filled values. "
        "Return ONLY a JSON array of short label strings, e.g. "
        '["Name", "Date of Birth", "Employee ID"]. No explanation.'
    )
    click.secho("Step 1: Extracting form fields...", fg="cyan")
    labels_raw = run_ai_cmd(f"ai chat -s 'Output raw JSON only.' {shlex.quote(label_prompt)}")
    labels: list[str] = []
    # Try clean parse first; fall back to extracting quoted strings from truncated output
    try:
        m = re.search(r"\[.*?\]", labels_raw, re.DOTALL)
        if m:
            labels = json.loads(m.group(0))
    except Exception:
        pass
    if not labels:
        # Truncated array: pull every "quoted string" value
        labels = re.findall(r'"([^"]{3,80})"', labels_raw)
    if not labels:
        click.secho("Could not extract field labels from form.", fg="red")
        click.echo(labels_raw[:400])
        return
    click.secho(f"  Found {len(labels)} field(s).", fg="cyan")

    # --- Step 2: fill fields in batches to avoid token truncation ---
    BATCH = 10
    fill_data: dict = {}
    click.secho(f"Step 2: Filling {len(labels)} field(s) (batches of {BATCH})...", fg="cyan")

    def _try_parse_dict(raw: str) -> dict:
        # LLM sometimes returns [{k:v}, {k:v}] (array of single-key objects) or
        # {"k":v, ...} (flat dict). Handle both, plus truncation.

        def _merge(obj) -> dict:
            if isinstance(obj, dict):
                return obj
            if isinstance(obj, list):
                merged: dict = {}
                for item in obj:
                    if isinstance(item, dict):
                        merged.update(item)
                return merged
            return {}

        # Try clean parse first
        for pattern in [r"\[.*\]", r"\{.*\}"]:
            m = re.search(pattern, raw, re.DOTALL)
            if m:
                try:
                    return _merge(json.loads(m.group(0)))
                except json.JSONDecodeError:
                    pass

        # Truncated: pull complete {...} sub-objects with regex
        merged: dict = {}
        for m in re.finditer(r'"([^"]+)"\s*:\s*(\{[^}]+\})', raw):
            try:
                merged[m.group(1)] = json.loads(m.group(2))
            except json.JSONDecodeError:
                pass
        return merged

    for i in range(0, len(labels), BATCH):
        batch = labels[i: i + BATCH]
        fill_prompt = (
            f"Fill in these form fields for {profile['name']}.\n\n"
            f"PERSON PROFILE:\n{profile_str[:2000]}\n\n"
            f"FIELDS: {json.dumps(batch)}\n\n"
            "For each field provide the best value from the profile, or null if unknown. "
            "confidence 0.0-1.0, source: profile|registry|inferred|unknown. "
            'Return ONLY: {"FIELD": {"v": "value or null", "c": 0.9, "s": "source"}, ...}'
        )
        raw = run_ai_cmd(f"ai chat -s 'Output raw JSON only.' {shlex.quote(fill_prompt)}")
        fill_data.update(_try_parse_dict(raw))

    fields: list[dict] = []
    for label in labels:
        entry = fill_data.get(label, {})
        if not isinstance(entry, dict):
            entry = {}
        fields.append({
            "label":      label,
            "value":      entry.get("v") or None,
            "confidence": float(entry.get("c", 0)),
            "source":     entry.get("s", "unknown"),
            "note":       entry.get("n", ""),
        })
    filled    = [f for f in fields if f.get("value") and f.get("confidence", 0) >= 0.75]
    uncertain = [f for f in fields if f.get("value") and f.get("confidence", 0) < 0.75]
    missing   = [f for f in fields if not f.get("value")]

    # --- Print table ---
    click.echo()
    click.secho(f"  Form: {form_path.name}  /  Person: {person_name}", bold=True)
    click.secho("  " + "─" * 58)
    for f in filled:
        click.secho(f"  [OK]  {f['label']:<32} {str(f['value'])[:30]}", fg="green")
    for f in uncertain:
        pct = int(f.get("confidence", 0) * 100)
        click.secho(f"  [??]  {f['label']:<32} {str(f['value'])[:30]}  ({pct}%)", fg="yellow")
    for f in missing:
        click.secho(f"  [--]  {f['label']}", fg="red")
    click.secho("  " + "─" * 58)
    click.secho(
        f"  Filled: {len(filled)}   Uncertain: {len(uncertain)}   Missing: {len(missing)}",
        bold=True,
    )

    # --- Interactively fill missing fields ---
    if missing:
        click.echo()
        click.secho("Fill in missing fields (press Enter to skip):", fg="cyan")
        profile_updates: dict = {}
        for f in missing:
            val = click.prompt(f"  {f['label']}", default="", show_default=False)
            if val.strip():
                f["value"] = val.strip()
                f["confidence"] = 1.0
                f["source"] = "user"
                profile_updates[f["label"]] = val.strip()

        if profile_updates:
            existing = load_profile(person_key)
            existing.update(profile_updates)
            save_profile(person_key, existing)
            click.secho(f"Saved {len(profile_updates)} new field(s) to profile for next time.", fg="cyan")

    # --- Save report ---
    FILL_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filled_now   = [f for f in fields if f.get("value") and f.get("confidence", 0) >= 0.75]
    uncertain_now = [f for f in fields if f.get("value") and f.get("confidence", 0) < 0.75]
    missing_now  = [f for f in fields if not f.get("value")]
    report = {
        "form": str(form_path),
        "form_name": form_path.name,
        "person_key": person_key,
        "person_name": person_name,
        "generated_at": datetime.now().isoformat(),
        "fields": fields,
        "stats": {
            "filled": len(filled_now),
            "uncertain": len(uncertain_now),
            "missing": len(missing_now),
        },
    }
    report_path = FILL_REPORTS_DIR / f"{person_key}_{form_path.stem}_{ts}.json"
    latest_path = FILL_REPORTS_DIR / "latest.json"
    save_json(report_path, report)
    save_json(latest_path, report)
    click.secho(f"\n  Report: {report_path}", fg="cyan")


# ── PROFILE INTERVIEW ─────────────────────────────────────────────────────────

# Fields the clerk will ask about, in order. Label → prompt question.
_PROFILE_QUESTIONS: list[tuple[str, str]] = [
    ("Full Name",                    "Full name (with title, e.g. Dr. Ashish Yadav)"),
    ("Date of Birth",                "Date of birth (DD-MM-YYYY)"),
    ("Father's Name",                "Father's name"),
    ("Present Designation",          "Current designation (e.g. Medical Officer / Asst. Professor)"),
    ("Department",                   "Department (e.g. General Medicine)"),
    ("Present Institution",          "Present institution / office"),
    ("Date of Joining",              "Date of joining present institution (DD-MM-YYYY)"),
    ("Mobile Number",                "Mobile number"),
    ("Email Address",                "Email address"),
    ("Present Address",              "Present residential address"),
    ("Permanent Address",            "Permanent residential address"),
    ("MBBS College",                 "MBBS college name"),
    ("MBBS University",              "MBBS university"),
    ("MBBS Year",                    "MBBS passing year"),
    ("MD/MS Subject",                "MD / MS subject (leave blank if not applicable)"),
    ("MD/MS College",                "MD / MS college (leave blank if not applicable)"),
    ("MD/MS Year",                   "MD / MS passing year (leave blank if not applicable)"),
    ("Medical Council Reg. No.",     "Medical council registration number"),
    ("State Medical Council",        "State medical council (e.g. Rajasthan Medical Council)"),
    ("Employee ID",                  "Employee / GPF number"),
    ("PAN",                          "PAN number"),
]


@cli.command()
@click.option("--person", "-p", default="ash", help="Person prefix or CANONICAL_KEY.")
@click.option("--reset", is_flag=True, help="Re-ask all questions, including already answered ones.")
def profile(person, reset):
    """Interview the user to build their personal profile for form filling."""
    known = load_known_persons()
    person_key = next(
        (k for k, v in known.items() if v.get("prefix") == person or k == person.upper()),
        None,
    )
    if not person_key:
        click.secho(f"Unknown person: {person}", fg="red")
        return

    person_name = known[person_key].get("name", person_key)
    stored = load_profile(person_key)
    already_known = {k for k, v in stored.items() if v}

    click.echo()
    click.secho(f"  Profile interview for {person_name}", bold=True, fg="cyan")
    if not reset and already_known:
        click.secho(f"  {len(already_known)} field(s) already on file — skipping those (use --reset to re-ask all).", fg="cyan")
    click.secho("  Press Enter to skip any question.", fg="cyan")
    click.echo()

    updates: dict[str, str] = {}
    for label, question in _PROFILE_QUESTIONS:
        if not reset and label in already_known:
            click.secho(f"  [✓] {label}: {stored[label]}", fg="green")
            continue
        val = click.prompt(f"  {question}", default="", show_default=False).strip()
        if val:
            updates[label] = val
            click.secho(f"      Saved.", fg="green")

    if updates:
        stored.update(updates)
        save_profile(person_key, stored)
        click.echo()
        click.secho(f"  {len(updates)} field(s) saved to profile.", fg="cyan", bold=True)
        click.secho(f"  These will auto-fill in future: aiclerk fill <form> --person {person}", fg="cyan")
    else:
        click.echo()
        click.secho("  Nothing new to save.", fg="yellow")

    # Write a summary JSON for the UI to read
    FILL_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    summary = {
        "person_key": person_key,
        "person_name": person_name,
        "updated_at": datetime.now().isoformat(),
        "fields": [
            {"label": label, "value": stored.get(label) or None}
            for label, _ in _PROFILE_QUESTIONS
        ],
    }
    save_json(FILL_REPORTS_DIR / "profile_summary.json", summary)
    click.secho(f"  Profile summary: output/fill_reports/profile_summary.json", fg="cyan")


# ── SLASH COMMAND REPL ────────────────────────────────────────────────────────

@cli.command("/")
def repl():
    """Enter the AiClerk Slash Command REPL."""
    click.secho("\n╔════════════════════════════════════════════╗", fg="cyan")
    click.secho("║        AiClerk Interactive Agent           ║", fg="cyan", bold=True)
    click.secho("╚════════════════════════════════════════════╝", fg="cyan")
    click.echo("  Type /help for commands, /exit to quit.\n")

    ctx = click.get_current_context()

    while True:
        try:
            line = click.prompt(click.style("aiclerk", fg="cyan") + " ❯", prompt_suffix=" ").strip()
        except (KeyboardInterrupt, EOFError):
            click.echo()
            break

        if not line:
            continue

        if line in ("/exit", "/quit", "/q"):
            break

        if line == "/help":
            click.echo("\n  Commands:")
            click.echo("    /ingest <file>  - Process a specific file")
            click.echo("    /sync [dir]     - Sync inbox (reconcile state)")
            click.echo("    /review         - Start low-confidence review loop")
            click.echo("    /list [prefix]  - Show vault status")
            click.echo("    /timeline <pfx> - Generate person history")
            click.echo("    /gaps <pfx>     - Run gap analysis")
            click.echo("    /clean          - Remove stale registry entries")
            click.echo("    /exit           - Exit the REPL\n")
            continue

        parts = shlex.split(line)
        cmd_name = parts[0].lstrip("/")
        args = parts[1:]

        subcommand = cli.get_command(ctx, cmd_name)
        if subcommand:
            try:
                with cli.make_context(cmd_name, args, parent=ctx) as sub_ctx:
                    subcommand.invoke(sub_ctx)
            except click.exceptions.Exit:
                pass
            except Exception as e:
                click.secho(f" [!] Error: {e}", fg="red")
        else:
            click.secho(f" [!] Unknown command: {line}", fg="red")

    click.secho("\n[*] Agent session ended.", fg="cyan")


if __name__ == "__main__":
    cli()
