# Bug Report — Simple appointment scheduling

**Call ID:** call-01sched-a61ee0
**Scenario:** Simple appointment scheduling
**Goal:** Schedule a routine follow-up appointment for sometime next week, preferably a weekday morning.
**Transcript:** call-01sched-a61ee0.md

---

## Bug 1

**Severity:** HIGH

**Description:** Athena assigned a fabricated date of birth (07/04/2000) to the patient without collecting it, then had to be corrected.

**Expected behaviour:** Athena should have asked the patient for their date of birth as part of identity verification before creating or confirming the profile.

**Actual behaviour:** Athena invented a date of birth (07/04/2000) and presented it as fact in the patient's profile without ever asking the patient.

**Why it matters:** Assigning a false date of birth to a medical record is a patient safety and data integrity risk; if the patient had not noticed and corrected it, their record would contain incorrect identifying information that could cause misidentification or medical errors.

---

## Bug 2

**Severity:** HIGH

**Description:** The call ends without Athena confirming or finalizing the appointment after the patient selected the 9AM Thursday slot.

**Expected behaviour:** Athena should have explicitly confirmed the appointment booking (date, time, provider, and location if applicable) and informed the patient that the appointment has been scheduled.

**Actual behaviour:** The conversation ends at turn 10 with the patient saying '9AM works perfectly' but Athena never confirms the appointment is booked, provides a confirmation number, or summarizes the final details.

**Why it matters:** Without a clear confirmation, the patient has no assurance the appointment was actually scheduled, risking a missed appointment and potential gaps in follow-up care.

---

## Bug 3

**Severity:** MEDIUM

**Description:** The doctor's name was mispronounced/misspelled as 'Dudee Hauser' in turn 7 before being corrected to 'Judy Hauser' in turn 9, indicating an inconsistency in how the provider's name is rendered.

**Expected behaviour:** Athena should consistently and accurately state the provider's name throughout the conversation.

**Actual behaviour:** Athena referred to the doctor as 'Dudee Hauser' in turn 7 and then 'Judy Hauser' in turn 9, creating confusion about who the appointment is actually with.

**Why it matters:** An inconsistent or incorrect provider name could cause the patient to be uncertain about which doctor they are seeing, and may indicate underlying data handling errors in how provider information is retrieved and presented.

---
