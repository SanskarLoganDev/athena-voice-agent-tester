# Bug Report — call-06offic-d26133
**Scenario:** Office hours and weekend appointment request
**Date:** 2026-06-24 01:00 UTC

---

### Bug 1 — Severity: HIGH

**What happened:** Athena confirmed the appointment as "Monday, June 30" when June 30, 2026 is a Tuesday and the appointment had been discussed as a Tuesday throughout the entire call.

**Expected:** "Tuesday, June 30 at 12:45PM" — consistent with the day-of-week for that calendar date.

**Actual:** "You're all set for an appointment on Monday, June 30 at 12:45PM."

**Why it matters:** Patient could arrive on Monday (June 29) instead of Tuesday (June 30) and miss their appointment.

---

### Bug 2 — Severity: MEDIUM

**What happened:** Athena proactively offered "Would you like to book something on Monday morning?" without first checking whether Monday had any availability. When the patient agreed and pressed for a time, Athena revealed no Monday slots existed.

**Expected:** Check availability before suggesting a specific day.

**Actual:** False expectation set. Patient had to be redirected to Tuesday after already agreeing to Monday.

**Why it matters:** Creates misleading expectations and wastes conversational turns.

---

### Bug 3 — Severity: LOW

**What happened:** When the patient asked "What's the earliest you have?", Athena responded "Please provide your date of birth" with no transitional explanation.

**Expected:** A brief explanation of why identity information is needed at that point before requesting it.

**Actual:** Non-sequitur DOB request mid-availability question.

**Why it matters:** Confusing flow causes patients to disengage or distrust the system.

---

### Positive Finding — Weekend Hours

Athena correctly refused to book Sunday and Saturday appointments, stated the clinic was closed on both days, and proactively offered weekday alternatives. This is the expected behaviour and was handled well.
