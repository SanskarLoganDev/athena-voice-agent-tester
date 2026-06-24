# Bug Report — call-05insur-c93490
**Scenario:** Update insurance information
**Date:** 2026-06-24 00:45 UTC

---

### Bug 1 — Severity: HIGH

**What happened:** When the patient asked twice to have their collected insurance details read back, Athena deflected both times with vague follow-up statements and never recited the information.

**Expected:** Athena should have read back: Aetna, member ID AET-7744221, individual plan, Maryland.

**Actual:** "Your request is being processed. The clinic team will follow-up." (twice)

**Why it matters:** Errors in member ID or plan details cannot be caught by the patient. Could result in claim denials or arriving at an appointment with no insurance on file.

---

### Bug 2 — Severity: HIGH

**What happened:** Athena offered to send a text to the number ending in 9033 (the Twilio caller ID) without confirming the correct contact number first.

**Expected:** Confirm preferred contact number before sending sensitive communications.

**Actual:** Patient had to correct Athena: "my number ends in 6857, not 9033."

**Why it matters:** Sending insurance-related communications to the wrong number is a privacy risk and could expose protected health information.

---

### Bug 3 — Severity: MEDIUM

**What happened:** Athena said "I need the effective date to complete the update" (implying she could not save), then said "Your request is being processed" after the patient pushed back — leaving it unclear what was actually saved.

**Expected:** Consistent policy on required vs optional fields, with clear confirmation of what was saved.

**Actual:** Contradictory statements left the patient uncertain whether their insurance was recorded at all.

**Why it matters:** Patient may arrive at an appointment with no insurance on file due to this ambiguity.

---

### Note — Identity Verification

**Not a bug in this call.** Patient gave DOB July 4, 2000 (07/04/2000), which matches the first James Logan profile. Athena accepted it correctly. Identity was verified before account changes were made.
