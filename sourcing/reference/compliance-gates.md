# Pre-Order Compliance Gates (India)

Run this before confirming an order. A regulatory blocker discovered after the container sails is a
detention-and-demurrage problem, and in the worst case a confiscation problem.

| Gate | Applies to | Who must hold it | Where to check |
|------|-----------|------------------|----------------|
| **BIS Scheme-I (ISI mark)** | Products under a domestic QCO — steel, cement, footwear, toys, many others | The **foreign manufacturer**, licensed for the specific factory and product | `manakonline.in`, DPIIT / line-ministry QCO notifications |
| **BIS Scheme-II (CRS)** | Notified electronics & IT goods | Foreign manufacturer, registered per model | BIS CRS portal |
| **WPC / ETA** | Anything with Wi-Fi, Bluetooth, RF, LoRa, NFC | The **importer** | WPC Saral Sanchar |
| **TEC MTCTE** | Notified telecom equipment | Importer / OEM | TEC portal |
| **LMPC** | Any pre-packaged commodity sold retail | Importer — **registration required before import** | State / Central Legal Metrology |
| **EPR — Plastic Packaging** | Plastic packaging entering India | Importer, registered as Producer/Importer | `eprplastic.cpcb.gov.in` |
| **EPR — E-Waste** | EEE under the E-Waste Rules | Importer | CPCB e-waste EPR portal |
| **EPR — Batteries** | Cells, packs, devices containing batteries | Importer | CPCB battery EPR portal |
| **FSSAI** | Food, food-contact articles, supplements | Importer licence + product approval | FSSAI FoSCoS |
| **CDSCO** | Medical devices, cosmetics, drugs | Import licence per class | CDSCO SUGAM |
| **Plant / animal quarantine** | Wood packaging, plant or animal origin goods | ISPM-15 stamp on pallets; PQ clearance | DPPQS |
| **Import policy condition** | Every line — Free / Restricted / Prohibited | DGFT licence if Restricted | DGFT ITC(HS) schedule |

## Non-negotiable rules

1. **BIS licences belong to the factory, not the trader.** Ask for the licence number, then verify
   it on the BIS portal against the exact manufacturer name, address and product model. A scanned
   certificate emailed by a supplier is not verification.
2. **LMPC registration must exist before the goods arrive.** Customs will hold pre-packaged retail
   goods without it. Label content (importer name and address, net quantity, MRP, month/year of
   import, country of origin, consumer care details) must be printed or affixed **before**
   clearance — relabelling in the CFS is expensive and not always permitted.
3. **Country-of-origin marking** is a customs requirement, not a marketing choice. Unmarked or
   mismarked goods invite detention.
4. **When the QCO status of an HS line is unclear, stop and verify.** Never proceed on a supplier's
   assurance that "others import this without BIS".

## Output of this gate

For each SKU record: ITC(HS) 8-digit • import policy • applicable QCO + licence number and validity
• EPR registration reference • labelling artwork approved • owner of each item. Any blank field
blocks the PO.
