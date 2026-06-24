# Bug Report — call-08inter-f30287
**Scenario:** Barge-in and mid-sentence topic switch
**Date:** 2026-06-24 11:35 UTC

---

### Bug 1 — Severity: MEDIUM

**What happened:** Athena offered callbacks to the number ending in 9033 (the Twilio caller ID) rather than the patient's personal number ending in 6857 — even though the patient had corrected this in a prior call (call-04refil-231390).

**Expected:** The corrected phone number should be persisted to the patient profile and used in subsequent calls.

**Actual:** "I have your number as 4 2 4 6 8 8 9 0 3 3." Patient had to correct again.

**Why it matters:** Refill notifications and appointment reminders sent to the wrong number mean the patient misses critical communications. The fact that the correction from call-04 was not retained shows phone number updates are not persisted to the profile.

---

### Positive Finding — Barge-in Handling

Athena handled three sequential mid-sentence topic switches correctly — from refill to appointment check to reschedule, then back to refill. She did not replay interrupted turns, maintained context throughout all interruptions, and gracefully clarified intent when genuinely ambiguous ("I want to make sure I understand — are you looking to schedule an appointment for next Monday morning, or do you still need help with a medication refill?"). This is the expected standard of behaviour and was met.
