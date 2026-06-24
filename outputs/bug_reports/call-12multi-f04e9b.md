# Bug Report — call-12multi-f04e9b
**Scenario:** Three things at once: reschedule, two refills, insurance update
**Date:** 2026-06-24 22:07 UTC

---

### Bug 1 — Severity: MEDIUM

**What happened:** Athena asked the patient to repeat the pharmacy name and address for the ibuprofen refill even though the patient said "same pharmacy as before" and the CVS address at 8319 Baltimore Avenue had been confirmed two turns earlier for the naproxen refill.

**Expected behaviour:** Athena should have carried the confirmed pharmacy details forward and applied them to the second refill without requiring repetition.

**Actual behaviour:** After the patient said "same pharmacy as before," Athena responded "Could you please tell me the name of pharmacy you want to use" — forcing the patient to repeat the full address.

**Why it matters:** Requiring patients to repeat information already established in the same call indicates no session-level context retention across tasks within a single conversation.

---

### Bug 2 — Severity: HIGH

**What happened:** The patient provided full Aetna insurance details twice (member ID AET-7744221, individual plan, Maryland) but Athena never confirmed the details were saved, instead sending a text link to upload a photo of the insurance card.

**Expected behaviour:** Athena should have confirmed the member ID, plan type, and state back to the patient and confirmed the insurance record was updated.

**Actual behaviour:** Athena said "There is currently no insurance on file for you. Would you like to receive a text message at the number ending in 9033 to upload photos of your new Aetna insurance card?" — ignoring the member ID and plan details the patient had already provided twice.

**Why it matters:** The patient ended the call believing insurance was updated. It was not — only a text link was sent. If the patient does not complete the photo upload separately, they will arrive at their next appointment with no insurance on file.

---

### Positive Finding — Multi-item Agenda Tracking

Athena successfully tracked all three agenda items and provided an accurate end-of-call summary covering the reschedule, both refills, and the insurance update. She treated the two medication refills as separate requests and processed each individually. This is the expected standard of behaviour and was met.
