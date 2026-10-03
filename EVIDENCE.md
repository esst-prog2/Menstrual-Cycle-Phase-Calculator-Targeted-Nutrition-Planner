# Evidence for the phase-nutrient claims in nutrition_rules.json

**Spike question** (PLANNING_LOG.md, 2026-09-30): for how many of the twelve
phase-nutrient claims in `nutrition_rules.json` is there a traceable scientific
source (PubMed, Cochrane, ACOG, NHS, or EFSA) supporting that nutrient in that
specific menstrual cycle phase?

**Answer: 7 of 12** claims have a traceable supporting source. Only 2 reach
**Strong**; 5 have no supporting source and are **Speculative**.

Searched: 2026-09-30. Quotes are copied verbatim from the PubMed abstract, the
PMC full text, or the official web page as served on that date.

## Summary

| # | Phase | Nutrient | Tier | Key source |
|---|---|---|---|---|
| 1 | Menstrual | Iron | **Strong** | Cochrane CD009747 (2016); NHS |
| 2 | Menstrual | Vitamin C | **Moderate** | EFSA 2014 opinion; Cook & Reddy 2001 |
| 3 | Menstrual | Magnesium | **Moderate** | Cochrane CD002124 (2001, 2016); Saei Ghare Naz 2020 |
| 4 | Follicular | Folate | **Speculative** | none found |
| 5 | Follicular | Protein | **Speculative** | none found |
| 6 | Follicular | Vitamin E | **Speculative** | none found |
| 7 | Ovulatory | Fiber | **Speculative** | none found (the evidence that exists points the other way) |
| 8 | Ovulatory | Zinc | **Speculative** | none found |
| 9 | Ovulatory | Omega-3 | **Weak** | Mumford 2016 (BioCycle) |
| 10 | Luteal | Magnesium | **Moderate** | ACOG; Moslehi 2019; Robinson 2025 |
| 11 | Luteal | Calcium | **Strong** | Thys-Jacobs 1998; Whelan 2009; Arab 2020; ACOG |
| 12 | Luteal | Vitamin B6 | **Moderate** | Wyatt 1999 (BMJ); Robinson 2025 |

### Final count by tier

| Tier | Count | Claims |
|---|---|---|
| Strong | 2 / 12 | Menstrual Iron, Luteal Calcium |
| Moderate | 4 / 12 | Menstrual Vitamin C, Menstrual Magnesium, Luteal Magnesium, Luteal Vitamin B6 |
| Weak | 1 / 12 | Ovulatory Omega-3 |
| Speculative | 5 / 12 | Follicular Folate, Follicular Protein, Follicular Vitamin E, Ovulatory Fiber, Ovulatory Zinc |
| **Supported (Strong + Moderate + Weak)** | **7 / 12** | |

The pattern is clear: the Menstrual and Luteal phases have real evidence,
mostly from studies of period pain and PMS. None of the three Follicular
claims and only one of the three Ovulatory claims has a source.

## How claims were graded

The tiers are the ones defined in README.md Section 4:

- **Strong**: a systematic review or meta-analysis with consistent findings,
  or a well-established physiological mechanism.
- **Moderate**: some supporting evidence, but reviews note inconsistency or a
  lack of consensus.
- **Weak**: a single small study, or only a narrative (non-systematic) review.
- **Speculative**: no traceable primary study supporting the claim.

Two interpretation rules were applied throughout:

1. **The source must support the nutrient in that phase.** A study showing a
   nutrient matters for reproduction in general, or in a *different* phase,
   does not count. These are listed under "Closest evidence checked" so the
   search is auditable, but the claim is still marked "none found".
2. **A source pointing the opposite way counts against the claim.** It is not
   neutral.

## Caveats that apply to every tier

- **Most supporting evidence is for supplements, not food.** The calcium,
  magnesium, B6 and omega-3 trials tested pills (e.g. 1,200 mg/day calcium
  carbonate), not the foods in `nutrition_rules.json`.
- **"In that phase" usually means the phase where symptoms occur, not the
  phase when the nutrient was taken.** Most PMS and dysmenorrhoea trials
  gave the supplement every day across the whole cycle. They show the
  nutrient helps symptoms that appear in the luteal or menstrual phase. They
  do not show that eating it *only during that phase* works.
- **Iron stores are rebuilt over weeks, not days.** Iron loss happens during
  menstruation, but nothing found shows that eating iron-rich food *during
  that week* matters more than eating it at any other time.
- Several trials come from small, single-country cohorts. Two of the reviews
  below say most included trials were low quality or at high risk of bias.

---

## Menstrual phase

### 1. Iron: Strong

The mechanism is well established: menstrual blood loss depletes iron, and
iron supplementation in menstruating women is backed by a Cochrane review.
README.md Section 4 uses this exact case as its example of Strong evidence.

- **Low MS et al. (2016).** *Daily iron supplementation for improving anaemia,
  iron status and health in menstruating women.* Cochrane Database Syst Rev.
  DOI: [10.1002/14651858.CD009747.pub2](https://doi.org/10.1002/14651858.CD009747.pub2)
  > "Daily iron supplementation effectively reduces the prevalence of anaemia
  > and iron deficiency, raises haemoglobin and iron stores, improves exercise
  > performance and reduces symptomatic fatigue."
- **NHS, Iron deficiency anaemia.**
  <https://www.nhs.uk/conditions/iron-deficiency-anaemia/>
  > "Heavy periods and pregnancy are very common causes of iron deficiency
  > anaemia."

### 2. Vitamin C: Moderate

This claim rests on vitamin C helping the body absorb iron, not on anything
specific to the menstrual phase. EFSA confirms that vitamin C increases non-haem
(plant) iron absorption. However, the effect across a whole diet is much smaller
than in single-meal tests, and long-term supplementation has not reliably
improved iron status. That mixed picture is why it is Moderate rather than
Strong.

- **EFSA NDA Panel (2014).** *Scientific Opinion on the substantiation of a
  health claim related to vitamin C and increasing non haem iron absorption
  pursuant to Article 14 of Regulation (EC) No 1924/2006.* EFSA Journal.
  DOI: [10.2903/j.efsa.2014.3514](https://doi.org/10.2903/j.efsa.2014.3514)
  > "The Panel concludes that a cause and effect relationship has been
  > established between the dietary intake of vitamin C and increasing non haem
  > iron absorption."
- **Cook JD, Reddy MB (2001).** *Effect of ascorbic acid intake on
  nonheme-iron absorption from a complete diet.* Am J Clin Nutr.
  DOI: [10.1093/ajcn/73.1.93](https://doi.org/10.1093/ajcn/73.1.93)
  > "The facilitating effect of vitamin C on iron absorption from a complete
  > diet is far less pronounced than that from single meals."

### 3. Magnesium: Moderate

The link here is magnesium for period pain (dysmenorrhoea). The 2001 Cochrane
review called magnesium "promising" based on three small trials. Its 2016
update found no high-quality evidence for *any* supplement, and magnesium is
not among the supplements it names. A 2020 meta-analysis is supportive but
notes how little research exists. The reviews do not agree, so this is Moderate.

- **Proctor ML, Murphy PA (2001).** *Herbal and dietary therapies for primary
  and secondary dysmenorrhoea.* Cochrane Database Syst Rev.
  DOI: [10.1002/14651858.CD002124](https://doi.org/10.1002/14651858.CD002124)
  (superseded by the 2016 update below)
  > "Results suggest that magnesium is a promising treatment for
  > dysmenorrhoea."
- **Pattanittum P et al. (2016).** *Dietary supplements for dysmenorrhoea.*
  Cochrane Database Syst Rev.
  DOI: [10.1002/14651858.CD002124.pub2](https://doi.org/10.1002/14651858.CD002124.pub2)
  > "There is no high quality evidence to support the effectiveness of any
  > dietary supplement for dysmenorrhoea, and evidence of safety is lacking."
- **Saei Ghare Naz M et al. (2020).** *The Effect of Micronutrients on Pain
  Management of Primary Dysmenorrhea: a Systematic Review and Meta-Analysis.*
  J Caring Sci.
  DOI: [10.34172/jcs.2020.008](https://doi.org/10.34172/jcs.2020.008)
  > "Vitamins (K, D, B1, and E) and calcium, magnesium, zinc sulfate and boron
  > contributed effectively to dysmenorrhea pain management."

---

## Follicular phase

### 4. Folate: Speculative (supporting source: none found)

No source links folate to the follicular phase specifically. The closest study
ties higher folate to a *luteal*-phase hormone, which is a different phase.
General advice to take folic acid before pregnancy applies all month, not to
one phase.

- **Closest evidence checked:** Michels KA et al. (2017). *Folate,
  homocysteine and the ovarian cycle among healthy regularly menstruating
  women.* Hum Reprod.
  DOI: [10.1093/humrep/dex233](https://doi.org/10.1093/humrep/dex233)
  > "Higher homocysteine was associated with sporadic anovulation and hormonal
  > changes that may be indicative of impaired ovulatory function, but higher
  > serum folate was associated only with higher luteal phase progesterone."

### 5. Protein: Speculative (supporting source: none found)

No source supports a higher protein need in the follicular phase. The closest
study found people naturally eat *more* protein in the luteal phase. That
describes eating behaviour. It is not evidence of what the body needs.

- **Closest evidence checked:** Gorczyca AM et al. (2016). *Changes in
  macronutrient, micronutrient, and food group intakes throughout the
  menstrual cycle in healthy, premenopausal women.* Eur J Nutr.
  DOI: [10.1007/s00394-015-0931-0](https://doi.org/10.1007/s00394-015-0931-0)
  > "Our findings suggest an increased intake of protein, and specifically
  > animal protein, as well as an increase in reported food cravings, during
  > the luteal phase of the menstrual cycle independent of ovulatory status."

### 6. Vitamin E: Speculative (supporting source: none found)

No source supports vitamin E in the follicular phase. One observational study
found blood vitamin E levels move with estradiol, but it says nothing about
eating vitamin E in a particular phase. ACOG mentions vitamin E only for PMS,
which falls in the luteal phase. **The only trial found on vitamin E and the
uterine lining (PMID 28847198, J Matern Fetal Neonatal Med 2019) has been
retracted** (retraction notice DOI
[10.1080/14767058.2024.2364981](https://doi.org/10.1080/14767058.2024.2364981))
and must not be used.

- **Closest evidence checked:** Mumford SL et al. (2016). *Serum Antioxidants
  Are Associated with Serum Reproductive Hormones and Ovulation among Healthy
  Women.* J Nutr.
  DOI: [10.3945/jn.115.217620](https://doi.org/10.3945/jn.115.217620)
  > "Retinol and α-tocopherol were associated with higher estradiol"

---

## Ovulatory phase

### 7. Fiber: Speculative (supporting source: none found; the evidence found points the other way)

The only direct study found that **higher** fiber intake went with **lower**
reproductive hormones and **more** cycles without ovulation. That is the
opposite of what this rule implies. The rule should be reconsidered, not just
labelled.

- **Evidence against:** Gaskins AJ et al. (2009). *Effect of daily fiber
  intake on reproductive function: the BioCycle Study.* Am J Clin Nutr.
  DOI: [10.3945/ajcn.2009.27990](https://doi.org/10.3945/ajcn.2009.27990)
  > "These findings suggest that a diet high in fiber is significantly
  > associated with decreased hormone concentrations and a higher probability
  > of anovulation."

### 8. Zinc: Speculative (supporting source: none found)

No source supports extra zinc around ovulation. Zinc was one of the ten
minerals checked in the BioCycle minerals analysis, and none except sodium
and manganese was associated with ovulation (confirmed in the PMC full text,
PMC6019139). A 14-woman study shows blood zinc rises and falls with estradiol
across the cycle. That describes a natural pattern and does not show that
eating more zinc helps.

- **Closest evidence checked:** Kim K et al. (2018). *Dietary minerals,
  reproductive hormone levels and sporadic anovulation: associations in
  healthy women with regular menstrual cycles.* Br J Nutr.
  DOI: [10.1017/S0007114518000818](https://doi.org/10.1017/S0007114518000818)
  > "Other measured dietary minerals were not associated with ovulatory
  > function."
- **Also checked:** Michos C et al. (2010). *Changes in copper and zinc plasma
  concentrations during the normal menstrual cycle in women.* Gynecol
  Endocrinol. DOI: [10.3109/09513590903247857](https://doi.org/10.3109/09513590903247857)
  > "This study indicates that there is a cyclic fluctuation of Cu and Zn
  > concentrations in plasma during the menstrual cycle, in healthy
  > eumenorrhoic women."

### 9. Omega-3: Weak

One observational study, which its own authors call exploratory, found that
one specific omega-3 fatty acid (DPA) was linked to a lower risk of cycles
without ovulation. There is no trial and no review.

- **Mumford SL et al. (2016).** *Dietary fat intake and reproductive hormone
  concentrations and ovulation in regularly menstruating women.* Am J Clin
  Nutr. DOI: [10.3945/ajcn.115.119321](https://doi.org/10.3945/ajcn.115.119321)
  > "These results indicate that total fat intake, and PUFA intake in
  > particular, is associated with very small increases in testosterone
  > concentrations in healthy women and that increased docosapentaenoic acid
  > was associated with a lower risk of anovulation."

---

## Luteal phase

### 10. Magnesium: Moderate

The link here is magnesium for PMS. ACOG lists it as something that *may*
help. However, a 2019 meta-analysis found no overall link between blood
magnesium and PMS, a 2025 review found too little evidence, and a 2009 review
found only "preliminary" benefit for one form of magnesium and none for
another. The sources do not agree, so this is Moderate.

- **ACOG, Premenstrual Syndrome (PMS) FAQ.**
  <https://www.acog.org/womens-health/faqs/premenstrual-syndrome>
  > "Taking magnesium supplements may help reduce water retention
  > ("bloating"), breast tenderness, and mood symptoms."
- **Moslehi M et al. (2019).** *The Association Between Serum Magnesium and
  Premenstrual Syndrome: a Systematic Review and Meta-Analysis of
  Observational Studies.* Biol Trace Elem Res.
  DOI: [10.1007/s12011-019-01672-z](https://doi.org/10.1007/s12011-019-01672-z)
  > "Additional well-designed clinical trials should be considered in future
  > research to develop firm conclusions on the efficacy of magnesium on PMS."
- **Robinson J et al. (2025).** *Effect of nutritional interventions on the
  psychological symptoms of premenstrual syndrome in women of reproductive
  age: a systematic review of randomized controlled trials.* Nutr Rev.
  DOI: [10.1093/nutrit/nuae043](https://doi.org/10.1093/nutrit/nuae043)
  > "There was insufficient evidence to support the effects of vitamin B1,
  > vitamin D, whole-grain carbohydrates, soy isoflavones, dietary fatty acids,
  > magnesium, multivitamin supplementation, or PMS-specific diets."

### 11. Calcium: Strong

This is the best-supported claim in the file. A large randomised controlled
trial (466 women analysed) found a luteal-phase benefit, three systematic
reviews agree, and ACOG names a dose. The one limit is the dose: the evidence
is for 1,200 mg/day of supplemental calcium, which is more than a single food
suggestion provides.

- **Thys-Jacobs S et al. (1998).** *Calcium carbonate and the premenstrual
  syndrome: effects on premenstrual and menstrual symptoms.* Am J Obstet
  Gynecol. DOI: [10.1016/s0002-9378(98)70377-1](https://doi.org/10.1016/s0002-9378(98)70377-1)
  > "Calcium supplementation is a simple and effective treatment in
  > premenstrual syndrome, resulting in a major reduction in overall luteal
  > phase symptoms."
- **Whelan AM et al. (2009).** *Herbs, vitamins and minerals in the treatment
  of premenstrual syndrome: a systematic review.* Can J Clin Pharmacol.
  PMID: [19923637](https://pubmed.ncbi.nlm.nih.gov/19923637/) (no DOI assigned)
  > "Only calcium had good quality evidence to support its use in PMS."
- **Arab A et al. (2020).** *Beneficial Role of Calcium in Premenstrual
  Syndrome: A Systematic Review of Current Literature.* Int J Prev Med.
  DOI: [10.4103/ijpvm.IJPVM_243_19](https://doi.org/10.4103/ijpvm.IJPVM_243_19)
  > "This systematic review suggests a beneficial role for calcium in PMS
  > subjects."
- **ACOG, Premenstrual Syndrome (PMS) FAQ.**
  <https://www.acog.org/womens-health/faqs/premenstrual-syndrome>
  > "Taking 1,200 milligrams (mg) of calcium a day can help reduce the
  > physical and mood symptoms that are part of PMS."

### 12. Vitamin B6: Moderate

A BMJ systematic review found a benefit for PMS but warns that most of the
trials it included were low quality. A 2025 review found consistent positive
effects on mood symptoms. The NHS lists B6 among supplements that may help
but notes there is "not much evidence" for any of them.

- **Wyatt KM et al. (1999).** *Efficacy of vitamin B-6 in the treatment of
  premenstrual syndrome: systematic review.* BMJ.
  DOI: [10.1136/bmj.318.7195.1375](https://doi.org/10.1136/bmj.318.7195.1375)
  > "Conclusions are limited by the low quality of most of the trials
  > included. Results suggest that doses of vitamin B-6 up to 100 mg/day are
  > likely to be of benefit in treating premenstrual symptoms and premenstrual
  > depression."
- **Robinson J et al. (2025).** Nutr Rev.
  DOI: [10.1093/nutrit/nuae043](https://doi.org/10.1093/nutrit/nuae043)
  > "Treatment with vitamin B6, calcium, and zinc consistently had significant
  > positive effects on the psychological symptoms of PMS."
- **NHS, PMS (premenstrual syndrome).**
  <https://www.nhs.uk/conditions/pre-menstrual-syndrome/>
  > "Complementary therapies and dietary supplements may help with PMS, but
  > there's not much evidence that they work."

---

## What this means for nutrition_rules.json

- **Fiber (Ovulatory)** is the only claim where the evidence found points
  against the rule. It should be removed or replaced, not just labelled
  Speculative.
- The **Follicular phase has no supported nutrient**. Under README.md
  Section 4.4, Speculative rules may stay but must be labelled as such in the
  terminal output and nutrients.md.
- Two findings suggest better candidates, though neither was part of this
  spike and neither was graded: zinc for PMS (Robinson 2025) belongs in the
  *luteal* phase rather than the ovulatory one, and folate's only phase link
  is also luteal (Michels 2017).
