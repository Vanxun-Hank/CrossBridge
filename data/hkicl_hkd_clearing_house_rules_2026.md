---
id: "hkicl_hkd_clearing_house_rules_2026"
title: "Hong Kong Dollar Clearing House Rules"
issuer: "Hong Kong Interbank Clearing Limited"
authority_level: "official_dev"
region:
  - "Hong Kong"
topic:
  - "CHATS"
  - "RTGS"
  - "payment systems"
source_url: "https://www.hkicl.com.hk/files/page_file/120/12213/HKD%20Clearing%20House%20Rules%20%28April%202026%29_redacted_clean.pdf"
document_url: ""
source_type: "PDF"
language: "en"
trust_tier: "official_dev"
country: "HK"
subdivision: "hk_sar"
agency: "HKICL"
crawl_frequency: "monthly"
publish_date: "2026-04-01"
effective_date: ""
demo_relevance: "high"
collected_at: "2026-05-26T19:04:06+00:00"
raw_file_path: "data/raw/crawl_hkicl_hkd_clearing_house_rules_2026.pdf"
extraction_status: "ok"
content_hash: "46dc3a76c30a25a8f8aaddd733a64a5e2886c216c4a5f898fcee6de0607cb8c5"
---

# Hong Kong Dollar Clearing House Rules

## Page 1

Hong Kong Dollar Clearing House Rules
Rainstorm Procedures
Typhoon Procedures
(Redacted Version)

Date : April 2026

This redacted version of the Hong Kong Dollar Clearing House Rules and Rainstorm Procedures and
Typhoon Procedures is a partially edited version of the main text of these documents and is made
available publicly for general information purposes only. It has been edited to remove information that
might compromise the security of the system if made available to the general public. For operational
purposes, Members of the Hong Kong Dollar Clearing House should refer to the full text of the Hong
Kong Dollar Clearing House Rules and Rainstorm Procedures and Typhoon Procedures. Although due
care has been taken to ensure that the information provided in this document is accurate and up-to-date,
Hong Kong Interbank Clearing Limited does not warrant that all, or a ny part of, the information
provided in it is up-to-date and accurate in all respects.

## Page 2

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page i

Amendment Summary

Amendment Effective Date

(a) Revised the following provisions to cater for the implementation of
CCPMPNet settlement run in HKD CHATS:
• Rule 1.6 Definitions
➢ CCP Instruction
➢ CCPMP Commencement
➢ CCPMPNet Payment Instruction (new)
➢ CCPMPNet Payment Instruction Value Forward Day (new)
➢ CCPMPNet Payment Instruction Value Today (new)
➢ CCPMPNet Optimiser Payment Instruction (new)
➢ CCPMPNet Optimiser Payment Instruction Value Forward Day
(new)
➢ CCPMPNet Optimiser Payment Instruction Value Today (new)
➢ CCPMPNet Settlement Run (new)
➢ CHATS Payment Instruction Value Forward Day
➢ CHATS Payment Instruction Value Today
➢ Pending Queue
• Rule 4.6
• Rule 6.3.16 (new)
• Rule 6.3.17 (new)
• Rule 6.7.5
• Schedule II Part III
➢ Heading
➢ paragraph 3
(b) Revised the following provisions to cater the normalisation of bulk
settlement runs under severe weather conditions:
• Rule 1.6 Definitions
➢ CHATS Bank Cut-off
➢ CHATS Customer Cut-off
➢ CHATS Value Date Cut-off
➢ Day D
• Rule 6.3.14.3(a)
• Rule 6.5.3
• Rule 7.1.1(a)
• Rule 7.2.1
• Rule 7.6.2.2.2 (renumbered from Rule 7.6.4.2.2)
• Schedule III Part IV paragraph 5(a)
• Schedule IV
• Rainstorm Procedures
• Typhoon Procedures
• Revised the numbering of the referenced provisions
(c) Revised the following provisions to cater for the decommissioning of
Autodebit and Autocredit Services:
• Rule 1.4.2.3 (removed)
• Rule 1.6 Definitions
➢ Autocredit (removed)
➢ Autodebit (removed)
➢ CLG Items
➢ ECG Items
➢ Returned Articles
• Rule 7.1.5(c)
• Rule 7.1.7
• Rule 7.2.1(a)
27 April 2026

## Page 3

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page ii

Amendment Effective Date

• Rule 7.2.1 (c)
• Rule 7.2.2 (a)
• Rule 7.2.2(b)
• Rule 7.3
• Rule 7.4.1
• Rule 7.4.1(b)
• Rule 7.4.1(d)
• Rule 7.6.1
• Rule 7.6.2 (removed)
• Rule 7.6.3 (removed)
• Rule 7.6.9 (renumbered from Rule 7.6.11)
• Schedule III Part III Section A paragraph 4
• Schedule III Part II Section C (removed)
• Schedule III Part II Section E (removed)
• Schedule IV
• Revised the numbering in various provisions

## Page 4

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026

TABLE OF CONTENT

PART I INTRODUCTION .............................................................................................................. 2
PART II CLEARING HOUSE, CLEARING FACILITIES AND HKICL ................................ 18
PART III SETTLEMENT ................................................................................................................ 24
PART IV MEMBERS ....................................................................................................................... 25
PART V REFUSAL/SUSPENSION OF CLEARING FACILITIES .......................................... 27
PART VI CHATS (OTHER THAN THE PROCESSING IN RESPECT OF ARTICLES) ....... 29
PART VII THE PROCESSING IN RESPECT OF ARTICLES .................................................... 55
PART VIII MISCELLANEOUS ......................................................................................................... 68
SCHEDULE I DEFAULT ARRANGEMENTS FOR ARTICLES (OTHER THAN OTC ITEMS,
JETCO ITEMS, SJET ITEMS AND CREDIT CARD ITEMS), CCASS OPTIMISER
PAYMENT INSTRUCTIONS, SCCASS OPTIMISER PAYMENT INSTRUCTIONS,
CHATS OPTIMISER PAYMENT INSTRUCTIONS AND CCPO INSTRUCTIONS70
SCHEDULE II CHATS, CCASS, CCPMP CUT-OFF AND END OF DAY CUT-OFF ....................... 74
SCHEDULE III CLEARING & SETTLEMENT OF ARTICLES, CCASS OPTIMISER PAYMENT
INSTRUCTIONS, SCCASS OPTIMISER PAYMENT INSTRUCTIONS, CHATS
OPTIMISER PAYMENT INSTRUCTIONS AND CCPO INSTRUCTIONS ............. 80
SCHEDULE IV INTEREST ADJUSTMENT SCHEME .......................................................................... 91
SCHEDULE V PROTOCOL ...................................................................................................................... 92
RAINSTORM PROCEDURES ...................................................................................................................... 93
TYPHOON PROCEDURES ........................................................................................................................... 94

## Page 5

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 2

Part I Introduction

1.1 Expressions used herein are defined below.

1.2 The Clearing House shall be the medium and the location available to Members for the exchange, sorting
and balancing of cheques in Hong Kong dollars and other negotiable instruments in Hong Kong dollars
drawn payable on Members, and GD Cheques in Hong Kong dollars drawn payable on GD Banks, and
for the processing of direct debits and credits, funds transfers, e-Cheques and other banking transactions
in each case in Hong Kong dollars through CHATS and which (i) in respect of debits and credits and
funds transfers are presented by or on behalf of Members or by MA; (ii) in respect of e-Cheques are (a)
presented by Members or collected on behalf of Members from e -Cheque Drop Box Users through the
e-Cheque Portal ; (b) presented in Guangdong Province (excluding Shenzhen) in the GD e -Cheque
Platform and collected by HKICL on behalf of GD Agent acting on behalf of the relevant GD Settlement
Centre; or (c) presented in Shenzhen , delivered to HKICL by GD Agent and collected by HKICL on
behalf of GD Agent acting on behalf of the relevant GD Settlement Centre and (iii) in respect of other
banking transactions are presented by or on behalf of Members. It is also the medium and location for
the operation of FPS through FPS Facilities in accordance with the FPS Rules and the FPS Operating
Procedures.

1.3 HKICL owns the Clearing House and manages and operates the Clearing House and the Clearing
Facilities.

1.4 HKICL has made these Rules, with the approval of MA and the Association, which will apply:

1.4.1 to Members who are members of the Association, generally;

1.4.2 to Members who are not members of the Association in relation to (this provision does not
apply to HKSCC, HKCC and SEOCH):

1.4.2.1 their participation in CHATS (other than the processing in respect of Articles);

1.4.2.2 their receiving ECG Items in respect of CCASS Items or OTC Items (this provision
does not apply to CLS Bank);

1.4.3 in relation to the clearing and settlement of GD Cheques (this provision does not apply to CLS
Bank and HKSCC, HKCC and SEOCH);

1.4.4 to HKSCC, HKCC and SEOCH in relation to their participation in CHATS (other than the
processing in respect of Articles save in respect of those as stipulated in the Operating
Procedures); and

1.4.5 in relation to payments by MA to Members, or by Members to MA.

1.5 Subject to the conditions specified in Schedule V, HKICL may from time to time amend these Clearing
House Rules as it may consider necessary or desirable with the prior approval of MA and the Association.
Any amendments made thereto shall become effective from the effective date(s) as stated in HKICL’s
prior notice to Members and the amended version will be posted onto HKICL’s website
www.hkicl.com.hk (which shall specify the effective date(s) for the amendments according to the notice).

1.6 Definitions

Articles” means Paper Cheques, ECG Items, JETCO Items, SJET Items and Credit Card Items.

“Association” means The Hong Kong Association of Banks.

“Authorized Institution” has the meaning given to that term in the Banking Ordinance (Cap. 155 of the Laws
of Hong Kong).

## Page 6

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 3

“Balance-triggered Balance Sweeping Transaction” means a transaction initiated by a Member manually or
generated by FPS automatically to debit or credit funds from or to the FPS Ledger Account of a Member through
FPS for transferring funds to or from the CHATS Ledger Account of the Member for the purpose of liquidity
management, other than a Transaction-triggered Balance Sweeping Transaction.

“BKANVM” means the bank account number validation module and related information provided to HKICL by
Members subscribing to the e -Cheque Drop Box Service to facilitate the validation of bank account numbers
registered in the e-Cheque Drop Box Service in accordance with the Operating Procedures.

“BKANVM API ” means the application programming interface which HKICL distributes to Members
subscribing to the e-Cheque Drop Box Service from time to time to facilitate the development of BKANVM.

“BOJ” means the Bank of Japan, which operates BOJ-NET JGB Services for transactions in Japanese
Government Bonds (“JGB”).

“BOJ DvP Payment Cut -off” means a time as announced by HKICL from time to time as such on a Working Day
after which all incoming BOJ DvP Payment Instructions on such Working Day will be rejected and HKICL will
only perform other related actions on such Working Day in accordance with the Operating Procedures.

“BOJ DvP Payment Instruction” means a payment instruction effected through CHATS as of the Working Day
on which BOJ-NET JGB Services is operational and the instruction is received by the Clearing House Computer
for payment against the transfer of securities held under BOJ-NET JGB Services.

“BOJ DvP Processing Window” means the time period between BOJ DvP Processing Window Open and BOJ
DvP Processing Window Close on a Working Day on which BOJ-NET JGB Services is operational in accordance
with the Operating Procedures.

“BOJ DvP Processing Window Open” means a time as announced by HKICL from time to time as such on a
Working Day from which BOJ -NET JGB Services will again be re -opened for the settlement of BOJ DvP
Payment Instructions on the Working Day immediately following BOJ DvP Processing Window Close.

“BOJ DvP Processing Window Close” means a time as announced by HKICL from time to time as such on a
Working Day after which the settlement of BOJ DvP Payment Instructions shall cease on such Working Day and
the related arrangements will only be performed on such Working Day as set out in the Operating Procedures.

“BOJ-NET JGB Services” means the BOJ-NET platform operated by the BOJ for JGB settlements with linkage
to the Clearing House Computer to enable real -time delivery versus payment for money settlement of JGB
transactions in Hong Kong dollars.

“BOJ-NET JGB Services Rules” means the rules, operation guides and manuals issued by the BOJ from time
to time in respect of JGB transactions as the same may be amended from time to time.

“Bulk Clearing Commitment” means the obligation of a Member to pay a Settlement Amount in a Bulk Clearing
Settlement Run as provided in these Clearing House Rules.

“Bulk Clearing Settlement Run” means a settlement run effected through CHATS for the settlement of Articles
on a bulk clearing and/or settlement basis as provided in these Clearing House Rules.

“Card Agent” means a Member who is appointed by a Credit Card Company to perform either or both of the
following functions: (a) to act as its agent bank to present the settlement file of its Credit Card Items to the
Clearing House for processing and receive the settlement completion report after completion of the Settlement
Process; and/or (b) to act as its agent bank to take up the settlement obligations of a Credit Card Member under
paragraph 5.1(a) of Part V of Schedule III . A Credit Card Company may, a t the same time, appoint more than
one Card Agent to act as its agent banks.

“CBCA” means the Central Bank Contingency Automation, a standardized automated system developed by CLS
Bank, to facilitate the secure uploading and downloading of message files to/from CLS Bank when the
communication link between the Clearing House Computer and the CLS System fails as described in Rule 6.9.4.

## Page 7

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 4

“CCASS” means the Central Clearing and Settlement System operated by HKSCC.

“CCASS Commencement” means the time notified by HKSCC to HKICL as being the time on each Working
Day at which CCASS is operational.

“CCASS End of Day Cut-off” means the earlier of (i) the time notified by HKSCC to HKICL as being the time
on each Working Day at which CCASS will reject all incoming validation requests from the Clearing House
Computer and perform other actions in relation to CCASS End of Day Cut -off Payment in accordance with
Schedule II Part II and (ii) CHATS Customer Cut-off.

“CCASS End of Day Cut -off Payment” means a CCASS Payment Instruction with such classification a s
determined by HKSCC and notified to HKICL from time to time and effected through CHATS between CCASS
Commencement and CCASS End of Day Cut-off.

“CCASS Interim Cut-off” means the earlier of (i) the time notified by HKSCC to HKICL as being the time on
each Working Day at which CCASS will reject all incoming validation requests from the Clearing House
Computer and perform other actions in relation to CCASS Interim Cut-off Payment in accordance with Schedule
II Part II and (ii) CHATS Customer Cut-off.

“CCASS Interim Cut -off Payment” means a CCASS P ayment Instruction with such classification as
determined by HKSCC and notified to HKICL from time to time and effected through CHATS between CCASS
Commencement and CCASS Interim Cut-off.

“CCASS Investor Items ” means ECG Items for clearing generated by CCASS in respect of investor account
holders and other money settlement instructions as may be determined by HKSCC from time to time.

“CCASS Items” means CCASS Investor Items, CCASS Participant Items , Special CCASS Items and SCCASS
Participant Items.

“CCASS Optimiser Payment Instruction ” means a payment instruction which is settled in accordance with
Rule 6.3.6 and includes a CCASS Optimiser Payment Instruction Value Today and CCASS Optimiser Payment
Instruction Value Forward Day.

“CCASS Optimiser Payment Instruction Value Forward Day ” means a payment instruction input by a
Member to the Clearing House Computer for the effecting of a CCASS Optimiser Payment Instruction for value
through CHATS as of the Supported Forward Day referred to in the payment instruction.

“CCASS Optimiser Payment Instruction Value Today ” means a payment instruction input by a Member to
the Clearing House Computer for the effecting of a CCASS Optimiser Payment Instruction for value through
CHATS as of the Working Day on which the instruction is received by the Clearing House Computer. For the
avoidance of doubt, if the instruction is received by the Clearing House Computer between a CHATS Value Date
Cut-off and the following CHATS Commencement, it will be deemed to be received on the Working Day
pertaining to that CHATS Commencement and value today shall be construed accordingly.

“CCASS Participant Items” means ECG Items for clearing generated by CCASS other than (i) CCASS Investor
Items, (ii) Special CCASS Items and (iii) SCCASS Participant Items , but including amendments to CCASS
Participant Items submitted by HKSCC to HKICL after the initial clearing process in accordance with Schedule
III.

“CCASS Payment Instruction ” means (i) an instruction effected through CHATS for payment against the
transfer by CCASS of securities held in CCASS, or (ii) any other payment instruction relating to a CCASS
transaction, which is to be settled in accordance with Rule 6.3.3 . In these Clearing House Rules, a CCASS
Payment Instruction can be a CCASS Interim Cut-off Payment or a CCASS End of Day Cut-off Payment.

“CCP Instruction ” means a payment instruction which is to be settled only if CCPMP confirms that a
corresponding payment ( “Corresponding Payment”) from the Receiving Member of that payment instruction
to the Sending Member in another relevant currency will be settled at the same time and includes a CCP
Instruction Value Today and a CCP Instruction Value Forward Day. For the avoidance of doubt, CCP Instruction
does not include a CCPMPNet Payment Instruction and a CCPMPNet Optimiser Payment Instruction.

## Page 8

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 5

“CCP Instruction Value Forward Day” means a CCP Instruction to effect a payment for value through CHATS
as of the Supported Forward Day referred to in the payment instruction.

“CCP Instruction Value Today” means a CCP Instruction to effect a payment for value through CHATS as of
the Working Day on which the instruction is received by the Clearing House Computer. For the avoidance of
doubt, if the instruction is received between a CCPMP Cut-off and the following CCPMP Commencement, it will
be deemed to be received on the Working Day of that CCPMP Commencement and value today shall be construed
accordingly.

“CCPMP” means the Cross Currency Payment Matching Processor which links up the Clearing House Computer,
and provides a payment versus payment (“PvP”) facility for foreign exchange transactions.

“CCPMP Commencement” means a time determined from time to time by MA by which CCPMP will again be
re-opened for processing CCP Instructions and CCPMPNet Payment Instructions on the Working Day
immediately following CCPMP Cut-off.

“CCPMP Cut-off” means the time on a Working Day specified as such in Schedule II Part III as varied pursuant
to Rule 6.9.1.

“CCPMPNet Payment Instruction” means a payment instruction input by a Member to the Clearing House
Computer for the effecting of a funds transfer through CHATS which is to be settled in the CCPMPNet Settlement
Run and includes a CCPMPNet Payment Instruction Value Today and a CCPMPNet P ayment Instruction Value
Forward Day.

“CCPMPNet Payment Instruction Value Forward Day” means a CCPMPNet Payment Instruction to effect a
payment for value through CHATS as of the Supported Forward Day referred to in the payment instruction.

“CCPMPNet Payment Instruction Value Today” means a CCPMPNet Payment Instruction to effect a payment
for value through CHATS as of the day of the CCPMP Commencement on the Working Day on which the
instruction is received by the Clearing House Computer. For the avoidance of doubt and in addition to Rule
6.3.16.1, if the instruction is received between a CCPMP Cut -off and the following CCPMP Commencement, it
will be deemed to be received on the Working Day of that CCPMP Commencement and value today shall be
construed accordingly.

“CCPMPNet Optimiser Payment Instruction” means a payment instruction input by a Direct Participant to
the Clearing House Computer which is to be settled in accordance with Rule 6.3.17 and includes a CCPMPNet
Optimiser Payment Instruction Value Today and a CCPMPNet Optimiser Payment Instruction V alue Forward
Day.

“CCPMPNet Optimiser Payment Instruction Value Forward Day” means a CCPMPNet Optimiser Payment
Instruction to effect a payment for value as of the Supported Forward Day referred to in the payment instruction.

“CCPMPNet Optimiser Payment Instruction Value Today” means a CCPMPNet Optimiser Payment
Instruction to effect a payment for value as of the day of the CHATS Commencement on the Working Day on
which the instruction is received by the Clearing House Computer. For the avoidance of doubt and in addition to
Rule 6.3.17.1, if the instruction is received between a CHATS Value Date Cut -off and the following CHATS
Commencement, it will be deemed to be received on the Working Day of that CHATS Commencement and value
today shall be construed accordingly.

“CCPMPNet Settlement Run” means a settlement run which is (i) effected through CHATS for the settlement
of CCPMPNet Payment Instructions and CCPMPNet Optimiser Payment Instructions on a net settlement basis
as provided in these Clearing House Rules, and (ii) effected only if the C learing House Computer confirms that
the corresponding CCPMPNet Settlement Runs (“Corresponding CCPMPNet Settlement Runs”) in all other
relevant currencies will be effected at the same time.

“CCPO Instruction” means a CCP Instruction which is settled in accordance with Rule 6.3. 9 and includes a
CCPO Instruction Value Today and a CCPO Instruction Value Forward Day.

## Page 9

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 6

“CCPO Instruction Value Forward Day” means a CCPO Instruction input by a Member to the Clearing House
Computer for value as of the Supported Forward Day referred to in the payment instruction.

“CCPO Instruction Value Today ” means a CCPO Instruction input by a Member to the Clearing House
Computer to effect a payment for value as of the Working Day on which the instruction is received by the Clearing
House Computer. For the avoidance of doubt, if the instruction is received between a CCPMP Cut -off and the
following CCPMP Commencement, it will be deemed to be received on the Working Day of that CCPMP
Commencement and value today shall be construed accordingly.

“CHATS” means the computer based Clearing House Automated Transfer System owned and operated in Hong
Kong by HKICL for (i) the automated electronic processing and settlement of funds transfers including credit and
debit transfers effected by MA directly in a Member’s CHATS Ledger Account as described in Rules 6.3. 10 to
6.3.13; (ii) the automated electronic processing and settlement of funds transfers by virtue of Special Posting or
End of Day Net Settlement; and (iii) the processing and settlement of inter-Member funds in respect of the clearing
and settlement of Articles.

“CHATS Bank Cut-off” means the time during a Working Day specified as such in Schedule II Part I paragraph
1 as varied pursuant to Rule 6.9.1.

“CHATS Commencement” means a time determined from time to time by HKICL by which the Clearing House
Computer will again be re -opened for the settlement of CHATS Transactions (other than CHATS Transactions
in respect of Articles) involving funds transfers on the Working Day immediately following CHATS Value Date
Cut-off.

“CHATS Customer Cut -off” means the time during a Working Day specified as such in Schedule II Part I
paragraph 1 as varied pursuant to Rule 6.9.1.

“CHATS Ledger Account” has the meaning given to it in the definition of “Settlement Account”.

“CHATS Optimiser Payment Instruction ” means a payment instruction which is settled in accordance with
Rule 6.3.5 and includes a CHATS Optimiser Payment Instruction Value Today and CHATS Optimiser Payment
Instruction Value Forward Day.

“CHATS Optimiser Payment Instruction Value Forward Day ” means a payment instruction input by a
Member to the Clearing House Computer for the effecting of a CHATS Optimiser Payment Instruction for value
through CHATS as of the Supported Forward Day referred to in the payment instruction.

“CHATS Optimiser Payment Instruction Value Today ” means a payment instruction input by a Member to
the Clearing House Computer for the effecting of a CHATS Optimiser Payment Instruction for value through
CHATS as of the Working Day on which the instruction is received by the Clearing House Computer. For the
avoidance of doubt, if the instruction is received between a CHATS Value Date Cut-off and the following CHATS
Commencement, it will be deemed to be received on the Working Day pertaining to that CHATS Commencement
and value today shall be construed accordingly.

“CHATS Payment Instruction ” means a CHATS Payment Instruction Value Today or a CHATS Payment
Instruction Value Forward Day.

“CHATS Payment Instruction Value Forward Day ” means an instruction including Mainland FX Payment
and Regional CHATS Payment (other than an instruction in respect of Articles, a CCASS Optimiser Payment
Instruction, SCCASS Optimiser Payment Instruction, CCASS Payment Instruction, CCP Instruction, CCPO
Instruction, CCPMPNet Payment Instruction, CCPMPNet Optimiser Payment Instruction, CHATS Optimiser
Payment Instruction , CLS Payment Instruction , BOJ DvP Payment Instruction and OTC Clear Payment
Instruction) inp ut by a Member to the Clearing House Computer for the effecting of a CHATS Payment
Instruction for value through CHATS as of the Supported Forward Day referred to in the payment instruction.

“CHATS Payment Instruction Value Today ” means an instruction including Mainland FX Payment and
Regional CHATS Payment (other than an instruction in respect of Articles, a CCASS Optimiser Payment
Instruction, SCCASS Optimiser Payment Instruction, CCASS Payment Instruction, CCP Instruction, CCPO
Instruction, CCPMPNet Payment Instruction, CCPMPNet Optimiser Payment Instruction, CHATS Optimiser

## Page 10

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 7

Payment Instruction , CLS Payment Instruction , BOJ DvP Payment Instruction and OTC Clear Payment
Instruction) input by a Member or generated or by virtue of a Special Posting or End of Day Net Settlement to
the Clearing House Computer for the effecting of a CHATS Payment Instruction for value through CHATS as of
the Working Day on which the instruction is received by the Clearing House Computer . For the avoidance of
doubt, if the instruction is received between a CHATS Value Date Cut -off and the following C HATS
Commencement, it will be deemed to be received on the Working Day pertaining to that CHATS Commencement
and value today shall be construed accordingly.

“CHATS Transactions” means transactions involving funds transfers effected through CHATS including, for
the avoidance of doubt (but without limitation), Regional CHATS Payments and the general administrative or
system messages transmitted through CHATS.

“CHATS Value Date Cut -off” means the time during a Working Day specified as such in Schedule II Part I
paragraph 1 as varied pursuant to Rule 6.9.1.

“China” means the Mainland of the People ’s Republic of China excluding for the purposes of these Clearing
House Rules the Hong Kong Special Administrative Region and the Maca o Special Administrative Region.

“Clearing Facilities” means all premises, personnel, machinery, equipment, facilities, software, operational and
processing systems, computer systems including CHATS and FPS, arrangements and procedures for or in relation
to the services provided by and the operation of the Clearing House.

“Clearing House” means the medium and the location owned, provided, operated and managed by HKICL which
is available to Members for the exchange, sorting and balancing of cheques in Hong Kong dollars and other
negotiable instruments in Hong Kong dollars drawn on Members, a nd GD Cheques, and for the processing of
direct debits and credits, funds transfers , e-Cheques and other banking transactions in each case in Hong Kong
dollars and which (i) in respect of debits and credits and funds transfers are presented by or on behalf of Members
or by MA; (ii) in respect of e-Cheques are (a) presented by Members or collected on behalf of Members from e -
Cheque Drop Box Users through the e-Cheque Portal; (b) presented in Guangdong Province (excluding Shenzhen)
in the GD e -Cheque Platform and collected by HKICL on behalf of GD Agent acting on behalf of the relevant
GD Settlement Centre; or (c) presented in Shenzhen, delivered to HKICL by GD Agent and collected by HKICL
on behalf of GD Agent acting on behalf of the relevant GD Settlement Centre and (iii) in respect of other banking
transactions are presented by or on behalf of Members. It is also the medium and location for the operation of
FPS through FPS Facilities in accordance with the FPS Rules and the FPS Operating Procedures.

“Clearing House Computer” means (i) the computer system of the Clearing House (a) to which Members may
connect to effect CHATS Transactions and other transactions through the Clearing House as the case may be via
the SWIFT network, (b) to which Members (except CLS Bank) may connect through the MBT in order to perform
administrative functions related to CHATS Transactions (other than initiating/receiving payment instructions) or
submit instructions relating to Special Posting transactions as stipulated in the Operating Procedures, (c) to which
CLS Bank connects its CLS System in order to effect CHATS Transactions and other transactions through the
Clearing House as the case may be, (d) to which OTC Clear connects its system in order to transmit OTC Clear
Debit Requests for the generation of OTC Clear Payment Instructions through the Clearing House and (e) to
which other computer systems may connect in order to effect CHATS Transactions and other transactions through
the Clearing House as the case may be; and (ii) other computer system(s) in respect of the Clearing House.

“Clearing House Rules ” or “Rules” means these Hong Kong Dollar Clearing House Rules in relation to the
operation of CHATS as amended from time to time by HKICL with prior approval of MA and the Association.

“CLG Items” means Paper Cheques, CCASS Investor Items and Special CCASS Items.

“CLS Bank” means CLS Bank International, an Edge Act corporation under Section 25A of the United States
Federal Reserve Act, as amended, and a Member which maintains a CHATS Ledger Account with MA.

“CLS Participant” means a Member that has subscribed to the CLS Bank -related Hong Kong dollars payment
service, and is eligible to send and receive CLS Bank-related payments to and from CLS Bank.

“CLS Pay-in” means a CLS Payment Instruction being sent from a CLS Participant to CLS Bank.

## Page 11

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 8

“CLS Pay-out” means a CLS Payment Instruction being sent from CLS Bank to a CLS Participant.

“CLS Payment Instruction” means a payment instruction input in favour of CLS Bank or in favour of a CLS
Participant and includes a CLS Payment Instruction Value Today and a CLS Payment Instruction Value Forward
Day.

“CLS Payment Instruction Value Forward Day” means an instruction input by a CLS Participant or CLS Bank
as the case may be, to the Clearing House Computer for the effecting of a CLS Payment Instruction for value
through CHATS as of the Supported Forward Day referred to in the payment instruction.

“CLS Payment Instruction Value Today” means an instruction input by a CLS Participant or CLS Bank as the
case may be, or by virtue of a Special Posting or End of Day Net Settlement (for CLS Pay -outs only) to the
Clearing House Computer for the effecting of a CLS Payment Instruction for value t hrough CHATS as of the
Working Day on which the instruction is received by the Clearing House Computer. For the avoidance of doubt,
if the instruction is received between a CHATS Value Date Cut -off and the following CHATS Commencement,
it will be deemed to be received on the Working Day pertaining to that CHATS Commencement and value today
shall be construed accordingly.

“CLS Service” means the continuous linked settlement service of CLS Bank.

“CLS System” means the computer hardware and software system used by CLS Bank to deliver the CLS Service,
which system links up with the Clearing House Computer.

“CMU” means the Central Moneymarkets Unit of the MA.

“Committee” means the Committee of the Association.

“Conditions” means the terms and conditions as applicable to each Member for the operation of Settlement
Accounts (including the CHATS Ledger Accounts and the FPS Ledger Accounts) as the Financial Secretary may
require in pursuance to Section 3(1A) or 3A(1) of the Exchange Fund Ordinance (Cap. 66 of the Laws of Hong
Kong).

“Credit Card Company” means Visa International Service Association, MasterCard International Incorporated
or UnionPay International Co., Ltd as the case may be and “Credit Card Companies” means Visa International
Service Association, MasterCard International Incorporated and Union Pay International Co., Ltd.

“Credit Card Member” means (a) a Member which is a member of a Credit Card Company; or (b) a Member
which acts as a settlement agent (for the purpose of Settlement Processes in respect of Credit Card Items) for a
Non-bank Card Member.

“Credit Card Items” means payment instructions for net settlement regarding transactions processed by a Credit
Card Company for its members, generated by a Credit Card Company or a Credit Card Company’s Card Agent(s),
as the case may be.

“crisis prevention measure” has the meaning given to that term in section 86 of the FIRO.

“Data Subject(s)” has the meaning given to that term in the PDPO.

“Day D” means a day on which an Article is presented to or deemed to be presented to and accepted by HKICL
for clearing and/or settlement as provided in these Clearing House Rules.

“Day D+1” means the Working Day immediately following Day D.

“Default Arrangement” means the default arrangements for Bulk Clearing Settlement Runs of Articles (other
than OTC Items, JETCO Items, SJET I tems and Credit Card Items), CCASS Optimiser Payment Instructions,
SCCASS Optimiser Payment Instruction s, CHATS Optimiser Payment Instructions and CCPO Instructions set
out in Schedule I as amended from time to time.

“default event provision” has the meaning given to that term in section 86 of the FIRO.

## Page 12

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 9

“Delayed Payment” means those funds transferred through CHATS (other than those funds transferred in respect
of Articles) which are credited to an account on a value date later than that specified in the relevant transfer or
payment details.

“Digital Signature” has the meaning given to it by section 2(1) of the Electronic Transactions Ordinance (Cap .
553 of the Laws of Hong Kong).

“Direct Credit Instruction ” means an instruction effected in real time by MA to credit a Member ’s CHATS
Ledger Account through CHATS to settle an obligation of MA to that Member and includes a Direct Credit
Instruction Value Today and a Direct Credit Instruction Value Forward Day.

“Direct Credit Instruction Value Forward Day” means a Direct Credit Instruction to effect a payment for value
through CHATS as of the Supported Forward Day referred to in the Direct Credit Instruction.

“Direct Credit Instruction Value Today ” means a Direct Credit Instruction input or generated after CHATS
Commencement and before End of Day Cut-off to effect a payment for value through CHATS as of the Working
Day on which the instruction is received by the Clearing House Computer.

“Direct Debit Instruction ” means an instruction effected in real time by MA to debit a Member ’s CHATS
Ledger Account through CHATS to settle an obligation of that Member to MA.

“Direct Debit Instruction Value Forward Day” means a Direct Debit Instruction to effect a payment for value
through CHATS as of the Supported Forward Day referred to in the Direct Debit Instruction.

“Direct Debit Instruction Value Today ” means a Direct Debit Instruction input or generated after CHATS
Commencement and before End of Day Cut-off to effect a payment for value through CHATS as of the Working
Day on which the instruction is received by the Clearing House Computer.

“ECG Items” means the various types of electronic payments to be cleared and settled through CHATS on a
bulk clearing basis as provided by these Clearing House Rules, including for the time being EPS Items, SEPS
Items, CCASS Items, OTC Items, MPF Items, E-bill Payments , e -Cheques and Returned Articles or Unpaid
Articles in respect thereof (but excluding JETCO Items, SJET Items and Credit Card Items).

“Electronic Media” means such electronic media for the delivery of information or images of items permitted
by virtue of the Operating Procedures to be delivered to and/or collected from the Clearing House pursuant to
these Clearing House Rules and, where the context admits, such format thereof as (in each case) may be specified
from time to time in the Operating Procedures.

“Electronic Record” has the meaning given to it by section 2(1) of the Electronic Transactions Ordinance (Cap.
553 of the Laws of Hong Kong).

“eMBT” means the terminal system enabling connection to the Clearing House Computer via the SWIFT network,
whereby a Member (except CLS Bank) may gain access to such terminal system through terminals located within
the premises of such Member (except CLS Bank). Access to the eMBT is for the purposes of a Member (other
than CLS Bank) performing administrative functions related to CHATS Transactions (other than
initiating/receiving payment instructions) or submitting instructions relating to Special Posting transactions as
stipulated in the Operating Procedures.

“End of Day Cut-off” means the time during a Working Day after which the settlement of transactions including
funds transfers initiated by MA shall cease and the related arrangements as set out in Schedule II, Part IV or as
from time to time determined (and/or amended) by MA.

“End of Day Net Settlement ” means a contingency arrangement to facilitate the settlement of all eligible
transactions as stipulated in the Operating Procedures which may be triggered if (a) the computer system of the
Clearing House is not functional in both HKICL’s production and backup data centres for a prolonged period,
and (b) the conditions as stipulated in the Operating Procedures are satisfied. The decision to trigger such
arrangement shall be made in accordance with the Operating Procedures and wit h the prior approval of HKICL
and MA.

## Page 13

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 10

“EPSCO” means EPS Company (Hong Kong) Limited.

“EPS Items” means ECG Items for clearing generated by EPSCO which are presented on Day D and settled on
Day D+1.

“Extreme Conditions” means the existence of extreme conditions as announced by the Government of the Hong
Kong Special Administrative Region that arise from a super typhoon or other natural disaster of a substantial
scale which caused serious disruption of public transport se rvices, extensive flooding, major landslides, large -
scale power outage or any other adverse conditions.

“E-bill Payments” means electronic payments covering bill payments and charity donation payments which are
cleared and settled on the same Working Day among Members referred to in Rule 7.6. 2.

“e-Cheque” means a cheque, including a cashier ’s order, issued in the form of an Electronic Record with an
image of the front and back of the cheque or cashier ’s order, and, in the case of a cheque (other than cashier ’s
order), bears the Digital Signatures of the account holder(s) and/or authorized signer(s) and the payer bank
Member; and, in the case of a cashier’s order, bears the Digital Signatures of the payer bank Member.

“e-Cheque Drop Box” means an electronic drop box operated by HKICL, provided (i) on a website accessible
through a supported internet browser and/or (ii) on a mobile application, and/or (iii) through a direct application
interface or any other similar facilities, which accepts presentment of e-Cheques.

“e-Cheque Drop Box Service” means the service of providing the e-Cheque Drop Box by HKICL.

“e-Cheque Drop Box User ” means an individual or entity who registers an e -Cheque Drop Box account with
one or more payee bank accounts for the purpose of presenting e -Cheque(s). For the avoidance of doubt, this
term includes an e -Cheque Drop Box User who registers an e -Cheque Dro p Box account with a payee bank
account (i) in his/her/its sole name, (ii) in the joint names of the e -Cheque Drop Box User and another person or
(iii) in the name of another person.

“e-Cheque Payments” means electronic payments of e -Cheques generated by HKICL on Day D in accordance
with Rule 7.6.8.2.

“e-Cheque Portal” means a computer system which is part of the Clearing Facilities operated by HKICL to
support the e-Cheque Presentment Service and performs functions in accordance with the Operating Procedures.

“e-Cheque Presentment Service” means the e-Cheque Drop Box Service, the Payee Bank Presentment Service
and any other eligible e-Cheque presentment channel(s) provided by HKICL.

“Final Cut-off time” means the final cut-off time for settlement in a Bulk Clearing Settlement Run.

“FIRO” means the Financial Institutions (Resolution) Ordinance (Cap. 628 of the Laws of Hong Kong).

“FPS” has the meaning given to that term in the FPS Rules.

“FPS Console” has the meaning given to that term in the FPS Rules.

“FPS Facilities” has the meaning given to that term in the FPS Rules.

“FPS Ledger Account” has the meaning given to it in the definition of “Settlement Account”.

“FPS Operating Procedures” has the meaning given to that term in the FPS Rules.

“FPS Rules” means the rules for Hong Kong Dollar Faster Payment System as amended from time to time by
HKICL with prior approval of MA.

“FPS Transactions” means transactions involving funds transfers effected through FPS as defined in the FPS
Rules.

## Page 14

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 11

“GD Agent” means the Member(s) appointed or authorised by the People ’s Bank of China, Guangzhou Branch
or Shenzhen Central Sub -branch (and notified by it to MA and HKICL) to act as the agent of the relevant GD
Settlement Centre and the relevant GD Banks in relation to the clearing and settlement of (i) GD Cheques and
Paper Cheques drawn on Members which are presented in Guangdong Province ( including Shenzhen) ; (ii) e-
Cheques drawn on Members which are presented in Guangdong Province (excluding Shenzhen) in the GD e -
Cheque Platform and collected by HKICL on behalf of GD Agent acting on behalf of the relevant GD Settlement
Centre; and (iii) e-Cheques drawn on Members which are presented in Shenzhen , delivered to HKICL by GD
Agent and collected by HKICL on behalf of GD Agent acting on behalf of the relevant GD Settlement Centre .
The Member who is acting as a GD Agent shall cease to be the GD Agent for the purposes of these Clearing
House Rules as and when (a) such Member shall, for whatever reason, cease to be so appointed or authorised by
the People’s Bank of China, Guangzhou Branch or as the case may be Shenzhen Central Sub -branch, (the
“appointing branch”), and (b) a successor GD Agent has been appointed or authorised by the appointing branch
and notified by such branch to MA and HKICL.

“GD Banks ” means bodies corporate which are authorised or licensed under applicable law in Guangdong
Province in relation to the clearing of GD Cheques and, Paper Cheques and e-Cheques drawn on Members relating
to the Guangdong Province, to offer and operate current accounts from which withdrawals, and into which
deposits, can be made by use of cheques and e-Cheques.

“GD Cheques” means Paper Cheques in Hong Kong dollars, in the form(s) from time to time specified by HKICL,
and drawn on GD Banks.

“GD e-Cheque Platform” means an electronic drop box operated by Guangzhou Electronic Banking Settlement
Centre which collects e-Cheques drawn on, and for presentation to, via HKICL on behalf of GD Agent, Members
on behalf of GD Banks and the relevant GD Settlement Centre.

“GD e-Cheque Platform User” means an individual or entity who registers a GD e -Cheque Platform account
with one or more accounts at GD Banks for the purpose of presenting e -Cheque(s). For the avoidance of doubt,
this term includes a GD e-Cheque Platform User who registers a GD e-Cheque Platform account with a GD Bank
account (i) in his/her/its sole name, (ii) in the joint names of the GD e-Cheque Platform User and another person
or (iii) in the name of another person.

“GD Settlement Centre” means the Guangzhou Electronic Banking Settlement Centre, or as the case may be
the Shenzhen Financial Electronic Settlement Center Co., Ltd, or its respective successor as recognised by the
People’s Bank of China and “relevant GD Settlement Centre” means: (i) in respect of GD Cheques and, Paper
Cheques and e-Cheques drawn on Members relating to Guangdong Province (excluding Shenzhen), Guangzhou
Electronic Settlement Centre; and (ii) in respect of GD Cheques and, Pa per Cheques and e -Cheques drawn on
Members relating to Shenzhen, Shenzhen Financial Electronic Settlement Center Co., Ltd.

“Group A Members ” means Members who themselves are able to produce images in accordance with the
Operating Procedures for the clearing of Paper Cheques excluding GD Cheques.

“Group B Members” means Members other than Group A Members who make arrangements with HKICL in
accordance with the Operating Procedures for HKICL to produce images for the clearing of Paper Cheques
excluding GD Cheques on their behalf.

“group company” has the meaning given to that term in section 2 of the FIRO.

“Held Funds” means in respect of a BOJ DvP Payment Instruction, a hold up to the relevant transaction amount
applied by HKICL to the Sending Member’s CHATS Ledger Account pursuant to Rule 6.3.15.2.

“HKCC” means HKFE Clearing Corporation Limited, a wholly-owned subsidiary of HKEX that is incorporated
in Hong Kong and recognised by the Securities and Futures Commission under Section 37(1) of the Securities
and Futures Ordinance (Cap. 571 of the Laws of Hong Kong) as a recognised clearing house, and a Member
which maintains a CHATS Ledger Account with MA.

“HKEX” means Hong Kong Exchanges and Clearing Limited.

## Page 15

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 12

“HKICL” means Hong Kong Interbank Clearing Limited.

“HKSCC” means Hong Kong Securities Clearing Company Limited, a wholly-owned subsidiary of HKEX that
is incorporated in Hong Kong and recognised by the Securities and Futures Commission under Section 37(1) of
the Securities and Futures Ordinance (Cap. 571 of the Laws of Hong Kong) as a recognized clearing house, and
a Member which maintains a CHATS Ledger Account with MA.

“iMBT” means the terminal system enabling connection to the Clearing House Computer via the HKICL network
and/or internet, whereby a Member (except CLS Bank) may connect to such terminal system through terminals
located within the premises of such Member (except CLS Bank) according to the security requirements provided
by HKICL from time to time. The iMBT (i) is to be used by a Member (other than CLS Bank) as a contingency
in case such Member is unable to connect to the Clearing House Computer through the eMBT via the SWIFT
network for the purposes of performing administrative functions related to CHATS Transactions (other than
initiating/receiving payment instructions) or submitting instructions relating to Special Posting transactions as
stipulated in the Operating Procedures and (ii) will only be provided to the Member concerned where it is enabled
by HKICL upon request of such Member.

“inoperable” in relation to all or part of the Clearing Facilities, means all or part of the Clearing Facilities
becoming incapable of normal operation or in the opinion of HKICL difficult to operate normally by reason of (i)
a system failure; (ii) non -availability of HKICL’s production or backup contingency sites; (iii) circumstances
affecting the staff of HKICL or Members or any other relevant third parties rendering it difficult or impossible to
operate part or all of the Clearing Facilities normally; (iv) a requirement from the Government of the Hong Kong
Special Administrative Region or MA; or (v) any other unforeseen disruption scenarios rendering it difficult or
impossible to operate part or all of the Clearing Facilities normally.

“Interbank Intraday Liquidity Facility” or “IILF” means a liquidity facility to facilitate the provision of
liquidity from Liquidity Providers to Liquidity Consumers in accordance with Rule 6.14.

“Interest Adjustment Rate” means the daily HKD Overnight Index Average (HONIA) rate published by TMA.

“Interest Adjustment Scheme” means the Interest Adjustment Scheme provided in Rule 7.3 as amended from
time to time.

“JETCO” means Joint Electronic Teller Services Ltd.

“JETCO Items” means payment instructions for net settlement regarding transactions processed by JETCO for
its members, generated by JETCO which are presented on Day D and settled on Day D + 1.

“JETCO Members” means Members which are members of, or which act as agent (for the purpose of Settlement
Processes in respect of JETCO Items and SJET Items) for members of, JETCO.

“Liquidity Consumer” means a Member who registers with HKICL to borrow liquidity through the IILF from
a single Liquidity Provider in accordance with Rule 6.14.

“Liquidity Provider” means a Member who registers with HKICL to provide liquidity through the IILF to one
or more Liquidity Consumer(s) in accordance with Rule 6.14.

“MA” means the Monetary Authority appointed under the Exchange Fund Ordinance (Cap. 66 of the Laws of
Hong Kong).

“Macau” means Macao Special Administrative Region of the People’s Republic of China.

“Mainland FX Payment ” means a payment instruction relating to China’s foreign exchange transaction (as
identified by a designated payment code for such transaction) input by a Member who has registered as a user
group member, effected through CHATS.

“MBT” means eMBT and/or iMBT as appropriate.

“MC Agent” means the Member appointed or authorised by the MC Settlement Centre (and notified by it to MA

## Page 16

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 13

and HKICL) to act as the agent of the MC Settlement Centre in relation to the clearing and settlement of Paper
Cheques (which are drawn on Members) presented to MC Banks for payment. The Member who is acting as the
MC Agent shall cease to be the MC Agent for the purposes of these Clearing House Rules as and when (a) such
Member shall, for whatever reason, cease to be so appointed or authorised by the MC Settlement Centre, and (b)
a successor MC Agent has been appointed or authorised by the MC Settlement Ce ntre and notified by it to MA
and HKICL.

“MC Banks” means banks in Macau in relation to the collection of Paper Cheque s drawn on Members.

“MC Settlement Centre” means Bank of China, Macau Branch or any successor clearing operator of the clearing
house of Monetary Authority of Macao as recognised by Monetary Authority of Macao.

“Members” means the licensed banks, restricted licence banks, CLS Bank, HKSCC, HKCC and SEOCH which
in each case have agreed with HKICL to be bound by these Clearing House Rules. For the avoidance of doubt,
this term does not include a branch or the head office of the licensed banks and restricted licence banks located
outside Hong Kong.

“Monetary Authority of Macao” means the Monetary Authority of Macau (Autoridade Monetaria de Macau).

“MPF Items” means ECG Items for clearing submitted to HKICL by CMU members who are trustees of MPF
Schemes in respect of payment instructions from one Member to another which are presented on Day D and
settled on Day D+1.

“MPF Schemes” means provident fund schemes registered under the Mandatory Provident Fund Schemes
Ordinance (Cap. 485 of the Laws of Hong Kong).

“Non-bank Card Member ” means a member of a Credit Card Company who is not a Member, whose Credit
Card Items are settled through a Member and “its Non-bank Card Members” means, in relation to a Member, the
Non-bank Card Members whose Credit Card Items are agreed between such Member and such Non-bank Card
Members to be settled through such Member’s CHATS Ledger Account.

“Non-Clearing Day” means a Working Day in relation to which HKICL has given a notice pursuant to Rule 5.8,
5.9 or 5.10 to the effect that all or part of the Clearing Facilities will be suspended.

“Normal Queue” means a queue of Direct Debit Instructions already input by or generated by MA and/or the
queue mode specified by a Member for a n applicable payment instruction in relation to which such payment
instruction (subject to Rule 6.3.1. 5, Rule 6.3.3.5, Rule 6.3.4.4, Rule 6.3.8.5, Rule 6.3.10.5, Rule 6.3.14.3(f) and
Rule 6.3.15.5) or Direct Debit Instruction will be settled immediately if the available balance of the Member in
its CHATS Ledger Account is sufficient to meet the payment instruction or Direct Debit Instruction where the
payment instruction or Direct Debit Instruction is first in priority in the queue . Save in respect of OTC Clear
Payment Instruction s (whereby initial queue mode is determined according to the criteria stipulated in the
Operating Procedures), the Clearing House Computer will treat the payment instruction as Normal Queue if the
queue mode is not specified in an applicable payment instruction.

“Operating Procedures” means the operating procedures issued by HKICL pursuant to Rule 2.5 and for the time
being in force.

“OTC Clear” means OTC Clearing Hong Kong Limited , a subsidiary of HKEX that is incorporated in Hong
Kong and recognised by the Securities and Futures Commission under Section 37(1) of the Securities and Futures
Ordinance (Cap. 571 of the Laws of Hong Kong) as a recognised clearing house .

“OTC Clear Debit Request” means a request transmitted or delivered by OTC Clear to the Clearing House
Computer for the generation of an OTC Clear Payment Instruction for the effecting of a payment through CHATS
to settle an obligation of a Member or one of its customers which is not a Member to OTC Clear by paying into
the CHATS Ledger Account of a bank Member designated by OTC Clear in accordance with the Operating
Procedures as of the Working Day referred to in the request which can be the day on which the request is received
by the Clearing House Computer or any Supported Forward Day.

“OTC Clear Payment Instruction” means an OTC Clear Payment Instruction Value Today or an OTC Clear

## Page 17

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 14

Payment Instruction Value Forward Day.

“OTC Clear Payment Instruction Value Forward Day” means an instruction generated by CHATS upon
receipt of an OTC Clear Debit Request transmitted by OTC Clear for the effecting of a payment to settle an
obligation of a Member or one of its customers which is not a Member to OTC Clear by paying into the CHATS
Ledger Account of a bank Member designated by OTC Clear in accordance with the Operating Procedures for
value through CHATS as of the Supported Forward Day referred to in the OTC Clear Debit Request.

“OTC Clear Payment Instruction Value Today” means an instruction generated by CHATS upon receipt of
an OTC Clear Debit Request transmitted by OTC Clear or delivered by OTC Clear by virtue of Special Posting
for the effecting of a payment to settle an obligation of a Member or one of its customers which is not a Member
to OTC Clear by paying into the CHATS Ledger Account of a bank Member designated by OTC Clear in
accordance with the Operating Procedures for value through CHATS as of the Working Day on which the OTC
Clear Debit Request is received by the Clearing House Computer.

“OTC Items” means ECG Items for clearing generated and submitted by OTC Clear in respect of the money
clearing and settlement of transactions between Members which contain instructions for the money clearing and
settlement of the Hong Kong dollar portion of Hong Kong dollar and US dollar payment transactions (i.e.
“OTCCHU Items”) to be settled in accordance with Part VI of Schedule III.

“Paper Cheques” means paper cheques, demand drafts, cashier’s orders, dividend warrants, remittance advices,
travellers’ cheques, gift cheques and negotiable instruments drawn on Members who are members of the
Association to be cleared and settled through CHATS on a bulk clearing basis as provided by these Clearing
House Rules, and includes GD Cheque s; and where the context so admits includes the front and reverse of such
documents and for the avoidance of doubt excludes e-Cheques.

“Payee Bank Presentment Service ” means a service other than the e -Cheque Drop Box Service provided to
payee bank Members to facilitate the presentment of e -Cheques which they have collected through their own
means including through the internet banking system.

“PDPO” means the Personal Data (Privacy) Ordinance (Cap. 486 of the Laws of Hong Kong).

“Pending Queue” means the queue mode specified by a Member for a payment instruction in relation to which
such payment instruction (save as provided in Rule 6.3.1. 5, Rule 6.3.3.5, Rule 6.3.4.4, Rule 6.3.8.5, Rule
6.3.14.3(f) and Rule 6.3.15.5) will not at any time be settled even if the available balance of the Member in its
CHATS Ledger Account is sufficient to meet the payment instruction. Such payment instruction (save as
provided in Rule 6.3.1.5, Rule 6.3.3.5, Rule 6.3.4.4, Rule 6.3.8.5, Rule 6.3.14.3(f) and Rule 6.3.15.5) will remain
in the Pending Queue until (a) it is automatically transferred by the Clearing House Computer to the Normal
Queue after the time stipulated in the Operating Procedures , (b) it is cancelled by the Member or (c) it is
transferred by the Member to the Normal Queue. For the avoidance of doubt, the Pending Queue is not applicable
to (a) a Direct Debit Instruction input or generated by MA, (b) a CHATS Optimiser Payment Instruction, (c) a
CCASS Optimiser Payment Instruction , (d) a SCCASS Optimiser Payment Instruction , (e) a CCPO Instruction,
(f) a CCPMPNet Payment Instruction or (g) a CCPMPNet Optimiser Payment Instruction .

“People’s Bank of China” means People’s Bank of China acting as the central bank of the People’s Republic of
China pursuant to the Law of the People’s Republic of China on the People’s Bank of China promulgated by the
National People’s Congress on 18 March 1995.

“Personal Data” has the meaning given to that term in the PDPO.

“PSSVFO” means the Payment Systems and Stored Value Facilities Ordinance (Cap. 584 of the Laws of Hong
Kong).

“Rainstorm Procedures” means the Rainstorm Procedures determined by HKICL and for the time being in force.

“Receiving Member” means a Member which receives a credit transfer (other than credit transfers in respect of
Articles) which has been effected through CHATS.

“Regional CHATS Payments ” means payment instructions relating to cross -border transactions (as identified

## Page 18

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 15

by designated payment codes for such transactions) input by a Member in favour of a Service Provider (which,
for the avoidance of doubt, may include that Member), effected through CHATS.

“Returned Articles” means, in respect of E-bill Payments, Articles which cannot be processed for any reason as
stipulated in the Operating Procedures or for any other reasons which make it impossible for a direct credit to be
credited to an account.

“RTGS Liquidity Optimiser ” means a settlement mechanism allowing simultaneous gross settlement of
selected CHATS Transactions in accordance with Rule 6.13.

“SCCASS Optimiser Payment Instruction ” means a payment instruction which is settled in accordance with
Rule 6.3.7 and includes a SCCASS Optimiser Payment Instruction Value Today and SCCASS Optimiser Payment
Instruction Value Forward Day.

“SCCASS Optimiser Payment Instruction Value Forward Day ” means a payment instruction input by a
Member to the Clearing House Computer for the effecting of a SCCASS Optimiser Payment Instruction for value
through CHATS as of the Supported Forward Day referred to in the payment instruction.

“SCCASS Optimiser Payment Instruction Value Today ” means a payment instruction input by a Member to
the Clearing House Computer for the effecting of a SCCASS Optimiser Payment Instruction for value through
CHATS as of the Working Day on which the instruction is received by the Clearing House Computer . For the
avoidance of doubt, if the instruction is received by the Clearing House Computer between a CHATS Value Date
Cut-off and the following CHATS Commencement, it will be deemed to be received on the Working Day
pertaining to that CHATS Commencement and value today shall be construed accordingly.

“SCCASS Participant Items” means ECG Items for clearing generated by CCASS which are presented and
settled on Day D including (i) amendments to SCCASS Participant It ems submitted by HKSCC to HKICL after
the initial clearing process and (ii) further amendments to SCCASS Participant Items submitted by Members to
HKSCC after the settlement of SCCASS Participant Items in accordance with Schedule III.

“Security and Anti-fraud Requirements” refers to the set of requirements on endpoint security measures for
combatting payment fraud as specified by HKICL and amended by HKICL as and when necessary and notified
to Members from time to time.

“Sending Member” means a Member which initiates a credit transfer (other than credit transfers in respect of
Articles) through CHATS.

“SEOCH” means The SEHK Options Clearing House Limited, a wholly -owned subsidiary of HKEX that is
incorporated in Hong Kong and recognised by the Securities and Futures Commission under Section 37(1) of the
Securities and Futures Ordinance (Cap. 571 of the Laws of Hong Kong) as a recogni sed clearing house , and a
Member which maintains a CHATS Ledger Account with MA.

“SEPS Items” means ECG Items for clearing generated by EPSCO which are presented and settled on Day D .

“Service Provider” means a Member who registers with HKICL as such and authorises HKICL to provide its
correspondent banks’ information in accordance with Rule 6.8 to enable Members to effect Regional CHATS
Payments through CHATS to that Member for its onward transmission to the correspondent bank designated by
the relevant Members.

“Settlement Account” means the account maintained by a Member with MA as provided in Rule 3.1.1 for the
purpose of settlement of payments through CHATS or FPS which shall comprise two separate ledger accounts
with separate account balances as follows: (i) the “CHATS Ledger Account” for the purpose of settlement of
payments by or to the Member through CHATS and (ii) the “FPS Ledger Account” for the purpose of settlement
of payments by or to the Member through FPS and for the purpose of conducting Balance -triggered Balance
Sweeping Transactions and Transaction-triggered Balance Sweeping Transactions, and all references to payment
to or by the CHATS Ledger Account or to or by the FPS Ledger Account shall refer to payments to or by the
Settlement Account which shall be credited or debited to the relevant Member’s CHATS Ledger Account or the
FPS Ledger Account (as the case may be).

## Page 19

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 16

“Settlement Amount” means the net amount payable to or payable by a Member in a Bulk Clearing Settlement
Run including the net settlement balance payable to or payable by it for the Articles to be settled in the Bulk
Clearing Settlement Run concerned together with the amount of any interest adjustment payable or receivable
under the Interest Adjustment Scheme in respect of the Bulk Clearing Settlement Run concerned and, depending
on the context, includes a Re-Settlement Amount as defined in Schedule I, a net amount payable to or payable by
a JETCO Member in a settlement of JETCO Items or SJET Items as provided for in Part IV of Schedule III, a net
amount payable to or payable by a Member in a settlement of Credit Card Items as provided for in Part V of
Schedule III and a net amount payable to or payable by a Member in a settlement of OTC Items as provided for
in Part VI of Schedule III. In relation to a GD Agent, the Settlement Amount includes the amounts payable to or
payable by the relevant GD Banks. In relation to the MC Agent, the Settlement Amount includes the amounts
payable to the relevant MC Banks.

“Settlement Hold” means a hold or earmarking of funds, in an amount equal to the relevant debit Settlement
Amount, in the CHATS Ledger Account of a Member for the debit Settlement Amount payable by it in a Bulk
Clearing Settlement Run as from the commencement of a Settlement Process as provided in section J of Part III
of Schedule III, Clauses 3 and 4 of Part IV of Schedule III and Clause 3 of Part V of Schedule III.

“Settlement Process” means the process of debiting and crediting the CHATS Ledger Accounts of the Members
for purposes of settlement of their respective Settlement Amounts in a Bulk Clearing Settlement Run and,
depending on the context, includes a Re -Settlement as defined in Schedule I, a settlement of JETCO Items or
SJET Items as provided for in Part IV of Schedule III , a settlement of Credit Card Items as provided for in Part
V of Schedule III and a settlement of OTC Items as provided for in Part VI of Schedule III.

“SJET Items” means payment instructions for net settlement regarding transactions processed by JETCO for its
members which are presented and settled on Day D.

“Special CCASS Items ” means ECG Items for clearing generated by CCASS in respect of the refund monies
for electronic initial public offering (“eIPO”) and other money settlement instructions as may be determined by
HKSCC from time to time.

“Special Posting” means a contingency arrangement to handle the situation w here the computer of any of the
Members, OTC Clear or the Clearing House Computer has failed to connect to SWIFT for delivery of CHATS
transactions. The decision to trigger such arrangement shall be made at the request of the Member , OTC Clear
or HKICL subject to the relevant approval (s) being sought in accordance with the provisions as set out in the
Operating Procedures. This contingency arrangement is not applicable to payment instructions valued on any
Supported Forward Day or to OTC Clear Debit Requests which request generation of OTC Clear Payment
Instructions valued on any Supported Forward Day.

“Supported Forward Day ” means in respect of any instruction or OTC Clear Debit Request a Working Day
referred to in the instruction or the OTC Clear Debit Request which is within 12 calendar days of the System Date
on which the instruction or the OTC Clear Debit Request is received by the Clearing House Computer and
“Supported Forward Days” means in respect of any instruction or OTC Clear Debit Request all Working Days
within 12 calendar days of the System Date on which the instruction or the OTC Clear Debit Request is received
by the Clearing House Computer.

“SWIFT” means the Society for Worldwide Interbank Financial Telecommunication.

“System Date ” means the date adopted by the Clearing House Computer (other than for the clearing and
settlement of Articles), such that immediately after the CHATS Value Date Cut-off on a Working Day, the System
Date will become the date of the next Working Day.

“TMA” means the Treasury Markets Association which is a company limited by guarantee incorporated under
the Companies Ordinance (Cap. 622 of the Laws of Hong Kong).

“Transaction-triggered Balance Sweeping Transaction” means a transaction generated by FPS automatically
in order to transfer funds from the CHATS Ledger Account of a Member to the FPS Ledger Account of that
Member through FPS for the purpose of settlement of outstanding direct debit transactions effected through FPS.
For the avoidance of doubt, this term does not include a Balance-triggered Balance Sweeping Transaction.

## Page 20

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 17

“Typhoon Procedures” means the Typhoon Procedures determined by HKICL and for the time being in force.

“Unpaid Articles” means Articles returned unpaid from the Clearing House (excluding JETCO Items , SJET
Items, Credit Card Items, CCASS Participant Items , E-bill Payments, Returned Articles of E -bill Payments,
SCCASS Participant Items and OTC Items).

“Working Day” means (i) in respect of settlement of BOJ DvP Payment Instructions, a day other than a Saturday,
a general holiday as specified in the General Holidays Ordinance (Cap. 149 of the Laws of Hong Kong) and any
other day on which BOJ -NET JGB Services does not operate; and (ii) in any other case, a day other than a
Saturday and a general holiday as specified in the General Holidays Ordinance (Cap. 149 of the Laws of Hong
Kong).

1.7 HKICL has entered into a Protocol with MA and the Association in the substantive terms set out in
Schedule V to provide for the manner in which HKICL will exercise certain of its powers under these
Clearing House Rules. All Members accept that neither MA nor the Association incurs any duty or
liability to them in connection with the exercise or non -exercise of any of HKICL’s powers under the
Protocol.

1.8 Interpretation

Unless the context otherwise requires:

(a) a word or expression defined in these Clearing House Rules and the Schedules hereto bears the
defined meaning; terms defined in these Clearing House Rules shall bear the same meaning
when used in the Schedules;

(b) where a word or expression is given a particular meaning, other parts of speech and grammatical
forms of that word or expression have a corresponding meaning;

(c) a person includes individuals, bodies corporate (wherever and howsoever incorporated),
unincorporated associations and partnerships;

(d) a person includes its successor;

(e) reference to the singular includes the plural and vice versa;

(f) reference to one gender includes all genders;

(g) “including” and similar expressions are not words of limitation;

(h) reference to a group or thing includes any part thereof;

(i) headings are for convenience only and do not affect interpretation.

## Page 21

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 18

Part II Clearing House, Clearing Facilities and HKICL

2.1 Clearing House

No Member shall use or provide in Hong Kong any facilities for clearing of cheques and other negotiable
instruments in Hong Kong dollars drawn on Members, and GD Cheque s in Hong Kong dollars drawn
payable on GD Banks, and for processing of direct debits and credits, funds transfers , e-Cheques and
other banking transactions in each case in Hong Kong dollars other than the Clearing House and Clearing
Facilities provided by HKICL (either directly or through a sub -contractor). Each Member shall be
entitled to the use of the Clearing House and the Clearing Facilities subject to the provisions of these
Clearing House Rules, the Conditions and any agreement between that Member and MA.

2.2 Location

The Clearing House shall be located at such place in Hong Kong as shall be notified from time to time
by HKICL to the Members.

2.3 Responsibility for the Clearing House and the Clearing Facilities

2.3.1 HKICL shall, subject to the provisions of these Clearing House Rules and in accordance with
the Operating Procedures, provide, manage and operate the Clearing House and the Clearing
Facilities and make available the services of the Clearing House and the Clearing Facilities to
the Members. HKICL may (with the approval of MA) subcontract the performance of its
obligations hereunder.

2.3.2 HKICL shall exercise a degree of skill, care and responsibility commensurate with third parties
in Hong Kong providing substantially similar services. The exercise of such skill, care and
responsibility shall constitute a full and complete discharge of the obligations and duties of
HKICL to Members and other persons in respect of and concerning the Clearing House and the
Clearing Facilities under these Clearing House Rules and the Operating Procedures.

2.3.3 (a) Save in respect of the total or substantial destruction of a Paper Cheque in the Clearing
House on any day such that HKICL is unable to process the clearing of such Paper Cheque
on that day (see Rule 2.3.3(b)), HKICL shall assume full responsibility for all claims
arising out of any failure, error or inaccuracy in its provision, management or operation of
the Clearing House and/or the Clearing Facilities under these Clearing House Rules which
are proved to have resulted substantially from (i) a reckless act or omission or the
intentional misconduct of its servants or agents or (ii) fire or theft affecting the premises or
property of HKICL except that HKICL shall not be responsible for any consequential loss
suffered by (i) a Member and its Non-bank Card Members, (ii) any correspondent bank of
a Service Provider , (iii) any customer of a Member , (iv) any customer or participant or
nominated agent bank of HKSCC , HKCC or SEOCH, (v) any e-Cheque Drop Box User ,
(vi) any GD e -Cheque Platform User and/or (vii) any other person (each a “Relevant
Party”), arising from any cause whatsoever other than substantially as a result of a reckless
act or omission or intentional misconduct on the part of the servants or agents of HKICL.

(b) In the event of the total or substantial loss of Paper Cheques in the Clearing House on any
day such that HKICL is unable to process the clearing of such Paper Cheque s on that day,
HKICL shall be liable for all direct losses resulting from such loss of Paper Cheque
substantially caused by the reckless act or omission or the intentional misconduct of its
servants or agents but shall not be otherwise liable nor shall it b e liable for any
consequential loss however caused.

(c) Save and except those claims for which HKICL shall assume responsibility as provided
above, no claim shall be made by a Relevant Party as defined in Rule 2.3.3 (a) against
HKICL concerning, arising out of or in connection with the Clearing House and/or the
Clearing Facilities and/or HKICL’s provision, management and/or operation of the same.

## Page 22

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 19

(d) Notwithstanding anything herein and for the avoidance of doubt, MA and HKICL shall,
when acting in good faith, not be liable in respect of any act or omission pursuant to
Schedule I.

2.3.4 Each Member (other than HKSCC, HKCC, SEOCH and CLS Bank but including CLS
Participants in their capacity as such) shall in respect of all claims, losses, damages and
expenses incurred by it, any of its customers (including trustees of MPF Schemes, or any of the
e-Cheque Drop Box Users of the customers), a Non-bank Card Member or (where such Member
is a Service Provider) any of its correspondent banks, HKSCC, HKCC, SEOCH shall in respect
of all claims, losses, damages and expenses incurred by it or any of its customers or participants
(other than a customer or a participant which is a Member) and CLS Bank shall in respect of
all claims, losses, damages and expenses incurred by it or any of its customers or participants
(other than a customer or a participant which is a Member), indemnify and hold MA and HKICL
harmless against all actions, proceedings, costs, claims, demands, liabilities, losses or expenses
whatsoever and h owsoever arising out of or in connection with HKICL’s provision,
management or operation of the Clearing House and/or the Clearing Facilities and/or HKICL’s
performance of its obligations under these Clearing House Rules and the Operating Procedures
save and except those claims for which HKICL shall assume responsibility as provided in Rule
2.3.3.

2.3.5 The provisions in this Rule 2.3 shall be in addition to and shall not be affected by any other
provisions of these Rules which (i) exclude or limit the liability of MA or HKICL; or (ii) set
out an indemnity provision in favour of MA or HKICL.

2.3.6 HKICL shall not be responsible for debiting and crediting the CHATS Ledger Accounts. MA
shall settle all payments effected through CHATS by debiting and crediting the CHATS Ledger
Accounts concerned in accordance with Rule 3.1.3.

2.4 GD Agent and MC Agent

2.4.1 (a) Each GD Agent, who was acting at the time the relevant claim was made as such agent,
shall indemnify and hold HKICL harmless against all losses, damages, liabilities, costs
and expenses whatsoever and howsoever arising out of or in connection with any claim,
demand, action or proceeding against HKICL by the relevant GD Settlement Centre
for which such agent acts, any GD Bank clearing through such GD Settlement Centre,
or any customer of any such GD Bank in connection with or arising out of any act or
omission on the part of HKICL or its servants or agents in relation to the clearing or
settlement of relevant GD Cheque s or, Paper Cheque s or e -Cheques drawn on
Members, save and except any claim which is proved to have resulted substantially
from a reckless act or omission or intentional misconduct of HKICL ’s servants or
agents. HKICL will notify the relevant GD Agent of any such claim, demand, action
or proceeding within 7 Working Days of receipt of formal written notice thereof by
HKICL.

(b) The MC Agent, who was acting at the time the relevant claim was made as such agent,
shall indemnify and hold HKICL harmless against all losses, damages, liabilities, costs
and expenses whatsoever and howsoever arising out of or in connection with any claim,
demand, action or proceeding against HKICL by the MC Settlement Centre, any MC
Bank clearing through the MC Settlement Centre, or any customer of any s uch MC
Bank in connection with or arising out of any act or omission on the part of HKICL or
its servants or agents in relation to the clearing or settlement of relevant Paper Cheques
drawn on Members, save and except any claim which is proved to have resu lted
substantially from a reckless act or omission or intentional misconduct of HKICL’s
servants or agents. HKICL will notify the MC Agent of any such claim, demand,
action or proceeding within 7 Working Days of receipt of formal written notice thereof
by HKICL.

2.4.2 Each GD Agent shall indemnify and hold HKICL and each other Member harmless against all
actions, proceedings, costs, claims, demands, liabilities, losses or expenses whatsoever and

## Page 23

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 20

howsoever arising out of or in connection with its certification of or failure to certify relevant
unpaid GD Cheque s (including in relation to the Default Transactions referred to in Part II,
Schedule I) and/or its notice to or failure to notify HKICL that any relevant GD Bank is in
default. Without prejudice to the foregoing indemnity, it is acknowledged that each GD Agent
will only act in accordance with notification from the relevant GD Settlement Centre for which
such agent acts as to whether any relevant GD Bank is in default.

2.4.3 No GD Agent or MC Agent is an agent of HKICL for any purpose, and HKICL shall not be
liable in any way in relation to any act or omission of any GD Agent or MC Agent.

2.5 Clearing House Operating Procedures

HKICL shall be entitled with MA’s and the Association’s approval to issue operating procedures
(“Operating Procedures”) for the Clearing House and the Clearing Facilities and to amend such
Operating Procedures from time to time as it thinks fit. To the extent of any inconsistency between these
Clearing House Rules and the Operating Procedures, these Clearing House Rules shall prevail save
where otherwise specifically provided for in these Clearing House Rules . The current version of the
Operating Procedures can be found on HKICL's website www.hkicl.com.hk. Any amendments made
thereto shall become effective from the effective date(s) as stated in HKICL’s prior notice to Members
and the amended version will be posted onto HKICL’s website (which shall specify the effective date(s)
for the amendments according to the notice). In the event of any inconsistency between the version of
the Operating Procedures on HKICL’s website and any other versio n of the Operating Procedures, the
version on HKICL’s website shall prevail.

2.6 Clearing Facilities Expenses

2.6.1 All expenses incurred by HKICL in providing, managing and operating the Clearing House and
the Clearing Facilities shall be borne by HKICL.

2.6.2 Members shall pay to HKICL fees for the use of the Clearing Facilities calculated in the manner
determined by HKICL from time to time (“Fees”).

2.6.3 Unless otherwise agreed, payment of the Fees shall be made monthly in arrears by direct debit
instruction generated by HKICL pursuant to a direct debit authorisation issued by each Member
in HKICL’s favour, failing due payment interest shall become payable on the outstanding sum
at the rate which HKICL certifies from time to time to be equal to the average of the best lending
rates for Hong Kong Dollars for the time being quoted by three Members whi ch are members
of the Association as selected by HKICL.

2.7 Confidentiality

2.7.1 HKICL shall keep confidential all information received from or collected on behalf of Members
in connection with the Clearing House and/or Clearing Facilities and shall, except as otherwise
required by law or pursuant to these Rules and /or the Operating Procedures, disclose the same
only to those of its staff who require the information for the purpose of providing, managing
and operating the Clearing House and/or the Clearing Facilities, or to MA or the Association.
HKICL shall take all reasonable steps to ensure that its staff are aware of HKICL’s
confidentiality obligations.

2.7.2 Each GD Agent shall keep confidential all information relating to the other Members and their
customers which that GD Agent obtains in its capacity as GD Agent, and shall not use or
disclose any such information except (a) for the purposes of clearing and settling relevant GD
Cheques and, Paper Cheques and e-Cheques drawn on Members and presented to the Clearing
House by Members or as the case may be by the GD Banks or customers of GD Banks through
that GD Agent or GD e-Cheque Platform or (b) as required by law.

2.7.3 The MC Agent shall keep confidential all information relating to the other Members and their
customers which the MC Agent obtains in its capacity as the MC Agent, and shall not use or
disclose any such information except (a) for the purposes of clearing and settling Paper Cheques

## Page 24

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 21

drawn on Members and presented to the Clearing House by the MC Banks through the MC
Agent or (b) as required by law.

2.8 Contract

2.8.1 HKICL and each Member agree that these Clearing House Rules constitute a contract between
HKICL, such Member and all other Members from time to time. It is recognised that HKICL ,
with approval of MA and the Association, may amend these Clearing House Rules from time
to time as it thinks fit.

2.8.2 Each Member (including HKSCC’s nominated agent bank but other than HKSCC) which
participates in the clearing and settlement of CCASS Items agrees that HKSCC may present
CCASS Items to HKICL for clearing and settlement in accordance with these Rules and on the
terms set out in an agreement between HKICL and HKSCC (the “HKSCC Agreement”) and
MA is authorised by such Members to debit and credit such Members’ CHATS Ledger
Accounts to settle the relevant CCASS Items presented by HKSCC without making any
independent verification of the correctness or integrity of the contents of the CCASS Items .
According to the terms of the HKSCC Agreement, HKSCC will be responsible for the
correctness of the contents of each CCASS Item and will indemnify such Members , MA and
HKICL against all liabilities and expenses incurred by any of them arising out of or as a result
of any error in a CCASS Item or discrepancy between information in a CCASS Item and the
related underlying transaction. HKICL and MA shall not be liable for, and expressly exclude
any such liability for, any direct, indirect, consequential, special or incidental damage, loss or
expense, whether caused by negligence or otherwise, which arises directly or indirectly as a
consequence of t he processing, clearing or settlement of (or any failure or delay to process,
clear or settle), any CCASS Items in accordance with these Rules.

2.8.3 (a) Each Member (including OTC Clear’s nominated agent bank) which participates in
the clearing and settlement of OTC Items agrees that OTC Clear may present OTC
Items to HKICL for clearing and settlement in accordance with these Rules and on the
terms set out in an agreement between HKICL and OTC Clear (the “ OTC Clear
Agreement”) and MA is authorised by such Members to debit and credit such
Members’ CHATS Ledger Accounts to settle the relevant OTC Items presented by
OTC Clear without making any independent verification of the correctness or integrity
of the contents of the OTC Items. According to the terms of the OTC Clear Agreement,
OTC Clear will be responsible for the correctness of the contents of each OTC Item
and will indemnify such Members, MA and HKICL against all liabilities and expenses
incurred by any of them arising out of or as a result of any error in an OTC Item or
discrepancy between information in an OTC Item and the related underlying
transaction. HKICL and MA shall not be liable fo r, and expressly exclude any such
liability for, any direct, indirect, consequential, special or incidental damage, loss or
expense, whether caused by negligence or otherwise, which arises directly or
indirectly as a consequence of the processing, clearing or settlement of (or any failure
or delay to process, clear or settle), any OTC Items in accordance with these Rules.

(b) Each Member which participates in money settlement of OTC Clear Payment
Instructions via CHATS agrees that OTC Clear may transmit or deliver OTC Clear
Debit Requests to HKICL for generation of OTC Clear Payment Instructions and
agrees to the effecting of funds transfer in accordance with these Rules and on the
terms set out in the OTC Clear Agreement and MA is authorised by such Members to
debit such Members’ CHATS Ledger Accounts and credit the CHATS Ledger
Account of OTC Clear’s designated b ank Member to settle the relevant OTC Clear
Payment Instructions generated by CHATS pursuant to the OTC Clear Debit Requests
transmitted or delivered by OTC Clear without making any independent verification
of the correctness or integrity of the contents of the OTC Clear Debit Requests or OTC
Clear Payment Instructions . According to the terms of the OTC Clear Agreement,
OTC Clear will be responsible for the correctness of the contents of each OTC Clear
Debit Request and will indemnify such Members, MA and HKICL against all
liabilities and expenses incurred by any of th em arising out of or as a result of any

## Page 25

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 22

error in an OTC Clear Debit Request or discrepancy between information in an OTC
Clear Debit Request and the related underlying transaction. HKICL and MA shall not
be liable for, and expressly exclude any such liability for, any direct, indirect,
consequential, special or incidental damage, loss or expense, whether caused by
negligence or otherwise, which arises directly or indirectly as a consequence of the
processing or settlement of (or any failure or delay to process or settle), any OTC Clear
Debit Request and OTC Clear Payment Instruction in accordance with these Rules.

2.9 Compliance with the PSSVFO

2.9.1 Each Member and HKICL shall comply with all obligations under the PSSVFO and all
directions or regulations made by MA thereunder, as may be applicable to each of them.

2.9.2 Without prejudice to the generality of Rule 2.9.1, HKICL shall:

(a) operate the Clearing House and/or the Clearing Facilities in a safe and efficient manner
calculated to minimise the likelihood of any disruption to the functioning of the
Clearing House and/or the Clearing Facilities;

(b) operate the Clearing House and /or the Clearing Facilities in accordance with the
PSSVFO insofar as it applies in relation to the Clearing House and /or the Clearing
Facilities; and

(c) provide (and be entitled to provide) all information and reports required to be provided
by a system operator pursuant to the PSSVFO including Sections 6 (Obligation to
inform MA of name and address etc.), 12 (MA may request information or documents
from system operator, settlement institution, participant or licensee), 30 (Duty to report
on completion of default proceedings) and 53 (Requirement to give information
relating to default) of the PSSVFO.

For the avoidance of doubt, HKICL shall not be responsible for debiting and crediting the
CHATS Ledger Accounts.

2.9.3 Without prejudice to the generality of Rule 2.9.1, each Member shall notify HKICL and MA
forthwith if there comes to its attention any of the following circumstances occurring in Hong
Kong or any analogous circumstances occurring outside Hong Kong:

(a) a Member becoming unable to meet its obligations;

(b) the presentation of a petition for winding up of the Member;

(c) the making of an order for winding up of the Member;

(d) the passing of a resolution for voluntary winding up of the Member;

(e) the making of a directors’ voluntary winding up statement in respect of the Member ;
or

(f) subject to any confidentiality obligations binding on it, the taking of any crisis
prevention measure in relation to the Member or a group company of the Member.

HKICL shall inform MA forthwith if it becomes aware of any of the foregoing.

2.9.4 Without prejudice to the generality of Rule 2.9.1, none of the Members nor HKICL shall
contravene Section 45 (Giving false information to MA) of the PSSVFO.

2.9.5 Each Member shall have systems in place which are complementary to HKICL’s contingency
arrangements so as to enable HKICL to ensure the timely recovery of its usual operations in the
event of the occurrence of an adverse contingency affecting such operations. Such contingency

## Page 26

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 23

arrangements shall be modified from time to time in the manner required by HKICL or MA,
and HKICL shall notify Members of the changes accordingly. Members shall participate in the
contingency drills arranged by HKICL from time to time so as to verify their readiness.

2.9.6 In the event of any inconsistency between the provisions of this Rule 2.9 and any of the other
provisions of these Clearing House Rules, this Rule 2.9 shall prevail.

2.10 Compliance with the Security and Anti-fraud Requirements

2.10.1 Each Member shall comply with the applicable Security and Anti -fraud Requirements as
specified by HKICL.

2.10.2 Each Member shall submit a self -declaration of compliance with the Security and Anti -fraud
Requirements to HKICL when required, and in a form specified, by HKICL; responses from
Members may be passed to MA for follow up and record.

2.11 Monitoring of Compliance with these Rules

2.11.1 HKICL will monitor performance by Members of their obligations under these Rules.

2.11.2 In the event that HKICL becomes aware of any non performance by any Member of its
obligations under these Rules, HKICL shall as soon as practicable inform (i) the Member
concerned and require it to ensure performance of the relevant provision; and (ii) MA of such
incident.

## Page 27

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 24

Part III Settlement

3.1 Settlement Institution, Settlement Account and CHATS Ledger Account

3.1.1 The settlement institution is MA and each Member (other than CLS Bank, HKSCC, HKCC and
SEOCH) shall open and keep a Settlement Account (including a CHATS Ledger Account and
an FPS Ledger Account) with MA in accordance with the Conditions for the operation of
Settlement Accounts including CHATS Ledger Accounts and FPS Ledger Accounts for the
purposes of settlement of payments effected through CHATS. CLS Bank, HKSCC, HKCC and
SEOCH shall each open and keep a Settlement Account (including a CHATS Ledger Account
only) with MA in accordance with the applicable Conditions for the operation of CHATS
Ledger Accounts for the purposes of settlement of payments effected through CHATS.

3.1.2 Each Member shall maintain an available balance in its CHATS Ledger Account sufficient to
meet in time its and its Non-bank Card Members’ payment obligations as and when due.

3.1.3 Notwithstanding the mode and means by which they are made, all payments effected through
CHATS shall be settled by MA debiting or crediting the CHATS Ledger Accounts concerned
through CHATS and once debited or credited to such CHATS Ledger Accounts, such payments
shall be deemed made, completed, irrevocable and final.

3.1.4 Each Member authorises MA to debit or, as the case may be, credit its CHATS Ledger Account
for payments effected through CHATS in accordance with the provisions of these Clearing
House Rules and the Conditions. To the extent there is any conflict between the Conditions
and these Clearing House Rules, the Conditions shall prevail.

3.1.5 Each Member (other than CLS Bank, HKSCC, HKCC and SEOCH) authorises MA to debit or,
as the case may be, credit its CHATS Ledger Account and its FPS Ledger Account for the
purpose of implementing Balance -triggered Balance Sweeping Transactions and Transaction -
triggered Balance Sweeping Transactions in accordance with the provisions of these Clearing
House Rules, the FPS Rules and the Conditions. To the extent there is any conflict among the
Conditions, these Clearing House Rules and the FPS Rules, the Conditions shall prevail.

3.2 Settlement of CHATS Transactions other than those in respect of Articles

All CHATS Transactions (other than CHATS Transactions in respect of Articles) involving payments
or funds transfers shall be settled as provided in Part VI of these Clearing House Rules.

3.3 Settlement of Articles

Settlement of Articles cleared through CHATS shall be effected as provided in Part VII of these Clearing
House Rules.

3.4 Member to Member payments

A Member can open accounts with another Member for operational purposes and the nostro Member
can directly debit or credit such accounts for payments of an operational nature, but these accounts and
such in-house transfers should not be used for large scale funds transfers, in particular in connection with
the settlement of capital market or treasury type transactions or for funds transfers from the account
opening Member to a third Member.

3.5 Settlement Obligations

Notwithstanding any provisions in these Clearing House Rules but without prejudice to HKICL’s
obligations in respect of the management and operation of the Clearing House and the Clearing Facilities,
HKICL and MA shall be under no liability whatsoever for any settlement obligations of or between
Members.

## Page 28

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 25

Part IV Members

4.1 Clearing House Rules and Operating Procedures

These Clearing House Rules and the Operating Procedures are binding on the Members. Members shall
comply with and observe these Clearing House Rules and each book of Operating Procedures (as
amended from time to time and insofar as the Member participates in an activity that is a subject matter
of such book of Operating Procedures) from time to time in force.

4.2 Withdrawal

4.2.1 A Member may withdraw from membership of the Clearing House by giving 90 days ’ prior
written notice to HKICL and by paying the accrued fees and other payments, if any, due by it
to HKICL in relation to the Clearing House and the Clearing Facilities to the date of withdrawal.
Such withdrawal shall be without prejudice to any liability accrued up to and including the date
of withdrawal.

4.2.2 Notwithstanding Rule 4.2.1, withdrawal of HKSCC, HKCC or SEOCH from membership shall
only take effect upon consultation and agreement with MA.

4.2.3 Notwithstanding Rule 4.2.1, a GD Agent’s withdrawal from membership shall only take effect
upon the appointment or authorisation of a replacement agent by the People ’s Bank of China,
Guangzhou Branch or, as the case may be, Shenzhen Central Sub-branch and after notification
thereof by it to MA and HKICL.

4.2.4 Notwithstanding Rule 4.2.1, the MC Agent ’s withdrawal from membership shall only take
effect upon the appointment or authorisation of a replacement agent by the MC Settlement
Centre and after notification thereof by it to MA and HKICL.

4.3 Clearing Codes

Clearing codes which are used to identify each Member, each Non-bank Card Member, each Credit Card
Company (and in case a Credit Card Company appoints more than one Card Agent, a separate clearing
code will be allocated to the Credit Card Company for each Card Agent appointed by it in order to
identify the separate Bulk Clearing Settlement Runs in respect of Cr edit Card Items generated by each
Card Agent ), each trustee of MPF Schemes , HKSCC, HKCC, SEOCH and OTC Clear (collectively
referred to as “entities”) (one per entity or at the discretion of HKICL more than one per entity) and each
GD Settlement Centre, and branch codes which are used in conjunction with each entity’s clearing code
or one of its clearing codes to identify each of an entity’s branches, are allocated by HKICL to be used
by the entities for the purposes of the services provided by the Clearing House. No entity may use a
clearing code which is allocated to another entity. Common branch codes may be allocated to different
entities and no entity may use a branch code except in conjunction with its clearing code or one of its
clearing codes. All such rights as may subsist in the clearing and branch codes are owned by HKICL,
and such codes may be used by it for all purposes connected with or incidental to its businesses.

4.4 Outsourcing by Members

Members may outsource any of their systems required for the purpose of participation in the Clearing
House. In so doing Members shall exercise reasonable skill and care in choosing the outsourcing party.
Each of MA and HKICL is authorised to deal with an y such outsourcing party notified to it as being
authorised to act on such Member’s behalf provided that the Member shall be responsible for all acts,
omissions, neglects or defaults of its outsourcing party and such Member appointing an outsourcing
party will indemnify and hold each of MA and HKICL harmless against all actions, proceedings, costs,
claims, demands, liabilities, losses and expenses whatsoever and howsoever arising out of or incurred
by MA or HKICL as a result of the acts, omissions, neglects or defaults of its outsourcing party or arising
out of or incurred by MA or HKICL by virtue of any dealings by MA or HKICL with an outsourcing
party of a Member which it would not have incurred if MA or HKICL had dealt with that Member
directly. This rul e shall not apply to the production of images of Paper Cheque s by HKICL for Group

## Page 29

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 26

B Members in accordance with the Operating Procedures.

4.5 Migration

(a) A Member which at any time is a Group A Member may, with the consent of HKICL and
subject to such notice period as HKICL requires, change its status to a Group B Member.

(b) A Member which at any time is a Group B Member may, on giving 12 months’ notice to HKICL,
change its status to a Group A Member.

4.6 Intra Member Payments

For the avoidance of doubt, it is declared that (a) a Sending Member may make funds transfers to itself
as Receiving Member in respect of CHATS Transactions (including transfers effected pursuant to
CHATS Payment Instructions, CCASS Payment Instructions, CCP Instructions, CCPMPNet Payment
Instructions, CCASS Optimiser Payment Instructions, SCCASS Optimiser Payment Instructions,
CHATS Optimiser Payment Instructions , CCPO Instructions , CCPMPNet Optimiser Payment
Instructions and BOJ DvP Payment Instructions but not CLS Payment Instructions); and (b) OTC Clear
may initiate OTC Clear Debit Requests to the Clearing House Computer for generation of OTC Clear
Payment Instructions to make funds transfers from the paying Member referred to in Rule 6.3.14.3(a) to
the bank Member designated by OTC Clear being the same as the paying Member .

## Page 30

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 27

Part V Refusal/Suspension of Clearing Facilities

5.1 Clearing Facilities shall be suspended by HKICL to a Member in accordance with the provisions of the
Default Arrangement.

5.2 Part or all of the Clearing Facilities shall be refused forthwith by HKICL in relation to a Member if:

(a) the authorisation of the Member (if it is an Authorized Institution) under the Banking Ordinance
(Cap. 155 of the Laws of Hong Kong) has been suspended or revoked, unless HKICL receives notice
in writing by MA that Clearing Facilities to such Authorized Institution may be continued in the
manner as specified in such notice; or

(b) HKICL receives notice in writing from MA that Clearing Facilities in relation to the Member are to
be refused.

5.3 Part or all of the Clearing Facilities shall be suspended forthwith for a Member by HKICL:

(a) upon receipt by HKICL of a notice in writing from MA that Clearing Facilities to such Member
have been suspended by MA for such period as shall be stipulated in such notice; or

(b) if the Member becomes insolvent.

5.4 In a case to which Rule 5.1 , 5.2 or 5.3 applies, Clearing Facilities shall only be restored to the Member
in question upon receipt by HKICL of a notice in writing to such effect from MA.

5.5 For the avoidance of doubt, these Rules are subject to the provisions of section 89 of the FIRO.
Accordingly nothing in this Rule 5 shall be construed to require or entitle HKICL (or MA) to suspend
Clearing Facilities to a Member or to trigger any default event provision under these Rules in relation to
a Member by reason solely of:

(a) the taking of any crisis prevention measure in relation to the Member or a group company of the
Member;

(b) the occurrence of an event directly linked to the taking of any crisis prevention measure referred to
in paragraph (a) of this Rule 5.5; or

(c) the occurrence of any other event that does not of itself trigger a default event provision under these
Rules in relation to the Member pursuant to section 89 of the FIRO,

provided the substantive obligations (including payment and delivery obligations) applicable to the
Member under these Rules continue to be performed.

5.6 In the event of any refusal or suspension of Clearing Facilities affecting a Member or if the clearing of
any GD Cheque has been refused or suspended, HKICL shall, as soon as practicable thereafter, notify
all other Members by a broadcast in the manner provided in the Operating Procedures , and shall notify
JETCO, Credit Card Companies, HKSCC, HKCC, SEOCH, OTC Clear and the relevant GD Settlement
Centre in a manner separately agreed with them and thereafter such other Members, JETCO, Credit Card
Companies, HKSCC, HKCC, SEOCH, OTC Clear and the relevant GD Settlement Centre shall not
deliver to HKICL any Articles payable by or to, or initiate any other CHATS Transactions involving,
the Member for which Clearing Facilities are refused or suspended while such refusal or suspension shall
continue in effect (or deliver to HKICL any relevant GD Cheque, if the Member in question is a GD
Agent, or any GD Cheque relating to a GD Bank in the case of default by that GD Bank).

5.7 For the avoidance of doubt, in the event of any refusal or suspension of Clearing Facilities in accordance
with Rule 5.1, 5.2 or 5.3 , the e -Cheque Presentment Service being part of the Clearing Facilities is
entitled to not accept any e -Cheques drawn on or payable into an account operated by the Member for
which Clearing Facilities are refused or suspended while such refusal or suspens ion shall continue in
effect.

## Page 31

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 28

5.8 If it appears that part or all of the Clearing Facilities are inoperable, HKICL may at any time after
consultation with MA, declare by notice in writing to all Members, JETCO , Credit Card Companies ,
HKSCC, HKCC, SEOCH, OTC Clear and the relevant GD Settlement Centre in respect of clearing and
settlement of e-Cheques, that all or part of the Clearing Facilities will be suspended for the Working Day
on which the notice is given and shall provide information as to which of the Clearing Facilities will be
available. Any such notice from HKICL in relation to the inoperability of an e -Cheque Presentment
Service may be published on any website, mobile application or on any other system on which an e -
Cheque Presentment Service is made available.

5.9 At the end of each Non-Clearing Day, HKICL will consult with MA with a view to determining whether
and the extent to which Clearing Facilities will be resumed for the following Working Day. After such
consultation HKICL will give notice in writing to all Members, JETCO , Credit Card Companies ,
HKSCC, HKCC, SEOCH, OTC Clear and the relevant GD Settlement Centre in respect of clearing and
settlement of e -Cheques, as to which of the Clearing Facilities will be available on the next Working
Day. Any such notice from HKICL in relation to the resumption of an e -Cheque Presentment Service
may be published on any website, mobile application or on any other system on which an e -Cheque
Presentment Service is made available.

5.10 At any time during a Non-Clearing Day, HKICL may at any time after consultation with MA declare by
notice in writing to all Members, JETCO, Credit Card Companies, HKSCC, HKCC, SEOCH, OTC Clear
and the relevant GD Settlement Centre in respect of clearing and settlement of e -Cheques, that part or
all of the Clearing Facilities which have been suspended on that Non-Clearing Day shall resume normal
operation. Any such notice from HKICL in relation to the resumption of an e -Cheque Presentment
Service may be published on any website, mobile application or on any other system on which an e -
Cheque Presentment Service is made available.

5.11 During a Non -Clearing Day, the Clearing Facilities that are operable shall be operated in accordance
with the Operating Procedures and any other circulars issued by HKICL dealing with the operation of
the Clearing Facilities during periods of suspension.

5.12 The resumption of normal operation of the Clearing Facilities shall be in accordance with the Operating
Procedures.

5.13 Neither MA nor HKICL shall owe any duty or incur any liability to (i) any Member (including HKSCC,
HKCC and SEOCH) , (ii) any Non -bank Card Member, (iii) any correspondent bank of a Service
Provider, (iv) any customer of a Member (including trustees of MPF Schemes) , (v) any customer or
participant or nominated agent bank of HKSCC, HKCC or SEOCH, (vi) any e-Cheque Drop Box User,
(vii) any GD e-Cheque Platform User, or (viii) any other person whatsoever (each a “Relevant Party”)
by the giving of any notice or advice pursuant to or purporting to be given pursuant to this Rule 5 and/or
the Default Arrangement and/or Part IV of Schedule III and/or Part V of Schedule III and/or Part VI of
Schedule III or by the failure to give or any delay in giving any such notice or advice. HKICL shall
incur no liability to any Relevant Party as defined in this Rule for the consequences of acting on the
Default Arrangement, these Clearing House Rules or the Operating Procedures or any such notice or
advice given or purportedly given to it pursuant to this Rule 5 and/or Part IV of Schedule III and/or Part
V of Schedule III and/or Part VI of Schedule III . Each Member hereby agrees to indemnify and hold
each of MA and HKIC L harmless against all actions, proceedings, costs, claims, demands, liabilities,
losses and expenses whatsoever and howsoever arising out of or in connection with any of the matters
referred to in this Rule , or incurred by either MA or HKICL to the Non -bank Card Member of that
Member, or to any of the correspondent banks of that Member if it is a Service Provider , or to any
customer or participant or nominated agent bank of that Member if it is HKSCC, HKCC or SEOCH, in
each case in their capacities as such.

## Page 32

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 29

Part VI CHATS (other than the processing in respect of Articles)

6.1 Introduction

6.1.1 Each Member shall access CHATS via the SWIFT network. Payment instructions effected
through CHATS and their related request s shall be in designated SWIFT format as stipulated
in the Operating Procedures.

6.1.2 All Members (except CLS Bank) must be connected to the Clearing House Computer through
the eMBT as provided in Rule 6.2 to perform administrative functions related to CHATS
Transactions (other than initiating/receiving payment instructions) or submit instructions
relating to Special Posting transactions as stipulated in the Operating Procedures.

6.1.3 Requests for enhancement of or changes relating to CHATS (a) by Members who are members
of the Association shall be submitted by that Member to the Association, and (b) by Members
who are not members of the Association shall be submitted by that Member through HKICL to
the Association, in each case to enable the Association to decide whether they should be
implemented, subject in each case to prior consultation by HKICL with MA after approval has
been given by the Association.

6.1.4 The provisions of this part relating to CHATS Transactions effected by way of Special Posting
or End of Day Net Settlement shall be subject to the provisions of Rules 6.11 and 6.12
respectively.

6.2 MBT and SWIFT network

6.2.1 Each Member (except CLS Bank) connecting its terminal to the Clearing House Computer
through the eMBT (via the SWIFT network) is required to also be able to connect to the
Clearing House Computer through the iMBT (via the HKICL network and/or internet) as a
contingency in case it is unable to connect to the eMBT through the SWIFT network.

6.2.2 Each Member (except CLS Bank) shall at its own cost install and maintain in good order a
terminal which can access the MBT as prescribed or approved by HKICL from time to time.
Use of the terminal which can access the MBT shall be restricted to that Member’s authorised
personnel who use passwords or other systems to ensure only authorised personnel of that
Member may access the MBT. HKICL is authorised to rely and act on instructions using such
passwords or systems. Members shall be liable for all consequences of misuse of such
passwords or other systems.

6.2.3 Each Member (except CLS Bank) must connect its terminal to the MBT in order to connect to
the Clearing House Computer. A terminal must be a computer or intelligent terminal device (i)
which (in the case of the eMBT) is installed with software provided by SWIFT and which can
access the eMBT in order to connect to the Clearing House Computer via the SWIFT network,
or (ii) which (in the case of the iMBT) can access the iMBT in order to connect to the Clearing
House Computer via the HKICL network and/or internet, as the case may be . The connection
must undergo formal verification and connection tests with final approval being at the discretion
of HKICL. All telecommunications charges or charges levied by SWIFT relating to the
connection shall be borne by the relevant Member.

6.2.4 Each Member (except CLS Bank) shall strictly observe and comply with the guidelines as
stipulated in the relevant Operating Procedures relating to its access or use of the MBT and/or
the operation of the Clearing Facilities by it.

6.2.5 Requests for enhancement of or changes to the MBT functions provided by HKICL (a) by
Members who are members of the Association shall be submitted by that Member to the
Association, and (b) by Members (except CLS Bank) who are not members of the Association
shall be submitted by that Member through HKICL to the Ass ociation, in each case to enable
the Association to decide whether they should be implemented, subject in each case to prior

## Page 33

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 30

consultation by HKICL with MA after approval has been given by the Association.

6.2.6 All software, data, specifications and similar intellectual property comprised within the MBT
are owned by, or licensed to, HKICL and may not be copied, downloaded, distributed or
published in any way without the prior written consent of HKICL. Members m ay utilise such
proprietary information of HKICL solely for the purposes of performing administrative
functions relating to CHATS Transactions (other than initiating/receiving payment instructions)
or submitting instructions relating to Special Posting transactions as stipulated in the Operating
Procedures, and in accordance with the Clearing House Rules.

6.2.7 HKICL provides access to the MBT on an “as is” basis, and save as provided in these Rules,
makes no representation as to, and does not warrant, the accuracy or completeness of the MBT
or data derived from its use (including for the avoidance of doubt accuracy or completeness of
any information in any fraud detection or other tools provided by HKICL to Members via the
MBT separate from the clearing and settlement functions provided by HKICL pursuant to these
Rules). HKICL gives no warranties, express, implied or statutory, of any kind, including
without limitation as to the merchantability, fitness for a particular purpose, title, non -
infringement of third party rights or freedom from viruses, worms, trojan horses or other
contaminating programming or code relating to the use of the MBT, except to the extent the
same cannot be excluded or limited at law or as otherwise given in these Rules.

6.2.8 To the fullest extent permitted by law (and subject only to the provisions of Rule 2.3 of the
Clearing House Rules), each of HKICL and MA shall not be liable for, and expressly excludes
any such liability for, any direct, indirect, consequential, special or incidental damage, loss or
expense, whether caused by negligence or otherwise, which arises directly or indirectly as a
consequence of the use of (or inability to use) the MBT, whether or not HKICL or MA has been
notified of the possibility of such damage, loss or expense.

6.2.9 [This provision has been left blank intentionally]

6.3 Settlement of CHATS Transactions other than those in respect of Articles

6.3.1 CHATS Payment Instruction Value Today

6.3.1.1 A CHATS Payment Instruction Value Today will not be effected or settled through
CHATS unless the available balance in the Sending Member ’s CHATS Ledger
Account for the time being is sufficient to make the payment referred to in such
payment instruction. In case the available balance in the relevant Sending Member ’s
CHATS Ledger Account is insufficient to make such payment, the relevant CHATS
Payment Instruction Value Today, unless subsequently cancelled, will remain in the
Normal Queue until either:

(a) such time as the available balance is sufficient to meet such payment
instruction when it is first in priority in the Normal Queue, and in such case,
the CHATS Payment Instruction Value Today will be effected automatically;
or

(b) the CHATS Value Date Cut -off and in such case, the CHATS Payment
Instruction Value Today will be cancelled automatically.

This provision shall not apply to CHATS Payment Instructions Value Today in the
Pending Queue.

6.3.1.2 Subject to Rule 6.3.1.1, a funds transfer initiated by a CHATS Payment Instruction
Value Today will be settled through CHATS immediately upon the completion of its
processing.

6.3.1.3 In a case to which Rule 6.3.1.1(a) applies, the relevant CHATS Payment Instruction
Value Today will be settled through CHATS immediately upon the completion of its

## Page 34

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 31

processing.

6.3.1.4 Settlement of a CHATS Payment Instruction Value Today will be effected across the
books of MA pursuant to Rule 3.1.3 by debiting the CHATS Ledger Account of the
Sending Member for the funds transferred and crediting the same to the CHATS
Ledger Account of the Receiving Member.

6.3.1.5 A Member shall be entitled to re-sequence the Normal Queue of its CHATS Payment
Instructions Value Today at any time prior to the CHATS Value Date Cut -off or to
transfer CHATS Payment Instructions Value Today from the Normal Queue to the
Pending Queue or vice versa before the specified time as stipulated in the Operating
Procedures. However, a Member can only cancel its CHATS Payment Instructions
Value Today in the Normal Queue and the Pending Queue up to the CHATS Customer
Cut-off time. This Rule 6.3.1.5 is subject to Rule 6.13.8.

6.3.1.6 Rules 6.3.1.1 to 6.3.1.5 shall in all respects be subject to the arrangements provided
for in the Operating Procedures in rel ation to the CMU Optimiser Runs and to that
extent the Operating Procedures shall prevail over Rules 6.3.1.1 to 6.3.1.5.

6.3.2 CHATS Payment Instruction Value Forward Day

6.3.2.1 Members may not make payments/funds transfers through CHATS for value dates
later than the last of the Supported Forward Days.

6.3.2.2 CHATS Payment Instructions Value Forward Day will be stored in the Clearing House
Computer and will not be processed or settled until the value day specified.

6.3.2.3 CHATS Payment Instruction Value Forward Day will be automatically processed for
settlement after the CHATS Commencement on the relevant Supported Forward Day
(“Value Day”) in the same way and manner as CHATS Payment Instructions Value
Today input during that Value Day and all provisions in Rule 6.3.1 shall apply.

6.3.3 CCASS Payment Instructions

6.3.3.1 A CCASS Payment Instruction will not be effected or settled through CHATS except
on a Working Day (i) between CCASS Commencement and CCASS Interim Cut -off
for CCASS Interim Cut -off Payment; or (ii) between CCASS Commencement and
CCASS End of Day Cut-off for CCASS End of Day Cut-off Payment as the case may
be and unless:

(a) the Clearing House Computer has received a positive validation of the
CCASS Payment Instruction from CCASS; and

(b) the available balance in the Sending Member ’s CHATS Ledger Account for
the time being is sufficient to settle the CCASS Payment Instruction. This
provision shall not apply to CCASS Payment Instructions in the Pending
Queue.

6.3.3.2 In case the provisions of Rule 6.3.3.1 (b) cannot be complied with, the CCASS
Payment Instruction will remain in the Normal Queue until:

(a) the available balance in the Sending Member ’s CHATS Ledger Account is
sufficient to settle the CCASS Payment Instruction when it is first in priority
in the Normal Queue, and in such case, the CCASS Payment Instruction will
be effected automatically; or

(b) the CCASS Interim Cut-off or CCASS End of Day Cut-off (as the case may
be);

## Page 35

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 32

and a CCASS Interim Cut-off Payment not settled by CCASS Interim Cut -off or a
CCASS End of Day Cut -off Payment not settled by CCASS End of Day Cut -off, as
the case may be, will be cancelled automatically.

6.3.3.3 Subject to Rule 6.3.3.2, a CCASS Payment Instruction will be settled through CHATS
immediately upon the completion of its processing.

6.3.3.4 Settlement of a CCASS Payment Instruction will be effected across the books of MA
pursuant to Rule 3.1.3 by debiting the CHATS Ledger Account of the Sending
Member for the funds transferred and crediting the same to the CHATS Ledger
Account of the Receiving Member.

6.3.3.5 Subject to Rule 6.13.8 and save as provided for in the Operating Procedures in relation
to the CMU Optimiser Run , a Member shall be entitled to re -sequence the Normal
Queue or to transfer CCASS Payment Instructions from the Normal Queue to the
Pending Queue or vice versa or cancel any of its CCASS Payment Instructions in the
Normal Queue and the Pending Queue at any time prior to the CCASS Interim Cut -
off or CCASS End of Day Cut -off, as the case may be . This Rule 6.3.3.5 does not
apply to CCASS Payment Instructions in case of an emergency by reason of which
HKSCC rolls back the data for system recovery in accordance with Rule 6.9.2.

6.3.3.6 No CCASS Payment Instructions may be made requiring payment on a future date.

6.3.4 CCP Instructions

6.3.4.1 A CCP Instruction will not be effected or settled through CHATS except on a Working
Day between CCPMP Commencement and CCPMP Cut-off and unless:

(a) the Clearing House Computer has received a positive validation of the CCP
Instruction from CCPMP; and

(b) the available balance in the Sending Member ’s CHATS Ledger Account for
the time being is sufficient to settle the CCP Instruction. This provision shall
not apply to CCP Instructions in the Pending Queue.

6.3.4.2 If Rule 6.3.4.1 (b) is not complied with, the CCP Instruction will remain in the Normal
Queue until:

(a) the available balance in the Sending Member ’s CHATS Ledger Account is
sufficient to settle the CCP Instruction when it is first in priority in the Normal
Queue, and in such case, the CCP Instruction will be effected in accordance
with Rules 6.3.4.3 and 6.3.4.5;

(b) the CCP Instruction is being selected in an RTGS Liquidity Optimiser
process, and in such case, the CCP Instruction will be processed pursuant to
Rule 6.13; or

(c) either CCPMP Cut -off or CHATS Bank Cut -off, whichever is the earlier,
when the CCP Instruction will be cancelled automatically.

6.3.4.3 A hold up to the transaction amount will be applied to the Sending Member’s CHATS
Ledger Account as soon as (i) a CCP Instruction complies with Rule 6.3.4.1 or (ii) a
CCP Instruction is selected in an RTGS Liquidity Optimiser process (provided that
such CCP Instruction is not excluded pursuant to Rule 6.13.4) and such RTGS
Liquidity Optimiser process is completed successfully.

6.3.4.4 Subject to Rule 6.13.8 and save as provided for in the Operating Procedures in relation
to the CMU Optimiser Run , a Member shall be entitled to re -sequence the Normal
Queue of its CCP Instructions or to transfer CCP Instructions from the Normal Queue

## Page 36

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 33

to the Pending Queue or vice versa before the specified time as stipulated in the
Operating Procedures or cancel any of its CCP Instructions in the Normal Queue and
the Pending Queue at any time prior to such holding.

6.3.4.5 The funds held in the Sending Member’s CHATS Ledger Account under Rule 6.3.4.3
will only be released to the Receiving Member by debiting the Sending Member’s
CHATS Ledger Account and crediting the Receiving Member’s CHATS Ledger
Account by MA pursuant to Rule 3.1.3, if CCPMP confirms that the Corresponding
Payment will be settled at the same time.

6.3.4.6 The hold on the funds in the Sending Member’s CHATS Ledger Account will be
released if a notification to that effect is sent by CCPMP to the Clearing House
Computer, when CCPMP cannot confirm that the Corresponding Payment will be
settled at the same time.

6.3.4.7 Members may not give CCP Instructions Value Forward Day a value date later than
the last of the Supported Forward Days.

6.3.4.8 CCP Instructions Value Forward Day will be stored in the Clearing House Computer
on receipt. A hold of funds will only be applied pursuant to Rule 6.3.4.3 and in
accordance with Rule 6.3.4.1 after CHATS Commencement on the relevant Supported
Forward Day and settlement will only take place after the relevant funds have been
held and after CCPMP Commencement on the relevant Working Day, subject to Rule
6.3.4.9.

6.3.4.9 CCP Instructions for value as of a date on which the clearing house for the
Corresponding Payment is not open, will be rejected.

6.3.5 CHATS Optimiser Payment Instructions

6.3.5.1 A CHATS Optimiser Payment Instruction will be effected and settled through CHATS
simultaneously with the selected CCPO Instructions as stipulated in Rule 6.3. 9.3 and
the Bulk Clearing Settlement Run for CLG Items and e-Cheques.

6.3.5.2 A Sending Member should input CHATS Optimiser Payment Instructions according
to the timetable stipulated in the Operating Procedures so that such CHATS Optimiser
Payment Instructions can be extracted (“Extracted CHATS Optimiser Payment
Instructions”) and settled simultaneously with the CLG Items and e-Cheques.

6.3.5.3 The projected balance of a CHATS Ledger Account in respect of the Extracted
CHATS Optimiser Payment Instructions (taking into account payments or receipts by
virtue of CHATS Optimiser Payment Instructions, CCPO Instructions, CLG Items and
e-Cheques) will be computed in accordance with the formula stipulated in Operating
Procedures.

6.3.5.4 If the projected balance of a CHATS Ledger Account is found to be positive or zero,
the gross amount of each Extracted CHATS Optimiser Payment Instruction will be
effected automatically through CHATS and settled pursuant to Rule 3.1.3. If a
Member has a projected negative balance at the Final Cut-off time of a Bulk Clearing
Settlement Run, that Member will be treated as being in default in the Bulk Clearing
Settlement Run and the Default Arrangements set out in Schedule I shall apply.

6.3.5.5 A Sending Member may cancel its CHATS Optimiser Payment Instructions which
have not yet been extracted and settled. The extraction timetables are stipulated in the
Operating Procedures.

6.3.5.6 CHATS Optimiser Payment Instructions Value Today that are received by the
Clearing House Computer between the last payment extraction process of the day and
CHATS Bank Cut-off will be rejected by CHATS.

## Page 37

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 34

6.3.5.7 Members may not give CHATS Optimiser Payment Instructions Value Forward Day
a value date later than the last of the Supported Forward Days.

6.3.5.8 The validation rules for CHATS Optimiser Payment Instructions are stipulated in the
Operating Procedures.

6.3.6 CCASS Optimiser Payment Instructions

6.3.6.1 A CCASS Optimiser Payment Instruction will be effected and settled through CHATS
simultaneously with the Bulk Clearing Settlement Run for CCASS Participant Items.

6.3.6.2 A Sending Member should input CCASS Optimiser Payment Instructions to the
Clearing House Computer according to the timetable stipulated in the Operating
Procedures so that such CCASS Optimiser Payment Instructions can be extracted
(“Extracted CCASS Optimiser Payment Instructions”) and settled simultaneously with
the CCASS Participant Items.

6.3.6.3 The projected balance of a CHATS Ledger Account in respect of the Extracted
CCASS Optimiser Payment Instructions (taking into account payments or receipts by
virtue of CCASS Optimiser Payment Instructions and the CCASS Participant Items)
will be computed in accordance with the formula stipulated in Operating Procedures.

6.3.6.4 If the projected balance of a CHATS Ledger Account is found to be positive or zero,
the gross amount of each Extracted CCASS Optimiser Payment Instruction will be
effected automatically through CHATS and settled pursuant to Rule 3.1.3. If a
Member has a projected negative balance at the Final Cut-off time of a Bulk Clearing
Settlement Run, that Member will be treated as being in default in the Bulk Clearing
Settlement Run and the Default Arrangements set out in Schedule I shall apply.

6.3.6.5 A Sending Member may cancel its CCASS Optimiser Payment Instructions which
have not yet been extracted and settled. The extraction timetables are stipulated in the
Operating Procedures.

6.3.6.6 CCASS Optimiser Payment Instructions Value Today that are received by the Clearing
House Computer between the last payment extraction process of the day and CHATS
Bank Cut-off will be rejected by CHATS.

6.3.6.7 Members may not give CCASS Optimiser Payment Instructions Value Forward Day
a value date later than the last of the Supported Forward Days.

6.3.6.8 The validation rules for CCASS Optimiser Payment Instructions are stipulated in the
Operating Procedures.

6.3.7 SCCASS Optimiser Payment Instructions

6.3.7.1 A SCCASS Optimiser Payment Instruction will be effected and settled through
CHATS simultaneously with the Bulk Clearing Settlement Run for SCCASS
Participant Items.

6.3.7.2 A Sending Member should input SCCASS Optimiser Payment Instructions to the
Clearing House Computer according to the timetable stipulated in the Operating
Procedures so that such SCCASS Optimiser Payment Instructions can be extracted
(“Extracted SCCASS Optimiser Payment Instructions”) and settled simultaneously
with the SCCASS Participant Items.

6.3.7.3 The projected balance of a CHATS Ledger Account in respect of the Extracted
SCCASS Optimiser Payment Instructions (taking into account payments or receipts
by virtue of SCCASS Optimiser Payment Instructions and the SCCASS Participant

## Page 38

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 35

Items) will be computed in accordance with the formula stipulated in Operating
Procedures.

6.3.7.4 If the projected balance of a CHATS Ledger Account is found to be positive or zero,
the gross amount of each Extracted SCCASS Optimiser Payment Instruction will be
effected automatically through CHATS and settled pursuant to Rule 3.1.3. If a
Member has a projected negative balance at the Final Cut-off time of a Bulk Clearing
Settlement Run, that Member will be treated as b eing in default in the Bulk Clearing
Settlement Run and the Default Arrangements set out in Schedule I shall apply.

6.3.7.5 A Sending Member may cancel its SCCASS Optimiser Payment Instructions which
have not yet been extracted and settled. The extraction timetables are stipulated in the
Operating Procedures.

6.3.7.6 SCCASS Optimiser Payment Instructions Value Today that are received by the
Clearing House Computer between the last payment extraction process of the day and
CHATS Bank Cut-off will be rejected by CHATS.

6.3.7.7 Members may not give SCCASS Optimiser Payment Instructions Value Forward Day
a value date later than the last of the Supported Forward Days.

6.3.7.8 The validation rules for SCCASS Optimiser Payment Instructions are stipulated in the
Operating Procedures.

6.3.8 CLS Payment Instructions

6.3.8.1 A CLS Payment Instruction Value Today will not be effected or settled through
CHATS unless the available balance in the Sending Member ’s CHATS Ledger
Account for the time being is sufficient to make the payment referred to in such
payment instruction. In case the available balance in the relevant Sending Member ’s
CHATS Ledger Account is insufficient to make such payment, the relevant CLS
Payment Instruction Value Today, unless subsequently cancelled, will remain in the
Normal Queue until either:

(a) such time as the available balance is sufficient to meet such payment
instruction when it is first in priority in the Normal Queue, and in such case,
the CLS Payment Instruction Value Today will be effected automatically; or

(b) the CHATS Bank Cut -off and in such case, the CLS Payment Instruction
Value Today will be cancelled automatically.

This provision shall not apply to CLS Payment Instructions Value Today in the
Pending Queue.

6.3.8.2 Subject to Rule 6.3.8.1, a funds transfer initiated by a CLS Payment Instruction Value
Today will be settled through CHATS immediately upon the completion of its
processing.

6.3.8.3 In a case to which Rule 6.3.8.1(a) applies, the relevant CLS Payment Instruction Value
Today will be settled through CHATS immediately upon the completion of its
processing.

6.3.8.4 Settlement of a CLS Payment Instruction Value Today will be effected across the
books of MA pursuant to Rule 3.1.3 by debiting the CHATS Ledger Account of the
Sending Member for the funds transferred and crediting the same to the CHATS
Ledger Account of the Receiving Member.

6.3.8.5 Subject to Rule 6.13.8 and save as provided for in the Operating Procedures in relation
to the CMU Optimiser Run , a Member (except CLS Bank) shall be entitled to re -

## Page 39

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 36

sequence the Normal Queue of its CLS Payment Instructions Value Today at any time
prior to the CHATS Bank Cut-off or transfer CLS Payment Instructions Value Today
from the Normal Queue to the Pending Queue or vice versa before the specified time
as stipulated in the Operating Procedures . However, subject to Rule 6.13.8 and save
as provided for in the Operating Procedures in relation to the CMU Optimiser Run , a
Member can only cancel its CLS Payment Instructions Value Today in the Normal
Queue and the Pending Queue up to the CHATS Customer Cut-off time.

6.3.8.6 Members may not give CLS Payment Instructions Value Forward Day a value date
later than the last of the Supported Forward Days.

6.3.8.7 CLS Payment Instructions Value Forward Day will be stored in the Clearing House
Computer and will not be processed or settled until the value day specified.

6.3.8.8 CLS Payment Instruction Value Forward Day will be automatically processed for
settlement after the CHATS Commencement on the relevant Supported Forward Day
(“Value Day”) in the same way and manner as CLS Payment Instructions Value Today
received by the Clearing House Computer during that Value Day and all provisions in
Rules 6.3.8.1 to 6.3.8.5 shall apply.

6.3.8.9 CHATS will reject CLS Payment Instructions from/to those Members who are not
CLS Participants.

6.3.8.10 CHATS will reject CLS Payment Instructions with a value date falling on a day which
is not a Working Day.

6.3.9 CCPO Instructions

6.3.9.1 A CCPO Instruction should be input by a Sending Member according to the
requirements as stipulated in the Operating Procedures.

6.3.9.2 A CCPO Instruction will be effected and settled through CHATS simultaneously with
the Extracted CHATS Optimiser Payment Instructions as stipulated in Rule 6.3.5.2
and the Bulk Clearing Settlement Run for CLG Items and e -Cheques when the
Clearing House Computer has received a positive validation of the CCPO Instruction
from CCPMP.

6.3.9.3 At the time of commencement of the Bulk Clearing Settlement Run for CLG Items
and e-Cheques, only those CCPO Instructions for which CCPMP confirms that the
Corresponding Payment will be settled at the same time will be selected (“Selected
CCPO Instructions”).

6.3.9.4 The projected balance of a CHATS Ledger Account in respect of the Selected CCPO
Instructions (taking into account payments or receipts by virtue of Selected CCPO
Instructions, CHATS Optimiser Payment Instructions, CLG Items and e-Cheques) will
be computed in accordance with the formula stipulated in the Operating Procedures.

6.3.9.5 If the projected balance of a CHATS Ledger Account is found to be positive or zero,
the gross amount of each Selected CCPO Instruction will be effected automatically
through CHATS and settled pursuant to Rule 3.1.3. If a Member has a projected
negative balance at the Final Cut -off time of a Bulk Clearing Settlement Run, that
Member will be treated as being in default in the Bulk Clearing Settlement Run and
the Default Arrangements set out in Schedule I shall apply.

6.3.9.6 Any CCPO Instruction Value Today that has not been settled will be cancelled at the
CHATS Bank Cut-off or CCPMP Cut-off, whichever shall first occur.

6.3.9.7 CCPO Instructions Value Forward Day will be stored in the Clearing House Computer
on receipt. Such instructions will be processed on the relevant Supported Forward

## Page 40

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 37

Day in the same way and manner as stipulated in Rules 6.3.9.3 and 6.3.9.6.

6.3.9.8 Members may not give CCPO Instructions Value Forward Day a value date later than
the last of the Supported Forward Days.

6.3.10 Direct Debit Instruction Value Today

6.3.10.1 A Direct Debit Instruction Value Today will be settled immediately in case the
available balance in the Member’s CHATS Ledger Account for the time being is
sufficient to make the payment referred to in such payment instruction. In case the
available balance in the relevant Member’s CHATS Ledger Account is insufficient to
make such payment, the relevant Direct Debit Instruction Value Today unless
subsequently cancelled, will remain in the Normal Queue (ahead of the other CHATS
Transactions (other than CHATS Transactions in respect of Articles)) until either:

(a) such time as the available balance is sufficient to meet such payment instruction
when it is first in priority in the Normal Queue, and in such case, the Direct Debit
Instruction Value Today will be effected automatically; or

(b) the End of Day Cut -off and in such case, the Direct Debit Instruction Value
Today will be cancelled automatically.

6.3.10.2 Subject to Rule 6.3. 10.1, a payment initiated by a Direct Debit Instruction Value
Today will be settled through CHATS immediately upon the completion of its
processing.

6.3.10.3 In a case to which Rule 6.3.10.1(a) applies, the relevant Direct Debit Instruction Value
Today will be settled through CHATS immediately upon the completion of its
processing.

6.3.10.4 Settlement of a Direct Debit Instruction Value Today will be effected across the books
of MA pursuant to Rule 3.1.3 by debiting the CHATS Ledger Account for the payment.

6.3.10.5 Subject to Rule 6.13.8, MA shall be entitled to re -sequence the Normal Queue of
Direct Debit Instruction Value Today or cancel any of the Direct Debit Instructions
Value Today in the Normal Queue at any time prior to the End of Day Cut-off.

6.3.10.6 Rules 6.3.10.1 to 6.3.10.5 shall in all respects be subject to the arrangements provided
for in the Operating Procedures in relation to the CMU Optimiser Runs and to that
extent the Operating Procedures shall prevail over Rules 6.3.10.1 to 6.3.10.5.

6.3.11 Direct Debit Instruction Value Forward Day

6.3.11.1 Direct Debit Instruction Value Forward Day will be stored in the Clearing House
Computer and will not be processed or settled until the relevant Supported Forward
Day.

6.3.11.2 Direct Debit Instruction Value Forward Day will be automatically processed for
settlement after the CHATS Commencement on the relevant Supported Forward Day
(“Value Day”) in the same way and manner as Direct Debit Instruction Value Today
received by the Clearing House Computer during that Value Day and all provisions in
Rule 6.3.10 shall apply.

6.3.12 Direct Credit Instruction Value Today

6.3.12.1 A payment initiated by a Direct Credit Instruction Value Today will be settled through
CHATS immediately upon the completion of its processing.

6.3.12.2 Settlement of a Direct Credit Instruction Value Today will be effected across the books

## Page 41

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 38

of MA pursuant to Rule 3.1.3 by crediting the CHATS Ledger Account for the
payment.

6.3.13 Direct Credit Instruction Value Forward Day

6.3.13.1 Direct Credit Instruction Value Forward Day will be stored in the Clearing House
Computer and will not be processed or settled until the relevant Supported Forward
Day.

6.3.13.2 Direct Credit Instruction Value Forward Day will be automatically processed for
settlement after the CHATS Commencement on the relevant Supported Forward Day
(“Value Day”) in the same way and manner as Direct Credit Instruction Value Today
received by the Clearing House Computer during that Value Day and all provisions in
Rule 6.3.12 shall apply.

6.3.14 OTC Clear Payment Instruction

6.3.14.1 Only Members who have registered with HKICL in accordance with the Operating
Procedures to participate in the money settlement of OTC Clear Payment Instructions
via CHATS may so participate.

6.3.14.2 OTC Clear will make OTC Clear Debit Requests according to the Operating
Procedures. An OTC Clear Debit Request transmitted or delivered by OTC Clear to
the Clearing House Computer will be validated in accordance with the validation
criteria stipulated in the Operating Procedures. An OTC Clear Payment Instruction
Value Today or OTC Clear Payment Instruction Value Forward Day will be generated
according to the intended value day referred to in the corresponding OTC Clear Debit
Request. For the avoidance of doubt, an OTC Clear Debit Request which requests for
the generation of an OTC Clear Payment Instruction Value Today received after the
CHATS Bank Cut-off will be rejected.

6.3.14.3 OTC Clear Payment Instruction Value Today

(a) An OTC Clear Payment Instruction Value Today generated in accordance with
Rule 6.3.14.2 will be added to the Normal Queue or Pending Queue of the relevant
Member according to the criteria stipulated in the Operating Procedures.

(b) An OTC Clear Payment Instruction Value Today in the Normal Queue will not
be effected or settled through CHATS unless the available balance in the paying
Member’s CHATS Ledger Account for the time being is sufficient to make the
payment referred to in such payment instruction. In case the available balance in
the relevant paying Member’s CHATS Ledger Account is insufficient to make
such payment, the relevant OTC Clear Payment Instruction Value Today, unless
subsequently cancelled, will remain in the Normal Queue until either:

(i) such time as the available balance is sufficient to meet such payment
instruction when it is first in priority in the Normal Queue, and in such case,
the OTC Clear Payment Instruction Value Today will be effected
automatically; or

(ii) the CHATS Value Date Cut -off and in such case, the OTC Clear Payment
Instruction Value Today will be cancelled automatically.

This provision shall not apply to OTC Clear Payment Instructions Value Today
in the Pending Queue.

(c) Subject to Rule 6.3. 14.3(b), a funds transfer initiated by an OTC Clear Payment
Instruction Value Today will be settled through CHATS immediately upon the
completion of its processing.

## Page 42

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 39

(d) In a case to which Rule 6.3. 14.3(b)(i) applies, the relevant OTC Clear Payment
Instruction Value Today will be settled through CHATS immediately upon the
completion of its processing.

(e) Settlement of an OTC Clear Payment Instruction Value Today will be effected
across the books of MA pursuant to Rule 3.1.3 by debiting the CHATS Ledger
Account of the paying Member for the funds transferred and crediting the same
to the CHATS Ledger Account of a bank Member designated by OTC Clear in
accordance with the Operating Procedures.

(f) A paying Member shall be entitled to re -sequence the Normal Queue of its OTC
Clear Payment Instructions Value Today at any time prior to the CHATS Value
Date Cut-off or to transfer OTC Clear Payment Instructions Value Today from
the Normal Queue to the Pending Queue or vice versa before the specified time
as stipulated in the Operating Procedures . However, a paying Member can only
cancel its OTC Clear Payment Instructions Value Today in the Normal Queue and
the Pending Queue up to the CHATS Customer Cut-off time. This Rule 6.3.14.3(f)
is subject to Rule 6.13.8.

(g) Rules 6.3. 14.3(a) to (f) shall in all respects be subject to the arrangements
provided for in the Operating Procedures in relation to the CMU Optimiser Runs
and to that extent the Operating Procedures shall prevail over Rules 6.3.14.3(a) to
(f).

6.3.14.4 OTC Clear Payment Instruction Value Forward Day

(a) An OTC Clear Debit Request for the generation of an OTC Clear Payment
Instruction Value Forward Day for effecting payments through CHATS may not
be made for value dates later than the last of the Supported Forward Days.

(b) OTC Clear Payment Instructions Value Forward Day will be stored in the
Clearing House Computer and will not be processed or settled until the value day
specified.

(c) OTC Clear Payment Instruction Value Forward Day will be automatically
processed for settlement after the CHATS Commencement on the relevant
Supported Forward Day (“Value Day”) in the same way and manner as OTC Clear
Payment Instructions Value Today generat ed during that Value Day and all
provisions in Rule 6.3.14.3 shall apply.

6.3.14.5 In the event that an OTC Clear Payment Instruction is cancelled by the paying Member
or by the system in accordance with the Operating Procedures, MA and HKICL are
not responsible and not liable to OTC Clear or the paying Member concerned for such
cancellation and any claim, loss, damage, expense or other consequences directly or
indirectly resulting from the cancellation.

6.3.15 BOJ DvP Payment Instructions

6.3.15.1 After CHATS Commencement, a BOJ DvP Payment Instruction may be input only by
a Member at any time between the BOJ DvP Processing Window Open and the BOJ
DvP Payment Cut -off on a Working Day and shall be for a funds transfer through
CHATS for value as of that Working Day. For the avoidance of doubt, BOJ DvP
Payment Instructions input before CHATS Commencement will be rejected by
CHATS.

6.3.15.2 As from a BOJ DvP Processing Window Open until the following BOJ DvP Payment
Cut-off, a BOJ DvP Payment Instruction which has been validated by CHATS and
BOJ-NET JGB Services will be put in the Normal Queue or the Pending Queue as

## Page 43

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 40

requested by the Sending Member , and will be pending for funds to be held . If the
available balance in the Sending Member’s CHATS Ledger Account is sufficient to
settle the BOJ DvP Payment Instruction when it is first in priority in the Normal Queue,
a hold up to the transaction amount will thereupon be applied to the Sending Member’s
CHATS Ledger Account.

6.3.15.3 Within the BOJ DvP Processing Window of the Working Day, if BOJ -NET JGB
Services confirm that the corresponding security transaction will be settled at the same
time, the Held Funds will be released to the Receiving Member by debiting the
Sending Member’s CHATS L edger Account and crediting the Receiving Member’s
CHATS Ledger Account by MA pursuant to Rule 3.1.3. If before the BOJ DvP
Processing Window Close BOJ -NET JGB Services notif y CHATS that the
corresponding security transaction will not be settled, the Held Funds will be released
to the Sending Member. At the BOJ DvP Payment Cut -off of the Working Day, all
BOJ DvP Payment Instructions in relation to which funds are not held will be cancelled.

6.3.15.4 A BOJ DvP Payment Instruction cannot be cancelled by a Member after validation by
CHATS and BOJ-NET JGB Services.

6.3.15.5 Save as provided for in the Operating Procedures in relation to the CMU Optimiser
Run, the Member may re -sequence a BOJ DvP Payment Instruction or transfer such
instructions from the Normal Queue to the Pending Queue or vice versa, via MBT.
For the avo idance of doubt, a BOJ DvP Payment Instruction for which funds have
been held in accordance with Rule 6.3.15.2 above cannot be re-sequenced.

6.3.15.6 At the BOJ DvP Processing Window Close, all BOJ DvP Payment Instructions in
relation to which funds are held but are not settled will be cancelled , and Held Funds
will be released to the Sending Member.

6.3.15.7 Each Member agrees with MA and HKICL that:

(a) MA and HKICL shall not be held liable for verifying the correctness, origin or
integrity of the contents of any BOJ DvP Payment Instruction which involves a
DvP linkage between the Clearing House Computer and BOJ-NET JGB Services
(“BOJ-NET Linkage”);

(b) in respect of a BOJ DvP Payment Instruction, the provisions of these Rules shall
govern that part of the BOJ -NET Linkage which is operated by HKICL, and the
BOJ-NET JGB Services Rules shall govern that part of BOJ-NET Linkage which
is operated by the B OJ. Each Member acknowledges that these Rules and the
BOJ-NET JGB Services Rules may be amended in accordance with these Rules
and the BOJ-NET JGB Services Rules respectively from time to time;

(c) MA and HKICL shall not owe any duty or incur any liability to any Member, or
the customers of such Member or any other person who uses the BOJ -NET
Linkage through such Member in respect of any claim, loss, damage or expense
(including without limitation, loss of business, loss of business opportunity, loss
of profit, special, indirect or consequential loss, even if the MA and HKICL knew
or ought reasonably to have known of their possible existence) of any kind or
nature whatsoever arising in whatever ma nner directly or indirectly out of or in
connection with the BOJ -NET Linkage, the contents of messages input into the
BOJ-NET Linkage, the use of the BOJ -NET Linkage, the operation or
malfunction of computer systems, equipment (including without limitation , the
host system and the front -end computer programs), software (including without
limitation, BOJ-NET JGB Services) or hardware used in respect of the BOJ-NET
Linkage, the processing of Held Funds in emergencies or otherwise, the provision
of DvP settlem ent service for any security transactions under the BOJ -NET
Linkage, or as a result of the giving of any consent, notice, instruction, advice or
approval in relation or pursuant to these Rules by MA or HKICL;

## Page 44

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 41

(d) in respect of a BOJ DvP Payment Instruction which involves the BOJ -NET
Linkage, the law relating to finality of settlement (if any) which applies to BOJ -
NET JGB Services may be different from the finality of settlement provisions
provided in the PSSVFO and the PSSVFO does not apply to BOJ -NET JGB
Services; MA and HKICL shall incur no liability to any Member or the customers
of such Member or any other person who uses the BOJ -NET Linkage through
such Member in respect of any claim, loss, damage or expense (including without
limitation, loss of business, loss of business opportunity, loss of profit, special,
direct or consequential loss, even if the MA and HKICL knew or ought reasonably
to have known of their possible existence) of any kind or nature whats oever
arising in whatever manner directly or indirectly out of or in connection with any
difference between the law relating to finality of settlement (if any) of the
jurisdiction of Japan and of Hong Kong;

(e) MA and HKICL shall not be liable for any claim, loss, damage or expense arising
in whatever manner directly or indirectly out of or in connection with any defect
in title in relation to any securities transferred to a Member or the customers of
such Member or any other person who uses the BOJ -NET Linkage through such
Member; and

(f) each Member shall procure that the customers of such Member and any other
person who uses the BOJ -NET Linkage through its participation in such BOJ -
NET Linkage agree to the foregoing.

6.3.16 CCPMPNet Payment Instruction

6.3.16.1 A CCPMPNet Payment Instruction should be input by a Sending Member according
to the requirements as stipulated in the Operating Procedures. Any CCPMPNet
Payment Instructions with value date being the current Working Day input after the
input cut-off time as stipulated in the Operating Procedures will be rejected, while
CCPMPNet Payment Instructions Value Forward Day will still be accepted.

6.3.16.2 A CCPMPNet Payment Instruction will not be selected for settlement in a
CCPMPNet Settlement Run at the appointed time as set out in the Operating
Procedures unless:

(a) the Clearing House Computer has received a positive validation of the
CCPMPNet Payment Instruction from CCPMP; and

(b) such CCPMPNet Payment Instruction and the corresponding CCPMPNet
Payment Instruction in another relevant currency have been validated by
CHATS according to the validation rules as stipulated in the Operating
Procedures.

The CCPMPNet Payment Instructions selected for settlement pursuant to this Rule
6.3.16.2 shall be referred to as “Selected CCPMPNet Payment Instruction” in this
Rule 6.3.16 and Rule 6.3.17. Any CCPMPNet Payment Instructions Value Today
which is not selected for settlement pursuant to this Rule 6.3.16.2 will be cancelled
by CHATS at such appointed time as stipulated in the Operating Procedures.

6.3.16.3 At the time of commencement of the CCPMPNet Settlement Run, the total net
settlement amount of each Member will be computed (taking into account the
amount payables and receivables of the Selected CCPMPNet Payment Instructions
and the Extracted CC PMPNet Optimiser Payment Instructions as defined in Rule
6.3.17.2) in accordance with the formula stipulated in the Operating Procedures.

6.3.16.4 A hold will be applied to earmark funds in the Settlement Account of a Member, in
an amount equal to the total net debit settlement amount computed pursuant to Rule

## Page 45

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 42

6.3.16.3 payable by such Member.

6.3.16.5 If (i) all relevant Members have sufficient funds in their Settlement Accounts and
(ii) the Clearing House Computer confirms that the Corresponding CCPMPNet
Settlement Runs will be effected at the same time, settlement of the CCPMPNet
Settlement Runs will be effected immediately. The total net settlement amount of
each Member computed pursuant to Rule 6.3.16.3 will be settled through CHATS
pursuant to Rule 3.1.3.

6.3.16.6 If one or more Member(s) is/are short of funds when applying the hold to earmark
the total net debit settlement amount pursuant to Rule 6.3.16.4, HKICL will re -try
in accordance with the arrangement as stipulated in the Operating Procedures. For
the avoidance of doubt, the funds held in the Settlement Accounts of the relevant
Members under Rule 6.3.16.4 will only be released upon completion or
rescheduling of the CCPMPNet Settlement Run.

6.3.16.7 If a previous Bulk Clearing Settlement Run in Hong Kong Dollar or in any other
relevant currency of the Corresponding CCPMPNet Settlement Run s is still in
progress by the time of commencement of the CCPMPNet Settlement Run, the
CCPMPNet Settlement Run and the Corresponding CCPMPNet Settlement Runs
shall be rescheduled in accordance with the arrangement as stipulated in the
Operating Procedures. For the avoidance of doubt, the hold to earmark funds in the
Settlement Account of a Member will not be applied until the commencement of
the rescheduled CCPMPNet Settlement Run.

6.3.16.8 Selected CCPMPNet Payment Instructions that have not been settled in the
CCPMPNet Settlement Run will be converted to CCP Instructions in accordance
with the arrangements as set out in the Operating Procedures.

6.3.16.9 Sending Members may not give CCPMPNet Payment Instructions Value Forward
Day a value date later than the last of the Supported Forward Days.

6.3.16.10 CCPMPNet Payment Instructions Value Forward Day will be stored in the Clearing
House Computer on receipt. Such instructions will be processed on the relevant
Supported Forward Day in the same way and manner as stipulated in this Rule
6.3.16.

6.3.17 CCPMPNet Optimiser Payment Instructions

6.3.17.1 A CCPMPNet Optimiser Payment Instruction should be input by a Sending
Member according to the requirements as stipulated in the Operating Procedures.
Any CCPMPNet Optimiser Payment Instructions with value date being the current
Working Day input after the extraction time as stipulated in the Operating
Procedures will be rejected, while CCPMPNet Optimiser Payment Instructions
Value Forward Day will still be accepted.

6.3.17.2 CCPMPNet Optimiser Payment Instructions will be extracted (“Extracted
CCPMPNet Optimiser Payment Instructions”) according to the extraction
timetables as stipulated in the Operating Procedures and settled simultaneously with
the Selected CCPMPNet Payment Instructions in the CCPMPNet Settlement Run
in accordance to Rule 6.3.16.3 to Rule 6.3.16.5.

6.3.17.3 Any CCPMPNet Optimiser Payment Instruction Value Today that has not been
settled will be cancelled at the CHATS Value Date Cut-off.

6.3.17.4 Sending Members may not give CCPMPNet Optimiser Payment Instructions Value
Forward Day a value date later than the last of the Supported Forward Days.

6.3.17.5 CCPMPNet Optimiser Payment Instructions Value Forward Day will be stored in

## Page 46

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 43

the Clearing House Computer on receipt. Such instructions will be processed on
the relevant Supported Forward Day in the same way and manner as stipulated in
this Rule 6.3.17.

6.4 Input Transactions

CHATS Transactions (other than CHATS Transactions in respect of Articles) may only be input by
Members addressed to themselves, other Members, MA or the Clearing House Computer or by virtue of
a Special Posting or End of Day Net Settlement.

6.5 CHATS Customer Cut -off, CHATS Bank Cut -off, CHATS Value Date Cut -off, CCASS
Commencement, CCASS Interim Cut-off, CCASS End of Day Cut-off and CCPMP Cut-off

6.5.1 The current time and arrangements for CHATS Customer Cut -off, CHATS Bank Cut -off,
CHATS Value Date Cut-off and CCPMP Cut-off are set out in Schedule II.

6.5.2 HKICL shall be entitled to extend a CHATS Customer Cut -off, CHATS Bank Cut -off and
CHATS Value Date Cut-off in the circumstances provided in Rule 6.9.1.

6.5.3 Subject to any exceptional circumstances , the CHATS Customer Cut -off, CHATS Bank Cut -
off and CHATS Value Date Cut -off will proceed as normal in accordance with these Rules
notwithstanding any typhoon, rainstorm or Extreme Conditions.

6.5.4 The current time and arrangements for CCASS Interim Cut-off and CCASS End of Day Cut -
off are set out in Schedule II. One month ’s prior notice will be given of any variation to
Schedule II.

6.5.5 The CCASS Commencement, CCASS Interim Cut -off or CCASS End of Day Cut -off will
continue in accordance with these Rules notwithstanding any typhoon, rainstorm or Extreme
Conditions.

6.5.6 The CCPMP Cut-off will continue in accordance with these Rules notwithstanding any typhoon,
rainstorm or Extreme Conditions.

6.5.7 To ensure that CLS Bank can successfully complete its settlement services, CLS Bank may
with the prior approval of MA occasionally request HKICL to extend the CHATS Bank Cut -
off and the CHATS Value Date Cut -off. HKICL shall comply with any such request to the
extent reasonably practicable.

6.6 Returns of CHATS Transactions (other than those in respect of Articles)

6.6.1 All returns of CHATS Transactions (other than CHATS Transaction s in respect of Articles)
should be effected through CHATS not later than the time appointed by HKICL, such time
currently being prior to the CHATS Customer Cut -off for CHATS Transactions which are
customer related and CHATS Bank Cut -off for CHATS Transacti ons which are not customer
related in each case of the Working Day immediately following the date of the original transfer,
and must include in the text of the transfer the information as stipulated in the Operating
Procedures.

6.6.2 A return of a CHATS Transaction (other than a CHATS Transaction in respect of Articles) may
only be initiated by the Receiving Member of the transfer. If a Receiving Member is unable to
apply funds from a credit transfer for any reason, then that Receiving Member must send the
funds actually received through CHATS back to the original Sending Member in accordance
with the procedure set out in Rule 6.6.1.

6.7 Responsibility of Members

In addition to the other provisions of these Clearing House Rules, each Member shall be responsible for
the following matters:

## Page 47

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 44

6.7.1 the control of access by Members to the MBT and the security of the Member’s terminal(s) (in
the case of the eMBT) connecting to SWIFT and the eMBT or (in the case of the iMBT)
connecting to the HKICL network and/or internet, as the case may be, and the iMBT (including
security and confidentiality of passwords or other systems to ensure that only authorised
personnel of Members may access the MBT) (and in the case of CLS Bank, the terminals of the
CLS System), and lines, modems and other computer equipment relating thereto of the Member
and the security of the transmission lines between the Clearing House Computer and the
Member’s terminals having access to the MBT (and in the case of CLS Bank, the terminals of
the CLS System);

6.7.2 the operation of all equipment and software relating to the access to the eMBT and terminal(s)
connecting to SWIFT, or relating to the access to the iMBT and the terminal(s) connecting to
the HKICL network and/or internet, as the case may be (and in the case of CLS Bank, the
terminals of the CLS System);

6.7.3 ensuring that:

(a) the access to and/or use of the MBT is in full compliance with these Rules; and

(b) all data transmitted from terminals owned by, or under its control, through which it
gains access to the MBT:

(i) do not infringe the copyright or other intellectual property rights of third
parties; and

(ii) do not create and/or introduce into the Clearing House Computer any virus,
worms, trojan horses or other destructive or contaminating program or codes;
and

(c) all data, including Personal Data, retrieved, obtained and archived from the Clearing
House and/or the Clearing Facilities shall be used solely for the purpose of operation
of the Clearing House and/or the Clearing Facilities in accordance with these Clearing
House Rules and the Operating Procedures, that no such Personal Data is used for any
other purpose, including without limitation, direct marketing and that use of such data
is in full compliance with the relevant laws and regulations in Hong Kong; and

it shall indemnify and hold HKICL, MA and other Members harmless against the consequences
of breach of any of the obligations under this Rule 6.7.3;

6.7.4 delay or non-delivery of CHATS Transactions (other than CHATS Transactions in respect of
Articles) where the delay is due to force majeure or technical failure caused by act or omission
of any carrier (including, for the avoidance of doubt, SWIFT);

6.7.5 the correct dispatch to the Clearing House Computer and the correct receipt by the Clearing
House Computer of all CHATS Payment Instructions, CCASS Payment Instructions, CCASS
Optimiser Payment Instructions, SCCASS Optimiser Payment Instructions, CHATS Optimiser
Payment Instructions, CCP Instructions, CCPO Instructions, CCPMPNet Payment Instructions,
CCPMPNet Optimiser Payment Instructions, CLS Payment Instructions , BOJ DvP Payment
Instructions and CHATS Transactions (other than CHATS Transactions in respect of Articles);

6.7.6 any loss incurred due to a fraudulent transfer originating from a Member or the fraudulent
insertion or alteration of a transfer between a Member and the Clearing House Computer;

6.7.7 the verification of the transfer result as shown in the MBT received from the Clearing House
Computer before the processing of the transfer. If the result is not in order the Receiving
Member must immediately effect a return of the transfer quoting the original transaction details
and giving the reason for the return. If the transfer is returned to the Sending Member after the
CHATS Customer Cut -off for CHATS Transactions which are customer related and CHATS

## Page 48

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 45

Bank Cut-off for CHATS Transactions which are not customer related in each case immediately
following the input of the transfer then any loss of interest is for the account of the Sending
Member subject to Rules 6.7.8 and 6.7.9;

6.7.8 as a Sending Member, Delayed Payments in the following circumstances:

(a) if the transfer has not been accepted by the Clearing House Computer;

(b) if the Sending Member addresses a transfer incorrectly; and/or

(c) if the Sending Member ignores Clearing House Computer generated messages
concerning the operational system;

6.7.9 as a Receiving Member, Delayed Payments in the following circumstances:

(a) if the Receiving Member ignores Clearing House Computer generated messages
concerning the operational system;

(b) if the Receiving Member (except CLS Bank) does not reconcile its settlement total as
supplied by the Clearing House Computer as shown in the MBT or through SWIFT
and accounting totals to ensure receipt of all CHATS Transactions (other than CHATS
Transactions in respect of Articles) involving funds transfers;

(c) if a Receiving Member (except CLS Bank) is not connected to the MBT or a Receiving
Member is not connected to the SWIFT network or unable to receive information
relating to transfers; and/or

(d) if CLS Bank does not reconcile its settlement total as supplied by the Clearing House
Computer with its own record and accounting totals to ensure receipt of all CLS Pay -
ins;

6.7.10 such Member’s failure to report discrepancies for CHATS Transactions (other than CHATS
Transactions in respect of Articles) as shown in the MBT to the Officer-in-Charge of HKICL
within two hours of a CHATS Value Date Cut-off (this provision does not apply to CLS Bank).

6.8 Responsibility of Service Provider

6.8.1 A Member may register as a Service Provider with HKICL and once its registration is
successful, it shall provide HKICL with a list of its correspondent banks in accordance with the
schedules and requirements specified in the Operating Procedures.

6.8.2 When a Service Provider provides HKICL with any information relating to it, in its capacity as
a Service Provider, and its correspondent banks (including, without limitation, any lists and
other information provided under Rule 6.8.1):

(a) it will take all reasonable steps to ensure the correctness of such information and in
particular, but without limitation, the correctness of any such information provided in
Electronic Media;

(b) it will authorise HKICL to disclose such information to HKICL’s sub -contractor for
the posting of such information on HKICL’s website and to other Members or other
persons; and

(c) it will indemnify HKICL and MA against all liabilities and expenses incurred by either
of them arising out of or in relation to its failure to comply with Rule 6.8.2(a).

6.8.3 Notwithstanding the provisions of Rule 6.8.2, HKICL and MA shall incur no liability to any
Members or any other persons arising out of or in relation to any information relating to Service
Providers and their correspondent banks appearing on the HKICL’s website.

## Page 49

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 46

6.8.4 A Service Provider which receives a Regional CHATS Payment for the account of one of its
correspondent banks shall promptly on receipt thereof pay the amount of that Regional CHATS
Payment to the relevant correspondent bank.

6.8.5 For the avoidance of doubt, (a) any funds transfer by a Service Provider to a correspondent
bank for the purposes of a Regional CHATS Payment will not be effected through CHATS, and
(b) except as provided for in Rule 6.8.4, these Rules shall not apply to any such transfer. Neither
HKICL nor MA shall incur any liability arising out of or in relation to any such transfer or a
Service Provider’s delay or failure to pay a Regional CHATS Payment to a correspondent bank
and the relevant Service Provider sh all indemnify HKICL and MA in respect of all liability
incurred by either of them arising out of or in relation to any such transfer or by reason of any
such delay or failure.

6.8.6 A correspondent bank of a Service Provider shall not be a Member and shall have no rights or
obligations vis-à-vis Members, MA or HKICL. All rights and obligations vis -à-vis Members,
MA or HKICL arising out of or in relation to the making of a Regional CHATS Payment shall
be the rights and obligations of the Member making the Regional CHATS Payment and the
Service Provider receiving it.

6.9 Emergencies

6.9.1 In the event that communications between the Clearing House Computer and the SWIFT
network, between the SWIFT network and one or more of the Members, between the Clearing
House Computer and CCASS, between the Clearing House Computer and CCPMP, between
the Clearing House Computer and the CLS System, between the Clearing House Computer and
BOJ-NET JGB Services or between the Clearing House Computer and OTC Clear are halted,
or if the Clearing House Computer, CCASS , the CLS System, BOJ-NET JGB Services, the
SWIFT network or OTC Clear system is closed down, or if some other emergency affects its
operation, CHATS Transactions (other than CHATS Transactions in respect of Articles) shall
be handled in accordance with the Operating Procedures or, if applicable, (where permitted) by
virtue of a Special Posting or End of Day Net Settlement. HKICL may, at its own discretion or
under the instruction of MA:

(a) extend the CHATS Customer Cut -off and/or CHATS Bank Cut -off and/or CHATS
Value Date Cut-off and/or CCPMP Cut-off;

(b) direct any, all or some of the Members not to make payments through CHATS
awaiting resolution of the problem; and/or

(c) direct such other action as it may deem necessary or as required by the Committee or
MA.

For any Held Funds, MA, after confirmation with the BOJ-NET JGB Services, may manually
process the Held Funds to release the Held Funds to the Sending Member or the Recei ving
Member (as the case may be ). In the event that the BOJ-NET JGB Services cannot confirm
that the corresponding security transactions will be settled, Held Funds will be released to the
Sending Member at a time pre -defined by MA as stipulated in Operating Procedures. Any
obligation of MA to hold any funds shall be discharged thereupon notwithstanding anything
provided in Rule 6.3.15.

6.9.2 If following an emergency HKSCC requires to roll back the data for system recovery all
CCASS Payment Instructions in the Normal Queue and the Pending Queue will be cancelled in
accordance with the Operating Procedures.

6.9.3 During any such emergency all Members should limit their communications through the
Clearing House Computer and with HKICL to those which are essential.

6.9.4 In the event that the communication link between the Clearing House Computer and the CLS

## Page 50

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 47

System fails, the following contingency measures will apply:

6.9.4.1 Handling of CLS Pay-outs

(a) CLS Bank will send CLS Pay-out details to the Clearing House in message file
format via CBCA.

(b) Based on the message file received from CLS Bank , HKICL will capture the
CLS Payment Instructions and trigger Special Posting for the affected CLS Pay-
outs.

(c) After the CLS Pay-outs have been successfully settled, HKICL will send debit
advices to CLS Bank according to the arrangement as stipulated in the Operating
Procedures.

6.9.4.2 Handling of CLS Pay-ins

(a) At regular time intervals as agreed with CLS Bank from time to time, HKICL
will produce a report detailing the CLS Pay-ins in a pre-defined format and send
the report to CLS Bank via CBCA.

(b) HKICL will continue sending various advices to CLS Bank via SWIFT such
that CLS Bank will receive the advices after its communication link resumes.

6.9.4.3 When CLS Bank delivers to the Clearing House information relating to CLS Pay-outs
in message file format via CBCA:

(a) it will be responsible for the correctness of the contents in the message file; and

(b) it will indemnify HKICL and MA against all liabilities and expenses incurred
by either of them arising out of or as a result of any error in instructions or
discrepancy between such information and the original instruction.

6.9.4.4 CLS Bank shall be responsible for the proper functioning of the CBCA and shall
ensure that all messages generated pursuant to this Rule will comply with the relevant
requirements as set out in the Operating Procedures.

6.9.4.5 For the avoidance of doubt, this Rule shall not apply in the event that End of Day Net
Settlement is triggered under Rule 6.12.3.

6.10 Receiving Members

No Receiving Member or Service Provider shall be obliged to credit any funds received by it through
CHATS (other than funds received in respect of Articles) to the beneficiary’s account if the instructions
for the transfer are incomplete or inaccurate.

6.11 Special Posting

6.11.1 Special Posting Request

This contingency arrangement will be invoked when (a) the computer of any of the Members,
or (b) the Clearing House Computer has failed to connect to SWIFT for delivery of CHATS
transactions. The Members (except CLS Bank) who require Special Posting, or any Member
(other than CLS Bank) when it is requested by HKICL to do so, should prepare a Special
Posting authorisation letter and the instructions for Special Posting in electronic format and
submit them to HKICL for triggering the operation of the Special Posting. A request for Special
Posting shall be made during the period referred to in the Operating Procedures. Any request
submitted after that period shall be subject to the prior approval of HKICL and MA. Details of
the notification and approval arrangements are stipulated in the Operating Procedures.

## Page 51

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 48

6.11.1.1 The lay-out of instructions submitted to the Clearing House by Members by Electronic
Media shall comply with the requirements set out in the Operating Procedures.

6.11.1.2 Payment instructions for Supported Forward Days will not be effected by Special
Posting.

6.11.2 Indemnity

A Member which submits to the Clearing House instructions relating to Special Posting
transactions in Electronic Media:

(a) will be responsible for the correctness of the contents of the instructions submitted;

(b) authorises HKICL not to process any one transaction which fails certain validation
criteria implemented by HKICL from time to time and set out in the Operating
Procedures;

(c) indemnifies HKICL and MA against all liabilities and expenses incurred by either of
them as a result of any error or discrepancy in the instructions or otherwise.

6.11.3 Settlement of Special Posting Transactions

It is the Sending Member’s responsibility (or in relation to an OTC Clear Payment Instruction,
the responsibility of the paying Member of the OTC Clear Payment Instruction) to ensure that
there are sufficient funds in its CHATS Ledger Account for settlement of Special Posting
transactions. Any Special Posting transactions not settled by the cut-off times for the respective
payment instructions on the day of the request for Special Posting will be cancelled.

6.11.3.1 Any Special Posting transaction which passes validation criteria will be treated as
a normal payment instruction and processed in the same way and manner as the
payment instruction from which it originated.

6.11.3.2 Settlement of Special Posting transactions will be effected across the books of MA
pursuant to Rule 3.1.3 by debiting the CHATS Ledger Account of the Sending
Member (or in relation to an OTC Clear Payment Instruction, the paying Member
of the OTC Clear Pay ment Instruction) for the funds transferred and crediting to
the CHATS Ledger Account of the respective Receiving Members (or in relation
to an OTC Clear Payment Instruction, the bank Member designated by OTC Clear
in accordance with the Operating Procedur es in relation to the settlement of OTC
Clear Payment Instructions).

6.11.4 Responsibility of Members

6.11.4.1 Sending Members should verify the details of instructions shown on the data
capture report or response file provided to them by HKICL and follow the
procedures as stipulated in the Operating Procedures.

6.11.4.2 Sending Members should reconcile the Special Posting report produced at the end
of posting provided to them by HKICL and report discrepancies to HKICL
immediately.

6.11.4.3 For the avoidance of doubt, this Rule 6.11.4 does not apply to paying Members in
relation to the OTC Clear Payment Instructions.

6.12 End of Day Net Settlement

This contingency measure will only be invoked when all of the conditions stipulated in the Operating
Procedures are fulfilled. The measure will be operated in accordance with the Operating Procedures and

## Page 52

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 49

the Operating Procedures will provide for the resumption of normal procedures. In the event that End
of Day Net Settlement is triggered, all queued payments that are yet to be settled will be cancelled.

6.12.1 End of Day Net Settlement for Members other than CLS Bank

Upon receipt of notice from HKICL to the effect that End of Day Net Settlement has been
triggered, Members should prepare an End of Day Net Settlement authorisation letter and pass
the same to HKICL. While End of Day Net Settlement remains in effect all eligible transactions
as stipulated in the Operating Procedures consolidated by Sending Members (one payment to
each Receiving Member) shall be prepared by each Member in Electronic Media and passed to
the Clearing House according to the schedules specified in the Operating Procedures.

6.12.1.1 The lay-out of instructions delivered to the Clearing House by Members in Electronic
Media shall comply with the requirements set out in the Operating Procedures.

6.12.1.2 Each Member can only submit one payment file in a Working Day.

6.12.1.3 Only specific types of instruction will be accepted for End of Day Net Settlement.
The types of instructions which are acceptable are set out in the Operating Procedures.

6.12.1.4 Rule 6.12.1 shall not apply to CLS Bank; Rule 6.12.3 shall apply to CLS Bank in the
event that End of Day Net Settlement is triggered.

6.12.2 Indemnity

A Member (except CLS Bank) which delivers to the Clearing House instructions relating to
End of Day Net Settlement transactions in Electronic Media:

(a) will be responsible for the correctness of the contents in the Electronic Media;

(b) authorises HKICL not to process the whole batch in case any one transaction fails
certain validation criteria implemented by HKICL from time to time and set out in the
Operating Procedures;

(c) authorises HKICL to adjust the net settlement amount when one or more Members
is/are in default;

(d) indemnifies HKICL and MA against all liabilities and expenses incurred by either of
them as a result of any error or discrepancy in instructions contained in Electronic
Media.

6.12.3 End of Day Net Settlement for CLS Bank

6.12.3.1 Upon receipt of notice from HKICL to the effect that End of Day Net Settlement
has been triggered, CLS Bank will send CLS Pay -out details to the Clearing
House via email in accordance with the schedules and requirements specified in
the Operating Procedures.

6.12.3.2 Based on the email, HKICL will consolidate the CLS Pay -outs (one payment
from CLS Bank to each Receiving Member) and prepare the payment file in
Electronic Media on behalf of CLS Bank for effecting End of Day Net Settlement.

6.12.3.3 CLS Payment Instructions Value Forward Day will not be effected by End of Day
Net Settlement.

6.12.3.4 CLS Bank:

(a) will be responsible for the correctness of the contents of the email sent to
the Clearing House under Rule 6.12.3.1;

## Page 53

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 50

(b) authorises HKICL to adjust the net settlement amount when one or more
Members is/are in default; and

(c) will indemnify HKICL and MA against all liabilities and expenses incurred
by either of them arising out of or as a result of any error in the email
delivered to the Clearing House under Rule 6.12.3.1 or discrepancy
between such information and the original instruction.

6.12.3.5 HKICL will distribute copies of the email received from CLS Bank containing
the CLS Pay-out details to the relevant Receiving Members.

6.12.4 Settlement of End of Day Net Settlement Transactions

6.12.4.1 It is Member’s responsibility to ensure that there are sufficient funds in its
CHATS Ledger Account for settlement of End of Day Net Settlement
transactions at any time before CHATS Value Date Cut-off on the day when End
of Day Net Settlement is operative.

6.12.4.2 If all the Members with debit settlement amounts have sufficient available funds
in their CHATS Ledger Accounts at any time before CHATS Value Date Cut-off
on the day when End of Day Net Settlement is operative, such settlement amounts
will be automatically debited and the relevant credit settlement amounts will be
automatically credited to all relevant CHATS Ledger Accounts, and the
settlement will immediately be deemed to be effected and completed.

6.12.4.3 The principle of “all or none” shall apply to the End of Day Net Settlement run.
If the available balance in the CHATS Ledger Account of a Member other than
HKSCC is insufficient, the Member shall be deemed to have defaulted in the End
of Day Net Settlement run. However, in the case of default by one or more GD
Banks, only the GD Cheques relating to such GD Bank(s) will be excluded from
the End of Day Net Settlement run.

6.12.4.4 If a Member is in default, (i) its name will be identified and announced and (ii)
the defaulted End of Day Net Settlement run will be unwound and there will be a
settlement excluding the Member in default. This Rule 6.12.4.4 does not apply
to HKSCC, HKCC and SEOCH.

6.12.4.5 If the available balance in the CHATS Ledger Account of HKSCC is insufficient
to meet its settlement obligation in the End of Day Net Settlement run, HKICL
shall notify all other Members that the Bulk Clearing Settlement Run for CCASS
Participant Items will be cancelled an d the CHATS Transactions related to
HKSCC in the End of Day Net Settlement run will be excluded. Details are
stipulated in the Operating Procedures.

6.12.5 Responsibility of Members

In addition to the other provisions of these Clearing House Rules, each Member shall be
responsible for the following matters:

6.12.5.1 Sending Members (except CLS Bank) should verify the details of instructions
shown on the data capture report provided to them by HKICL and confirm that
the End of Day Net Settlement may proceed.

6.12.5.2 Sending Members (except CLS Bank) should advise the Receiving Members of
details of the relevant transactions.

6.12.5.3 Members should reconcile the settlement totals as supplied by HKICL and report
discrepancies to HKICL according to the schedules stipulated in the Operating

## Page 54

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 51

Procedures.

6.12.5.4 Receiving Members should rely on the detailed transaction listing sent by the
Sending Member and CLS Pay -out details from HKICL for internal posting and
reconciliation purposes.

6.12.5.5 The Receiving Member is at its own risk to release funds to customers prior to
the successful settlement.

6.13 RTGS Liquidity Optimiser

Subject to Rule 6.13.9, between the CHATS Commencement and CHATS Value Date Cut -off, RTGS
Liquidity Optimiser effected through CHATS can be triggered automatically according to a pre-defined
interval or manually by MA.

6.13.1 When RTGS Liquidity Optimiser process starts, eligible CHATS Transactions in the Normal
Queue as specified in the Operating Procedures will be extracted (“Selected Payments”).

6.13.2 The projected balance of the CHATS Ledger Accounts for each paying Member of the Selected
Payments (“Selected Payment Member”) based on assumed settlement of the Selected
Payments will be computed in accordance with the formula as stipulated in the Operating
Procedures.

6.13.3 If the projected balances of each Selected Payment Members are found positive or zero, the
gross amount of the Selected Payments, save in respect of the CCP Instructions being extracted
as Selected Payments, will each be effected through CHATS automatically and settled
immediately upon completion of its processing and effected across the books of MA pursuant
to Rule 3.1.3 by debiting and crediting the CHATS Ledger Accounts for the funds transferred.
The CCP Instructions being extracted as Selected Payments will be processed pursuant to Rules
6.3.4.3 and 6.3.4.5.

6.13.4 In case the projected balances of the CHATS Ledger Account for some Selected Payment
Members are negative, the system will try to exclude the Selected Payments of such Selected
Payment Members based on the criteria as specified in the Operating Procedures in order to
reach positive or zero projected balan ces of each of the Selected Payment Members. Selected
Payments which are excluded from the R TGS Liquidity Optimiser will be placed back to the
Normal Queue.

6.13.5 CHATS Transactions (other than CHATS Transactions in respect of Articles) received by
Clearing House Computer after commencement of the RTGS Liquidity Optimiser process will
not be processed as part of that process and will be placed at the end of the Normal Queue and
processed in due course in accordance with these Rules provided that Direct Debit Instructions
will be placed at the top of the Normal Queue.

6.13.6 Under any of the following situations, the process of RTGS Liquidity Optimiser will be
terminated:

(a) all Selected Payments are excluded in the process of Rule 6.13.4;

(b) the process of the RTGS Liquidity Optimiser has not been completed prior to CHATS
Value Date Cut-off;

(c) any Selected Payment Member(s) or relevant Receiving Member(s) is/are in default or if
it is/are insolvent;

(d) the processing time exceeds the maximum processing time defined for each RTGS
Liquidity Optimiser run from time to time as stipulated in the Operating Procedures; or

(e) any of the specific critical events which are stipulated in the Operating Procedures is

## Page 55

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 52

activated.

6.13.7 On termination of the process of RTGS Liquidity Optimiser pursuant to Rule 6.13.6, all relevant
Selected Payments and any CHATS Transactions (other than CHATS Transactions in respect
of Articles) received by Clearing House Computer after commencement of the process of RTGS
Liquidity Optimiser will be reinstated in the Normal Queue as if the process of the RTGS
Liquidity Optimiser had not been commenced.

6.13.8 Requests for re -sequencing and cancellation of its payments in the Normal Queue (including
the Selected Payments and other CHATS Transactions (other than CHATS Transactions in
respect of Articles)) initiated by the Selected Payment Member or MA after the start of RTGS
Liquidity Optimiser process and before completion or termination of the process will be
rejected.

6.13.9 RTGS Liquidity Optimiser will not be available when End of Day Net Settlement has been
invoked.

6.14 Interbank Intraday Liquidity Facility

The IILF shall be made available through CHATS between the CHATS Commencement and CHATS
Value Date Cut-off by Liquidity Providers to Liquidity Consumers in accordance with this Rule.

6.14.1 Liquidity Providers shall indicate their willingness to participate in the IILF by registering with
HKICL. Liquidity Providers shall also on behalf of the Liquidity Consumers with whom they
have agreed to provide liquidity through IILF register those Liquidity Consumers with HKICL
indicating their Liquidity Consumers’ desire to obtain liquidity from the Liquidity Providers
under the IILF. Liquidity Consumers may only obtain liquidity through IILF from one
Liquidity Provider and:

(a) prior to registration Liquidity Providers and Liquidity Consumers shall separately agree
among themselves on a bilateral basis the terms on which liquidity through IILF is
provided including the intra-day and overnight interest rates;

(b) after registration, the relevant Liquidity Provider shall maintain in the records of HKICL
via the MBT:

(i) the limit of the IILF for the time being assigned by it to each Liquidity Consumer,
which limit may be amended by the Liquidity Provider via the MBT at any time
without prior notice to HKICL or the Liquidity Consumer;

(ii) the priority arrangement by it to each Liquidity Consumer in the event that it has
more than one Liquidity Consumer and provision of liquidity is triggered by more
than one Liquidity Consumer at the same time and all such requests cannot be met
in full; and

(iii) the intra-day and overnight interest rates agreed with each Liquidity Consumer.

(c) HKICL shall publicise on the members’ section of its website the names and contact
details of registered Liquidity Providers.

6.14.2 The provision of l iquidity through IILF process is triggered automatically during the RTGS
Liquidity Optimiser process.

6.14.3 If a Liquidity Provider is a Selected Payment Member in the RTGS Liquidity Optimiser process,
the provision of liquidity through IILF by such Liquidity Provider will not be triggered in that
process.

6.14.4 If a Liquidity Provider is not a Selected Payment Member in the RTGS Liquidity Optimiser
process and a Liquidity Consumer to which the Liquidity Provider has agreed to provide

## Page 56

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 53

liquidity through IILF is a Selected Payment Member in the RTGS Liquidity Optimiser process,
the projected balance as stipulated in Rule 6.13.2 shall take into account the available IILF limit
specified in Rule 6.14.1(b)(i) to the extent required to make t he projected balance of the
Liquidity Consumer positive or zero. Should the IILF be taken into account to the extent
required to make the projected balance of a Liquidity Consumer positive or zero as provided in
the previous sentence, there shall be a dee med request for the provision of liquidity through
IILF by the Liquidity Consumer in that amount from the Liquidity Provider to the Liquidity
Consumer. The ultimate liquidity drawn by Liquidity Consumer out of the available IILF limit
and the detailed arrangements are stipulated in the Operating Procedures.

6.14.5 If more than one Liquidity Consumer are deemed to make a request pursuant to Rule 6.14.4
from the same Liquidity Provider, and such Liquidity Provider does not have sufficient funds
to fulfil the requests of all such Liquidity Consumers, the available amounts under the IIL F
from that Liquidity Provider will be allocated to each Liquidity Consumer according to the
priority specified by the Liquidity Provider in Rule 6.14.1(b)(ii).

6.14.6 The lending under the IILF is effected through the settlement of a CHATS Payment Instruction
Value Today with a designated payment code indicating that it is a payment of principal under
the IILF (“IILF Payment Instruction”) generated by HKICL to debit the Liquidity Provider’s
CHATS Ledger Account and credit the Liquidity Consumer’s CHATS Ledger Account.

6.14.7 Liquidity provision through IILF by a Liquidity Provider to one or more of its Liquidity
Consumers may also be triggered manually by such Liquidity Provider inputting an IILF
Payment Instruction.

6.14.8 For each settled IILF Payment Instruction, the Liquidity Consumer shall be under an obligation
to repay the Liquidity Provider the amount of the IILF Payment Instruction (i.e. principal) and
an intra-day interest calculated based on the IILF Payment Instruction. The intra -day interest
rate is assigned by the Liquidity Provider to each of its Liquidity Consumer(s) by separate
agreement and maintained by the Liquidity Provider in the record s of HKICL via the MBT
under Rule 6.14.1(b)(iii).

6.14.9 The total outstanding IILF repayable amount of a Liquidity Consumer in respect of each
Working Day includes:

(a) the amount of all settled IILF Payment Instruction(s) of the current day not yet repaid by
the Liquidity Consumer; and

(b) intra-day interest of the current day not yet paid by the Liquidity Consumer for which the
calculation of such interest is stipulated in the Operating Procedures.

6.14.10 If there is any outstanding IILF repayable amount of a Liquidity Consumer as defined in Rule
6.14.9, the repayment process for the Liquidity Consumer will be triggered automatically by
HKICL according to the scheduled repayment time on each Working Day det ermined by MA
and subject to change from time to time. CHATS Payment Instructions Value Today with
different designated payment codes indicating they are either repayments of outstanding IILF
Payment Instructions or payments of outstanding intra-day interest under the IILF (collectively
known as “IILF Repayment Instructions”) will be generated by HKICL to debit the Liquidity
Consumer’s CHATS Ledger Account and credit the Liquidity Provider’s CHATS Ledger
Account to repay outstanding (i) IILF Payment Instruction (i.e. principal); and (ii) intra -day
interest separately.

6.14.11 An IILF Repayment Instruction may also be triggered manually by a Liquidity Consumer to its
Liquidity Provider by the Liquidity Consumer inputting such an instruction.

6.14.12 If the Liquidity Consumer has insufficient funds to meet the total outstanding IILF repayable
amount, the IILF Repayment Instructions will still be generated by HKICL to partially repay
the outstanding IILF repayable amount. The detailed arrangements are stipulated in the
Operating Procedures.

## Page 57

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 54

6.14.13 If there is any outstanding IILF Payment Instruction of Liquidity Consumer after CHATS Value
Date Cut -off, an overnight interest assigned by the Liquidity Provider to the Liquidity
Consumer and maintained by the Liquidity Provider in the records of HKICL v ia the MBT
under Rule 6.14.1(b)(iii) shall apply. HKICL shall then calculate the overnight interest
according to the formula stipulated in the Operating Procedures and provide such information
to the Liquidity Provider and Liquidity Consumer. However, th e overnight interest, together
with the outstanding IILF repayable amount, shall be settled outside of the CHATS after
CHATS Value Date Cut-off between the Liquidity Provider and Liquidity Consumer, and MA
and HKICL shall have no further involvement.

6.15 Account Balance Sweeping Facility between CHATS and FPS

6.15.1 Rule 6.15 is only applicable to Members (other than CLS Bank, HKSCC, HKCC and SEOCH)
that are also Settlement Participants (as defined in the FPS Rules).

6.15.2 The account balance sweeping facility shall be made available on a Working Day within the
timeframe stipulated in the FPS Operating Procedures for the transfer of funds between a
CHATS Ledger Account of a Member and its FPS Ledger Account.

6.15.3 [This provision has been left blank intentionally]

6.15.4 [This provision has been left blank intentionally]

6.15.5 [This provision has been left blank intentionally]

6.15.6 [This provision has been left blank intentionally]

6.15.7 [This provision has been left blank intentionally]

6.15.8 [This provision has been left blank intentionally]

6.15.9 [This provision has been left blank intentionally]

6.15.10 [This provision has been left blank intentionally]

6.15.11 [This provision has been left blank intentionally]

6.15.12 Neither HKICL nor MA shall be liable for any claim, loss, damage or expense of any kind or
nature whatsoever arising in whatever manner directly or indirectly out of or in connection with
any transaction settlement delay or failure in CHATS and/or FPS due to insufficient funds with
or without account balance sweeping facility applied.

## Page 58

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 55

Part VII The Processing in respect of Articles

7.1 Provisions Relating to the Processing in respect of Articles

7.1.1 Timetable

(a) In the interests of Members, the times for the delivery of Articles to the Clearing House and
relating to the various processes of clearing and/or settlement may be amended at the discretion
of HKICL and the Association upon prior consultation with MA and at least 3 days ’ notice of
any amendment will be given by HKICL to all Members. The timetables for the delivery of
Articles for clearing and/or settlement , Returned Articles and Unpaid Articles are set out in
Schedule III and the Operating Procedures. Each of such times is hereinafter, separately,
referred to as “the appointed time”.

(b) Subject to Rule 7.1.1(c), HKICL as owner, operator and manager of the Clearing House will
have the discretion to postpone or extend any of the appointed times (including the appointed
time for: a Bulk Clearing Settlement Run; the delivery of Returned Articles, Unpaid Articles
and/or Articles for clearing and/or settlement) in cases of emergencies or exceptional
circumstances due to reasons of an operational or technical nature (e.g. breakdown in facilities,
power failure etc.). In such cases, HKICL shall notify all Members by a broadcast in the manner
as stipulated in the Operating Procedures, and shall notify HKSCC and OTC Clear in a manner
separately agreed with them or, in the case of JETCO and JETCO Members shall advise JETCO,
or in the case of Credit Card Companies and Credit Card Members shall advise Credit Card
Companies or in the case of CMU members who are trustees of MPF Schemes shall advise the
CMU, or in the case of users of the e -Cheque Presentment Service shall advise Members and
publish on any website, mobile application or on any other system on which an e -Cheque
Presentment Service is made available notice of the revision of the appointed time(s), or in the
case of the GD e -Cheque Platform Users shall advise the relevant GD Settlement Centre and
such revision shall be binding on the Members.

(c) In the case of CHATS Commencement being delayed due to urgent system maintenance and
when it is reasonably certain that the normal operation of CHATS can resume within the same
Working Day, the affected appointed times shall be adjusted according to th e principles
stipulated in Rules 7. 11. HKICL will notify all Members by a broadcast in the manner as
stipulated in the Operating Procedures the revision of the appointed time(s) and such revision
shall be binding on Members.

7.1.2 Delivery

All Articles (or information relating thereto and/or (where permitted) images thereof contained
in Electronic Media) to be processed in a Bulk Clearing Settlement Run must be delivered at
the Clearing House by the relevant appointed time.

HKICL, after consultation with MA, has authority to refuse to accept Articles for clearing and
settlement after the relevant appointed time.

Members may appoint staff members or any other person to act as their agents for the purpose
of delivery and collection of Articles , Returned Articles and Unpaid Articles to or from the
Clearing House. Such persons shall bear authorisation cards issued by HKICL. Each Member
shall be responsible for all acts and omissions of its agents who shall be regulated in accordance
with the Operating Procedures.

7.1.3 List of Articles

Lists of Articles (except those which are to pass through electronic clearing) containing such
information as is currently required must accompany all deliveries of Articles for clearing ,
Returned Articles and Unpaid Articles. This Rule 7.1.3 does not apply to JETCO Items, SJET
Items and Credit Card Items.

## Page 59

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 56

7.1.4 Settlement

(a) The process for the settlement of Articles (other than OTC Items, JETCO Items, SJET
Items and Credit Card Items), CCASS Optimiser Payment Instruction s, SCCASS
Optimiser Payment Instructions, CHATS Optimiser Payment Instructions and CCPO
Instructions are set out in Schedule I and detailed provisions relating to the settlement
of such items are set out in Schedule III.

(b) The process for the settlement of JETCO Items and SJET Items are set out in Part IV
of Schedule III.

(c) The process for the settlement of Credit Card Items is set out in Part V of Schedule III.

(d) The process for the settlement of OTC Items is set out in Part VI of Schedule III.

7.1.5 Returned Articles and Unpaid Articles

(a) All Returned Articles and Unpaid Articles shall be delivered to the Clearing House by
the relevant appointed time. HKICL has authority to refuse to accept Returned
Articles and Unpaid Articles delivered to it after the relevant appointed time.

(b) Returned Articles and Unpaid Articles returned in physical form shall be delivered to
the Clearing House accompanied by a list containing such information as is currently
required.

(c) Unpaid Articles in respect of e-Cheques and Returned Articles of E-bill Payments shall
be delivered to the Clearing House in Electronic Media unless otherwise permitted by
HKICL.

(d) Unpaid Articles of Paper Cheques shall be delivered to the Clearing House in
Electronic Media in accordance with the Operating Procedures unless otherwise
permitted by HKICL. Unpaid Articles of GD Cheque shall be dealt with in accordance
with section H(2) of Part III of Schedule III.

(e) [This provision has been left blank intentionally]

(f) This Rule 7.1.5 applies to Paper Cheques initially exchanged between Group A
Members pursuant to Rule 7.1.9, but does not apply to JETCO Items, SJET Items and
Credit Card Items.

7.1.6 Wrongly Delivered Articles

Articles wrongly delivered through the clearing should be returned to the Clearing House with
Unpaid Articles or Returned Articles, as the case may be . A Member receiving a wrongly
delivered Article shall give immediate telephone notice to HKICL, which will advise the
Member by or through which the Article is payable. This Rule 7.1.6 does not apply to JETCO
Items, SJET I tems, Credit Card Items, CCASS Participant Items, E-bill Payments, Returned
Articles of E-bill Payments, SCCASS Participant Items and OTC Items.

7.1.7 Articles Returned to a Wrong Party

If any E-bill Payment, CCASS Investor Item, Paper Cheque or e-Cheque Payment is returned
to a wrong party as Returned Articles or Unpaid Articles, the Member discovering the error
should advise HKICL of the details and HKICL should then notify the Member concerned of
the error and the amount payable or receivable (including the amount payable or receivable
under the Interest Adjustme nt Scheme) by each of them in order to rectify the error and the
Member from whom a payment is due should effect the payment b y means of a CHATS
Payment Instruction immediately. The Member which made the error will be responsible for

## Page 60

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 57

the re-delivery of the Returned Articles or the Unpaid Articles to the correct party.

7.1.8 Direct Presentation of Articles

These Clearing House Rules do not deprive any Member of the right to present an Article (other
than e -Cheque) direct to another Member by or through which that Article is payable for
payment in cash. This provision does not apply to HKSCC which does not present Articles
direct to other Members.

7.1.9 Clearing without Delivery of Paper Cheques by Group A Members (other than GD
Cheques)

Group A Members may after giving 60 days’ notice in writing to HKICL:

(a) exchange physical Paper Cheques and /or images of Paper Cheques in Electronic
Media among themselves without delivery to the Clearing House; and

(b) deliver information relating to such Paper Cheques by Electronic Media to the
Clearing House (such information to be delivered to the Clearing House by each Group
A Member concerned) for clearing without physical delivery of such Paper Cheques
and with out delivery of images of such Paper Cheques in Electronic Media to the
Clearing House.

Group A Members who have given such notice may by 60 days ’ prior notice in writing to
HKICL revert to exchange of Paper Cheques through the Clearing House in accordance with
Rule 7.5.1. All such notices must be given on behalf of all the Group A Members participating
in the same exchange arrangement. Notices gi ven under this Rule may not be given more
frequently than once per calendar year. Group A Members who exchange Paper Cheques
among themselves in the manner contemplated by this Rule shall ensure that each Paper Cheque
that is cleared pursuant to an exchange among themselves in the manner contemplated by this
Rule shall bear a notation with the word “clearing” and stating the date of presentation. A Paper
Cheque which has been exchanged between Group A Members but is not paid shall be returned
to the Clearing House pursuant to Rule 7.1.5. This Rule does not apply to GD Cheques.

7.2 Value Date of Articles

7.2.1 Inter-Member Level

(a) The value date of payment of an Article (other than Credit Card Items, e-Cheques, E-
bill Payments, Returned Articles of E -bill Payments, SEPS I tems, SJET I tems,
SCCASS Participant Items (but including further amendments to SCCASS Participant
Items reported by Members to CCASS after completion of the Bulk Clearing
Settlement Run for SCCASS Participant Items but before 20.00 hours on Day D ) and
OTC Items) cleared and/or settled through CHATS at the inter-Member level shall be
the Working Day immediately following the day of presentation of such Article to the
Clearing House for clearing, except as otherwise provided in Schedule III .

(b) The value date of payment of e -Cheques cleared and settled through CHATS at the
inter-Member level shall be the Working Day immediately following the day of
generation of the relevant e-Cheque Payments by HKICL.

(c) The value date of payment of Credit Card Items, E-bill Payments, Returned Articles
of E -bill Payments, SEPS I tems, SJET I tems, SCCASS Participant Items (but
excluding further amendments to SCCASS Participant Items reported by Members to
CCASS after completion of the Bulk Clearing Settlement Run for SCCASS Participant
Items but before 20.00 hours on Day D ) and OTC Items at the inter -Member level
shall be the Working Day of presentation of such Credit Card Items, E-bill Payments,
Returned Articles of E-bill Payments, SEPS Items, SJET Items, SCCASS Participant
Items and OTC Items to the Clearing House for clearing.

## Page 61

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 58

7.2.2 Member-customer Level

(a) Notwithstanding Rule 7.2.1 (a) and (b) and subject to Rule 7.2.2 (b), at the Member-
customer level, payment of an Article (except Special CCASS Items , e-Cheques and
Returned Articles of E -bill Payments) shall be valued the same day as the day of
presentation of that Article by the customer of a Member to the Member concerned;
and payment of Special CCASS Items shall be valued at the Member -customer level
and settled at the inter-Member level on the same day being the Working Day after the
day of presentation of the Special CCASS Items ; and payment of e -Cheques shall be
valued at the Member -customer level on the day of generation of the relevant e -
Cheque Payments by HKICL . This Rule 7.2.2 does no t apply to JETCO Items and
Credit Card Items.

(b) At the Member-customer level, payment of a Returned Article of E-bill Payment due
to reasons other than refund shall be valued on the Working Day of original
presentation of such E-bill Payment that need to be returned to the presenting Member.

7.3 Interest Adjustment Scheme

In order to avoid arbitrage and to deal fairly with the situation created by the difference between the
value dat e of payments of Articles (except JETCO Items; SJET Items; Credit Card Items ; E -bill
Payments (but including Returned Articles of E-bill Payments); SEPS Items; SCCASS Participant Items
(but including further amendments to SCCASS Participant Items reported by Members to CCASS after
completion of the Bulk Clearing Settlement Run for SCCASS Participant Items but before 20.0 0 hours
on Day D); OTC Items; and Special CCASS Items) at the inter-Member level and the Member-customer
level, a Member which is required t o pay a Settlement Amount in a Bulk Clearing Settlement Run will
pay, and a Member which is entitled to receive a Settlement Amount in the same Bulk Clearing
Settlement Run will receive, their respective Settlement Amount plus or minus an interest adjustment in
respect thereof in accordance with the provisions of the Interest Adjustment Scheme set out in Schedule
IV. References to “Settlement Amount” in this Rule 7.3 exclude an interest adjustment under the Interest
Adjustment Scheme. The Interest Adjustment Scheme does not apply to amounts payable or receivable
in a Bulk Clearing Settlement Run of JETCO Items; SJET Items; Credit Card Items; E-bill Payments
(but including Returned Articles of E -bill Payments); SEPS Items; SCCASS Participant Items (other
than further amendments to SCCASS Participant Items reported by Members to CCASS after completion
of the Bulk Clearing Settlement Run for SCCASS Participant Items but before 20.00 hours on Day D);
OTC Items; and Special CCASS Items.

7.4 Indemnity

7.4.1 Subject to Rule 7.4.2, a Member (including in its capacity as an agent bank of EPSCO or a
Credit Card Company and, where applicable, as a GD Agent or the MC Agent) which delivers
to the Clearing House information relating to Articles, Unpaid Articles of MPF Items, Returned
Articles of E -bill Payments, Unpaid Articles in respect of e -Cheques, return of presented e -
Cheques by payee bank Members pursuant to Rule 7.6.8.4 (“return of presented e -Cheques”),
Unpaid Articles of Paper Cheques and an image of a Paper Cheque itself in Electronic Media
(whether or not it also delivers the related Paper Cheque):

(a) will be responsible for the correctness of the contents in the Electronic Media;

(b) authorises HKICL to rely exclusively on the relevant information relating to the
Articles, Unpaid Articles of MPF Items, Returned Articles of E-bill Payments, Unpaid
Articles in respect of e -Cheques, return of presented e -Cheques, Unpaid Articles of
Paper Cheques and on the image of the Paper Cheque without making any other
independent verification of the Articles , Unpaid Articles of MPF Items, Returned
Articles of E -bill Payments , Unpaid Articles in respect of e -Cheques, return of
presented e-Cheques and Unpaid Articles of Paper Cheques;

(c) authorises HKICL to rely exclusively on the Electronic Records of presented e -

## Page 62

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 59

Cheques, Unpaid Articles in respect of e -Cheques and return of presented e -Cheques
should such Electronic Records fulfil duplicate presentment checking and validations
as defined in the Operating Procedures, without making any other independent
verification of the presented e-Cheques, Unpaid Articles in respect of e -Cheques and
return of presented e-Cheques; and

(d) indemnifies MA and HKICL against all liabilities and expenses incurred by either of
them arising out of or as a result of any error in instructions or discrepancy between
such information and the related Articles , Unpaid Articles of MPF Items, Returned
Articles of E -bill Payments, Unpaid Articles in respect of e -Cheques, return of
presented e-Cheques, Unpaid Articles of Paper Cheques, any discrepancy between the
original Paper Cheque and an image of the Paper Cheque, and the discrepancy arising
from the failure of any e-Cheque format used by the Member to comply with the lay -
out requirements stipulated in the Operating Procedures.

This Rule does not apply to GD Cheques.

7.4.2 Notwithstanding the provisions of Rule 7.4.1:

(a) (i) no Group A Member shall incur any liability to any other Member or HKICL;
and

(ii) HKICL shall incur no liability to any Member

arising out of an image of a Paper Cheque or information relating to a Paper Cheque
in Electronic Media not corresponding with the original of the Paper Cheque as long
as the Group A Member or HKICL as the case may be can demonstrate that in
production of the image of the Paper Cheque or information relating to the Paper
Cheque, it has followed a Compliance Assessment Programme for Cheque Imaging
Systems and Related Processes as amended by the Group A Member or HKICL (as
appropriate) from time to time at its discretion; and

(b) MA shall incur no liability to any Member or HKICL arising out of an image of a
Paper Cheque or information relating to a Paper Cheque in Electronic Media not
corresponding with the original of the Paper Cheque.

7.5 Special Rules for Paper Cheques

The following Rules shall apply to clearing Paper Cheques:

7.5.1 Presentation of Paper Cheques

Save as hereinafter provided, Paper Cheques shall be presented to the Clearing House and
forwarded by the Clearing House to the Member on which the Paper Cheques are drawn by
delivery of their images in Electronic Media provided however that:

(a) Presentation of an image of a Paper Cheque by Group B Members will be effected by
the Group B Members delivering the physical Paper Cheque to the Clearing House for
HKICL to produce the image of the Paper Cheque for the purpose of clearing and
settlement;

(b) Presentation of GD Cheques shall be made physically;

(c) In respect of any Paper Cheque presented by an image of the Paper Cheque in
Electronic Media, the Member on whom that Paper Cheque is drawn may require it to
be presented physically in accordance with the Operating Procedures;

(d) Paper Cheques may be cleared by Group A Members without delivery of the Paper
Cheques to the Clearing House in accordance with the provisions of Rule 7.1.9. In the

## Page 63

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 60

event of the giving of a notice to HKICL to revert to exchange of Paper Cheques
through the Clearing House presentation of Paper Cheques shall be subject to the
provisions of this Rule.

7.5.2 Stamps

(a) All Paper Cheques which have been delivered by Group A Members to the Clearing
House for the purpose of clearing shall as evidence of such delivery and clearing be
impressed by Group A Members with a stamp on the reverse with the word “Clearing”,
the date of presentation and the name of the presenting Group A Members.

(b) All Paper Cheques which have been delivered by Group B Members for the purpose
of clearing pursuant to Rule 7.5.1(a) shall as evidence of such delivery and clearing be
impressed by HKICL with a stamp on the reverse with the word “Clearing”, the date
of presentation and the name of HKICL.

(c) All GD Cheques which have been delivered physically to the Clearing House pursuant
to Rule 7.5.1(b) for the purpose of clearing shall as evidence of such delivery and
clearing be impressed with HKICL’s clearing stamp on the back.

(d) Members and each GD Agent (for relevant GD Banks) shall not return Paper Cheques
unpaid on the ground that they do not bear the appropriate stamp, but shall liaise with
the relevant Group A Member or HKICL (as appropriate) for confirmation.

(e) In order to identify the presenting Member, all Paper Cheques must be enfaced by the
relevant presenting Member with a crossing stamp bearing the presenting Member ’s
name.

7.5.3 Endorsement of Paper Cheques and Responsibility for Endorsement

All Paper Cheques to be cleared and where appropriate images of Paper Cheques should be
properly endorsed before being sent to the Clearing House.

7.5.4 [This provision has been left blank intentionally]

7.5.5 [This provision has been left blank intentionally]

7.5.6 [This provision has been left blank intentionally]

7.5.7 Paper Cheques Lost or Destroyed

7.5.7.1 In the event of loss or destruction of a Paper Cheque outside the Clearing House , the
presenting Member shall arrange settlement through the Clearing House or with the
Member on whom the Paper Cheque is drawn in accordance with the Operating
Procedures and shall submit a certified copy of the lost or destroyed Paper Cheque:

(a) to HKICL in the event of settlement of the Paper Cheque through the Clearing
House, upon such submission to HKICL, the presenting Member shall be
deemed as having irrevocably (save where otherwise provided in this Rule)
and unconditionally agreed to indemnify and hold each of MA, HKICL and
the drawee Member on which the Paper Cheque is drawn harmless from and
against all losses, costs, claims or demands arising as a result of HKICL
clearing and the drawee Member making payment against the certified copy
of the Paper Cheque rather than the original including (but without prejudice
to the generality of the foregoing) any loss, cost, claim or demand arising out
of the drawee Member being required subsequently to make payment against
the original of the Paper Cheque; or

(b) to the Member on whom the Paper Cheque is drawn in the event of settlement

## Page 64

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 61

between the presenting Member and the Member on whom the Paper Cheque
is drawn , and upon such submission to the Member on whom the Paper
Cheque is drawn, the presenting Member shall be deemed as having
irrevocably (save as otherwise provided in this Rule) and unconditionally
agreed to indemnify and hold the drawee Member harmless from and against
all losses, costs, claims or demands arising as a result of the drawee Member
making payment agains t the certified copy of the Paper Cheque rather than
the original including (but without prejudice to the generality of the foregoing)
any loss, cos t, claim or demand arising out of the drawee Member being
required subsequently to make payment against the original of the Paper
Cheque.

Where

(i) two hours before the submission deadline of Unpaid Articles of Paper Cheque,
or

(ii) when agreed between the presenting Member and the drawee Member, before
any other lead time prior to such submission deadline,

the original of the Paper Cheque is recovered and is delivered directly to the
drawee Member concerned (for settlement with the drawee Member or for
settlement through the Clearing House ), upon such delivery of the original
Paper Cheque for settlement, the indemnity given by the presenting Member
under paragraph (a) or (b) above in this Rule (as the case may be) shall be
treated as having been revoked.

7.5.7.2 In the case of a Paper Cheque presented by a Group B Member is lost or destroyed
within the Clearing House:

(a) where the details of such Paper Cheque have already been captured by the
Clearing House Computer, HKICL will notify the Member on whom the
Paper Cheque was drawn in writing and provide details of the Paper Cheque
concerned;

(b) where the details of such Paper Cheque have not yet been captured by the
Clearing House Computer, HKICL shall forthwith give notice to the Group
B Member concerned of the loss or destruction of its outward clearing for
that day;

(c) upon receipt of notice of loss or destruction from HKICL, the Group B
Member concerned shall forthwith arrange for copies of the Paper Cheque
which have been so lost or destroyed to be reproduced from its records and
submitted to the Clearing House in batches;

(d) each copy referred to in Rule 7.5.7.2(c) shall bear the certification signed by
an authorised signatory of the presenting Group B Member.

7.5.7.3 Any copy of a Paper Cheque presented by a Group B Member bearing the certification
referred to in Rule 7.5.7.2 above shall be treated by the drawee Member in all respects
as though it were the original and be dealt with accordingly.

7.5.7.4 The provisions of Rules 7.5.7.1 to 7.5.7.3 do not apply to GD Cheques. In the event
of loss or destruction of a GD Cheque within HKICL ’s or a Member ’s premises,
HKICL or, as the case may be, the Member concerned shall forthwith give a written
confirmation thereof to each presenting Member concerned for necessary action.

## Page 65

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 62

7.5.8 Lay-out Requirements

Lay-out requirements for data and images of Paper Cheques and data in respect of Unpaid
Articles of Paper Cheques exchanged between the Clearing House and Members in Electronic
Media must comply with the specifications set out from time to time by HKICL. T he
specifications currently applicable are set out in the Operating Procedures. HKICL is entitled
not to accept such exchanges which do not conform with the above -mentioned specifications.
This Rule 7.5.8 does not apply to GD Cheques.

7.5.9 GD Banks

7.5.9.1 In relation to Paper Cheques payable to GD Banks, references in these Rules to the
presenting Member are references to the relevant GD Agent.

7.5.9.2 In relation to GD Cheques or Paper Cheques payable by or to GD Banks, references
in these Rules to amounts payable by or to a Member where that Member is a GD
Agent include references to the amounts payable by or to the relevant GD Banks
(which amounts shall be paid by or to the relevant GD Agent).

7.5.10 Collection and Payment of Paper Cheques in Macau

7.5.10.1 Paper Cheques collected from MC Banks shall be presented to HKICL by the MC
Agent. In relation to items payable to MC Banks, references in these Rules to the
presenting Member are references to the MC Agent.

7.5.10.2 In relation to items payable to MC Banks, references in these Rules to amounts payable
to a Member where that Member is the MC Agent include references to the amounts
payable to the relevant MC Banks (which amounts shall be paid to the MC Agent).

7.6 Special Rules for ECG Items

7.6.1 HKICL may decide from time to time what electronic payment items may be accepted for
clearing by the Clearing House on a bulk clearing and settlement basis. Currently, EPS Items,
CCASS Items, OTC Items, E-bill Payments, SEPS Items, MPF Items, e-Cheques and Returned
Articles or Unpaid Articles in respect thereof are accepted for clearing by the Clearing House.

7.6.2 E-bill Payments

7.6.2.1 Paperless direct credits in respect of electronic bill payments and charity donation
payments addressed to participating Members to be cleared and settled on the same
Working Day may be accepted. Members to whom direct credits are addressed will
return to HKICL any direct credits which cannot be credited for any reasons as
stipulated in the Operating Procedures or for any other reasons which make it
impossible for a direct credit to be credited to an account or for refund purpose. Such
returns must be made within the peri ods defined for different return reasons as
stipulated in the Operating Procedures.

7.6.2.2 Interest adjustment for Returned Articles of E-bill Payments due to refund:

7.6.2.2.1 Members making payments shall pay Members receiving payments on the
date of settlement of the relevant Bulk Clearing Settlement Run the amount
of the payment of the Returned Articles of E -bill Payments due to refund
with interest adjustment calculated in respect thereof for the period
between the Working Day of presentation of such Returned Articles of E-
bill Payments due to refund (Day R) and the preceding Working Day (Day
R-1) at the Interest Adjustment Rate of Day R-1.

7.6.2.2.2 In case of holidays and Non-Clearing Day etc. on which the settlement of
the Returned Articles of E -bill Payments due to refund concerned has to

## Page 66

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 63

be postponed and interest adjustment is applicable for more than one day:

(a) the rate applicable to the Working Day preceding the date of
presentation of such Returned Articles of E -bill Payments due to
refund (Day R -1) for the calculation of interest adjustment as
stipulated in Rule 7.6. 2.2.1 shall be applied throughout the whole
period of the relevant interest adjustment; and

(b) simple interest shall be used in accordance with interbank money
market practice.

7.6.3 EPS Items

Paperless direct credits or debits addressed to participating Members may be accepted for
clearing when presented by EPSCO’s agent bank for this purpose.

7.6.4 CCASS Items

Paperless direct credits and direct debits addressed to participating Members may be accepted
for clearing when presented for clearing by HKSCC for this purpose.

7.6.5 OTC Items

Paperless direct credits and direct debits addressed to participating Members may be accepted
for clearing when presented by OTC Clear for this purpose.

7.6.6 SEPS Items

Paperless direct credits or debits addressed to participating Members may be accepted for
clearing and settlement on the same Working Day when presented by EPSCO’s agent bank to
the Clearing House.

7.6.7 MPF Items

Paperless direct credits and direct debits generated by HKICL following payment instruction to
HKICL via the CMU by CMU members who are trustees of MPF Schemes and which are
addressed to participating Members may be accepted for clearing.

7.6.8 e-Cheques

7.6.8.1 Presentment of e-Cheques

(a) Presentment of e -Cheques shall only be effected in Electronic Media by (i)
presentment by a Member via the Payee Bank Presentment Service, (ii)
presentment by an e -Cheque Drop Box User via the e -Cheque Drop Box
Service, (iii) presentment by GD e -Cheque Platform Users via the GD e -
Cheque Platform and collected by HKICL on behalf of GD Agent acting on
behalf of the relevant GD Settlement Centre , (iv) presentment in Shenzhen,
delivery to HKICL by GD Agent and collection by HKICL on behalf of GD
Agent acting on behalf of the relevant GD Settlement Centre or ( v)
presentment via any other e-Cheque Presentment Service in accordance with
the rules and requirements applicable thereto.

(b) Payer bank Members should follow the waiver of presentment requirement
as stipulated in the Operating Procedures. Notwithstanding the Bills of
Exchange Ordinance (Cap. 19 of the Laws of Hong Kong), no Member shall
demand any other form of presentation of an e-Cheque.

(c) If any Member shall notwithstanding this Rule require any other Member to

## Page 67

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 64

make any presentation of an e-Cheque other than in the manner set out in this
Rule, the Member making such a requirement shall indemnify the Member
who is required to make such presentation, HKICL and MA from and against
any loss, liability, costs, claims or demands incurred by any of them in respect
thereof.

7.6.8.2 Generation of e-Cheque Payments

HKICL shall generate e-Cheque Payments at the appointed time on each Working Day
as stipulated in Schedule III for the e -Cheques presented in accordance with Rule
7.6.8.1(a) and are not returned by the corresponding payee bank Members.

7.6.8.3 Responsibilities of payer bank Members

(a) Notwithstanding Rule 7.6. 9, a Member which issues e -Cheques upon the
request of its customers should ensure that there is no discrepancy between
the information shown on the display layer of an e -Cheque it issues and the
corresponding information carried in the data layer of that e -Cheque, unless
the difference is intentionally and reasonably made and is deemed necessary
for better clarity and the information in the display layer and the data layer
remains correct.

(b) Payer bank Members are responsible for identifying fraudulent e -Cheques,
notwithstanding that HKICL may also check the Digital Signature of the
payer bank Member on each presented e-Cheque and validate it in accordance
with the Operating Procedures. Neither HKICL nor MA is liable under any
circumstances for any losses or expenses whatsoever and howsoever arising
out of or in connection with HKICL’s identification or failure to identify any
relevant fraudulent e -Cheque. Neither HKICL nor MA shall be liable or
responsible for any fraud or unlawful activities practiced by a third party or
any loss or damage suffered or incurred by a Member, an e-Cheque Drop Box
User, a GD e-Cheque Platform User, or any other person arising out of or in
connection with the provision of the e -Cheque Presentment Service or the
presentation of e-Cheques through the relevant GD Settlement Centre or GD
Agent.

7.6.8.4 Responsibilities of payee bank Members

If a payee bank Member is unable to credit an e-Cheque presented in accordance with
Rule 7.6.8.1(a) into the relevant account for any reason, then that payee bank Member
must return such e-Cheque to HKICL before the designated cut-off times stipulated in
Schedule III and the Operating Procedures and HKICL shall exclude such e -Cheque
from the generation of e-Cheque Payments for clearing.

7.6.8.5 e-Cheque Drop Box Service

Rule 7.6.8.5 only applies to Members who have subscribed to the e-Cheque Drop Box
Service:

(a) HKICL is the owner of the copyright subsisting in the BKANVM API,
including all source and machine codes and the BKANVM Development
Guide. Members shall use the BKANVM API only for the purpose of the
development of BKANVM.

(b) A Member who provides a BKANVM or other related validation rules to
HKICL authorises HKICL to rely exclusively on the function of the
BKANVM and the validation rules irrespective of the correctness of the
contents of the BKANVM. HKICL shall not be lia ble for any inaccuracies,
omissions, mistakes or errors in any transactions, directly or indirectly

## Page 68

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 65

resulting from the use of or any malfunction of a BKANVM, or any error in
the validation rules, or for any economic or other loss which may be directly
or indirectly suffered or incurred.

(c) HKICL shall use the BKANVM and the other related validation rules
provided by a Member only for the purpose stipulated in the Operating
Procedures without further modification, enhancement or conversion.

(d) A Member may terminate the application of a BKANVM or other related
validation rules in the e -Cheque Drop Box Service in accordance with the
Operating Procedures. Upon receipt of a termination request from a Member,
HKICL will withdraw such BKANVM or validation rules from the e-Cheque
Drop Box Service as soon as practicable.

7.6.8.6 GD Banks

(a) In relation to e -Cheques payable to GD Banks, references in these Rules to
the presenting Member are references to the relevant GD Agent.

(b) In relation to e -Cheques payable to GD Banks, references in these Rules to
amounts payable to a Member where that Member is a GD Agent include
references to the amounts payable to the relevant GD Banks (which amounts
shall be paid to the relevant GD Agent).

7.6.9 Lay-out Requirements

Lay-out requirements for electronic debits, credits , e-Cheques and the relevant information
relating thereto, return of presented e -Cheques, Unpaid Articles of MPF Items, Returned
Articles of E -bill Payments and Unpaid Articles in respect of e -Cheques exchanged between
the Clearing House and Members by Electronic Media must comply with the specifications set
out from time to time by HKICL. The specifications currently applicable are set out in the
Operating Procedures. HKICL is entitled not to accept such exchanges which do not conform
with the above-mentioned specifications.

7.7 Special Rules for JETCO Items and SJET Items

7.7.1 Payment instructions of net settlement amounts payable or receivable by JETCO Members in
respect of settlement regarding transactions processed by JETCO for its members may be
accepted for settlement when presented by JETCO (pursuant to an authority from a Member)
to the Clearing House.

7.7.2 Such instructions shall be delivered by JETCO to the Clearing House by Electronic Media in a
format agreed between HKICL and JETCO, or in such other format and through such other
media as may be agreed from time to time between HKICL and JETCO.

7.7.3 HKICL will charge JETCO for HKICL ’s services in respect of the settlement of payment
instructions provided by JETCO in an amount separately agreed between HKICL and JETCO.

7.8 Special Rules for Credit Card Items

7.8.1 Payment instructions of net settlement amounts payable or receivable by Credit Card Members
in respect of settlement of transactions processed by a Credit Card Company for its members
may be accepted for settlement when presented by a Credit Card Company or a Card Agent to
the Clearing House.

7.8.2 Each Card Agent or Credit Card Company as the case may be shall deliver the settlement file
containing Credit Card Items to the Clearing House for processing at least one hour before the
commencement of the Bulk Clearing Settlement Run for Credit Card Items.

## Page 69

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 66

7.8.3 Payment instructions shall be delivered by a Card Agent or Credit Card Company as the case
may be to the Clearing House by Electronic Media in a format agreed between HKICL and the
Card Agent or Credit Card Company as the case may be, or in such other format and through
such other media as may be agreed from ti me to time between HKICL and the Card Agent or
Credit Card Company as the case may be.

7.8.4 HKICL will charge a Card Agent or Credit Card Company as the case may be for HKICL ’s
services in respect of the settlement of payment instructions provided by the Card Agent or
Credit Card Company as the case may be in an amount separately agreed between HKICL and
the Card Agent or Credit Card Company as the case may be.

## Page 70

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 67

7.9 GD Agent

Amounts payable to Members on GD Cheques (net of Unpaid Articles in respect of GD Cheques but
including interest under the Interest Adjustment Scheme) shall be debited from the relevant GD Agent’s
CHATS Ledger Account. Amounts payable by Members to GD Banks are regarded to have been paid
when credit has been given to the relevant GD Agent in respect of such amounts in a settlement through
the Clearing House.

7.10 MC Agent

Amounts payable by Members to MC Banks are regarded to have been paid when credit has been given
to the MC Agent in respect of such amounts in a settlement through the Clearing House.

7.11 Guiding Principles for Clearing, Return and Settlement of Articles due to Delay of CHATS
Commencement

7.11.1 At the discretion of HKICL after consultation with MA, the principles under Rule 7.11 shall be
applicable only for the situation when the delay of CHATS Commencement is due to urgent
system maintenance and where it is reasonably certain that the normal operation of CHATS can
resume within the same Working Day and the start up time can be anticipated under the
notification of HKICL as stipulated in Rule 7.1 .1(c). Otherwise, contingency measures
stipulated in Rules 6.9 shall apply.

7.11.2 Subject to Rule 7.11.1, 7.11.3, 7.11.4, 7.11.5 and 7.11. 6, the clearing and return process of
Articles shall proceed according to the original schedule.

7.11.3 The clearing and return process of Articles shall proceed only in the case when the clearing
systems for all Articles are available.

7.11.4 Subject to Rule 7.11.5, all Bulk Clearing Settlement Run(s) that cannot be executed due to delay
in CHATS Commencement (delayed Bulk Clearing Settlement Run) shall be executed in their
original sequential order one by one consecutively once CHATS has resumed.

7.11.5 If the first (one or more) delayed Bulk Clearing Settlement Run(s) cannot be completed before
the beginning of the next immediate scheduled Bulk Clearing Settlement Run after the revised
CHATS Commencement, priority shall be given to the next immediate Bulk Clearing
Settlement Run, followed by the delayed Bulk Clearing Settlement Run(s).

7.11.6 In the case where CHATS Commencement cannot occur on a Working Day, the delayed Bulk
Clearing Settlement Runs can, at the discretion of HKICL after consultation with MA , be
deferred to the time at which CHATS can resume for value as at the Working Day on which
the Bulk Clearing Settlement Runs were originally scheduled and this Rule shall apply to them
accordingly.

## Page 71

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 68

Part VIII Miscellaneous

8.1 PDPO

8.1.1 Each Member represents to HKICL that:

(a) all Personal Data provided by it to HKICL:

(i) have been collected by lawful means; and

(ii) are accurate in all material respects so far as it is aware;

(b) in relation to Personal Data collected by it all necessary consents required from Data
Subjects have been obtained:

(i) to enable Personal Data to be used for the purpose of the operation of the
Clearing House and the Clearing Facilities in accordance with these Clearing
House Rules;

(ii) to enable Personal Data to be delivered to HKSCC for the purpose of giving
effect to a CCASS Payment Instruction;

(iii) to enable Personal Data to be transferred to BOJ-NET JGB Services for the
purpose of giving effect to a BOJ DvP Payment Instruction;

(iv) to enable Personal Data to be transferred or delivered to any other person to
the extent necessary for the purpose of the operation of the Clearing House
and the Clearing Facilities in accordance with these Clearing House Rules;
and

(v) to enable HKICL to provide Personal Data to any party pursuant to any
obligation binding upon it under the PDPO; and

(c) it has complied in all aspects with the provisions of the PDPO; and

(d) use of the MBT and any equipment through which Members gain access to the MBT
complies with all applicable data protection laws, codes of practices and licences.

8.1.2 Each Member confirms that the collection, use and retention of Personal Data by any
outsourcing party in relation to the operation of the Clearing House and the Clearing Facilities
pursuant to these Rules comply with all relevant laws and regulations in Hong Kong.

8.1.3 Each GD Agent confirms that the collection, use and retention of personal data in relation to
the relevant GD Cheques and , Paper Cheques and e-Cheques drawn on Members pursuant to
these Rules complies with any relevant laws and regulations in China and Hong Kong.

8.1.4 The MC Agent confirms that the collection, use and retention of personal data in relation to the
Paper Cheques drawn on Members presented to MC Banks and through the MC Agent to the
Clearing House pursuant to these Rules complies with any relevant laws an d regulations in
Macau and Hong Kong.

8.2 Contracts (Rights of Third Parties) Ordinance, Cap. 623 of the Laws of Hong Kong

8.2.1 Save in respect of MA, a person who is not a party to these Clearing House Rules pursuant to
Rule 2.8.1 shall not have any rights to enforce or enjoy the benefit of any term or provision of
these Clearing House Rules, and the application of the Contracts (Rights of Third Parties)
Ordinance (Cap. 623 of the Laws of Hong Kong) and/or any comparable law in any jurisdiction
giving to or conferring on third parties the right to enforce or enjoy the benefit of any term or
provision of these Clearing House Rules is expressly excluded.

## Page 72

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 69

8.2.2 Any rights or benefits granted to MA under these Clearing House Rules are personal to MA
and may not be assigned or enforced by any person other than MA.

8.3 Law and Jurisdiction

8.3.1 These Clearing House Rules and the Operating Procedures shall be governed by and construed
in accordance with the laws of the Hong Kong Special Administrative Region of the People’s
Republic of China.

8.3.2 The Courts of the Hong Kong Special Administrative Region of the People’s Republic of China
shall have jurisdiction to settle any disputes which may arise in connection with these Clearing
House Rules or the Operating Procedures and HKICL and each Member hereby submit to the
jurisdiction of such Courts. Proceedings may also be initiated in any other courts of competent
jurisdiction.

8.4 Effective Date

This revision of the Clearing House Rules has consolidated all amendments up to the date HKICL
announces that they will take effect and shall take effect from the same date. In the event of any
inconsistency between the version of the Clearing House Rules on HKICL’s website and any other
version of the Clearing House Rules, the version on HKICL’s website shall prevail.

Hong Kong Interbank Clearing Limited

Date: 27 April 2026

## Page 73

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 70

SCHEDULE I DEFAULT ARRANGEMENTS FOR ARTICLES (OTHER THAN OTC ITEMS,
JETCO ITEMS, SJET ITEMS AND CREDIT CARD ITEMS), CCASS OPTIMISER
PAYMENT INSTRUCTIONS, SCCASS OPTIMISER PAYMENT INSTRUCTIONS,
CHATS OPTIMISER PAYMENT INSTRUCTIONS AND CCPO INSTRUCTIONS

Part I

Event TIME at which the Event is to occur

I. Settlement

i. Access by Members to the Settlement Amounts
of the Bulk Clearing Settlement Run and
amounts of CCASS Optimiser Payment
Instructions, SCCASS Optimiser Payment
Instructions, CHATS Optimiser Payment
Instructions and CCPO Instructions scheduled
to be settled simultaneously with the Bulk
Clearing Settlement Run concerned ( “First
Settlement”) to Members via the MBT.

Completion of clearing or return process ing of
relevant Articles, as the case may be, but prior to
settlement

ii. Commencement of the Settlement Process.
During this period, Settlement Holds will be
applied to earmark debit Settlement Amounts
payable by Members in their CHATS Ledger
Accounts and if one or more Members is/are
short of funds, HKICL will re-try until the Final
Cut-off time.

If all Members have sufficient funds in their
CHATS Ledger Accounts, settlement will be
effected immediately for the First Settlement.
Settlement completed and will be deemed final.

According to the timetable for commencement of
the Bulk Clearing Settlement Run for the
respective Articles, CCASS Optimiser Payment
Instructions, SCCASS Optimiser Payment
Instructions, CHATS Optimiser Payment
Instructions and CCPO Instructions

II. Default Situation

If one or more Members other than HKSCC
(“Default Member(s) ”) is/are in default or if it or
they are insolvent at the Final Cut-off time –

Final Cut-off time
- Announcement of the name(s) of the Default
Member(s) and mandatory and immediate
suspension ( “Mandatory Immediate
Suspension”) of the Default Member(s) from
the clearing system, i.e. no payment to or from
the Default Member(s) will be accepted by the
Clearing House systems, including CHATS
and the e-Cheque Portal, unless the Mandatory
Immediate Suspension is lifted.

- Each GD Agent or the MC Agent to advise the
relevant GD Settlement Centre or the MC
Settlement Centre as the case may be
accordingly.

Immediately following announcement by the
clearing system

- Settlement Holds still apply to funds in CHATS
Ledger Accounts of Members (including the

## Page 74

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 71

Event TIME at which the Event is to occur

Default Member(s) and those not in default) up
to their respective debit Settlement Amounts of
the First Settlement until the notification of the
Re-Settlement Amounts and the
commencement of the Settlement Process for
the Re-Settlement via the MBT.

- HKICL to prepare the unwinding of the First
Settlement (including, where applicable the
unwinding of CCASS Optimiser Payment
Instructions, SCCASS Optimiser Payment
Instructions, CHATS Optimiser Payment
Instructions and CCPO Instructions) and
calculation of the Re-Settlement.

III. Notice of Unwinding and Re-Settlement

The following announcements will be made by
HKICL:

15 minutes after the Final Cut-off time of the First
Settlement

- Unwinding of the First Settlement announced.

- Estimate of the time of the Re -Settlement
announced.

- Estimates of any other deadline adjustments
announced.

IV. Unwinding and Re-Settlement

- HKICL notifies Members of their Re -
Settlement Amounts via the MBT.

As soon as possible after the Final Cut -off time
of the First Settlement

- Mandatory Immediate Suspension of the
Default Member(s) continues

- Settlement Holds on the non -default Members
for the First Settlement will be released but
such Settlement Holds will be replaced
immediately by new Settlement Holds for the
debit Re -Settlement Amounts and the
Settlement Process on the Re -Settlement will
immediately start at the same time.

- Final Cut-off time for the Re-Settlement.

30 minutes after the commencement of the Re -
Settlement

V. Declaration of default of the Default Member(s)

Declaration of default of the Default Member(s). In
the meantime, Mandatory Immediate Suspension
of the Default Member(s) will continue until the
declaration of MA otherwise.

Any time subject to the decision of MA.

## Page 75

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 72

Event TIME at which the Event is to occur

VI. Exception

Paragraphs II, III, IV and V of Part I of this
Schedule shall not apply to a Bulk Clearing
Settlement Run for CCASS Participant Items and
SCCASS Participant Items in which the available
balance of the CHATS Ledger Account of HKSCC
is insufficient to meet i ts Bulk Clearing
Commitment at the Final Cut-off time. Such Bulk
Clearing Settlement Run will be cancelled pursuant
to paragraphs 11 and 12 of section C of Part III of
Schedule III.

VII. Application

Schedule I does not apply in relation to OTC Items, JETCO Items, SJET Items and Credit Card Items.

Definitions:

“Re-Settlement” means the Settlement Process for and the settlement of a Bulk Clearing Settlement Run after
the unwinding of the First Settlement and the re-calculation of the Settlement Amounts of the Members excluding
those of the Default Member(s) in the event that one or more of the Member(s) default(s) in a Bulk Clearing
Settlement Run in the circumstances set out in II of this Schedule.

“Re-Settlement Amounts ” means the Settlement Amounts payable or receivable by the Members in a Re -
Settlement.

## Page 76

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 73

Part II

The following provisions apply in the event that one or more GD Banks are in default ( “Default GD Bank(s)”):

Event TIME at which the Event is to occur

(a) The relevant GD Settlement Centre will
notify the relevant GD Agent and the relevant
GD Agent will notify HKICL.

Notification of GD Bank default after
12.45 hours on a day (D) will not affect the
settlement of day D-1 GD Cheques.

Before 12.45 hours
(b) The relevant GD Settlement Centre will
provide to the relevant GD Agent details of
the GD Cheques ( “Default Transactions ”)
relating to the Default GD Bank(s). The
Default Transactions will be treated as
Unpaid Articles.

As soon as possible
(c) As soon as practicable after receipt of
notification from the relevant GD Agent,
HKICL will announce the name(s) of the
Default GD Bank(s) to the Members.
Members will not thereafter deliver to
HKICL any GD Cheques relating to the
Default GD Bank(s).

As soon as possible after receipt of notification
from the relevant GD Agent

(d) The relevant GD Agent will certify the
details of the Default Transactions and
submit the certified details to HKICL.

As soon as possible after receipt of the details
by the relevant GD Agent
(e) HKICL will process the Default Transactions
as Unpaid Articles and notify the Members.

As soon as possible
(f) Settlement will take place at the normal time
or a revised time to be announced by HKICL
after removal of the Default Transactions.

Normal Cut -off time or a revised time to be
announced by HKICL

## Page 77

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 74

SCHEDULE II CHATS, CCASS, CCPMP CUT-OFF AND END OF DAY CUT-OFF

Part I CHATS Customer Cut-off, CHATS Bank Cut-off and CHATS Value Date Cut-off

CHATS (other than the processing in respect of Articles) is available for around -the-clock processing, but there
is a need to have a cut-off time to distinguish payments for same-day value and payments for next-day value and
to enable Members to assess their end -of-day positions. The following are the arrangements relating to various
cut-off times:

1. CHATS (other than the processing in respect of Articles) will have 24 hours ’ availability (subject to
scheduled regular house keeping and maintenance work), but for Monday to Friday which is a Working
Day, CHATS Customer Cut-off will be at 18.00 hours and CHATS Bank Cut-off will be at 18.30 hours,
with the CHATS Value Date Cut -off (i.e. System Date changed) at 18.35 hours or such other time
determined by MA from time to time.

2. During the period between CHATS Customer Cut-off and CHATS Bank Cut-off, Members (save where
indicated otherwise) can

- (except CLS Bank) view details of incoming funds (other than those incoming funds in respect of
Articles) awaiting settlement via an enquiry function

- (except CLS Bank) subject to Rule 6.3.1. 5, Rule 6.3.8.5 , Rule 6.3. 14.3(f) and Rule 6.13.8, re -
sequence CHATS Payment Instructions Value Today , OTC Clear Payment Instructions Value
Today and CLS Payment Instructions Value Today in the Normal Queue

- input CHATS Payment Instructions Value Today which are non -customer related payments and
CLS Payment Instructions Value Today

- input CHATS Payment Instructions Value Forward Day, CCASS Optimiser Payment Instructions
Value Forward Day, SCCASS Optimiser Payment Instructions Value Forward Day, CHATS
Optimiser Payment Instructions Value Forward Day and CLS Payment Instructions Value Forward
Day

but Members cannot

- input CHATS Payment Instructions Value Today which are for customer related payments

- cancel CHATS Payment Instructions Value Today , OTC Clear Payment Instructions Value Today
and CLS Payment Instructions Value Today in the Normal Queue

3. During the period between CHATS Customer Cut-off and CHATS Bank Cut -off, OTC Clear Payment
Instructions Value Today or OTC Clear Payment Instructions Value Forward Day will be generated
according to any OTC Clear Debit Requests transmitted or delivered by OTC Clear to the Clearing
House Computer.

4. During the period between CHATS Bank Cut-off and CHATS Value Date Cut-off, Members can

- input CHATS Payment Instructions Value Forward Day, CCASS Optimiser Payment Instructions
Value Forward Day, SCCASS Optimiser Payment Instructions Value Forward Day, CHATS
Optimiser Payment Instructions Value Forward Day and CLS Payment Instructions Value Forward
Day

- subject to Rule 6.3.1.5, Rule 6.3.14.3(f) and Rule 6.13.8, re-sequence CHATS Payment Instructions
Value Today and OTC Clear Payment Instructions Value Today in the Normal Queue

but Members cannot

## Page 78

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 75

- input CHATS Payment Instructions Value Today, CCASS Optimiser Payment Instructions Value
Today, SCCASS Optimiser Payment Instructions Value Today, CHATS Optimiser Payment
Instructions Value Today and CLS Payment Instructions Value Today

- cancel CHATS Payment Instructions Value Today and OTC Clear Payment Instructions Value
Today in the Normal Queue

5. During the period between CHATS Bank Cut-off and CHATS Value Date Cut-off, OTC Clear Payment
Instructions Value Forward Day will be generated according to any OTC Clear Debit Requests
transmitted or delivered by OTC Clear but no OTC Clear Payment Instru ctions Value Today will be
generated.

6. After CHATS Bank Cut-off, the Clearing House Computer will:

- cancel any outstanding CLS Payment Instruction Value Today in the Normal Queue

- reject CLS Payment Instruction Value Today

- accept CLS Payment Instruction Value Forward Day

7. After the CHATS Value Date Cut-off:

- no CHATS Payment Instructions, OTC Clear Payment Instructions, CCASS Optimiser Payment
Instructions, SCCASS Optimiser Payment Instructions, CHATS Optimiser Payment Instructions or
CLS Payment Instructions with a value date prior to the System Date will be accepted

- only CHATS Payment Instructions, OTC Clear Payment Instructions, CCASS Optimiser Payment
Instructions, SCCASS Optimiser Payment Instructions, CHATS Optimiser Payment Instructions
and CLS Payment Instructions for value as of the System Date immediately after the CHATS Value
Date Cut-off or as of the Supported Forward Days will be accepted

8. After the CHATS Value Date Cut -off and the completion of the processing of the CHATS Payment
Instructions input prior to the CHATS Bank Cut-off or OTC Clear Payment Instructions generated prior
to the CHATS Bank Cut -off, CHATS Payment Instructions Value Today or OTC Clear Payment
Instructions Value Today in the Normal Queue will be cancelled automatically.

## Page 79

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 76

Part II CCASS Interim Cut-off and CCASS End of Day Cut-off

The following are the arrangements for CCASS Interim Cut-off and CCASS End of Day Cut-off:

1. At 3:30 p.m. CCASS will send a preliminary CCASS Interim Cut-off message to CHATS.

2. At 3:35 p.m. CCASS will send a final CCASS Interim Cut-off message to CHATS.

3. After receipt of the preliminary CCASS Interim Cut-off message referred to in paragraph 1:

(a) the Clearing House Computer will:

(i) not settle any further CCASS Interim Cut-off Payments;

(ii) reject all instructions for the processing of further CCASS Interim Cut-off Payments;

(iii) cancel all undelivered validation requests, validation requests awaiting response from
CCASS and queued payments pending in the Normal Queue and Pending Queue for the
CCASS Interim Cut-off Payments; and

(iv) continue to send outstanding confirmation advices to CCASS and to receive
acknowledgements from CCASS for the CCASS Interim Cut -off Payments which are
settled before the CCASS Interim Cut-off; and

(b) CCASS will:

(i) reject all incoming validation requests for the CCASS Interim Cut -off Payments which
are sent by CHATS before the CCASS Interim Cut-off but arrived afterwards; and

(ii) continue to process effected payments, to receive outstanding confirmation advices and
to send acknowledgements for the CCASS Interim Cut-off Payments.

4. After receipt of the final cut-off message to CHATS referred to in paragraph 2:

(a) the Clearing House Computer will stop all further processing of CCASS Interim Cut-off Payments;
and

(b) CCASS will stop all further processing of CCASS Interim Cut-off Payments.

5 At 6:00 p.m. CCASS will send a preliminary CCASS End of Day Cut -off message to CHATS.

6. At 6:05 p.m. CCASS will send a final CCASS End of Day Cut-off message to CHATS.

7. After receipt of the preliminary CCASS End of Day Cut-off message referred to in paragraph 5:

(a) the Clearing House Computer will:

(i) not settle any further CCASS End of Day Cut-off Payments;

(ii) reject all instructions for the processing of further CCASS End of Day Cut-off Payments;

(iii) cancel all undelivered validation requests, validation requests awaiting response from
CCASS and queued payments pending in the Normal Queue and Pending Queue for the
CCASS End of Day Cut-off Payments; and

(iv) continue to send outstanding confirmation advices to CCASS and to receive
acknowledgements from CCASS for the CCASS End of Day Cut-off Payments which are
settled before the CCASS End of Day Cut-off; and

## Page 80

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 77

(b) CCASS will:

(i) reject all incoming validation requests for the CCASS End of Day Cut-off Payments
which are sent by CHATS before the CCASS End of Day Cut-off but arrived afterwards;
and

(ii) continue to process effected payments, to receive outstanding confirmation advices and
to send acknowledgements for the CCASS End of Day Cut-off Payments.

8. After receipt of the final cut-off message to CHATS referred to in paragraph 6:

(a) the Clearing House Computer will stop all further processing of CCASS End of Day Cut-off
Payments; and

(b) CCASS will stop all further processing of CCASS End of Day Cut-off Payments.

For the avoidance of doubt, the above provisions apply to the normal process for CCASS Interim Cut -off and
CCASS End of Day Cut -off. In case of exceptional circumstances due to situations including but not limited to
CCASS failure, the communication link between the Clearing House Computer and CCASS fails or when the
CHATS Customer Cut -off is earlier than the CCASS Interim Cut -off or CCASS End of Day Cut -off, the
arrangements as stipulated in the Operating Procedures shall prevail.

## Page 81

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 78

Part III CCPMP Cut-off (in respect of CCP Instructions and CCPO Instructions)

The following are the arrangements for CCPMP:

1. CCPMP will commence operation on each Working Day at CCPMP Commencement or such other time
as determined by MA from time to time.

2. At 18.30 hours on Working Days or such other time as determined by MA from time to time, CCPMP
will send a cut-off message to CHATS.

3. After receipt of the cut-off message referred to in paragraph 2 or after CHATS Bank Cut-off, whichever
is the earlier, the Clearing House Computer will:

(i) cancel all CCP Instructions and CCPO Instructions with value date being the current Working Day
which are waiting for CCPMP’s validation response;

(ii) cancel all CCP Instructions with value date being the current Working Day which are in the
Normal Queue;

(iii) reject any incoming CCP Instructions and CCPO Instructions with value date being the current
Working Day; and

(iv) cancel all CCPO Instructions with value date being the current Working Day which has not been
settled;

4. After the cut-off message referred to in paragraph 2 is received, the Clearing House Computer will one
by one release the hold in Sending Member’s CHATS Ledger Account of the funds in respect of
outstanding CCP Instructions. This provision does not apply to CCPO Instructions.

## Page 82

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 79

Part IV End of Day Cut-off

CHATS (other than the processing in respect of Articles) is available for around the clock processing of Direct
Credit Instructions or Direct Debit Instructions but there is a need to have a cut off time to distinguish payments
for same day value and payments for next day value to enable Members and MA to assess their end of day
positions. The following are the arrangements relating to the cut off time.

1. The End of Day Cut-off will be triggered upon completion of the CHATS Value Date Cut -off, and will
occur at 18.45 hours on Working Days or such other time as determined by MA from time to time.

2. During the period prior to End of Day Cut-off

MA may

- input Direct Credit Instructions

- input Direct Debit Instructions

- subject to Rule 6.3.10.5 and Rule 6.13.8, re-sequence Direct Debit Instructions or cancel any of the
Direct Debit Instructions Value Today in the Normal Queue

3. After the End of Day Cut-off, the Clearing House Computer will:

- not settle any Direct Debit Instruction Value Today and Direct Credit Instruction Value Today; and

- cancel all Direct Debit Instructions Value Today in the Normal Queue

MA cannot

- input Direct Debit Instructions or Direct Credit Instructions Value Today

MA can

- input Direct Debit Instructions Value Forward Day or Direct Credit Instructions Value Forward
Day

## Page 83

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 80

SCHEDULE III CLEARING & SETTLEMENT OF ARTICLES, CCASS OPTIMISER PAYMENT
INSTRUCTIONS, SCCASS OPTIMISER PAYMENT INSTRUCTIONS, CHATS
OPTIMISER PAYMENT INSTRUCTIONS AND CCPO INSTRUCTIONS

Part I The Timetable for Delivery of Articles to the Clearing House

[This section has been left blank intentionally]

## Page 84

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 81

Part II The Timetable for the Settlement of Articles, CCASS Optimiser Payment Instructions,
SCCASS Optimiser Payment Instructions, CHATS Optimiser Payment Instructions and
CCPO Instructions

[This section has been left blank intentionally]

## Page 85

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 82

Part III Clearing & Settlement of Articles (Excepting OTC Items, JETCO Items , SJET I tems and
Credit Card Items)

A. General

1. If the available bal ance in the CHATS Ledger Account of a Member other than HKSCC is
insufficient to meet its Bulk Clearing Commitment at the Final Cut -off time of a Bulk Clearing
Settlement Run, the Member shall be deemed to have defaulted in the Bulk Clearing Settlement Run
concerned and the Default Arrangement set out in Schedule I shall apply. If the available balance
in the CHATS Ledger Account of HKSCC is insufficient to meet its Bulk Clearing Commitment at
the Final Cut-off time of a Bulk Clearing Settlement Run, the Bulk Clearing Settlement Run will be
cancelled pursuant to paragraphs C.11 and C.12 of Schedule III Part III.

2. Bulk Clearing Settlement Runs will be completed at specified times during the day as provided in
these Clearing House Rules and the principle of “all or none” shall apply to each of the Bulk Clearing
Settlement Runs. If a Member other than HKSCC is in default of its Bulk Clearing Commitment, (i)
its name will be identified and announced and (ii) the defaulted Bulk Clearing Settlement Run
concerned will be unwound and there will be a Re -settlement excluding the Member in default
subject to and in accordance with the provisions of the Default Arrangement.

3. The Settlement Amount of each Member for a particular Bulk Clearing Settlement Run will be made
available to that Member from the Clearing House Computer through the MBT upon completion of
Bulk Clearing Settlement Run or return process ing of relevant Articles as the case may be . The
details of notification arrangements are stipulated in the Operating Procedures.

4. The clearing items of the following respective Bulk Clearing Settlement Runs will be separately
merged:

(a) the Bulk Clearing Settlement Runs for CLG Items and e-Cheques.

(b) the Bulk Clearing Settlement Runs for SEPS Items and E-bill Payments for settlement in the
evening.

Members will be given only one aggregated Settlement Amount for the Bulk Clearing Settlement
Runs merged but a break-down for each of the merged Bulk Clearing Settlement Runs will also be
given for the relevant Member’s reference. The merged Bulk Clearing Settlement Runs will not be
split in the event of default. However, if there are problems of a technical or ope rational nature
preventing one of the merged Bulk Clearing Settlement Runs from being completed, HKICL shall
be entitled to exercise the management discretion to split the said Bulk Clearing Settlement Runs
with appropriate notification to the Members.

5. If there are payments in the Normal Queue, the payment of the Settlement Amount in respect of a
Bulk Clearing Settlement Run and the payment of any amounts in respect of CCASS Optimiser
Payment Instructions, SCCASS Optimiser Payment Instructions, CHATS Optimiser Payment
Instructions and CCPO Instructions scheduled to be settled simultaneously with a Bulk Clearing
Settlement Run will have priority over the other CHATS Payment Instructions Value Today, OTC
Clear Payment Instructions Value Today, CCP Instructions Value Today, CLS Payment Instructions
Value Today, CCASS Payment Instructions and Direct Debit Instructions Value Today in the
Normal Queue.

6. The above provisions apply to GD Cheques, except that the “all or none” principle applies, in the
case of default by one or more GD Banks, only to exclude the GD Cheques relating to such GD
Bank(s). In relation to GD Cheques, references to the Member are references to the relevant GD
Agent.

## Page 86

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 83

B. EPS Items

[This provision has been left blank intentionally]

C. CCASS Items

[This provision has been left blank intentionally]

D. E-bill Payments

[This provision has been left blank intentionally]

E. SEPS Items

[This provision has been left blank intentionally]

F. MPF Items

[This provision has been left blank intentionally]

G. Paper Cheques (other than GD Cheques)

[This provision has been left blank intentionally]

H. GD Cheques

[This provision has been left blank intentionally]

I. e-Cheques

[This provision has been left blank intentionally]

J. Settlement Holds

The Clearing House Computer will place a Settlement Hold for the debit Settlement Amount of a
Member as from the commencement of the Settlement Process of each Bulk Clearing Settlement Run
and if all Members with debit Settlement Amounts have sufficient av ailable funds in their CHATS
Ledger Accounts, such Settlement Amounts will be automatically debited and the relevant credit
Settlement Amounts will be automatically credited to all relevant CHATS Ledger Accounts, and the
settlement will immediately be deemed to be effected and completed notwithstanding that the Final Cut-
off time for the Bulk Clearing Settlement Run concerned has not yet arrived. Details of the Settlement
Process are set out in the Default Arrangement, except in relation to JETCO Items , SJET Items, Credit
Card Items and OTC Items where the details are set out in Part IV , Part V and Part VI below. For the
avoidance of doubt, the Settlement Holds are only applicable up to the debit Settlement Amount of the
Member concerned and a Settlement Hold will not affect the utilization of funds in the CHATS Ledger
Account which exceeds the debit Settlement Amount relating to the Bulk Clearing Settlement Run for
which the Settlement Process has commenced.

## Page 87

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 84

Part IV Settlement of JETCO Items and SJET Items

1. JETCO Items and SJET Items (containing only instructions to credit or debit net settlement amounts to
the CHATS Ledger Accounts of JETCO Members) will be submitted by JETCO to the Clearing House
on Day D before the cut-off time provided in Part I above and will be acted on by HKICL.

2. Inter-Member settlement for JETCO Items and SJET I tems will be effected in accordance with the
timetable set out in Part II above. The Settlement Amount of each JETCO Member for a particular Bulk
Clearing Settlement Run of JETCO Items and SJET I tems will be made available from the Clearing
House Computer to JETCO Members through the MBT upon successful capture of the settlement file.

3. The Clearing House Computer will place a Settlement Hold for the debit Settlement Amount of a JETCO
Member as from the commencement of the Settlement Process of each Bulk Clearing Settlement Run of
JETCO Items and SJET Items and if all JETCO Members with debit Settlement Amounts have sufficient
available funds in their CHATS Ledger Accounts, such Settlement Amounts will be automatically
debited and the relevant credit Settlement Amounts will be automatically credited to all relevant CHATS
Ledger Accounts, and the settlement will immediately be deemed to be effected and completed
notwithstanding that the Final Cut-off time for the Bulk Clearing Settlement Run concerned has not yet
arrived.

4. The principle of “all or none ” shall apply to eac h Bulk Clearing Settlement Run of JETCO Items and
SJET Items. If the available balance in the CHATS Ledger Account of a JETCO Member is insufficient
to meet its Bulk Clearing Commitment at the Final Cut -off time of a Bulk Clearing Settlement Run for
JETCO Items or SJET Items, as the case may be, the JETCO Member shall be deemed to have defaulted
in the Bulk Clearing Settlement Run concerned, and the following provisions shall apply:

(a) HKICL will directly inform JETCO and the Member (as notified by JETCO to HKICL in
writing from time to time) which is for the time being the chairman of JETCO's board of
directors of the default identifying the JETCO Member in default;

(b) HKICL shall not debit or credit the CHATS Ledger Account of any JETCO Member in respect
of the Bulk Clearing Settlement Run of the JETCO Items or SJET Items in default, but shall
maintain Settlement Holds on all JETCO Members (including so much as is available in the
CHATS Ledger Account of the JETCO Member in default) in respect of that Bulk Clearing
Settlement Run until such Settlement Holds are replaced by Settlement Holds in respect of the
settlement pursuant to paragraph (c) below;

(c) if the default occurs on any Working Day,

for JETCO Items

(i) JETCO shall deliver to the Clearing House instructions to credit or debit net settlement
amounts, after excluding all transactions relating to the JETCO Member in default, in
respect of the Bulk Clearing Settlement Run in default, at least 30 minutes b efore the
commencement of the settlement pursuant to (ii) below;

(ii) following receipt of the new net settlement instructions pursuant to (i) above, HKICL
will replace the Settlement Hold made pursuant to paragraph 3 with a new Settlement
Hold excluding JETCO Items of the JETCO Member in default and shall undertake a
Bulk Clearing Settlement Run based on such new instructions on the same day;

(iii) if for any reason a Bulk Clearing Settlement Run based on such new instructions
cannot be undertaken or completed in accordance with (ii) above, JETCO shall merge
the transactions covered by such new instructions into the next Working Day's JETCO
Items and provide to HK ICL, as the next Working Day's JETCO Items, payment
instructions containing the net settlement amounts for both sets of JETCO transactions;
if a settlement is not successfully undertaken or completed in accordance with (ii)
above, the Settlement Holds in respect of that settlement will only be released at the

## Page 88

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 85

time of the End of Day Cut-off on the day on which the default occurred or, if earlier,
at the time of commencement of another Bulk Clearing Settlement Run in respect of
any Articles.

for SJET Items

(i) JETCO shall deliver to the Clearing House instructions to credit or debit net settlement
amounts, after excluding all transactions relating to the JETCO Member in default, in
respect of the Bulk Clearing Settlement Run in default;

(ii) following receipt of the new net settlement instructions pursuant to (i) above, HKICL
will replace the Settlement Hold made pursuant to paragraph 3 with a new Settlement
Hold excluding SJET Items of the JETCO Member in default and will undertake a
Bulk Clearing Settlement Run based on suc h new instructions commencing at a time
decided by HKICL on the same day;

(iii) if for any reason a Bulk Clearing Settlement Run based on such new settlement
instructions cannot be undertaken in accordance with (ii) above, JETCO shall merge
the SJET Items (excluding all items relating to the JETCO Member in default) into the
same Working Day’s JETCO Items and provide to HKICL, payment instructions
containing the net settlement amounts for both sets of JETCO transactions before the
normal presentation time of the JETCO Items on the same Working Day; if a
settlement is not successfully undertaken or completed in accordance with (ii) above,
the Settlement Holds in respect of that settlement will only be released at the time
agreed between HKICL and JETCO.

5. (a) In the event that, in the opinion of JETCO, a member of JETCO (not being a Member) is
insolvent, JETCO may replace or retract the JETCO settlement file one hour before the
commencement of scheduled settlement process for JETCO Items or SJET Items as set out in
Part II.

(b) In case the settlement file is retracted and replaced prior to one hour before the commencement
of the settlement process as aforesaid, the Bulk Clearing Settlement Run will take place using
the replacement settlement file in lieu of that retracted.

(c) In case the JETCO settlement file is retracted and not replaced prior to one hour before the
commencement of the settlement process as aforesaid on any Working Day:

for JETCO Items

(i) JETCO may deliver to the Clearing House a new settlement file one hour before the
commencement of the scheduled settlement process in the afternoon for JETCO Items,
excluding all transactions relating to the insolvent member of JETCO (not being a
Member). Following receipt of the new settlement file, HKICL shall undertake a Bulk
Clearing Settlement Run based on the new instructions on same day ;

(ii) in case the JETCO settlement file is not replaced prior to one hour before the
commencement of the scheduled settlement process in the afternoon, there will be no
Bulk Clearing Settlement Run for JETCO Items on that day; and JETCO Items
excluding transactions relating to the insolvent member of JETCO (not being a
Member) will be merged into the next Working Day's JETCO Items. JETCO will, in
accordance with Schedule III Part I Section E, provide to HKICL a settlement file
containing the net settlement amounts for JETCO Items for that Working Day and for
the preceding Working Day (excl uding transactions relating to the insolvent member
of JETCO (not being a Member) in respect of the preceding Working Day).

for SJET Items

(i) SJET Items excluding transactions relating to the insolvent member of JETCO (not

## Page 89

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 86

being a Member) will be merged into the same Working Day’s JETCO Items. JETCO
will, in accordance with Schedule III Part I Section E, provide to HKICL a settlement
file containin g the net settlement amounts for both sets of SJET Items (excluding
transactions relating to the insolvent member of JETCO (not being a Member)) and
JETCO Items before the normal presentation time of the JETCO Items;

(ii) following receipt of the replace or retract settlement file pursuant above, JETCO shall
inform HKICL by phone followed by fax and detailing the reason of retraction or
replacement of the settlement file.

6. Part III of this Schedule does not apply to JETCO Items and SJET Items.

## Page 90

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 87

Part V Settlement of Credit Card Items

1. Procedures for settlement of Credit Card Items between Members are set out below and in Part II above.
The Settlement Amount of each Credit Card Member in respect of a Bulk Clearing Settlement Run of
Credit Card Items will be made available from the Clearing House Computer to such Credit Card
Member through the MBT upon successful capture of settlement files . Separate Bulk Clearing
Settlement Run s will be used for each Credit Card Company and for any Credit Card Company
appointing more than one Card Ag ent a separate Bulk Clearing Settlement Run will be used for Credit
Card Items generated by each Card Agent of that Credit Card Company. The schedule of the Bulk
Clearing Settlement Runs will be in the sequence specified in the Operating Procedures .

2. In the event that any Bulk Clearing Settlement Run of the Credit Card Items cannot be completed by the
Final Cut-off time, the outstanding Bulk Clearing Settlement Run will be re -scheduled on the same day
at MA’s discretion.

3. The Clearing House Computer will place a Settlement Hold on a debit Settlement Amount of a Credit
Card Member as from the commencement of the Settlement Process of each Bulk Clearing Settlement
Run of Credit Card Items. However, if in respect of a Bulk Clearing Settlement Run all Credit Card
Members with debit Settlement Amounts have sufficient funds in their CHATS Ledger Accounts, and if
the debit settlement amount of each member of the Credit Card Company does not exceed its pre-set
direct debit authorisation limit, the Settlement Amounts will be debited and the relevant credit Settlement
Amounts will be credited to all relevant CHATS Ledger Accounts pursuant to Rule 3.1.3
notwithstanding that the Final Cut-off time for the Bulk Clearing Settlement Run concerned has not yet
arrived.

4. The principle of “all or none” shall apply to each Bulk Clearing Settlement Run of Credit Card Items.

5. In the event that any Bulk Clearing Settlement Run of Credit Card Items cannot be completed before the
Final Cut-off Time, the following arrangements will apply and the options applicable to the Credit Card
Company concerned are stipulated in the Operating Procedures:

5.1 If in respect of a Bulk Clearing Settlement Run the debit Settlement Amount of a Credit Card
Member for Credit Card Items for the Credit Card Company concerned exceeds the pre-set
direct debit authorisation limit (s) of that Credit Card Member (if it is a member of the Credit
Card Company) and each of the Non -bank Card Member(s) (if any) for which the Credit Card
Member acts as a settlement agent; or if there are insufficient funds in a Credit Card Member’s
CHATS Ledger Account (i.e. the Credit Card Member has sufficient funds in its CHATS
Ledger Account to meet its Bulk Clearing Commitment other than Credit Card Items for the
Credit Card Company concerned but not sufficient also to meet its Bulk Clearing Commitment
in respect of Credit Card Items for the Credit Card Company concerned) in that Bulk Clearing
Settlement Run, subject to the advice of MA, one of the following arrangements shall apply in
the manner provided in the Operating Procedures:

(a) The Card Agent in respect of that Bulk Clearing Settlement Run may take up the
settlement obligation of the relevant Credit Card Member; or

(b) The relevant Bulk Clearing Settlement Run for the Credit Card Company concerned
will be withheld. The Credit Card Company concerned or its Card Agent as the case
may be shall exclude all Credit Card Items of the Credit Card Company concerned in
that Bulk Clearing Settlement Run relating to the Credit Card Member concerned and
re-submit a new settlement file to the Clearing House for settlement. The details of
arrangements are stipulated in the Operating Procedures; or

(c) The Bulk Clearing Settlement Run for the Credit Card Company concerned will be
cancelled. All settlement obligations related to the unprocessed Credit Card Items will
be handled according to the separate arrangements between the Credit Card Company
concerned and its members.

## Page 91

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 88

5.2 If in respect of a Bulk Clearing Settlement Run a Credit Card Member is in default (i.e. the
Credit Card Member is announced as a Default Member under Schedule I Part I Paragraph II
or Clearing Facilities have been suspended or refused to the Credit Card Member under Rule
5.1, 5.2 or 5.3), the following arrangements shall apply:

(a) The relevant Bulk Clearing Settlement Run of the Credit Card Company concerned
will be withheld. The Credit Card Company concerned or its Card Agent as the case
may be shall exclude all Credit Card Items of the Credit Card Company concerned in
that Bulk Clearing Settlement Run relating to the Credit Card Member in default and
re-submit a new settlement file to the Clearing House for settlement. The details of
arrangements are stipulated in the Operating Procedures; or

(b) The relevant Bulk Clearing Settlement Run of the Credit Card Company concerned
whose Credit Card Member is in default will be cancelled. All settlement obligations
relating to the unprocessed Credit Card Items will be handled according to the separate
arrangements between the Credit Card Company concerned and its members.

If the Bulk Clearing Settlement Run is not successfully undertaken or completed under paragraph 5.1 or
5.2, the Settlement Holds will be released upon replacement by new Settlement Hold s placed for a
subsequent Bulk Clearing Settlement Run.

6. Part III of this Schedule does not apply to Credit Card Items.

## Page 92

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 89

Part VI Clearing and Settlement of OTC Items

1. [This provision has been left blank intentionally]

2. [This provision has been left blank intentionally]

3. [This provision has been left blank intentionally]

4. [This provision has been left blank intentionally]

5. If the available balance in the CHATS Ledger Account of a Member for OTCCHU Items is insufficient
to meet its Bulk Clearing Commitment before the commencement of the Bulk Clearing Settlement Run
of OTC Items set out in Part II of Schedule III, the following provisions shall apply:

(a) The Member concerned shall directly inform OTC Clear in a manner agreed between the
Member and OTC Clear if it is a clearing member of OTC Clear; or else if it is a settlement
agent appointed by a clearing member of OTC Clear, the Member concerned should inform
OTC Clear through the clearing member(s) which designated it to be the settlement agent ;

(b) If OTC Clear should notify HKICL and generate and provide HKICL with a replacement file
in Electronic Media according to the handling procedures as stipulated in the Operating
Procedures, HKICL will generate a new set of clearing outputs to Members in the settlement
run in Electronic Media; and

(c) the settlement window of such Bulk Clearing Settlement Run of OTC Items will be extended
up to 60 minutes after the commencement of the settlement run on the same day.

6. If the available balance in the CHATS Ledger Account of a Member for OTCCHU Items is insufficient
to meet its Bulk Clearing Commitment after the commencement of the Bulk Clearing Settlement Run of
OTC Items set out in Part II of Schedule III, the following provisions shall apply:

(a) The Member concerned shall directly inform OTC Clear in a manner agreed between the
Member and OTC Clear if it is a clearing member of OTC Clear; or else if it is a settlement
agent appointed by a clearing member of OTC Clear, the Member concerned should inform
OTC Clear through the clearing member(s) which designated it to be the settlement agent ;

(b) If OTC Clear should notify HKICL and generate and provide HKICL with a replacement file
in Electronic Media according to the handling procedures as stipulated in the Operating
Procedures, HKICL will generate a new set of clearing outputs to Members in the settlement
run in Electronic Media;

(c) the settlement window of such Bulk Clearing Settlement Run of OTC Items will be extended
up to 60 minutes after the commencement of the settlement run on the same day; and

(d) HKICL shall not debit or credit the CHATS Ledger Account of any Member (including the
Member concerned with insufficient funds) in respect of the Bulk Clearing Settlement Run of
the OTC Items, but shall maintain Settlement Holds on all Members (including so much as is
available in the CHATS Ledger Account of the Member with insufficient funds) in respect of
that Bulk Clearing Settlement Run until such Settlement Holds are replaced by new Settlement
Holds in accordance with the replacement file provided by OTC Clear in (b).

7. If in respect of a Bulk Clearing Settlement Run of OTC Items a Member is in default (i.e. Clearing
Facilities have been suspended or refused to the Member under Rule 5.1, 5.2 or 5.3), the following
arrangements shall apply:

(a) Upon receipt of notification from MA, HKICL will inform OTC Clear the triggering of the
default and the identity of the Member in default in a manner agreed between HKICL and OTC
Clear;

## Page 93

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 90

(b) the Bulk Clearing Settlement Run of OTC Items relating to the Member in default will be
withheld. OTC Clear shall exclude all OTC Items relating to the Member in default and re -
submit a new clearing file to the Clearing House for clearing and settleme nt excluding the
Member in default. The details of arrangements are stipulated in the Operating Procedures;

(c) HKICL will generate a new set of clearing outputs to Members in the settlement run in
Electronic Media excluding the Member in default; and

(d) the settlement window of such Bulk Clearing Settlement Run will be extended up to 60 minutes
after the commencement of the settlement run on the same day.

8. If the Bulk Clearing Settlement Run of OTC Items is not successfully undertaken or completed under
paragraph 5, 6 or 7, the Settlement Holds will be released upon cancellation of Bulk Clearing Settlement
Run of OTC Items.

9. Part III of this Schedule does not apply to OTC Items.

## Page 94

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 91

SCHEDULE IV INTEREST ADJUSTMENT SCHEME

In order to avoid arbitrage and to deal fairly with the situation created by the difference between the value dating
of payments of Articles (other than JETCO Items; SJET Items; Credit Card Items; E-bill Payments (but including
Returned Articles of E -bill Payments); SEPS Items; SCCASS Participant It ems (but including further
amendments to SCCASS Participant Items reported by Members to CCASS after completion of the Bulk Clearing
Settlement Run for SCCASS Participant Items but before 20.00 hours on Day D); OTC Items; and Special CCASS
Items) at the inter-Member level and the Member-customer level:

(a) Paying Members shall pay Receiving Members or Receiving Members shall pay Paying Members on
the date of the relevant Bulk Clearing Settlement Run a n interest adjustment to be calculated on their
respective Net Balance Payable at the Interest Adjustment Rate.

(b) In case of holidays, Non-Clearing Day or exceptional circumstances where the settlement of the Articles
and Returned Articles of E -bill Payments has to be postponed and interest adjustment is applicable for
more than one day:

- the rate applicable for Day D for the calculation of interest adjustment under this Interest Adjustment
Scheme shall be applied throughout the whole period of the relevant interest adjustment; and

- simple interest will be used in accordance with interbank money market practice.

(c) Interest will be calculated on Friday items of GD Cheque from Friday to the settlement day, applying
the calculation method in (b) above.

(d) The Clearing House Computer calculates the total net interest adjustment payable or receivable, as the
case may be, by each Member for each Bulk Clearing Settlement Run and the same shall be made
available from the Clearing House Computer to the Members through the MBT at the time of the
completion of bulk clearing and return processing , as the case may be , of their respective Settlement
Amounts.

(e) In the event that a Member's Settlement Amount is zero, no interest adjustment will be made, but a record
therefor will still be displayed.

(f) In the event that the daily HKD Overnight Index Average (HONIA) rate for any reason is not available
on a day, the Interest Adjustment Rate that previously maintained in CHATS will be used for the
calculation of interest adjustment.

Definitions:

"Net Balance Payable" means the net amount (after ad justment for returned items) payable by a Member in a
Bulk Clearing Settlement Run for all Articles covered by the Interest Adjustment Scheme to be cleared excluding
interest adjustment under this Interest Adjustment Scheme.

"Paying Member" means a Member which will be making a payment in a Bulk Clearing Settlement Run.

"Receiving Member" means a Member which will be receiving a payment in a Bulk Clearing Settlement Run.

## Page 95

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Clearing House Rules

Redacted version: April 2026 Page 92

SCHEDULE V PROTOCOL

AGREEMENT

1. Terms defined in the Clearing House Rules (which expression includes the Clearing House Rules as
amended from time to time) will have the same meanings when used in this Protocol.

2. HKICL may, with the written approval of the Association and MA, and will, whenever requested to do
so (and in the manner so requested) by them amend the Clearing House Rules or Operating Procedures,
provided that (other than when required by MA to do so under the PSSVFO) HKICL may not be required
to amend the Clearing House Rules or Operating Procedures (as the case may be) to affect HKICL’s
rights and obligations without HKICL’s consent. (Rule 1.7)

3. If so directed by the Association and MA, HKICL will update, enhance or modify the software used by
it in relation to the operation of the Clearing House. (Rules 6.1.3 and 6.2.5)

4. HKICL will only amend the times for the delivery of Articles to the Clearing House and relating to the
various processes of clearing and/or settlement upon prior consultation with MA and the Association.
(Rule 7.1.1(a))

5. HKICL will comply with the Clearing House Rules and will promptly notify MA of any failure of any
of the Members to comply with the Clearing House Rules which comes to HKICL's attention.

6. This Protocol shall be governed by and construed in accordance with the laws of the Hong Kong Special
Administrative Region.

## Page 96

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Rainstorm Procedures
Redacted version: April 2026 Page 93

RAINSTORM PROCEDURES

1. This version of the Rainstorm Procedures is effective from the date HKICL announces that it will take
effect.

2. Subject to any exceptional circumstances, in the event of a “black” rainstorm warning being issued during
the day the Clearing House will continue to function normally . The processing, including the clearing,
return and/or settlement arrangements, and cut -off times of all CHATS Transactions and Articles (save
in respect of Paper Cheques) will be proceeded with according to the normal schedule. For the avoidance
of doubt, when “black” rainstorm signal is hoisted, the initial queue mode of OTC Clear Payment
Instruction shall be determined by the default queue mode in adverse weather/holiday as indicated by the
paying Member in accordance with the Operating Procedures.

3. Clearing, Return and Settlement Arrangement for Paper Cheques

(a) The Typhoon Procedures for the time being in force as amended will be applied to the clearing,
return and settlement arrangement for Paper Cheques.

(b) If clearing in a relevant GD Settlement Centre is suspended due to a rainstorm, the clearing or
settlement of relevant GD Cheques may be subject to variation and in such case, HKICL shall
broadcast by the MBT (and also by SWIFT to a Member who has requested that administrative
messages should also be sent to it by SWIFT) administrative message(s)/email(s) with
progressive serial number(s) a processing schedule or schedules as soon as practicable and such
processing schedule(s) so broadcasted shall be binding on Members.

(c) If banks in the Guangdong Province (excluding Shenzhen) or, as the case may be, in Shenzhen
(the "Affected Area") are not open fo r business on a day (D) due to a rainstorm, the return and
settlement of day D-1 GD Cheques relating to GD Banks in the Affected Area will be deferred
to the following day on which banks in Hong Kong and in the Affected Area are both open for
business.

4. HKICL may, at its ow n discretion, deliver broadcast or notice regarding (i) the issuance of “black”
rainstorm warning and (ii) the normal functioning of the Clearing House (including the clearing, return
and settlement arrangement for Paper Cheques) pursuant to these Rainstorm Procedures. Neither MA
nor HKICL shall owe any duty or incur any liability to any Member, OTC Clear, JETCO , any JETCO
Member, any Credit Card Company, any Credit Card Member, CMU, or any CMU member by delivering,
delaying the delivery of, or failing to deliver such broadcast or notice.

5. Notwithstanding the above, for exceptional circumstances or for operational considerations, after
consultation with MA, HKICL may vary any of the timings for and the processing schedule of the
CHATS Transactions and Articles. HKICL shall notify all Members, OTC Clear, JETCO, Credit Card
Companies and/or CMU (as the case may be) of such change which shall be binding on all Members.

## Page 97

Hong Kong Interbank Clearing Limited
Hong Kong Dollar Typhoon Procedures
Redacted version: April 2026 Page 94

TYPHOON PROCEDURES

1. This version of the Typhoon Procedures is effective from the date when HKICL announces that it will
take effect.

2. These Procedures have been drawn up to give guidance to Members as to the procedures to be adopted
in the event of the hoisting of Typhoon signal no. 8 or above or the announcement of Extreme Conditions.
The Procedures are drawn up so as to avoid confusion or misunderstanding among Members.

3. Subject to any exceptional circumstances, the processing, including the clearing, return and/or settlement
arrangements, and cut -off times of all CHATS Transactions and Articles (save in respect of Paper
Cheques) will be proceeded with according to the nor mal schedule. For the avoidance of doubt, when
typhoon signal no. 8 or above is hoisted or Extreme Conditions are in force, the initial queue mode of
OTC Clear Payment Instruction shall be determined by the default queue mode in adverse
weather/holiday as indicated by the paying Member in accordance with the Operating Procedures .

4. Clearing, Return and Settlement arrangements for Paper Cheques

(a) Subject to any exceptional circumstances, the presentation of Paper Cheques of the day for clearing
will be accepted according to the normal schedule except that the presentation of Paper Cheques
of the day and the clearing thereof will be held over to the immediately following Working Day in
the case when typhoon signal no. 8 or above or Extreme Conditions remain in force up to and
including 12.00 hours on the day. The return and settlement of the preceding Working Day Paper
Cheques will be proceeded with according to the normal schedule, provided that clearing of
preceding Working Day Paper Cheques has been processed as usual. The details of the
arrangements are stipulated in the Operating Procedures. If it is not a working day in the
Guangdong Province (excluding Shenzhen) or, as the case may be, Shenzhen (the “Affected
Area”), the return and settlement of GD Cheques relating to GD Banks in the Affected Area will
be held over to the following working day in both Hong Kong and the Affected Area.

(b) If clearing in one or more GD Settlement Centres is suspended due to a typhoon, the clearing or
settlement of relevant GD Cheques may be subject to variation and in such case, HKICL shall
broadcast by the MBT (and also by SWIFT to a Member who has requeste d that administrative
messages should also be sent to it by SWIFT) administrative message(s)/email(s) with progressive
serial number(s) a processing schedule or schedules as soon as practicable and such processing
schedule(s) so broadcasted shall be binding on Members.

(c) If banks in the Affected Area are not open for business on a day (D) due to a typhoon, the return
and settlement of day D-1 GD Cheques relating to GD Banks in the Affected Area will be deferred
to the following day on which banks in Hong Kong and in the Affected Area are both open for
business.

5. HKICL may, at its own discretion, deliver broadcast or notice regarding (i) the hoisting of Typhoon
signal no. 8 or above or the announcement of Extreme Conditions and (ii) the normal functioning of the
Clearing House (including the clearing, return and se ttlement arrangement for Paper Cheques) pursuant
to these Typhoon Procedures. Neither MA nor HKICL shall owe any duty or incur any liability to any
Member, OTC Clear, JETCO, any JETCO Member, any Credit Card Company, any Credit Card Member,
CMU, or any CMU member by delivering, delaying the delivery of, or failing to deliver such broadcast
or notice.

6. Notwithstanding the above, for exceptional circumstances or for operational considerations, after
consultation with MA, HKICL may vary any of the timings for and the processing schedule of the
CHATS Transactions and Articles. HKICL shall notify all Members, OTC Clear, JETCO, Credit Card
Companies and/or CMU (as the case may be) of such change which shall be binding on all Members.
