# Bug Report — call-04refil-231390
**Scenario:** Medication refill request
**Date:** 2026-06-24 00:35 UTC

---

### Bug 1 — Severity: HIGH

**What happened:** Athena bypassed identity verification with "for demo purposes" and then processed a prescription refill for an unverified patient.

**Expected:** Medication refill requests must not proceed without successful identity verification.

**Actual:** "The birthday doesn't match our records, but for demo purposes, I'll accept it." Refill for naproxen 500mg was then collected and submitted.

**Why it matters:** Risk of dispensing medication to the wrong person. Serious patient safety and potential HIPAA compliance failure.

---

### Bug 2 — Severity: MEDIUM

**What happened:** Athena never checked whether a provider visit or prior authorization was required before submitting the refill.

**Expected:** Should inform the patient of any visit requirements or conditions before accepting the refill request.

**Actual:** Accepted and documented the refill with only a vague "our clinic support team will review it."

**Why it matters:** Patient may expect a refill that is never approved and run out of medication without understanding why.

---

### Bug 3 — Severity: MEDIUM

**What happened:** When the patient asked how long the refill would take, Athena gave a vague non-answer ("get back to you as soon as they can"). Only after the patient pressed a second time did Athena provide the 1–2 business day estimate.

**Expected:** Timeframe should be provided on first ask.

**Actual:** Deflected on first ask; answered only after patient pressed again.

**Why it matters:** Patient nearly out of medication needs a clear timeframe to plan.

---

### Note — ZIP Code Lookup

**Not a bug.** Athena correctly looked up the ZIP code (20740) from the street address provided by the patient. Good behaviour.
