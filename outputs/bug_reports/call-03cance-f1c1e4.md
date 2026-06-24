# Bug Report — call-03cance-f1c1e4
**Scenario:** Cancel an existing appointment
**Date:** 2026-06-23 23:29 UTC

---

### Bug 1 — Severity: HIGH

**What happened:** Athena asked "How can I help you today?" after the patient had already stated they wanted to cancel their appointment, forcing a repeat.

**Expected:** Athena should have acknowledged the cancellation request and located the appointment.

**Actual:** Intent was dropped. Patient had to repeat the request.

**Why it matters:** Dialogue state tracking failure. Erodes trust and suggests intent may be dropped in other flows.

---

### Bug 2 — Severity: MEDIUM

**What happened:** Athena used "Doogie Howser" in the confirmation prompt while using a different name in every other turn of the same call.

**Expected:** Provider name must be consistent within a single call, especially in confirmation prompts.

**Actual:** "Judy Hauser" used in turns 9 and 15; "Doogie Howser" used in the cancellation confirmation at turn 13. Audio confirms this is Athena's own output, not an STT artefact.

**Why it matters:** Patient confirmed a cancellation against a name that did not match the appointment. Creates ambiguity about which appointment was cancelled.

---

### Bug 3 — Severity: MEDIUM

**What happened:** Athena did not offer to reschedule after completing the cancellation.

**Expected:** Should have offered to book a new appointment.

**Actual:** Confirmed cancellation and ended the call with no offer to reschedule.

**Why it matters:** Missed clinical safety net. Patient cancelling may still need future care.

---

### Bug 4 — Severity: HIGH

**What happened:** Athena flagged the patient's correct DOB (November 4, 2000) as not matching records, then bypassed verification with "for demo purposes."

**Context:** Two profiles exist for James Logan — one with DOB 07/04/2000, one with 11/04/2000. Athena inconsistently checked the wrong profile in this call, despite having accepted November 4, 2000 without issue in the prior reschedule call.

**Expected:** Consistent profile resolution across calls. If mismatch, ask for additional verification — never bypass with internal demo language.

**Actual:** "The birthday doesn't match our records, but for demo purposes, I'll accept it."

**Why it matters:** Compounding failure: wrong profile checked, verification bypassed, and internal system state exposed to the caller.
