---
id: "hkicl_hkd_fps_rules_2025"
title: "HKD Faster Payment System Rules"
issuer: "Hong Kong Interbank Clearing Limited"
authority_level: "official_dev"
region:
  - "Hong Kong"
topic:
  - "FPS"
  - "FPS rulebook"
  - "payment systems"
source_url: "https://www.hkicl.com.hk/files/page_file/126/10939/HKD%20FPS%20Rules_redacted%20version_Jun%202025_dist%20ver..pdf"
document_url: ""
source_type: "PDF"
language: "en"
trust_tier: "official_dev"
country: "HK"
subdivision: "hk_sar"
agency: "HKICL"
crawl_frequency: "monthly"
publish_date: "2025-06-01"
effective_date: ""
demo_relevance: "high"
collected_at: "2026-05-26T19:03:49+00:00"
raw_file_path: "data/raw/crawl_hkicl_hkd_fps_rules_2025.pdf"
extraction_status: "ok"
content_hash: "f31c390eb8694cf7294c4ca68697ec9fbe49f2adf2e7643c504a4a4882f74af1"
---

# HKD Faster Payment System Rules

## Page 1

Rules for Hong Kong Dollar Faster Payment System (FPS)

(Redacted Version)

Date : June 2025

This redacted version of the Rules for Hong Kong Dollar Faster Payment System is a partially edited
version of the main text of these documents and is made available publicly for general information
purposes only. It has been edited to remove information that might compromise the security of the
system if made available to the general public. For operational purposes, Participants of the Hong Kong
Dollar Faster Payment System should refer to the full text of the Rules for Hong Kong Dollar Faster
Payment System. Although due care has been taken to ensure that the information provi ded in this
document is accurate and up-to-date, Hong Kong Interbank Clearing Limited does not warrant that all,
or any part of, the information provided in it is up-to-date and accurate in all respects.

## Page 2

Hong Kong Interbank Clearing Limited
Rules for Hong Kong Dollar Faster Payment System

Redacted version: August 2025 Page i
Amendment Summary

Amendment Effective Date

1. Revised the following to cater for the enhancement to support Northbound CN-HK
Remittance Payment Instructions:
• Definition of “CN-HK Remittance Payment Instruction” (new)
• Definition of “Cross-boundary Payment Service”
• Definition of “Foreign Exchange Service Provider” (new)
• Definition of “Northbound CN-HK Remittance Payment Instruction” (new)
• Definition of “Southbound CN-HK Remittance Payment Instruction”
• Rule 6.2.9
• Rule 6.2.9.1
• Rule 6.2.9.2 (new)
• Rule 6.2.9.3 (renumbered from 6.2.9.2)
• Rule 6.2.9.4 (new)
• Rule 6.2.9.5 (new)
• Rule 6.2.9.6 (renumbered from 6.2.9.3)
• Rule 6.2.9.7 (new)
• Rule 6.2.9.8 (renumbered from 6.2.9.4)
• Rule 6.2.9.9 (renumbered from 6.2.9.5)
• Rule 6.3.1
2. Revised the following for better clarity and consistency:
• Rule 6.2.8.6 (removed)
• Rule 6.2.8.6 (renumbered from 6.2.8.7)
• Rule 6.2.8.7 (renumbered from 6.2.8.8)
• Rule 6.2.8.8 (renumbered from 6.2.8.9)

31 August 2025

## Page 3

Hong Kong Interbank Clearing Limited
Rules for Hong Kong Dollar Faster Payment System

Redacted version: August 2025
TABLE OF CONTENT

PART I INTRODUCTION .............................................................................................................. 1
PART II FPS FACILITIES AND HKICL ....................................................................................... 7
PART III SETTLEMENT ................................................................................................................ 11
PART IV PARTICIPANTS .............................................................................................................. 12
PART V REFUSAL/SUSPENSION OF FPS FACILITIES......................................................... 14
PART VI FPS .................................................................................................................................... 16
PART VII MISCELLANEOUS ......................................................................................................... 30

## Page 4

Hong Kong Interbank Clearing Limited
Rules for Hong Kong Dollar Faster Payment System
Redacted version: August 2025 Page 1
Part I Introduction

1.1 Expressions used herein are defined below.

1.2 The Hong Kong dollar F PS shall be the computer based system provided, operated and managed by
HKICL through the Clearing House which is available to Participants for (i) the processing of direct
debits and credits, funds transfers and other banking or payment transactions in each case in Hong Kong
dollars which are presented by or on behalf of Participants or by MA; and (ii) the exchange and
processing of instructions and other communications in relation to eDDA Service and Addressing Service
which are presented by or on behalf of Participants.

1.3 HKICL owns the Clearing House and manages and operates the Clearing House and the FPS Facilities
and CHATS in each case through the Clearing House.

1.4 These FPS Rules have been made by HKICL with the approval of MA.

1.5 These FPS Rules will apply:

1.5.1 to Settlement Participants who satisfy the criteria as stipulated in Rules 4.2.1 to 4.2.2;

1.5.2 to Clearing Participants who satisfy the criteria as stipulated in Rules 4.2.3 to 4.2.4;

1.5.3 in relation to payments by MA to Participants, or by Participants to MA.

1.6 HKICL may from time to time amend these FPS Rules as it may consider necessary or desirable with
prior approval of MA. Any amendments made thereto shall become effective from the effective date(s)
as stated in HKICL’s prior notice to Participants and the amended version will be posted onto HKICL’s
website www.hkicl.com.hk (which shall specify the effective date(s) for the amendments according to
the notice).

1.7 Definitions

“Addressing Service” means an overlay service of FPS which involves maintaining and operating a centralised
addressing repository to facilitate Participants and their customers to address the recipient of a Credit Transfer
Instruction or Direct Debit Instruction and other communications made in accordance with the FPS Rules and the
FPS Operating Procedures using a predefined Proxy ID instead of using the account number.

“Balance-triggered Balance Sweeping Transaction” means a transaction initiated by a Settlement Participant
manually or generated by FPS automatically to debit or credit funds from or to the FPS Ledger Account of the
Settlement Participant through FPS for transferring funds to or from the CHATS Ledger Account of the Settlement
Participant for the purpose of liquidity management , other than a Transaction -triggered Balance Sweeping
Transaction.

“bank” means an institution which has been granted a banking licence under the Banking Ordinance (Cap. 155
of the Laws of Hong Kong) and such licence has not been revoked.

“CHATS” means the computer based Clearing House Automated Transfer System in Hong Kong dollars
provided, owned, operated and managed in Hong Kong by HKICL.

“CHATS Ledger Account” has the meaning given to it in the definition of “Settlement Account”.

“CHATS Members” means the banks, restricted licence banks and CLS Bank participating in CHATS which in
each case have agreed with HKICL to be bound by the Clearing House Rules. For the avoidance of doubt, this
term does not include a branch or the head office of the banks and restricted licence banks located outside Hong
Kong.

“CHATS Working Day” means a day (other than a Saturday and a general holiday as specified in the General

## Page 5

Hong Kong Interbank Clearing Limited
Rules for Hong Kong Dollar Faster Payment System
Redacted version: August 2025 Page 2
Holidays Ordinance (Cap. 149 of the Laws of Hong Kong)) on which CHATS Members which are members of
The Hong Kong Association of Banks are open to the public for business in Hong Kong.

“Clearing House” means the medium and the location owned, provided, operated and managed by HKICL which
is available (i) to Participants for the processing of FPS Instructions in Hong Kong dollars through FPS in
accordance with the FPS Rules and the FPS Operating Procedures; and (ii) to CHATS Members for the processing
of CHATS Transactions (as defined in the Clearing House Rules) and other payments in Hong Kong dollars
through CHATS.

“Clearing House Rules” means the Clearing House Rules in relation to the operation of CHATS as amended
from time to time by HKICL with prior approval of MA and The Hong Kong Association of Banks.

“Clearing Participant” means a participant (other than a Settlement Participant that has access to the FPS
Facilities) which has agreed with a Settlement Participant that such participant’s payments will be settled through
that Settlement Participant’s FPS Ledger Account ; such participant in relation to the Settlement Participant with
whom it has agreed to settle its payments shall be referred to as “its Clearing Participant”.

“CLS Bank” means CLS Bank International, an Edge Act corporation under Section 25A of the United States
Federal Reserve Act, as amended, and a CHATS Member which maintains a CHATS Ledger Account.

“CN-HK Remittance Payment Instruction” refers to a Southbound CN-HK Remittance Payment Instruction or
a Northbound CN-HK Remittance Payment Instruction.

“CN-HK Settlement Bank” means the bank determined by the People’s Bank of China to be the settlement bank
of cross -boundary payment linkage between IBPS and FPS supporting real -time remittances between the
Mainland and Hong Kong. The CN-HK Settlement Bank is a participant in both IBPS and FPS.

“Conditions” means the terms and conditions for the operation of the Settlement Accounts (including the CHATS
Ledger Accounts and the FPS Ledger Accounts) as the Financial Secretary may require in pursuance of Section
3A(1) of the Exchange Fund Ordinance (Cap. 66 of the Laws of Hong Kong).

“Credit Transfer Instruction” means an instruction input by a payer Participant for the effecting of funds
transfer to a payee Participant through FPS to settle an obligation of the payer Participant (or one of its customers)
to the payee Participant (or one of its customers).

“Cross-boundary Payment Services ” means payment services enabl ing the transfer of funds via the linkage
between FPS and payment system s in other jurisdictions. The payment instruction s under such services include
CN-HK Remittance Payment Instructions and TH-HK Merchant Payment Instructions.

“Data Subject(s)” has the meaning given to that term in the Personal Data (Privacy) Ordinance (Cap. 486 of the
Laws of Hong Kong).

“Delayed Payment” means the funds transferred through FPS which are credited to an account at a time
significantly later than the time specified in the relevant transfer or payment details.

“Direct Debit Instruction” means an instruction input by a payee Participant for the effecting of a debit of funds
from a payer Participant through FPS to settle an obligation of the payer Participant (or one of its customers) to
the payee Participant (or one of its customers).

“eDDA Instruction” means an electronic direct debit authorisation instruction input by a Participant who initiates
such instruction (“initiating Participant”) to that Participant or another Participant who receives such instruction
(“receiving Participant”) for the purpose of the setup, amendment or cancellation of a direct debit authorisation
arrangement to facilitate the initiation of payment instructions by a Participant’s customer (being a payee) to that
Participant or another Participant which maintains an account for another customer (being a payer) to effect funds
transfers from the account of the payer -customer maintained with its Participant to the account of the payee -
customer maintained with its Participant in accordance with certain criteria bilaterally agreed between such
customers.

## Page 6

Hong Kong Interbank Clearing Limited
Rules for Hong Kong Dollar Faster Payment System
Redacted version: August 2025 Page 3
“eDDA Service” means an overlay service of FPS which involves the exchange and processing of eDDA
Instructions and related responses between Participants.

“Foreign Exchange Service Provider” means a bank or a financial institution agreed upon by MA to provide
foreign exchange conversion services to Participants for the purpose of facilitating Northbound CN-HK
Remittance Payment Instructions.

“FPS” means the computer based system provided, operated and managed by HKICL through the Clearing House
which is available to Participants for (i) the processing of direct debits and credits, funds transfers and other
banking or payment transactions in each case in Hong Kong dollars which are presented by or on behalf of
Participants or by MA; and (ii) the exchange and processing of instructions and other communications in relation
to eDDA Service and Addressing Service which are presented by or on behalf of Participants.

“FPS Console” means a terminal system provided by HKICL to which a Participant may gain access through
terminals located within the premises of the Participant for the purpose of performing operation, administrative
and monitoring functions related to FPS as stipulated in the FPS Operating Procedures.

“FPS Facilities” means all premises, personnel, machinery, equipment, facilities, software, operational and
processing systems, computer systems including FPS, arrangements and procedures for or in relation to the FPS
services provided by HKICL in accordance with these FPS Rules and the FPS Operating Procedures.

“FPS Identifier” means a unique random number generated by FPS at the request of a Participant on behalf of
its customer to be associated with such account of the customer with the Participant.

“FPS Instructions” means any instruction generated by FPS or input by a Participant or MA to FPS for (i) the
effecting of an FPS Transaction ; or (ii) the setup, amendment or cancellation of records in relation to the
Addressing Service or the eDDA Service.

“FPS Ledger Account” has the meaning given to it in the definition of “Settlement Account”.

“FPS Operating Procedures” means the operating procedures issued by HKICL pursuant to Rule 2.4 and for
the time being in force.

“FPS Optimiser” means a settlement mechanism allowing simultaneous gross settlement of selected eligible FPS
Transactions in accordance with Rule 6.7.

“FPS Payment Application Selection Gateway ” means an electronic platform operated by HKICL in relation
to the FPS services which enables electronic messages from a website of a Participant’s customer (being a payee)
to be redirected to a mobile payment application (such application being installed on the same electronic device
through which the payee’s website is accessed) operated by that Participant or another Participant which maintains
an account for another customer (being a payer) for the purposes of facilitating the initiation of a Credit Transfer
Instruction for a funds transfer from the account of the payer-customer maintained with its Participant (being a
payer Participant) to the account of the payee-customer maintained with its Participant (being a payee Participant).

“FPS Payment Application Selection Gateway User ” means (i) a payer Participant, (ii) a customer of a payer
Participant, (iii) a payee Participant and (iv) a customer of a payee Participant , in each case of a funds transfer
effected through FPS which is initiated by a Credit Transfer Instruction, whereby the initiation of such Credit
Transfer Instruction is facilitated through use of the FPS Payment Application Selection Gateway.

“FPS Rules” or “Rules” means these Rules for Hong Kong Dollar Faster Payment System in relation to the
operation of FPS Facilities as amended from time to time by HKICL with prior approval of MA.

“FPS Transactions” means transactions involving funds transfers effected through FPS including those initiated
by Credit Transfer Instructions, Direct Debit Instructions , SI Direct Credit Transactions , SI Direct Debit
Transactions, Balance-triggered Balance Sweeping Transactions and Transaction -triggered Balance Sweeping
Transactions and for the avoidance of doubt (but without limitation), the general administrative or system
messages transmitted through FPS.

## Page 7

Hong Kong Interbank Clearing Limited
Rules for Hong Kong Dollar Faster Payment System
Redacted version: August 2025 Page 4
“HK Settlement Bank” has the meaning given to it in Rule 6.2.8.2(b).

“HKICL” means Hong Kong Interbank Clearing Limited.

“Inbound TH-HK Merchant Payment Instruction ” means an instruction input through PromptPay by a Thai
bank participating in PromptPay engaged by a payer to effect funds transfer , to settle an obligation of the payer
from Thailand to a merchant in Hong Kong (as described in the FPS Operating Procedures) as the payee in
accordance with Rule 6.2.8.2. Such instruction is relayed by PromptPay to FPS which is then processed by FPS
in the form of a Credit Transfer Instruction, and is paid by the HK Settlement Bank as the payer Participant to the
Participant engaged by the payee.

“Internet Banking Payment System” or “IBPS” means the real-time payment system in the Mainland operated
by China National Clearing Center of the People’s Bank of China.

“ISO20022” means a standard published by the International Organisation for Standardisation which is used for
electronic data interchange between financial institutions.

“MA” means the Monetary Authority appointed under the Exchange Fund Ordinance (Cap. 66 of the Laws of
Hong Kong).

“Northbound CN -HK Remittance Payment Instruction ” means an instruction inp ut through FPS by a
Participant engaged by a payer in the form of a Credit Transfer Instruction to the CN -HK Settlement Bank as a
payee Participant, for the purpose of the CN-HK Settlement Bank effecting an onward funds transfer via IBPS to
a bank in the Mainland engaged by a payee, to settle an obligation of the payer from Hong Kong to a payee in the
Mainland in accordance with Rule 6.2.9.2. Such instruction is relayed by FPS to IBPS, and is then processed by
IBPS and delivered to the bank in the Mainland participating in IBPS engaged by the payee.

“Outbound TH-HK Merchant Payment Instruction” means an instruction input through FPS by a Participant
engaged by a payer in the form of a Credit Transfer Instruction to the HK Settlement Bank as a payee Participant,
for the purpose of the HK Settlement Bank effecting a funds transfer outside FPS to the TH Settlement Bank for
onward transfer to a Thai bank participating in PromptPay engaged by a payee, to settle an obligation of the payer
from Hong Kong to a merchant in Thailand as the payee in accordance with Rule 6.2.8.3 . Such instruction is
relayed by FPS to PromptPay and is then processed by PromptPay and delivered to the Thai bank participating in
PromptPay engaged by the payee.

“Participants” means the Settlement Participants and Clearing Participants which in each case have agreed with
HKICL to be bound by these FPS Rules.

“Personal Data” has the meaning given to that term in the Personal Data (Privacy) Ordinance (Cap. 486 of the
Laws of Hong Kong).

“PromptPay” means the real -time retail payment system in Thailand operated by National ITMX Company
Limited incorporated under the laws of the Kingdom of Thailand.

“Proxy ID” means the proxy identifier registered by a customer of a Participant in the Addressing Service to
identify the account of that customer with that Participant. Such proxy identifier can be registered by more than
one Participant on behalf of their customers where allowed pursuant to the FPS Operating Procedures.

“PSSVFO” means the Payment Systems and Stored Value Facilities Ordinance (Cap. 584 of the Laws of Hong
Kong).

“restricted licence bank” means an institution which has been granted a restricted banking licence under the
Banking Ordinance (Cap. 155 of the Laws of Hong Kong) and such licence has not been revoked.

“Settlement Account” means the account maintained with MA by a CHATS Member being also a Settlement
Participant for the purpose of settlement of payments through CHATS or FPS which shall comprise two separate
ledger accounts with separate account balances as follows: (i) the “CHATS Ledger Account” for the purpose of
settlement of payments by or to the CHATS Member through CHATS and (ii) the “ FPS Ledger Account ” for

## Page 8

Hong Kong Interbank Clearing Limited
Rules for Hong Kong Dollar Faster Payment System
Redacted version: August 2025 Page 5
the purpose of settlement of payments by or to the Settlement Participant through FPS and for the purpose of
conducting Balance -triggered Balance Sweeping Transactions and Transaction -triggered Balance Sweeping
Transactions; and all references to payment to or from the CHATS Ledger Account or to or from the FPS Ledger
Account of a CHATS Member being also a Settlement Participant shall refer to payments to or from the Settlement
Account of such CHATS Member (being also a Settlement Participant) which shall be credited or debited to the
CHATS Ledger Account of such CHATS Member or the FPS Ledger Account of such Settlement Participant (as
the case may be).

“Settlement Participant” means a participant which maintains an FPS Ledger Account for the purpose of
settlement of funds in FPS and “ its Settlement Participant ” means, in relation to a Clearing Participant, a
Settlement Participant with respect to whom it has been agreed with such Clearing Participant that such Settlement
Participant shall permit payments by or to such Clearing Participant to be settled through such Settlement
Participant’s FPS Ledger Account.

“SI Direct Credit Transaction” means a transaction initiated by MA to credit a Settlement Participant’s FPS
Ledger Account through FPS to settle an obligation of MA owed to that Settlement Participant.

“SI Direct Debit Transaction” means a transaction initiated by MA to debit a Settlement Participant’s FPS
Ledger Account through FPS to settle an obligation of that Settlement Participant owed to MA.

“Southbound CN-HK Remittance Payment Instruction” means an instruction input through IBPS by a bank
in the Mainland participating in IBPS engaged by a payer to effect funds transfer, to settle an obligation of the
payer from the Mainland to a payee in Hong Kong in accordance with Rule 6.2.9. 3. Such instruction is relayed
by IBPS to FPS which is then processed by FPS in the form of a Credit Transfer Instructi on, and is paid by the
CN-HK Settlement Bank as the payer Participant to the Participant engaged by the payee.

“stored value facility” has the meaning given to that term in the PSSVFO.

“TH Settlement Bank” has the meaning given to it in Rule 6.2.8.2(a).

“TH-HK Merchant Payment Instruction ” refers to an Inbound TH -HK Merchant Payment Instruction or an
Outbound TH-HK Merchant Payment Instruction.

“Transaction-triggered Balance Sweeping Transaction” means a transaction generated by FPS automatically
in order to transfer funds from the CHATS Ledger Account of a Settlement Participant to the FPS Ledger Account
of that Settlement Participant through FPS for the purpose of settlement of outstanding Direct Debit Instructions.
For the avoidance of doubt, this term does not include a Balance-triggered Balance Sweeping Transaction.

1.8 Interpretation

Unless the context otherwise requires:

(a) a word or expression defined in these FPS Rules hereto bears the defined meaning;

(b) where a word or expression is given a particular meaning, other parts of speech and grammatical
forms of that word or expression have a corresponding meaning;

(c) a person includes individuals, bodies corporate (wherever and howsoever incorporated),
unincorporated associations and partnerships;

(d) a person includes its successor;

(e) reference to the singular includes the plural and vice versa;

(f) reference to one gender includes all genders;

(g) “including” and similar expressions are not words of limitation;

## Page 9

Hong Kong Interbank Clearing Limited
Rules for Hong Kong Dollar Faster Payment System
Redacted version: August 2025 Page 6
(h) reference to a group or thing includes any part thereof; and

(i) headings are for convenience only and do not affect interpretation.

## Page 10

Hong Kong Interbank Clearing Limited
Rules for Hong Kong Dollar Faster Payment System
Redacted version: August 2025 Page 7
Part II FPS Facilities and HKICL

2.1 FPS Facilities

No Participant shall use or provide in Hong Kong any facilities for (i) the processing of FPS related direct
debits and credits, funds transfers and other banking or payment transactions in each case in Hong Kong
dollars; and (ii) the exchange and processing of instructions in relation to eDDA Service and Addressing
Service other than the FPS Facilities provided by HKICL (either directly or through a sub -contractor).
Each Participant shall be entitled to the use of all or part of the FPS Facilities subject to the provisions
of these FPS Rules, the Conditions and any agreement between that Participant and MA .

2.2 Location

The Clearing House for the operation of FPS through FPS Facilities shall be located at such place in
Hong Kong as shall be notified from time to time by HKICL to the Participants.

2.3 Responsibility for the Clearing House and/or the FPS Facilities

2.3.1 HKICL shall, subject to the provisions of these FPS Rules and in accordance with the FPS
Operating Procedures, provide, manage and operate the Clearing House and /or the FPS
Facilities and make available the services of the Clearing House and/or the FPS Facilities to the
Participants. HKICL may (with the approval of MA) subcontract the performance of its
obligations hereunder.

2.3.2 HKICL shall exercise a degree of skill, care and responsibility commensurate with third parties
in Hong Kong providing substantially similar services. The exercise of such skill, care and
responsibility shall constitute a full and complete discharge of the obligations and duties of
HKICL to Participants and other persons in respect of and concerning the Clearing House and/or
the FPS Facilities under these FPS Rules and the FPS Operating Procedures.

2.3.3 HKICL and MA shall not be liable to any Participant , any customer of a Participant (including
for the avoidance of doubt any FPS Payment Application Selection Gateway User ), and/or any
other person in respect of any claim, loss, damage or expense (including without limitation, loss
of business, loss of business opportunity, loss of profit, special, indirect or consequential loss,
even if HKICL or MA knew or ought reasonably to have known of their possible existence) of
any kind or nature whatsoever arising in whatever manner directly or indirectly from or as a
result of anything done or omitted to be done by HKICL or MA bona fide, except that HKICL’s
liability for loss or damage (other than loss of business, loss of business opportunity, loss of
profit, specia l, indirect or consequential loss) suffered by any Participant , any customer of a
Participant (including for the avoidance of doubt any FPS Payment Application Selection
Gateway User) and/or any other person as a result of any failure, error or inaccuracy in HKICL’s
provision, management or operation of the Clearing House and/or the FPS Facilities under these
FPS Rules which is proved to have resulted substantially from (i) a reckless act or omission or
the intentional misconduct of HKICL’s servants or agen ts or (ii) fire or theft affecting the
premises or property of HKICL shall not be so excluded.

2.3.4 Notwithstanding anything herein and for the avoidance of doubt, MA and HKICL shall, when
acting in good faith, not be liable in respect of any act or omission pursuant to Part V and/or
Part VI of the Rules.

2.3.5 Each Participant shall in respect of all claims, losses, damages and expenses incurred by it, any
of its customers (including for the avoidance of doubt any FPS Payment Application Selection
Gateway User) or any of its correspondent banks, indemnify and hold HKICL and MA harmless
against all actions, proceedings, costs, claims, demands, liabilities, losses or expenses
whatsoever and howsoever arising out of or in connection with HKICL’s provision,
management or operation of the Clearing House and/or the FPS Facilities and/or HKIC L’s
performance of its obligations under these FPS Rules and the FPS Operating Procedures save

## Page 11

Hong Kong Interbank Clearing Limited
Rules for Hong Kong Dollar Faster Payment System
Redacted version: August 2025 Page 8
and except those claims for which HKICL shall assume responsibility as provided in Rule 2.3.3.

2.3.6 MA shall not be liable to HKICL, any Participant, any customer of a Participant (including for
the avoidance of doubt any FPS Payment Application Selection Gateway User) or any other
person in respect of any claim, loss, damage or expense (including without limitation, loss of
business, loss of business opportunity, loss of profit, special, indirect or consequential loss, even
if MA knew or ought reasonably to have known of their possible existence) of any kind or nature
whatsoever arising in whatever manner directly or indirectly from or as a result of anything
done or omitted to be done by MA bona fide or by HKICL, any Participant or any other person
in the provision, management, operation or use (including without limitation, the termination
and/or suspension of the FPS Facilities or any Participant) of the Clearing House and/or the FPS
Facilities or any part of them.

2.3.7 The provisions in this Rule 2.3 shall be in addition to and shall not be affected by any other
provisions of these Rules which (i) exclude or limit the liability of MA or HKICL; or (ii) set out
an indemnity provision in favour of MA or HKICL.

2.3.8 HKICL shall not be responsible for debiting and crediting the FPS Ledger Accounts. MA shall
settle all payments effected through FPS by debiting and crediting the FPS Ledger Accounts
concerned in accordance with Rule 3.1.5.

2.4 FPS Operating Procedures

HKICL shall be entitled with MA’s approval to issue operating procedures for the FPS Facilities and to
amend such FPS Operating Procedures from time to time as it thinks fit with MA’s approval. To the
extent of any inconsistency between these FPS Rules and the FPS Operating Procedures, these FPS Rules
shall prevail save where otherwise specifically provided for in these FPS Rules. The current version of
the FPS Operating Procedures can be found on HKICL’s website www.hkicl.com.hk. Any amendments
made thereto shall become effective from the effective date(s) as stated in HKICL’s prior notice to
Participants and the amended version will be posted onto HKICL’s website (which shall specify the
effective date(s) for the amendments according to the notice). In the event of any inconsistency between
the version of the FPS Operating Procedures on HKICL’s website and any ot her version of the FPS
Operating Procedures, the version on HKICL’s website shall prevail.

2.5 FPS Facilities Expenses

2.5.1 All expenses incurred by HKICL in providing, managing and operating the Clearing House
and/or the FPS Facilities shall be borne by HKICL.

2.5.2 Participants shall pay to HKICL fees in Hong Kong dollars for the use of the FPS Facilities
calculated in the manner determined by HKICL from time to time (“Fees”).

2.5.3 Unless otherwise agreed, payment of the Fees shall be made monthly in arrears by direct debit
instruction generated by HKICL pursuant to a direct debit authorisation issued by each
Participant in HKICL’s favour in respect of Fees due from such Partic ipant. Failing due
payment interest shall become payable on the outstanding sum at the rate which HKICL certifies
from time to time to be equal to the average of the best lending rates for Hong Kong dollars for
the time being quoted by three banks as selected by HKICL.

2.6 Confidentiality

HKICL shall keep confidential all information received from or collected on behalf of Participants in
connection with the Clearing House and/or the FPS Facilities and shall, except as otherwise required by
law or pursuant to these FPS Rules and/or the FPS Operating Procedures, disclose the same only to those
of its staff who require the information for the purpose of providing, managing and operating the Clearing
House and/or the FPS Facilities, or to MA. HKICL shall take all reasonable steps to ensure that its staff
is aware of HKICL’s confidentiality obligations.

## Page 12

Hong Kong Interbank Clearing Limited
Rules for Hong Kong Dollar Faster Payment System
Redacted version: August 2025 Page 9
2.7 Contract

HKICL and each Participant agree that these FPS Rules constitute a contract between HKICL, such
Participant and all other Participants from time to time. It is recognised that HKICL may with MA’s
approval amend these FPS Rules from time to time as it thinks fit.

2.8 Compliance with the PSSVFO

2.8.1 Each Participant and HKICL shall comply with all obligations under the PSSVFO and all
directions or regulations made by MA thereunder, as may be applicable to each of them.

2.8.2 Without prejudice to the generality of Rule 2.8.1, HKICL shall:

(a) operate the Clearing House and /or the FPS Facilities in a safe and efficient manner
calculated to minimise the likelihood of any disruption to the functioning of the
Clearing House and/or the FPS Facilities;

(b) operate the Clearing House and/or the FPS Facilities in accordance with the PSSVFO
insofar as it applies in relation to the Clearing House and/or the FPS Facilities; and

(c) provide (and be entitled to provide) all information and reports required to be provided
by a system operator pursuant to the PSSVFO including Sections 6 (Obligation to
inform MA of name and address etc.), 12 (MA may request information or documents
from system operator, settlement institution, participant or licensee), 30 (Duty to report
on completion of default proceedings) and 53 (Requirement to give information
relating to default) of the PSSVFO.

For the avoidance of doubt, HKICL shall not be responsible for debiting and crediting the FPS
Ledger Accounts.

2.8.3 Without prejudice to the generality of Rule 2.8.1, each Participant shall notify HKICL and MA
forthwith if there comes to its attention any of the following circumstances occurring in Hong
Kong or any analogous circumstances occurring outside Hong Kong:

(a) a Participant becoming unable to meet its obligations;

(b) the presentation of a petition for winding up of the Participant;

(c) the making of an order for winding up of the Participant;

(d) the passing of a resolution for voluntary winding up of the Participant; or

(e) the making of a directors’ voluntary winding up statement in respect of the Participant.

HKICL shall inform MA forthwith if it becomes aware of any of the foregoing.

2.8.4 Without prejudice to the generality of Rule 2.8.1, none of the Participants nor HKICL shall
contravene Section 45 (Giving false information to MA) of the PSSVFO.

2.8.5 Each Participant shall have systems in place which are complementary to HKICL’s contingency
arrangements so as to enable HKICL to ensure the timely recovery of its usual operations in the
event of the occurrence of an adverse contingency affecting such operations. Such contingency
arrangements shall be modified from time to time in the manner required by HKICL or MA,
and HKICL shall notify Participants of the changes accordingly. Participants shall participate
in the contingency drills arranged by HKICL from time to time so as to verify their readiness.

2.8.6 In the event of any inconsistency between the provisions of this Rule 2.8 and any of the other
provisions of these FPS Rules, this Rule 2.8 shall prevail.

## Page 13

Hong Kong Interbank Clearing Limited
Rules for Hong Kong Dollar Faster Payment System
Redacted version: August 2025 Page 10

2.9 Monitoring of Compliance with these FPS Rules

2.9.1 HKICL will monitor performance by Participants of their obligations under these FPS Rules.

2.9.2 In the event that HKICL becomes aware of any non performance by any Participant of its
obligations under these FPS Rules, HKICL shall as soon as practicable inform (i) the Participant
concerned and require it to ensure performance of the relevant pro vision; and (ii) MA of such
incident.

## Page 14

Hong Kong Interbank Clearing Limited
Rules for Hong Kong Dollar Faster Payment System
Redacted version: August 2025 Page 11
Part III Settlement

3.1 Settlement Institution, Settlement Accounts and FPS Ledger Accounts

3.1.1 The settlement institution is MA and each Settlement Participant shall open and keep a
Settlement Account (including a CHATS Ledger Account and an FPS Ledger Account) with
MA in accordance with the Conditions for the operation of Settlement Accounts (including
CHATS Ledger Accounts and FPS Ledger Accounts) for the purposes of settlement of payments
effected through FPS.

3.1.2 Each Clearing Participant shall open and keep an account with a Settlement Participant and
agree with such Settlement Participant the terms and conditions on which such Settlement
Participant shall permit payments by or to such Clearing Participant t o be settled through such
Settlement Participant’s FPS Ledger Account.

3.1.3 Each Settlement Participant shall maintain an available balance in its FPS Ledger Account
sufficient to meet in time its and its Clearing Participants’ payment obligations which are to be
settled through such FPS Ledger Account as and when due.

3.1.4 Each Settlement Participant authorises MA to debit or, as the case may be, credit its FPS Ledger
Account and its CHATS Ledger Account for the purpose of implementing Balance -triggered
Balance Sweeping Transactions and Transaction -triggered Balance Sweeping Transactions in
accordance with the provisions of these FPS Rules, the Clearing House Rules and the Conditions.
To the extent there is any conflict among the Conditions, these FPS Rules and the Clearing
House Rules, the Conditions shall prevail.

3.1.5 Notwithstanding the mode and means by which they are made, all payments by or to each
Participant which are effected through FPS shall be settled by MA debiting or crediting the FPS
Ledger Account of the Settlement Participant through which the Participant settles its payments
through FPS (including payments related to both the Settlement Participant itself and its
Clearing Participants) and once debited or credited to such FPS Ledger Account, such payments
shall be deemed made, completed, irrevocable and final.

3.1.6 Each Settlement Participant authorises MA to debit or, as the case may be, credit its FPS Ledger
Account for payments by or to such Settlement Participant or its Clearing Participants which
are effected through FPS in accordance with the provisions of these FPS Rules and the
Conditions. To the extent there is any conflict among the Conditions and these FPS Rules, the
Conditions shall prevail.

3.2 Settlement of FPS Transactions

All FPS Transactions involving payments or funds transfers shall be settled as provided in Part VI of
these FPS Rules.

3.3 Settlement Obligations

Notwithstanding any provisions in these FPS Rules but without prejudice to HKICL’s obligations in
respect of the management and operation of the Clearing House and /or the FPS Facilities, HKICL and
MA shall be under no liability whatsoever for any FPS settlement obligations of or between Participants.

## Page 15

Hong Kong Interbank Clearing Limited
Rules for Hong Kong Dollar Faster Payment System
Redacted version: August 2025 Page 12
Part IV Participants

4.1 FPS Rules and FPS Operating Procedures

These FPS Rules and the FPS Operating Procedures are binding on the Participants. Participants shall
comply with and observe these FPS Rules and the FPS Operating Procedures (as amended from time to
time and insofar as the Participant participates in an activity that is a subject matter of the FPS Operating
Procedures) from time to time in force.

4.2 Membership

4.2.1 Unless otherwise approved by MA, banks being CHATS Members (that in each case maintains
a Settlement Account including a CHATS Ledger Account) are required to become Settlement
Participants.

4.2.2 Restricted licence banks or any institutions other than banks and restricted licence banks that in
either case maintain a Settlement Account including a CHATS Ledger Account may, subject to
MA’s approval, become Settlement Participants.

4.2.3 Licensees of a stored value facility licensed by MA under the PSSVFO, including banks that
are licensed under the PSSVFO as licensees of a stored value facility, may by agreement with a
Settlement Participant become Clearing Participants through such Settlement Participant.

4.2.4 Subject to MA’s approval and by agreement with a Settlement Participant, any other institutions
other than licensees of a stored value facility under the PSSVFO may become Clearing
Participants through such Settlement Participant.

4.2.5 For the avoidance of doubt, any party that meets the access criteria of both Settlement
Participant and Clearing Participant as provided in Rules 4.2.1 to 4.2.4 must become a
Settlement Participant and, in addition, may opt to become a Clearing Participant.

4.2.6 A Settlement Participant shall give 14 days’ prior written notice to MA and HKICL before it
allows an institution to become its Clearing Participant or before it terminates its agreement to
allow an institution to become its Clearing Participant.

4.2.7 With respect to Rule 4.2.6, a Clearing Participant, through its Settlement Participant, shall give
14 days’ prior written notice to MA and HKICL before it terminates an agreement to become
its Clearing Participant with such Settlement Participant and agrees with another Settlement
Participant to become its Clearing Participant.

4.2.8 Subject to Rule 4.2.5, a Participant shall give 14 days’ prior written notice to MA and HKICL
before it changes its status from a Settlement Participant to a Clearing Participant or vice versa
as the case may be.

4.3 Withdrawal

A Participant may withdraw from participation in FPS by giving 90 days’ prior written notice to HKICL
and by paying the accrued fees and other payments, if any, due by it to HKICL in relation to the Clearing
House and/or the FPS Facilities up to the date of withdrawal. A Clearing Participant shall also at the
same time notify its Settlement Participant. A Settlement Participant may not terminate its FPS Ledger
Account while it continues to be a Settlement Participant or while it continues to allow a Clear ing
Participant to be its Clearing Participant or during the running of any notice given under this Rule. Any
such withdrawal shall be without prejudice to any liability accrued up to and including the date of
withdrawal.

## Page 16

Hong Kong Interbank Clearing Limited
Rules for Hong Kong Dollar Faster Payment System
Redacted version: August 2025 Page 13
4.4 Participant Codes

Participant codes which are used to identify each Participant are allocated by HKICL to be used by
Participants for the purposes of the services provided by the Clearing House in relation to FPS. No
Participant may use a participant code which is allocate d to another Participant. All such rights as may
subsist in the participant codes are owned by HKICL and such codes may be used by it for all purposes
connected with or incidental to its businesses.

4.5 Outsourcing by Participants

Participants may outsource any of their systems required for the purpose of participation in FPS. In so
doing Participants shall exercise reasonable skill and care in choosing the outsourcing party. Each of
MA and HKICL is authorised to deal with any suc h outsourcing party notified to it as being authorised
to act on such Participant’s behalf provided that the Participant shall be responsible for all acts, omissions,
neglects or defaults of its outsourcing party and such Participant appointing an outsourc ing party will
indemnify and hold each of MA and HKICL harmless against all actions, proceedings, costs, claims,
demands, liabilities, losses and expenses whatsoever and howsoever arising out of or incurred by MA or
HKICL as a result of the acts, omissions, neglects or defaults of its outsourcing party or arising out of or
incurred by MA or HKICL by virtue of any dealings by MA or HKICL with an outsourcing party of a
Participant which it would not have incurred if MA or HKICL had dealt with that Participant directly.

4.6 Intra Participant Payments

For the avoidance of doubt, a Participant can initiate funds transfers to itself in respect of FPS
Transactions.

## Page 17

Hong Kong Interbank Clearing Limited
Rules for Hong Kong Dollar Faster Payment System
Redacted version: August 2025 Page 14
Part V Refusal/Suspension of FPS Facilities

5.1 Part or all of the FPS Facilities shall be refused forthwith by HKICL in relation to a Participant if:

(a) the authorisation of the Participant (if it is a Settlement Participant) under the Banking Ordinance
(Cap. 155 of the Laws of Hong Kong) has been suspended or revoked, unless HKICL receives notice
in writing by MA that FPS Facilities to such Participant may be continued in the manner as specified
in such notice;

(b) the licence or designation of the Participant (if it is a Clearing Participant) under the PSSVFO has
been suspended or revoked, unless HKICL receives notice in writing by MA that FPS Facilities to
such Participant may be continued in the manner as specified in such notice; or

(c) HKICL receives notice in writing from MA that FPS Facilities in relation to the Participant are to
be refused.

5.2 Part or all of the FPS Facilities shall be suspended forthwith for a Participant by HKICL:

(a) upon receipt by HKICL of a notice in writing from MA that FPS Facilities to such Participant have
been suspended by MA for such period as shall be stipulated in such notice; or

(b) if the Participant becomes insolvent.

5.3 In a case to which Rule 5.1 or 5.2 applies, FPS Facilities shall only be restored to the Participant in
question upon receipt by HKICL of a notice in writing to such effect from MA.

5.4 In the event that a Clearing Participant becomes insolvent or is the subject of a winding up petition or
other like process, the Settlement Participant which has agreed to become its Settlement Participant shall
forthwith advise MA thereof and forthwith stop initiating or otherwise processing or executing any FPS
Instructions in respect of that Clearing Participant or crediting or otherwise making any payment in
respect of any FPS Transaction by or to that Clearing Participant.

5.5 If any Participant’s use of the FPS Facilities has been refused or suspended, HKICL shall, as soon as
practicable thereafter, notify all other Participants by a broadcast in the manner provided in the FPS
Operating Procedures and thereafter all other Participants shall not initiate any o ther FPS Instructions
involving the Participant for which FPS Facilities are refused or suspended while such refusal or
suspension shall continue in effect.

5.6 If it appears that part or all of the FPS Facilities are inoperable, HKICL may at any time after consultation
with MA, declare by notice in writing to all Participants, that all or part of the FPS Facilities will be
suspended and shall provide information as to which (if any) of the FPS Facilities will be available.

5.7 During the time when part or all of the FPS Facilities are inoperable, HKICL may at any time after
consultation with MA declare by notice in writing to all Participants, that part or all of the FPS Facilities
which have been suspended shall resume normal operation.

5.8 During the time when part or all of the FPS Facilities are inoperable, the FPS Facilities that are operable
shall be operated in accordance with the FPS Operating Procedures and any other circulars issued by
HKICL dealing with the operation of the FPS Facilities during periods of suspension.

5.9 The resumption of normal operation of the FPS Facilities shall be in accordance with the FPS Operating
Procedures.

5.10 Neither MA nor HKICL shall owe any duty or incur any liability to any Participant, any customer of a
Participant (including for the avoidance of doubt any FPS Payment Application Selection Gateway User),
or any other person whatsoever (each a “ Relevant Person ”) by the giving of any notice or advice
pursuant to or purporting to be given pursuant to this Rule 5 or by the failure to give or any delay in

## Page 18

Hong Kong Interbank Clearing Limited
Rules for Hong Kong Dollar Faster Payment System
Redacted version: August 2025 Page 15
giving any such notice or advice. HKICL shall incur no liability to any Relevant Person for the
consequences of acting on these FPS Rules or the FPS Operating Procedures or any such notice or advice
given or purportedly given to any Relevant Person pursuant to this Rule 5. Each Participant hereby
agrees to indemnify and hold each of MA and HKICL harmless against all actions, proceedings, costs,
claims, demands, liabilities, losses and expenses whatsoever and howsoever arising out of or in
connection with any of the matters referred to in this Rule , or incurred by either MA or HKICL to any
Relevant Person in its capacity as such.

## Page 19

Hong Kong Interbank Clearing Limited
Rules for Hong Kong Dollar Faster Payment System
Redacted version: August 2025 Page 16
Part VI FPS

6.1 Introduction

6.1.1 Each Participant shall access FPS via the HKICL network. FPS Instructions effected through
FPS and their related request s shall be in designated ISO20022 format or any other format as
stipulated in the FPS Operating Procedures and the related technical specifications pertaining
to the FPS Operating Procedures.

6.1.2 All Participants must be connected to the FPS Console as provided in Rule 6.6 to perform
operation, administrati ve and monitoring functions as the case may be related to FPS
Instructions as stipulated in the FPS Operating Procedures.

6.1.3 Requests for enhancement of or changes relating to FPS by a Participant shall be submitted by
that Participant to HKICL, to enable HKICL to decide whether they should be implemented,
subject to prior consultation by HKICL with MA.

6.2 Settlement of FPS Transactions

6.2.1 Timing of Settlement

6.2.1.1 FPS Transactions are not guaranteed to be settled in accordance with the sequence of
receipt of such FPS Transactions by FPS nor the sequence of initiation of such FPS
Transactions.

6.2.1.2 HKICL may process the Credit Transfer Instructions, including those initiated for the
return of FPS Transactions, and Direct Debit Instructions involving the same payer
Participants and the same payee Participants within the same batch in a group but on
the basis that they are settled individually and simultaneously. If due to shortage of
funds in the relevant FPS Ledger Account that the settlement in accordance with this
Rule 6.2.1.2 is not possible, HKICL may at its discretion decouple a group and effect
and settle individual instructions in such order as it thinks fit. Any individual
instruction which cannot be effected or settled will be rejected subject to the exception
stipulated in Rule 6.2.3.1.

6.2.2 Credit Transfer Instruction

6.2.2.1 A Credit Transfer Instruction will not be effected or settled through FPS unless:

(a) if the payer Participant is a Settlement Participant, the available balance in the
payer Participant’s FPS Ledger Account is; or

(b) if the payer Participant is a Clearing Participant, the available balance of that
Clearing Participant maintained with its Settlement Participant and the
available balance of the FPS Ledger Account of its Settlement Participant are,

for the time being sufficient to make such funds transfer referred to in such Credit
Transfer Instruction. If a Credit Transfer Instruction cannot be effected or settled under
the above circumstances, the relevant Credit Transfer Instruction will be rejected
immediately.

6.2.2.2 Subject to Rule 6.2.1 and Rule 6.2.2.1, a funds transfer initiated by a Credit Transfer
Instruction will be settled through FPS immediately upon the completion of its
processing.

6.2.2.3 Settlement of a Credit Transfer Instruction will be effected across the books of MA
pursuant to Rule 3.1.5 by debiting the FPS Ledger Account of the payer Participant (or

## Page 20

Hong Kong Interbank Clearing Limited
Rules for Hong Kong Dollar Faster Payment System
Redacted version: August 2025 Page 17
if the payer Participant is a Clearing Participant, the FPS Ledger Account of its
Settlement Participant) for the funds transferred and crediting the same to the FPS
Ledger Account of the payee Participant (or if the payee Participant is a Clearing
Participant, the FPS Ledger Account of its Settlement Participant). Upon the
completion of settlement, the transaction will be reflected in the available balance of
the relevant Clearing Participant maintained with its Settlement Participant and/or FPS
Ledger Account of the relevant Settlement Participant.

6.2.2.4 [This provision has been left blank intentionally]

6.2.3 Direct Debit Instruction

6.2.3.1 A Direct Debit Instruction will not be effected or settled through FPS unless:

(a) if the payer Participant is a Settlement Participant, the available balance in the
payer Participant’s FPS Ledger Account is; or

(b) if the payer Participant is a Clearing Participant, the available balance of that
Clearing Participant maintained with its Settlement Participant and the
available balance of the FPS Ledger Account of its Settlement Participant are,

for the time being sufficient to make the funds transfer referred to in such Direct Debit
Instruction. If a Direct Debit Instruction cannot be effected or settled under the above
circumstances, the relevant Direct Debit Instruction will be rejected immediately
except in the case specified in the FPS Operating Procedures. If settlement of any
Direct Debit Instructions in accordance with the firs t sentence of this Rule 6.2.3.1 is
not possible and the settlement of such Direct Debit Instructions fall within the
exception as specified in the FPS Operating Procedures, the relevant outstanding
Direct Debit Instructions will be re-tried for settlement in accordance with the schedule
and conditions as stipulated in the FPS Operating Procedures, and if any such
outstanding Direct Debit Instructions cannot be settled by the cut-off time as stipulated
in the FPS Operating Procedures, such outstanding Direct Debit Instructions will be
rejected automatically.

6.2.3.2 Subject to Rule 6.2.1 and Rule 6.2. 3.1, a funds transfer initiated by a Direct Debit
Instruction will be settled through FPS immediately upon the completion of its
processing.

6.2.3.3 Settlement of a Direct Debit Instruction will be effected across the books of MA
pursuant to Rule 3.1.5 by debiting the FPS Ledger Account of the payer Participant (or
if the payer Participant is a Clearing Participant, the FPS Ledger Account of its
Settlement Participant) for the funds transferred and crediting the same to the FPS
Ledger Account of the payee Participant (or if the payee Participant is a Clearing
Participant, the FPS Ledger Account of its Settlement Participant). Upon the
completion of settlement, the transaction will be reflected in the available balance of
the relevant Clearing Participant maintained with its Settlement Participant and/or FPS
Ledger Account of the relevant Settlement Participant.

6.2.4 Settlement of SI Direct Debit Transactions

6.2.4.1 Rule 6.2.4 is only applicable to Settlement Participants.

6.2.4.2 An SI Direct Debit Transaction will be settled immediately in case the available
balance in the relevant Settlement Participant’s FPS Ledger Account for the time being
is sufficient to make the funds transfer referred to in such transaction. In case the
available balance in the relevant Settlement Participant’s FPS Ledger Account is
insufficient to make such funds transfer, the relevant SI Direct Debit Transaction will
be rejected immediately.

## Page 21

Hong Kong Interbank Clearing Limited
Rules for Hong Kong Dollar Faster Payment System
Redacted version: August 2025 Page 18

6.2.4.3 Subject to Rule 6.2.1.1 and Rule 6.2.4.2, an SI Direct Debit Transaction will be settled
through FPS immediately upon the completion of its processing.

6.2.4.4 Settlement of an SI Direct Debit Transaction will be effected across the book s of MA
pursuant to Rule 3.1.5 by debiting the relevant FPS Ledger Account for the payment
referred to in such transaction.

6.2.5 Settlement of SI Direct Credit Transactions

6.2.5.1 Rule 6.2.5 is only applicable to Settlement Participants.

6.2.5.2 Subject to Rule 6.2.1.1, a n SI Direct Credit Transaction will be settled through FPS
immediately upon the completion of its processing.

6.2.5.3 Settlement of an SI Direct Credit Transaction will be effected across the books of MA
pursuant to Rule 3.1.5 by crediting the relevant FPS Ledger Account for the payment
referred to in such transaction.

6.2.6 Settlement of Balance-triggered Balance Sweeping Transactions

6.2.6.1 Rule 6.2.6 is only applicable to Settlement Participants.

6.2.6.2 A Balance-triggered Balance Sweeping Transaction will be triggered manually by a
Settlement Participant or automatically by FPS in the following circumstances:

(a) to complete the account balance sweeping request by transferring funds from
the FPS Ledger Account of a Settlement Participant to its CHATS Ledger
Account pursuant to Rule 6.4.1.3(a), 6.4.1.6 and 6.4.1.10(b). Such Balance -
triggered Balance Sweeping Transaction is triggered to debit funds from the
FPS Ledger Account of the Settlement Participant. Subject to Rule 6.2.1.1,
the Balance-triggered Balance Sweeping Transaction will be settled through
FPS immediately upon the completion of its processing; or

(b) to complete the account balance sweeping request by transferring funds from
the CHATS Ledger Account of a Settlement Participant to its FPS Ledger
Account pursuant to Rule 6.4.1.3(b), 6.4.1.6 and 6.4.1.10(a). Such Balance -
triggered Balance Sweeping Transaction is triggered to credit funds to the
FPS Ledger Account of the Settlement Participant. Subject to Rule 6.2.1.1,
the Balance-triggered Balance Sweeping Transaction will be settled through
FPS immediately upon the completion of its processing.

6.2.7 Settlement of Transaction-triggered Balance Sweeping Transactions

6.2.7.1 Rule 6.2.7 is only applicable to Settlement Participants who have opted for the
automatic transaction-triggered account balance sweeping function.

6.2.7.2 A Transaction-triggered Balance Sweeping Transaction will be triggered automatically
by FPS if there are outstanding Direct Debit Instructions after the second settlement
retry in accordance with the schedule and conditions stipulated in the FPS Operating
Procedures. Such Transa ction-triggered Balance Sweeping Transaction will be
triggered in accordance with the schedule and conditions stipulated in the FPS
Operating Procedures to complete the automatically -triggered account balance
sweeping request by transferring the required funds from the CHATS Ledger Account
of the relevant Settlement Participant to its FPS Ledger Account pursuant to Rule
6.4.1.4 to settle the outstanding Direct Debit Instructions. Subject to Rule 6.2.1.1, a
Transaction-triggered Balance Sweeping Transaction will be settled through FPS
immediately upon the completion of its processing.

## Page 22

Hong Kong Interbank Clearing Limited
Rules for Hong Kong Dollar Faster Payment System
Redacted version: August 2025 Page 19
6.2.8 TH-HK Merchant Payment Instruction

6.2.8.1 Rule 6.2.8 is only applicable to Participants who are supporting TH-HK Merchant
Payment Instructions.

6.2.8.2 The flow of funds in settling the underlying payment of an Inbound TH-HK Merchant
Payment Instruction involves:

(a) the Thai bank participating in PromptPay engaged by the payer transferring
the funds in Thai Baht to the designated settlement bank in Thailand (“TH
Settlement Bank”) through means outside FPS of an amount calculated based
on the underlying Hong Kong dollar payment amount, where the provision of
the foreign exchange rate and the settlement arrangement is subject to the
agreement between the two parties;

(b) the TH Settlement Bank converting the fun ds processed in Rule 6.2.8.2 (a)
from Thai Baht to H ong Kong dollars and effecting a funds transfer through
means outside FPS to the Participant being designated as the settlement bank
in Hong Kong (“HK Settlement Bank”) in accordance with the settlement
arrangement as agreed between the two parties; and

(c) the HK Settlement Bank , which plays the role of the payer Participant ,
transferring the fu nds processed in Rule 6.2.8.2(b) to the Hong Kong payee
Participant via FPS. Such funds transfer is effected in the form of a Credit
Transfer Instruction in accordance with the settlement arrangement stipulated
in Rules 6.2.2.1 to 6.2.2.3.

6.2.8.3 The flow of funds in settling the underlying payment of an Outbound TH-HK Merchant
Payment Instruction involves:

(a) the Hong Kong payer Participant transferring the funds in Hong Kong dollars
to the HK Settlement Bank, which plays the role of the payee Participant, via
FPS. Such funds transfer is effected in the form of a Credit Transfer
Instruction of which (i) the amount is calculated based on the underlying Thai
Baht payment amount, where the provision of foreign exchange rate is subject
to Rule 6.2. 8.4; and (ii) the settlement arrangement is stipulated in Rules
6.2.2.1 to 6.2.2.3;

(b) the HK Settlement Bank converting the fu nds processed in Rule 6.2.8.3(a)
from Hong Kong dollars to Thai Baht and effecting a funds transfer to the TH
Settlement Bank through means outside FPS in accordance with the
settlement arrangement as agreed between the two parties; and

(c) the TH Settlement Bank transferring the funds processed in Rule 6.2.8.3(b) to
the Thai bank participating in PromptPay engaged by the payee through
means outside FPS in accordance with the settlement arrangement as agreed
between the two parties.

6.2.8.4 A payer Participant should note the following:

(a) the foreign exchange rate used for the currency conversion in Rule 6.2.8.3(a)
is provided by the HK Settlement Bank according to the agreement between
the payer Participant and the HK Settlement Bank . Eac h foreign exchange
rate provided is valid for a certain period as stipulated in the FPS Operating
Procedures;

(b) the foreign exchange rate provided in Rule 6.2.8.4(a) is relayed by FPS to the
payer Participant together with its period of validity upon receipt of an

## Page 23

Hong Kong Interbank Clearing Limited
Rules for Hong Kong Dollar Faster Payment System
Redacted version: August 2025 Page 20
enquiry by such Participant. The payer Participant should use the foreign
exchange rate provided to convert the Thai Baht payment amount of the
underlying payment to a Hong Kong dollar payment amount in an Outbound
TH-HK Merchant Payment Instruction and submit the payment instruction in
FPS while the rate is still valid;

(c) Neither HKICL nor MA shall be responsible for:

(i) verifying the correctness of the foreign exchange rate provided in
Rule 6.2.8.4(a); and

(ii) checking the validity of the foreign exchange rate used to calculate
the payment amount in Rule 6.2.8.4(b);

(d) before the settlement of an Outbound TH-HK Merchant Payment Instruction
between the payer Participant and the HK Settlement Bank in FPS, the foreign
exchange rate and related information is passed to the HK Settlement Bank
for validation. Subject to the validation result provided by the HK Settlement
Bank, the settlement of the Outbound TH-HK Merchant Payment Instruction
between the payer Participant and the HK Settlement Bank will be effected
through FPS as a Credit Transfer Instruction; and

(e) under exceptional circumstances where the provision of foreign exchange rate
by the HK Settlement Bank is unavailable, HKICL will notify the Participants
as soon as practicable. Neither HKICL nor MA shall be liable for any claim,
loss, damage or expense of any kind or nature whatsoever arising in whatever
manner directly or indirectly out of or in connection with the unavailability
of the foreign exchange rate or failure to give or any delay in giving any such
notice.

6.2.8.5 In processing an Outbound TH -HK Merchant Payment Instruction pursuant to Rule
6.2.8.3(a), the payer Participant is responsible for checking the payment amount
against the transaction limit and any other controls as agreed among th e Participants
from time to time. Payer Participants should not initiate Outbound TH -HK Merchant
Payment Instructions which do not comply with such limit and controls.

6.2.8.6 Returns of Inbound TH-HK Merchant Payment Instructions will be settled by the payer
and the payee outside FPS in accordance with the arrangement as agreed between the
two parties.

6.2.8.7 A return of an Outbound TH-HK Merchant Payment Instruction may only be initiated
by the HK Settlement Bank or generated by FPS upon receipt of instruction from
PromptPay. The amount of funds returned is the amount of funds transferred in Rule
6.2.8.3(a). The detailed return arrangement is stipulated in the FPS Operating
Procedures.

6.2.8.8 Neither HKICL nor MA shall be liable for any claim, loss, damage or expense of any
kind or nature whatsoever arising in whatever manner directly or indirectly out of or
in connection w ith the processing or settlement of (or any failure or delay to process
or settle) any TH-HK Merchant Payment Instructions outside FPS in accordance with
Rule 6.2.8.

## Page 24

Hong Kong Interbank Clearing Limited
Rules for Hong Kong Dollar Faster Payment System
Redacted version: August 2025 Page 21
6.2.9 CN-HK Remittance Payment Instruction

6.2.9.1 Rule 6.2.9 is only applicable to Participants who are supporting CN-HK Remittance
Payment Instructions.

6.2.9.2 The flow of funds in settling the underlying payment of a Northbound CN -HK
Remittance Payment Instruction involves:

(a) the Hong Kong payer Participant transferring the funds in Hong Kong dollars
to the CN-HK Settlement Bank, which plays the role of the payee Participant,
via FPS. Such funds transfer is effected in the form of a Credit Transfer
Instruction of which (i) the amount is calculated based on the underlying
Renminbi payment amount, where the provision of foreign exchange rate is
subject to Rule 6.2.9.4; and (ii) the settlement arrangement is stipulated in
Rules 6.2.2.1 to 6.2.2.3;

(b) the CN-HK Settlement Bank exchanges the funds processed in 6.2.9.2(a) with
the Foreign Exchange Service Provider on behalf of the payer Participant for
the currency conversion from Hong Kong dollars to Renminbi in accordance
with the settlement arrangement as agreed between the Foreign Exchange
Service Provider and the CN-HK Settlement Bank; and

(c) the CN -HK Settlement Bank transferring the funds processed in Rule
6.2.9.2(b) in Renminbi to the bank in the Mainland participating in IBPS
engaged by the payee via IBPS in accordance with the settlement arrangement
as agreed between the two parties.

6.2.9.3 The flow of funds in settling the underlying payment of a Southbound CN -HK
Remittance Payment Instruction involves:

(a) the bank in the Mainland participating in IBPS engaged by the payer
transferring the funds in Renminbi to the CN -HK Settlement Bank via IBPS
of an amount calculated based on the underlying Hong Kong dollar payment
amount that the payer from the Mainland intends to remit to the payee in Hong
Kong, where the pr ovision of the foreign exchange rate and the settlement
arrangement is subject to the agreement between the two parties;

(b) the CN-HK Settlement Bank converting the funds processed in Rule 6.2.9.3(a)
from Renminbi to Hong Kong dollars in accordance with the arrangement as
agreed with the bank in the Mainland; and

(c) the CN -HK Settlement Bank, which also plays the role of the payer
Participant, transferring the funds processed in Rule 6.2.9.3(b) in Hong Kong
dollars to the Hong Kong payee Participant via FPS. Such funds transfer is
effected in the form of a Credit Transfer Instruction in accordance with the
settlement arrangement stipulated in Rules 6.2.2.1 to 6.2.2.3.

6.2.9.4 A payer Participant should note the following:

(a) the foreign exchange rate used for the currency conversion in Rule 6.2.9.2(a)
is provided by the Foreign Exchange Service Provider according to the
agreement between the payer Participant and the Foreign Exchange Service
Provider. Each foreign exchange rate provided is valid for a certain period as
stipulated in the FPS Operating Procedures;

(b) the foreign exchange rate provided in Rule 6.2.9.4(a) is relayed by FPS to the
payer Participant together with its period of validity upon receipt of an
enquiry by such Participant. The payer Participan t should use the foreign

## Page 25

Hong Kong Interbank Clearing Limited
Rules for Hong Kong Dollar Faster Payment System
Redacted version: August 2025 Page 22
exchange rate provided to c onvert the Renminbi payment amount of the
underlying payment to a Hong Kong dollar payment amount in a Northbound
CN-HK Remittance Payment Instruction and submit the payment instruction
in FPS while the rate is still valid;

(c) Neither HKICL nor MA shall be responsible for:

(i) verifying the correctness of the foreign exchange rate provided in
Rule 6.2.9.4(a); and

(ii) checking the validity of the foreign exchange rate used to calculate
the payment amount in Rule 6.2.9.4(b);

(d) under exceptional circumstances where the provision of foreign exchange rate
by the Foreign Exchange Service Provider is unavailable, HKICL will notify
the Participants as soon as practicable. Neither HKICL nor MA shall be liable
for any claim, loss, damage or expense of a ny kind or nature whatsoever
arising in whatever manner directly or indirectly out of or in connection with
the unavailability of the foreign exchange rate or failure to give or any delay
in giving any such notice.

6.2.9.5 In processing a Northbound CN-HK Remittance Payment Instruction pursuant to Rule
6.2.9.2(a), the payer Participant is responsible for checking the payment amount
against the transaction limit, any regulatory requirements applicable to the payer
Participant, including but not limited to sanction screening, anti-money laundering and
counter-terrorist financing checking, and any other controls as deemed necessary by
the payer Participant. Payer Participants should not initiate Northbound CN -HK
Remittance Payment Instructions which do not comply with such limit, regulatory
requirements and controls.

6.2.9.6 In processing a Southbound CN-HK Remittance Payment Instruction pursuant to Rule
6.2.9.3, the payee Participant is responsible for checking the payment instruction
against any regulatory requirements applicable to the payee Participant, including but
not limited to sanction screening, anti-money laundering and counter -terrorist
financing checking, and other controls as deemed necessary by the payee Participant.

6.2.9.7 A return of a Northbound CN-HK Remittance Payment Instruction may be initiated by
the payee bank in the Mainland or the CN -HK Settlement Bank, or generated by FPS
upon receipt of instruction from IBPS. The amount of funds returned is the amount of
funds transferred in Rule 6.2.9. 2(a). The detailed return arrangement is stipulated in
the FPS Operating Procedures.

6.2.9.8 A payee Participant should only initiate a return of a Southbound CN-HK Remittance
Payment Instruction if the payee Participant is unable to apply funds from the payment
instruction to the payee’s account. The amount of funds returned shall be the amount
of funds transferred in Rule 6.2.9.3(c). The return of Southbound CN-HK Remittance
Payment Instructions will be settled via FPS and IBPS. The detailed return
arrangement is stipulated in the FPS Operating Procedures.

6.2.9.9 Neither HKICL nor MA shall be liable for any claim, loss, damage or expense of any
kind or nature whatsoever arising in whatever manner directly or indirectly out of or
in connection with the processing or settlement of (or any failure or delay to process
or settle) any CN-HK Remittance Payment Instructions outside FPS in accordance with
Rule 6.2.9.

## Page 26

Hong Kong Interbank Clearing Limited
Rules for Hong Kong Dollar Faster Payment System
Redacted version: August 2025 Page 23
6.3 Returns of FPS Transactions

6.3.1 For the avoidance of doubt, Rule 6.3 is only applicable to FPS Transactions effected by Credit
Transfer Instructions (other than TH -HK Merchant Payment Instructions and CN-HK
Remittance Payment Instructions ) or Direct Debit Instructions. Returns of TH -HK Merchant
Payment Instructions should be processed in accord ance with Rules 6. 2.8.6 to 6.2.8.7 and the
FPS Operating Procedures. Returns of CN-HK Remittance Payment Instructions should be
processed in accordance with Rule 6.2.9.7 to 6.2.9.8 and the FPS Operating Procedures. Returns
of FPS Transactions other than those aforementioned will be settled by the payee initiating
another FPS Transaction in favour of the appropriate party or by a transfer outside FPS.

6.3.2 All returns of Credit Transfer Instructions or Direct Debit Instructions should be effected
through FPS not later than the time appointed by HKICL, and must include in the instruction
the information as stipulated in the FPS Operating Procedures.

6.3.3 A return of a Credit Transfer Instruction or Direct Debit Instruction may only be initiated by the
payee Participant of the funds transfer. If a payee Participant is unable to apply funds from a
credit transfer for any reason or is requested by its customer to refund a credit transfer or a direct
debit for any reason, then that payee Participant must send the funds actually received or as
requested through FPS back to the original payer Participant in accordance with the procedure
set out in Rule 6.3.2.

6.4 Liquidity Management

6.4.1 Account Balance Sweeping

6.4.1.1 Rule 6.4.1 is only applicable to Settlement Participants.

6.4.1.2 The account balance sweeping facility shall be made available on a CHATS Working
Day within the timeframe stipulated in the FPS Operating Procedures for the transfer
of funds between an FPS Ledger Account of a Settlement Participant and its CHATS
Ledger Account.

6.4.1.3 [This provision has been left blank intentionally]

6.4.1.4 [This provision has been left blank intentionally]

6.4.1.5 [This provision has been left blank intentionally]

6.4.1.6 [This provision has been left blank intentionally]

6.4.1.7 [This provision has been left blank intentionally]

6.4.1.8 [This provision has been left blank intentionally]

6.4.1.9 [This provision has been left blank intentionally]

6.4.1.10 [This provision has been left blank intentionally]

6.4.1.11 [This provision has been left blank intentionally]

6.4.1.12 Neither HKICL nor MA shall be liable for any claim, loss, damage or expense of any
kind or nature whatsoever arising in whatever manner directly or indirectly out of or
in connection with any transaction settlement delay or failure in FPS and/or CHATS
due to insufficient funds with or without account balance sweeping facility applied.

## Page 27

Hong Kong Interbank Clearing Limited
Rules for Hong Kong Dollar Faster Payment System
Redacted version: August 2025 Page 24
6.4.2 Available Balance Adjustment

6.4.2.1 Each Clearing Participant agrees that its Settlement Participant can adjust its available
balance in accordance with the FPS Operating Procedures.

6.4.2.2 Each Clearing Participant shall separately agree with its Settlement Participant on a
bilateral basis the terms and arrangement on which liquidity is provided by the
Settlement Participant and shall monitor its available balance to ensure it has sufficient
funds for settlement of FPS Transactions.

6.4.2.3 If it is necessary to adjust the available balance of a Clearing Participant, its Settlement
Participant should do so in accordance with the FPS Operating Procedures.

6.5 Overlay Services

6.5.1 Addressing Service

6.5.1.1 Each Participant must comply with the rules and guidelines as stipulated in these FPS
Rules and the FPS Operating Procedures relating to the use of the Addressing Service.

6.5.1.2 [This provision has been left blank intentionally]

6.5.1.3 [This provision has been left blank intentionally]

6.5.1.4 [This provision has been left blank intentionally]

6.5.1.5 [This provision has been left blank intentionally]

6.5.1.6 [This provision has been left blank intentionally]

6.5.1.7 Participants should implement all necessary measures to (i) avoid usage of the
Addressing Service for the retrieval of data for purposes other than those contemplated
in the FPS Rules and FPS Operating Procedures, either by the Participant or on behalf
of its customers; (ii) detect and monitor any customer behaviour other than as provided
in paragraph (i) of this Rule 6.5.1.7, including but not limited to mass retrieval of payee
information and misuse of the addressing record retrieved from FPS; and (iii) ensure
that they refrain from disclosing or mentioning the use of the list of cancelled mobile
phone numbers referred to in Rule 6.5.1.2(e) as a supplementary measure to assist
HKICL to cancel the addressing record of any customers in accordance with Rule
6.5.1.2(e). Neither HKICL nor MA shall be responsible for any claim, loss, damage
or expense of any kind or nature whatsoever arising in whatever manner directly or
indirectly out of or in connection with a Partici pant’s failure to comply with this Rule
6.5.1.7.

6.5.1.8 Participants should ensure the correctness of information provided to HKICL via the
Addressing Service. Neither HKICL nor MA shall be responsible for any claim, loss,
damage or expense of any kind or nature whatsoever arising in whatever manner
directly or indirectly out of or in connection with any error or inaccuracy in the
addressing record. Participants shall indemnify and hold each of HKICL and MA
harmless against all actions, proceedings, costs, claims, demands, liabilities, losses and
expenses whatsoever and howsoever arising out of or as a result of a Participant’s
failure to perform any of its obligations under this Rule 6.5.1.

6.5.1.9 Each Participant shall indemnify and hold each of HKICL and MA harmless from and
against all actions, proceedings, costs, claims, demands, liabilities, losses and expenses
(including legal fees) directly or indirectly arising out of or resulting from:

(a) cancellation or overriding of the addressing record of a customer of that

## Page 28

Hong Kong Interbank Clearing Limited
Rules for Hong Kong Dollar Faster Payment System
Redacted version: August 2025 Page 25
Participant, or rejection of a Proxy ID registration request in accordance with
Rule 6.5.1.2(e), Rule 6.5.1.2(f) or Rule 6.5.1.4, and whether arising out of or
resulting from any error or inaccuracy in the list of cancelled mobile phone
numbers or other information provided to HKICL or for any other reason;

(b) any delay or failure in (i) cancellation or overriding of the addressing record
of a customer of that Participant, or rejection of a Proxy ID registration
request in accordance with Rule 6.5.1.2(e), Rule 6.5.1.2(f) or Rule 6.5.1.4, or
(ii) matching of Proxy ID or informing the payer Participant of the matching
result in accordance with Rule 6.5.1.2(g);

(c) any error or inaccuracy in (i) the processing of the cancellation or overriding
of the addressing record of a customer of that Participant, or rejection of a
Proxy ID registration request pursu ant to Rule 6.5.1.2(e), Rule 6.5.1.2 (f),
Rule 6.5.1.4, or (ii) matching of Proxy ID or informing the payer Participant
of the matching result in accordance with Rule 6.5.1.2(g), or otherwise;

(d) any act or omission by Participants, their customers, employees or agents or
any person authorised by Participants relating to the use (including
disclosure), of cancelled mobile phone numbers provided by HKICL to
Participants; and

(e) matching of Proxy ID in accordance with Rule 6.5.1.2(g), whether arising out
of or resulting from any error or inaccuracy in the list of suspicious Proxy ID
or other information provided by the law enforcement agencies or for any
other reason.

6.5.2 eDDA Service

6.5.2.1 Each Participant must comply with the rules and guidelines as stipulated in these FPS
Rules and the FPS Operating Procedures relating to the use of eDDA Service.

6.5.2.2 [This provision has been left blank intentionally]

6.5.2.3 [This provision has been left blank intentionally]

6.5.2.4 [This provision has been left blank intentionally]

6.5.2.5 Participants should ensure the correctness of information provided to HKICL via the
eDDA Service. Neither HKICL nor MA shall be responsible for any claim , loss,
damage or expense of any kind or nature whatsoever arising in whatever manner
directly or indirectly out of or in connection with any error or inaccuracy in the eDDA
Instructions provided to HKICL. Participants shall indemnify and hold each of HKICL
and MA harmless against all actions, proceedings, costs, claims, demands, liabilities,
losses and expenses whatsoever and howsoever arising out of or as a result of a
Participant’s failure to perform any of its obligations under this Rule 6.5.2.

6.6 FPS Console

6.6.1 Each Participant shall at its own cost install and maintain in good order a terminal which can
access the FPS Console as prescribed or approved by HKICL from time to time. Use of the
terminal which can access the FPS Console shall be restricted to that Participant’s authorised
personnel who use passwords or other systems to ensure only authorised personnel of
Participants may access the FPS Console. HKICL is authorised to rely and act on instructions
using such passwords or systems. Participants shall be liable for all consequences of misuse of
such passwords or other systems.

6.6.2 Each Participant must connect its terminal to the FPS Console in order to connect to FPS. A

## Page 29

Hong Kong Interbank Clearing Limited
Rules for Hong Kong Dollar Faster Payment System
Redacted version: August 2025 Page 26
terminal must be a computer or intelligent terminal device which can access the FPS Console.
The connection must undergo formal verification and connection tests with final approval being
at the discretion of HKICL. All telecommunications charges or charges levied by network
service providers relating to the connection shall be borne by the relevant Participant.

6.6.3 Each Participant shall strictly observe and comply with the guidelines as stipulated in the
relevant FPS Operating Procedures relating to its access or use of the FPS Console and/or the
operation of the FPS Facilities by it.

6.6.4 Requests for enhancement of or changes to the FPS Console functions by a Participant shall be
submitted by that Participant to HKICL, to enable HKICL to decide whether they should be
implemented, subject to prior consultation by HKICL with MA.

6.6.5 All software, data, specifications and similar intellectual property comprised within FPS
Facilities are owned by, or licensed to, HKICL and may not be copied, downloaded, distributed
or published in any way without the prior written consent of HKICL. Participants may utilise
such proprietary information of HKICL solely for the purposes of performing adm inistrative
functions relating to FPS Instructions, and in accordance with the FPS Rules and the FPS
Operating Procedures.

6.6.6 HKICL provides access to the FPS Console on an “as is” basis, and save as provided in these
FPS Rules, makes no representation as to, and does not warrant, the accuracy or completeness
of the FPS Console or data derived from its use. HKICL gives no war ranties, express, implied
or statutory, of any kind, including without limitation as to the merchantability, fitness for a
particular purpose, title, non-infringement of third party rights or freedom from viruses, worms,
trojan horses or other contaminating programming or code relating to the use of the FPS Console,
except to the extent the same cannot be excluded or limited at law or as otherwise given in these
FPS Rules.

6.6.7 To the fullest extent permitted by law (and subject only to the provisions of Rule 2.3 of the FPS
Rules), each of HKICL and MA shall not be liable for, and expressly excludes any such liability
for, any direct, indirect, consequential, special or incide ntal damage, loss or expense, whether
caused by negligence or otherwise, which arises directly or indirectly as a consequence of the
use of the FPS Console, whether or not HKICL or MA has been notified of the possibility of
such damage, loss or expense.

6.6.8 [This provision has been left blank intentionally]

6.7 FPS Optimiser

FPS Optimiser effected through FPS can be enabled to enhance system efficiency by increasing the
number of relevant FPS Transactions which can be processed by FPS (either through the FPS Optimiser
or Rule 6.2.2 or 6.2.3 as applicable) at a given time. Where FPS Optimiser is so enabled, FPS Optimiser
processes will be triggered automatically and repeatedly by FPS according to this Rule 6.7.

6.7.1 When an FPS Optimiser process starts, eligible FPS Transactions, comprising FPS Transactions
that are initiated by Credit Transfer Instructions or Direct Debit Instructions (including those
initiated for the return of FPS Transactions) and which are accepted for settlement and selected
through the FPS Optimiser as specified in the FPS Operating Procedures will be extracted
(“Selected Payments”) and processed according to the following provisions in Rule 6.7.

6.7.2 For each involved Participant of the Selected Payments in the FPS Optimiser run (“Selected
Participant”), FPS will compute:

(a) if the Selected Participant is a Settlement Participant, the projected available balance
in the FPS Ledger Account of the Selected Participant; and

(b) if the Selected Participant is a Clearing Participant, the projected available balance of:

## Page 30

Hong Kong Interbank Clearing Limited
Rules for Hong Kong Dollar Faster Payment System
Redacted version: August 2025 Page 27

(i) the Selected Participant maintained with its Settlement Participant; and

(ii) the FPS Ledger Account of the Selected Participant’s Settlement Participant,

for the time being based on assumed settlement of the Selected Payments in the FPS Optimiser
run through FPS immediately upon the completion of processing.

6.7.3 If the projected available balances of each of the Selected Participants and (where relevant)
Selected Participants’ Settlement Participants computed pursuant to Rule 6.7.2 in the FPS
Optimiser run are found positive or zero, the gross amount of the Selected Payments will each
be effected through FPS automatically and settled immediately upon completion of its
processing subject to Rule 6.2.1.1 and effected across the books of MA pursuant to Rule 3.1.5
by debiting and crediting the FPS Ledger Account of the Selected Participant (or if the Selected
Participant is a Clearing Participant, the FPS Ledger Account of the Selected Participant’s
Settlement Participant) for the funds transferred. Upon the completion of settlement of the
Selected Payments, the transactions will be reflected in the available balances of the relevant
Selected Participants and/or FPS Ledger Accounts of the relevant Selected Participants’
Settlement Participants.

6.7.4 In case the projected available balances computed pursuant to Rule 6.7.2 for some Selected
Participants or (where relevant) some Selected Participants’ Settlement Participants in the FPS
Optimiser run are found negative, FPS will exclude the relevant Selected Payments of such
Selected Participants from the FPS Optimiser run in accordance with the FPS Operating
Procedures in order to reach positive or zero projected available balances of each of the Selected
Participants and (where relevant) Selected P articipants’ Settlement Participants in the FPS
Optimiser run, at which point the amount of the Selected Payments which have not been so
excluded will each be effected through FPS according to Rule 6.7.3 (unless all Selected
Payments in the FPS Optimiser run are so excluded, in which case Rule 6.7.5 applies).

6.7.5 Selected Payments that are excluded from the FPS Optimiser run pursuant to Rule 6.7.4 will be
processed by FPS separately in accordance with Rules 6.2.2 and 6.2.3 (as applicable), and those
which cannot be effected and settled through FPS according t o Rule 6.2.2.1 or 6.2.3.1 (as the
case may be) will be rejected immediately accordingly.

6.8 Input FPS Instructions

FPS Instructions (except for those generated by FPS) may only be input by Participants addressed to
themselves, other Participants, MA or FPS, or by MA addressed to Participants or FPS.

6.9 Responsibility of Participants

In addition to the other provisions of these FPS Rules, each Participant shall be responsible for the
following matters:

6.9.1 the control of access to the FPS Console and the security of the Participant’s terminal(s)
connecting to the HKICL network and the FPS Console (including security and confidentiality
of passwords or other systems to ensure that only authorised personnel of Participants may
access the FPS Console), and lines, modems and other computer equipment relating thereto of
the Participant and the security of the transmission lines between FPS and the Participant’s
terminals having access to the FPS Console;

6.9.2 the operation of all equipment and software relating to the access to the FPS Console and
terminal(s) connecting to the HKICL network;

6.9.3 ensuring that:

(a) the access to and/or use of the FPS Console is in full compliance with these FPS Rules

## Page 31

Hong Kong Interbank Clearing Limited
Rules for Hong Kong Dollar Faster Payment System
Redacted version: August 2025 Page 28
and the FPS Operating Procedures;

(b) all data transmitted from terminals owned by, or under its control, through which it
gains access to the FPS Console:

(i) do not infringe the copyright or other intellectual property rights of third
parties; and

(ii) do not create and/or introduce into the HKICL network, the FPS Console
and/or FPS any virus, worms, trojan horses or other destructive or
contaminating program or codes;

(c) all data, including Personal Data, retrieved, obtained and archived from FPS shall be
used solely for the purpose of operation of FPS and facilitating FPS Instructions , FPS
Transactions and use of the Addressing Service and eDDA Service in accordance with
these FPS Rules and the FPS Operating Procedures, that no such Personal Data is used
for any other purpose, including without limitation, direct marketing and that use of
such data is in full compliance with the relevant laws and regula tions in Hong Ko ng;
and

(d) there are in place all necessary measures to:

(i) prevent usage by or on behalf of its customers of the FPS (and in particular
the Addressing Service) for retrieval of data including Personal Data for
purposes other than in accordance with Rule 6.9.3(c);

(ii) detect and monitor any misuse by or on behalf of its customers of data
including Personal Data retrieved from FPS (including mass retrieval of
payee information); and

each Participant shall indemnify and hold HKICL, MA and other Participants harmless against
the consequences of breach of any of the obligations under this Rule 6.9.3;

6.9.4 delay or non-delivery of FPS Instructions where the delay is due to force majeure or technical
failure caused by act or omission of any carrier or vendor;

6.9.5 the correct dispatch to FPS and the correct receipt by FPS of all FPS Instructions;

6.9.6 the processing of and the timely provision of response s to certain FPS Instructions in
compliance with the service level agreement as stipulated in these Rules and the FPS Operating
Procedures;

6.9.7 any loss incurred due to a fraudulent transfer of funds and information originating from a
Participant or the fraudulent insertion or alteration of a transfer of funds and information
between a Participant and FPS;

6.9.8 the verification of the funds transfer result received from FPS after funds settlement. If the
result is not in order the payee Participant must effect a return of the funds transfer quoting the
original transaction details and giving the reason for the return by the allowable period as
stipulated in the FPS Operating Procedures. If the funds transfer is returned to the payer
Participant after the allowable period as stipulated in the FPS Operating Procedures then any
loss of interest is for the account of the payer Participant;

6.9.9 as a Participant that initiates FPS Instructions, Delayed Payments in the following circumstances:

(a) if the instruction has not been accepted by FPS;

(b) if the Participant addresses an instruction incorrectly; and/or

## Page 32

Hong Kong Interbank Clearing Limited
Rules for Hong Kong Dollar Faster Payment System
Redacted version: August 2025 Page 29

(c) if the Participant ignores FPS generated messages concerning the operational system;

6.9.10 as a Participant that receives FPS Instructions, Delayed Payments in the following
circumstances:
(a) if the Participant ignores FPS generated messages concerning the operational system;

(b) if the Participant does not reconcile its settlement total as supplied by FPS as shown in
the FPS Console or through HKICL network and accounting totals to ensure receipt of
all FPS Transactions involving funds transfers; and/or

(c) if the Participant is not connected to the FPS Console or the Participant is not connected
to the HKICL network or unable to receive information relating to FPS Instructions ;

6.9.11 such Participant’s failure to report discrepancies for FPS Instructions as shown in the FPS
Console.

6.10 Indemnity

A Participant which delivers to HKICL FPS Instructions:

(a) will be responsible for the correctness of the information in the FPS Instructions;

(b) authorises HKICL to rely exclusively on the relevant information in the FPS Instructions
without making any other independent verification of such information; and

(c) indemnifies HKICL and MA against all liabilities and expenses incurred by either of them
arising out of or as a result of any error or discrepancy in the FPS Instructions.

6.11 Emergencies

6.11.1 In the event that communications between FPS and the HKICL network or between the HKICL
network and one or more of the Participants are halted, or if FPS or the HKICL network is
halted, or if some other emergency affects HKICL’s operation, FPS Instructions shall be
handled in accordance with the FPS Operating Procedures.
HKICL may, at its own discretion or under the instruction of MA:

(a) direct any, all or some of the Participants not to initiate FPS Instructions awaiting
resolution of the problem; and/or

(b) direct such other action as it may deem necessary or as required by MA.

6.11.2 During any such emergency all Participants should limit their communications through FPS and
with HKICL to those which are essential.

6.12 Payee Participants

No payee Participant shall be obliged to credit any funds received by it through FPS to its customer’s
account if the instructions for the funds transfer are incomplete or inaccurate.

## Page 33

Hong Kong Interbank Clearing Limited
Rules for Hong Kong Dollar Faster Payment System
Redacted version: August 2025 Page 30
Part VII Miscellaneous

7.1 Personal Data (Privacy) Ordinance, Cap. 486 of the Laws of Hong Kong

7.1.1 Each Participant represents to HKICL that:

(a) all Personal Data provided by it to HKICL:

(i) have been collected by lawful means; and

(ii) are accurate in all material respects so far as it is aware;

(b) in relation to Personal Data collected by it all necessary consents required from Data
Subjects have been obtained:

(i) to enable Personal Data to be used for the purpose of the operation of the
Clearing House and the FPS Facilities in accordance with these FPS Rules
including in particular the matching of Proxy IDs provided by the payer
Participant or, if applicable, the payer bank or payer-engaged financial
institution participating in a Cross-boundary Payment Service with the list of
suspicious Proxy IDs or other information provided by the law enforcement
agencies or informing the payer Participant or, if applicable, the payer bank
or payer-engaged financial institution participating in a Cross-boundary
Payment Service of the matching result in accordance with Rule 6.5.1.2(g);

(ii) to enable Personal Data to be transferred or delivered to any other person
(including person outside Hong Kong) to the extent necessary for the purpose
of the operation of the Clearing House and the FPS Facilities in accordance
with these FPS Rules; and

(iii) to enable HKICL to provide Personal Data to any party pursuant to any
obligation binding upon it under the Personal Data (Privacy) Ordinance (Cap.
486 of the Laws of Hong Kong);

(c) it has complied in all aspects with the provisions of the Personal Data (Privacy)
Ordinance (Cap. 486 of the Laws of Hong Kong); and

(d) use of the FPS Console and any equipment through which Participants gain access to
the FPS Console complies with all applicable data protection laws, codes of practices
and licences.

7.1.2 Each Participant confirms that the collection, use and retention of Personal Data by any
outsourcing party in relation to the operation of the Clearing House and the FPS Facilities
pursuant to these Rules comply with all relevant laws and regulations in Hong Kong.

7.2 Contracts (Rights of Third Parties) Ordinance, Cap. 623 of the Laws of Hong Kong

7.2.1 Save in respect of MA, a person who is not a party to these FPS Rules pursuant to Rule 2.7 shall
not have any rights to enforce or enjoy the benefit of any term or provision of these FPS Rules,
and the application of the Contracts (Rights of Third Parties) Ordinance (Cap. 623 of the Laws
of Hong Kong) and/or any comparable law in any jurisdiction giving to or conferring on third
parties the right to enforce or enjoy the benefit of any term or provision of these FPS Rules is
expressly excluded.

7.2.2 Any rights or benefits granted to MA under these FPS Rules are personal to MA and may not
be assigned or enforced by any person other than MA.

## Page 34

Hong Kong Interbank Clearing Limited
Rules for Hong Kong Dollar Faster Payment System
Redacted version: August 2025 Page 31
7.3 Law and Jurisdiction

7.3.1 These FPS Rules and the FPS Operating Procedures shall be governed by and construed in
accordance with the laws of the Hong Kong Special Administrative Region of the People’s
Republic of China.

7.3.2 The Courts of the Hong Kong Special Administrative Region of the People’s Republic of China
shall have jurisdiction to settle any disputes which may arise in connection with these FPS Rules
or the FPS Operating Procedures and HKICL and each Participa nt hereby submit to the
jurisdiction of such Courts. Proceedings may also be initiated in any other courts of competent
jurisdiction.

7.4 Effective Date

This revision of the FPS Rules has consolidated all amendments up to the date HKICL announces that
they will take effect and shall take effect from the same date. In the event of any inconsistency between
the version of the FPS Rules on HKICL’s website and any other version of the FPS Rules, the version
on HKICL’s website shall prevail.

Hong Kong Interbank Clearing Limited

Date: 31 August 2025
