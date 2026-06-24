# Bug Report — call-15past-70a270
**Scenario:** Patient asks to confirm an appointment that already passed
**Date:** 2026-06-24 22:39 UTC

---

### Bug 1 — Severity: HIGH

**What happened:** Athena confirmed a past appointment without clearly identifying it as elapsed, framing it ambiguously as something the patient could still act on.

**Expected behaviour:** Athena should have explicitly stated that the July 7 appointment has already passed, then asked whether the patient attended or missed it.

**Actual behaviour:** Athena said "You have an appointment that was scheduled for last Tuesday, July 7 at 8AM" and offered to provide details or reschedule — presenting a past date without marking it as elapsed.

**Why it matters:** Ambiguous presentation of past appointments confuses patients about their care status and whether they still have an active visit on record.

---

### Bug 2 — Severity: HIGH

**What happened:** Athena refused to book a new follow-up appointment citing an existing follow-up on record, without verifying whether that record was current or a stale entry from a prior test call.

**Expected behaviour:** Athena should have checked the date and status of the existing follow-up before using it to block a new booking, and should have communicated those details to the patient.

**Actual behaviour:** Athena said "It looks like you already have a follow-up appointment on record. So I can't book a new one" — no date, no status, no verification that the record was valid.

**Why it matters:** If the blocking record is stale, the patient is incorrectly denied access to care. This is the same stale-record failure pattern identified in call-10high-539531.

---

### Bug 3 — Severity: MEDIUM

**What happened:** Athena implied she could book a new appointment in turn 9, then stated she cannot reschedule appointments directly in turn 13 — a direct contradiction within the same call.

**Expected behaviour:** Athena should have a consistent understanding of her own capabilities, or clearly explain the distinction between booking new and rescheduling existing appointments.

**Actual behaviour:** Turn [9]: "You like help setting up another appointment" — implying booking capability. Turn [13]: "I can't reschedule appointments directly" — contradicting the earlier offer and routing the patient to live support unnecessarily.

**Why it matters:** Contradictory capability statements waste the patient's time and erode trust in the system.

---

### Bug 4 — Severity: LOW

**What happened:** Athena asked "Would you like me to transfer you now?" after the patient had already said "please transfer me now."

**Expected behaviour:** Athena should have proceeded with the transfer immediately after the patient's unambiguous instruction.

**Actual behaviour:** An unnecessary second confirmation was requested after a clear patient instruction.

**Why it matters:** Adds friction and can feel dismissive of clear patient instructions.

---

### Note — Provider Name

**Not a bug.** "Duggehauser" and "Doogie Howser" are recurring STT transcription artefacts of the intentionally fictionalised provider name used in the Pivot Point demo environment. Confirmed across multiple calls in this test suite.
