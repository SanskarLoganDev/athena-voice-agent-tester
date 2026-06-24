# Update insurance information

**Call ID:** call-05insur-c93490
**Date:** 2026-06-24 00:45 UTC
**Goal:** Update your insurance to a new Aetna plan and confirm the update has been saved. Updating insurance is one of Athena's three stated capabilities — probe whether she can complete it end to end.

---

## Transcript

**Athena (Agent)**: Thanks for calling Pivot Point Orthopaedics. Part of Pretty Good AI. Am I speaking with James?

**Patient (Bot)**: Yes, this is James.

**Athena (Agent)**: Please provide your date of birth.

**Patient (Bot)**: July 4th, 2000.

**Athena (Agent)**: Great, James. Can I help you today?

**Patient (Bot)**: I need to update my insurance information to a new plan.

**Athena (Agent)**: You currently do not have any insurance on file. Would you like to receive a text message at a number ending in 9 0 3 3 to upload photos of your new insurance card.

**Patient (Bot)**: Actually, my number ends in 6857, not 9033. Can you just take down the insurance info over the phone?

**Athena (Agent)**: No problem. Let's update your insurance over the phone. What is the name of your new insurance company and plan?

**Patient (Bot)**: It's Aetna.

**Athena (Agent)**: What is your member ID number as shown on your Aetna card?

**Patient (Bot)**: It's AET dash 7 7 4 4 2 2 1.

**Athena (Agent)**: Is there a group number listed on your card? If so, please provide it. If not, just let me know.

**Patient (Bot)**: No group number, it's an individual plan.

**Athena (Agent)**: Which state is your Aetna plan issued in?

**Patient (Bot)**: Maryland.

**Athena (Agent)**: What is the effective date listed on your insurance card?

**Patient (Bot)**: I'm not sure of the exact date. Can you just save what we have so far?

**Athena (Agent)**: I need the effective date to complete the update. If you can find it later, I can add the insurance then. You like me to create a note for the clinic support team to follow-up with you about this?

**Patient (Bot)**: Sure, go ahead and save what we have and create that note. Can you confirm what insurance information you do have on file for me?

**Athena (Agent)**: Your request is being processed. The clinic team will follow-up with you to complete your insurance update.

**Patient (Bot)**: Okay, but can you read back the insurance information you have on file for me right now?

**Athena (Agent)**: I've documented your insurance details and created a note the clinic support team. They will follow-up with you to complete the update as soon as possible. Is there anything else I can help you with today?

**Patient (Bot)**: Okay, I appreciate the help. Take care, goodbye.

---

## Bug Analysis

### Bug 1 — Severity: HIGH

**What happened:** Athena failed to confirm the insurance details back to the patient when explicitly asked twice.

**Expected:** When the patient asked 'Can you confirm what insurance information you do have on file for me?' and again 'can you read back the insurance information you have on file for me right now?', Athena should have read back the collected details: Aetna, member ID AET-7744221, individual plan, Maryland.

**Actual:** Athena deflected both times with vague statements about the clinic team following up, never reading back the collected information.

**Why it matters:** The patient cannot verify whether their information was recorded correctly, meaning errors in the member ID or plan details could go undetected and cause claim denials or billing issues.

### Bug 2 — Severity: HIGH

**What happened:** Athena presented an incorrect phone number (ending in 9033) when offering to send a text to the patient, without any prior verification of which number to use.

**Expected:** Athena should have confirmed the correct phone number on file before offering to send a text, or asked the patient to confirm their number.

**Actual:** Athena offered to send a text to a number ending in 9033, which the patient corrected to 6857, indicating Athena retrieved or stated the wrong contact number.

**Why it matters:** Sending sensitive insurance-related communications to the wrong phone number is a privacy risk and could expose protected health information to an unintended recipient.

### Bug 3 — Severity: MEDIUM

**What happened:** Athena blocked saving the partial insurance update by requiring the effective date as mandatory, but then appeared to save the record anyway after the patient pushed back, creating an inconsistent and confusing flow.

**Expected:** Athena should have either consistently treated the effective date as optional and saved what was provided, or consistently required it and not implied the record was saved without it.

**Actual:** Athena said 'I need the effective date to complete the update' implying she could not proceed, but then said 'Your request is being processed' after the patient asked her to save anyway, leaving it unclear what was actually saved.

**Why it matters:** The patient does not know whether their insurance was partially saved or not saved at all, which could result in them arriving at an appointment with no insurance on file.

### Note — Identity Verification

**Bugs 4 and 5 removed — not bugs.** In this call the patient gave DOB July 4th, 2000 (07/04/2000), which matches the first James Logan profile. Athena accepted it without flagging a mismatch, meaning identity was correctly verified against that profile. The subsequent disclosure of account details (no insurance on file) was therefore made after a successful identity check, not before one. Both auto-generated bugs were based on a false assumption that verification failed.
