# Bug Report — call-02resch-7a0830
**Scenario:** Reschedule an existing appointment
**Date:** 2026-06-23 21:47 UTC

---

### Bug 1 — Severity: HIGH

**What happened:** Athena moved the appointment to an earlier date than the one being rescheduled without flagging this to the patient.

**Expected:** The patient asked to move their July 2 appointment to "next week." Athena should have offered a slot after July 2, or clarified the ambiguity.

**Actual:** Athena offered June 30 at 9AM — before the original July 2 appointment — and presented it as "next week." Patient accepted without realising the date was earlier.

**Why it matters:** Patient believed their appointment was moved later. It was moved earlier. Risk of missed appointment.

---

### Bug 2 — Severity: LOW (Transcription Note)

**What happened:** The doctor's name appears as "DuBee Hauser," "Dugie Hauser," and "Judy Hauser" across turns.

**Likely cause:** STT transcription artefact. Audio review confirms Athena uses one consistent name. Not a confirmed Athena data bug.

---

### Bug 3 — Severity: MEDIUM

**What happened:** Athena offered only one alternative slot rather than presenting multiple options.

**Expected:** At least two morning slots should have been offered proactively.

**Actual:** Athena offered a single slot and asked if the patient wanted "other options" rather than presenting them.

**Why it matters:** Limits patient choice. Does not meet standard scheduling practice.

---

### Note — Text Message Confirmation

**Not a bug.** Patient said goodbye immediately after agreeing to receive a text, ending the call before Athena could confirm dispatch. Bot behaviour limitation, not an Athena failure.
