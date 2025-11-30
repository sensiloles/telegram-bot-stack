# Licensing Research for telegram-bot-stack v2.0.0

**Date:** 2025-11-30  
**Issue:** [#122](https://github.com/sensiloles/telegram-bot-stack/issues/122)  
**Author:** @sensiloles  
**Status:** Research complete, decision pending

---

## Executive Summary

This document presents comprehensive research on licensing options for telegram-bot-stack version 2.0.0. The project needs a license that:

- ✅ Allows external contributors to participate
- ✅ Keeps repository public and transparent
- ✅ Protects against free commercial exploitation
- ✅ Enables future monetization strategies

**Current State:** MIT License (fully permissive, no commercial protection)

**Recommendation:** See [Final Recommendation](#final-recommendation) section

---

## Table of Contents

1. [Current Situation Analysis](#current-situation-analysis)
2. [Requirements](#requirements)
3. [License Options Research](#license-options-research)
4. [Telegram Bot Frameworks Comparison](#telegram-bot-frameworks-comparison)
5. [Legal & Business Considerations](#legal--business-considerations)
6. [Final Recommendation](#final-recommendation)
7. [Implementation Plan](#implementation-plan)

---

## Current Situation Analysis

### Current License: MIT (Since 2024)

**Text:**

```
MIT License

Copyright (c) 2024 telegram-bot-stack contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software...
```

**Implications:**

✅ **Advantages:**

- Maximum community adoption (most popular open-source license)
- Simple, well-understood terms
- Compatible with all dependencies
- No contributor friction
- Great for building ecosystem

❌ **Disadvantages:**

- **Zero commercial protection** - anyone can fork and sell
- Cannot prevent competitors from using our code
- No leverage for monetization
- Cannot require attribution in commercial products
- Lost control over commercial derivatives

### Repository Status

- **Visibility:** Public on GitHub
- **Contributors:** Currently private, planned to open for external contributions
- **Dependencies:** Python packages (most under permissive licenses)
- **Target Audience:** Developers building Telegram bots
- **Competition:** python-telegram-bot, aiogram, pyTelegramBotAPI

### Business Goals

1. **Short-term (v2.0.0):**

   - Build community and adoption
   - Attract external contributors
   - Establish reputation as best-in-class framework

2. **Long-term (post v2.0.0):**
   - Potential monetization through:
     - Premium features (e.g., advanced deployment, monitoring)
     - Enterprise support/SLA
     - Hosted services (bot-as-a-service)
     - Training/consulting
   - Prevent competitors from simply copying framework and selling

---

## Requirements

### Must Allow ✅

| Requirement                  | Priority | Rationale                                         |
| ---------------------------- | -------- | ------------------------------------------------- |
| **Public repository**        | CRITICAL | Transparency builds trust, essential for security |
| **External contributions**   | CRITICAL | Community growth requires open participation      |
| **Code inspection**          | CRITICAL | Developers need to verify security/quality        |
| **Personal/educational use** | HIGH     | Community building, learning, adoption            |
| **Small business use**       | MEDIUM   | Practical use cases, potential customers          |
| **Forking for improvements** | MEDIUM   | Healthy ecosystem development                     |

### Must Restrict ❌

| Restriction                      | Priority | Rationale                                    |
| -------------------------------- | -------- | -------------------------------------------- |
| **Free commercial use**          | CRITICAL | Prevent competitors from exploiting our work |
| **Forking for profit**           | CRITICAL | Protect against commercial derivatives       |
| **Providing as managed service** | HIGH     | Reserve SaaS/hosting monetization            |
| **Rebranding and reselling**     | HIGH     | Protect brand and market position            |
| **Removing attribution**         | MEDIUM   | Maintain visibility and reputation           |

---

## License Options Research

### 1. Business Source License (BSL 1.1)

**Official Site:** https://mariadb.com/bsl11/

#### Overview

Source-available license that converts to open-source after a specified time period.

#### How It Works

```
BSL Parameters:
├── License Text: MariaDB BSL 1.1
├── Change Date: e.g., 4 years from release
├── Change License: e.g., Apache 2.0 or MIT
└── Additional Use Grant: Optional exceptions
```

**Example:**

```
Change Date: 2029-01-01
Change License: Apache License 2.0
Additional Use Grant: Personal use, educational use, development/testing
```

#### Real-World Usage

| Company         | Product          | Change Period | Change License |
| --------------- | ---------------- | ------------- | -------------- |
| **MariaDB**     | MaxScale         | 4 years       | GPL 2.0        |
| **CockroachDB** | CockroachDB      | 3 years       | Apache 2.0     |
| **Sentry**      | Sentry           | 3 years       | Apache 2.0     |
| **Couchbase**   | Couchbase Server | 4 years       | Apache 2.0     |

#### Pros ✅

- **Battle-tested:** Used by major companies (MariaDB, CockroachDB, Sentry)
- **Clear conversion timeline:** Code eventually becomes open-source
- **Flexible restrictions:** "Additional Use Grant" allows exceptions
- **Contributor-friendly:** Encourages contributions (code becomes OSS)
- **Business protection:** Blocks competitors during critical growth period
- **Community acceptance:** Better than SSPL, more transparent than proprietary

#### Cons ❌

- **Complex parameters:** Must carefully define:
  - Change Date (how long until OSS?)
  - Change License (which OSS license after conversion?)
  - Additional Use Grant (what's allowed before conversion?)
- **Not OSI-approved:** Some companies avoid non-OSI licenses
- **Marketing challenge:** "Source-available" vs "Open-source" confusion
- **Legal overhead:** Requires careful drafting of parameters
- **Contributor friction:** Some developers prefer pure OSS

#### Suitability for telegram-bot-stack

**Score: 9/10 - EXCELLENT FIT**

**Why it works:**

- Perfect for "grow now, monetize later" strategy
- Allows personal/educational use (community building)
- Protects against commercial exploitation during critical 3-4 years
- Eventually becomes Apache 2.0 (maximum adoption after maturity)
- Clear path: restrictive → permissive

**Example parameters:**

```
License: Business Source License 1.1
Change Date: January 1, 2029 (4 years from v2.0.0 release)
Change License: Apache License 2.0
Additional Use Grant: You may use this software for personal,
educational, or non-commercial purposes without restriction.
```

---

### 2. Elastic License 2.0 (ELv2)

**Official Site:** https://www.elastic.co/licensing/elastic-license

#### Overview

Simple source-available license prohibiting SaaS offerings. Created by Elastic (Elasticsearch, Kibana) in response to AWS offering Elasticsearch-as-a-service.

#### How It Works

Three main restrictions:

1. **Cannot provide as hosted/managed service** to third parties
2. **Cannot circumvent license key/protection mechanisms**
3. **Cannot remove/obscure licensing/copyright notices**

Everything else is allowed: use, modify, distribute, fork, commercial use on-premise.

#### Real-World Usage

| Company     | Product               | Reason                                           |
| ----------- | --------------------- | ------------------------------------------------ |
| **Elastic** | Elasticsearch, Kibana | Prevent cloud providers from offering as service |
| **Elastic** | Logstash              | Consistency across Elastic Stack                 |

#### Pros ✅

- **Simple and clear:** Only 3 restrictions, easy to understand
- **Allows commercial use:** Businesses can use internally without paying
- **Contributor-friendly:** Low barrier for external contributions
- **Allows distribution:** Can be packaged, bundled, resold (not as service)
- **Strong SaaS protection:** Perfect for preventing "X-as-a-service" competitors
- **Brand protection:** Built-in trademark protection

#### Cons ❌

- **Too permissive for some goals:** Allows free commercial use on-premise
- **SaaS-specific:** Only protects against hosting, not other commercial use
- **Not OSI-approved:** Some companies have "OSS-only" policies
- **Controversial history:** Bad PR from Elastic vs AWS battle
- **Limited monetization leverage:** Can't charge for on-premise use

#### Suitability for telegram-bot-stack

**Score: 6/10 - MODERATE FIT**

**Why it might work:**

- Simple, easy to communicate
- Good if main monetization is hosting/SaaS
- Low contributor friction

**Why it might not work:**

- Doesn't prevent commercial use on-premise
- Companies can build products using framework without paying
- Only protects ONE monetization path (hosting)
- Our main threat isn't cloud providers, it's competing frameworks

**Example use case:**

> "If you plan to offer telegram-bot-stack as a hosted service (customers deploy bots through your platform), you need a commercial license. Otherwise, use freely."

**Risk:** Doesn't prevent competitor from creating "XYZ Bot Framework Pro" using our code, selling licenses.

---

### 3. Server Side Public License (SSPL)

**Official Site:** https://www.mongodb.com/licensing/server-side-public-license

#### Overview

AGPL-like license requiring service providers to open-source their entire infrastructure. Created by MongoDB to prevent AWS from offering MongoDB-as-a-service.

#### How It Works

Similar to AGPL v3, but with extreme requirement:

> If you offer the software as a service, you must open-source **all software** used to provide that service (including infrastructure, deployment tools, monitoring, etc.).

#### Real-World Usage

| Company     | Product | Status                           |
| ----------- | ------- | -------------------------------- |
| **MongoDB** | MongoDB | Active (since 2018)              |
| **Graylog** | Graylog | Switched from GPL to SSPL (2021) |

#### Pros ✅

- **Strongest protection:** Essentially blocks all SaaS use
- **Simple concept:** "Use freely or open-source everything"
- **Allows contributions:** Copyleft encourages contribution over forking
- **Works for MongoDB:** Successfully prevented AWS MongoDB service

#### Cons ❌

- **Extremely controversial:** Rejected by OSI, labeled "not open source"
- **Huge community backlash:** Seen as hostile to cloud providers
- **Unclear legal status:** Untested in court
- **Vague requirements:** "All software" is poorly defined
- **Contributor deterrent:** Many developers refuse to contribute to SSPL projects
- **Enterprise blocker:** Most enterprises avoid SSPL (legal uncertainty)
- **Ecosystem damage:** Fedora, Debian, Red Hat refuse to package SSPL software

#### Suitability for telegram-bot-stack

**Score: 2/10 - POOR FIT**

**Why it doesn't work:**

- Too aggressive for a framework (MongoDB is a database, different use case)
- Would kill community growth (negative perception)
- Would prevent legitimate use cases (bot hosting platforms)
- Legal uncertainty would scare enterprise users
- Not suitable for ecosystem/library projects

**MongoDB lesson:**

- Works for critical infrastructure (databases) where users have no choice
- Doesn't work for frameworks/libraries where alternatives exist
- Created bad PR and community division

**Recommendation:** ❌ Avoid SSPL

---

### 4. Dual Licensing (AGPL + Commercial)

#### Overview

Offer software under two licenses:

1. **Free tier:** AGPL v3 (strong copyleft - modifications must be open-sourced)
2. **Paid tier:** Commercial license (proprietary use allowed)

#### How It Works

```
┌─────────────────────────────────────┐
│ telegram-bot-stack                  │
├─────────────────────────────────────┤
│                                     │
│  Choose your license:               │
│                                     │
│  1. AGPL v3 (Free)                  │
│     - Open-source your bot          │
│     - Share modifications           │
│     - Non-commercial use            │
│                                     │
│  2. Commercial ($$$)                │
│     - Proprietary bots allowed      │
│     - No source-code sharing        │
│     - Priority support              │
│                                     │
└─────────────────────────────────────┘
```

#### Real-World Usage

| Company    | Product            | Free License | Paid License     |
| ---------- | ------------------ | ------------ | ---------------- |
| **GitLab** | GitLab CE/EE       | MIT (CE)     | Proprietary (EE) |
| **Qt**     | Qt Framework       | LGPL v3      | Commercial       |
| **MySQL**  | MySQL Database     | GPL v2       | Commercial       |
| **Sentry** | Sentry (old model) | BSD          | Commercial       |

#### Pros ✅

- **Proven model:** Used successfully by GitLab, Qt, MySQL
- **Clear separation:** Free for open-source, paid for commercial
- **Revenue from day one:** Can charge immediately
- **Flexibility:** Can adjust commercial pricing/terms
- **Strong copyleft:** AGPL forces competitors to open-source or pay

#### Cons ❌

- **Complex management:** Requires:
  - Contributor License Agreement (CLA)
  - Copyright assignment or exclusive license
  - Legal entity to hold copyright
  - Commercial licensing infrastructure
- **Contributor friction:** CLA requirement reduces contributions
- **License ambiguity:** Users confused about which license applies
- **AGPL concerns:** Many companies fear AGPL (contagious licensing)
- **Enforcement challenge:** Hard to detect AGPL violations
- **Support burden:** Commercial customers expect professional support

#### AGPL Explanation

**AGPL v3 (Affero GPL):** Like GPL, but covers network use.

- **GPL:** Must share source if you distribute software
- **AGPL:** Must share source if you provide software as a service

Example:

> If you modify telegram-bot-stack and run bots for your customers (even without distributing code), you must open-source your modifications.

**Impact:** Forces commercial users to either:

1. Open-source their entire bot (most won't)
2. Buy commercial license (revenue!)

#### Suitability for telegram-bot-stack

**Score: 7/10 - GOOD FIT (but complex)**

**Why it works:**

- Clear monetization path from day one
- AGPL forces commercial users to pay
- Matches our goal: free for hobbyists, paid for businesses

**Why it's complex:**

- Requires CLA (legal friction)
- Need commercial licensing infrastructure
- Ongoing support burden for paid customers
- Copyright management complexity

**Implementation Requirements:**

1. **Legal entity:** LLC or corporation to sell licenses
2. **CLA:** Contributor License Agreement (e.g., via CLA Assistant)
3. **Commercial terms:** Pricing, license text, purchase flow
4. **Support system:** Commercial customers expect support
5. **Copyright tracking:** Track who contributed what

**Example pricing:**

- Personal/Open-Source: Free (AGPL v3)
- Startup (<$1M revenue): $99/month
- Business: $499/month
- Enterprise: Custom pricing + SLA

---

### 5. Commons Clause (on top of Apache/MIT)

**Official Site:** https://commonsclause.com/

#### Overview

An _addition_ (not a standalone license) that adds a single restriction to an existing open-source license:

> "You can't sell this software."

Example: **Apache 2.0 + Commons Clause**

#### How It Works

```
License: Apache License 2.0 with Commons Clause

Commons Clause Restriction:

"The Software is provided to you by the Licensor under the
License, as defined below, subject to the following condition:

Without limiting other conditions in the License, the grant
of rights under the License will not include, and the License
does not grant to you, the right to Sell the Software."
```

#### Real-World Usage

| Company            | Product               | Year | Outcome                              |
| ------------------ | --------------------- | ---- | ------------------------------------ |
| **Redis Labs**     | Redis Modules         | 2018 | Switched to SSPL (2019)              |
| **Confluent**      | Confluent Platform    | 2018 | Switched to Confluent License (2019) |
| **Cockroach Labs** | CockroachDB (briefly) | 2017 | Switched to BSL (2019)               |

**Pattern:** Most companies _abandoned_ Commons Clause within 1-2 years.

#### Pros ✅

- **Simple addition:** Just add clause to existing license
- **Easy to understand:** "You can't sell this"
- **Preserves OSS feel:** Still based on MIT/Apache
- **Low implementation cost:** No complex parameters to set

#### Cons ❌

- **Legal uncertainty:** "Sell" is poorly defined
  - Does "Sell the Software" include SaaS?
  - Does bundling count as selling?
  - What about consulting fees?
- **Not OSI-approved:** Violates Open Source Definition
- **Terrible community reception:** Seen as "fake open source"
- **Enforcement issues:** Vague language makes enforcement difficult
- **Companies abandoned it:** Redis, Confluent, CockroachDB all switched away
- **No legal precedent:** Never tested in court
- **Unclear scope:** Does it prevent commercial _use_ or just _sale_?

#### Why Companies Abandoned Commons Clause

1. **Legal ambiguity:** Customers kept asking "can we use this commercially?"
2. **Bad PR:** Community backlash for "bait and switch"
3. **Didn't solve problem:** Still allowed commercial use, just not resale
4. **Better alternatives emerged:** BSL, ELv2 provided clearer terms

#### Suitability for telegram-bot-stack

**Score: 3/10 - POOR FIT**

**Why it doesn't work:**

- Legal uncertainty scares users
- Vague "selling" restriction doesn't prevent our main concerns
- Historical evidence: failed for similar projects
- Community would see it as "trying to be open-source but not really"

**What it prevents:**

- ✅ Reselling framework directly
- ❌ Building commercial products on top
- ❌ Offering as a service
- ❌ Enterprise internal use

**Recommendation:** ❌ Avoid Commons Clause - proven to be ineffective

---

### 6. Fair Source License

**Official Site:** https://fair.io/

#### Overview

Limits number of users who can use the software, then converts to Apache 2.0 after a specified time.

#### How It Works

```
Fair Source License, version 0.9

Parameters:
- User Limit: e.g., 25 users
- License Grant: After [date], becomes Apache 2.0
```

**Example:**

```
Fair Source 25 (v0.9)

You can use this software for free if your organization has
fewer than 25 users. For more than 25 users, you need a
commercial license.

On [Change Date], this becomes Apache 2.0 for everyone.
```

#### Real-World Usage

**Very limited adoption.** No major companies using Fair Source.

| Company      | Product | Status                    |
| ------------ | ------- | ------------------------- |
| Few examples | Various | Rare, mostly experimental |

#### Pros ✅

- **Simple concept:** "Free for small teams, paid for large"
- **User-based pricing:** Natural pricing model
- **Conversion to OSS:** Eventually becomes Apache 2.0
- **Small business friendly:** Allows use below threshold

#### Cons ❌

- **User tracking complexity:** How to count "users"?
  - Bot users? (could be millions)
  - Developer users? (who counts?)
  - Organization size? (how to verify?)
- **Unproven:** Essentially no adoption in real projects
- **Enforcement nightmare:** Cannot verify user counts
- **Unclear definition:** "User" is ambiguous for frameworks
- **Self-reporting:** Relies on honesty (easy to cheat)
- **Not suitable for libraries:** Makes sense for apps, not frameworks

#### Suitability for telegram-bot-stack

**Score: 2/10 - VERY POOR FIT**

**Why it doesn't work:**

- **User counting is meaningless for bot framework:**
  - Count bot end-users? (Could be millions, irrelevant to our value)
  - Count developers? (Hard to track)
  - Count bots built? (Easy to circumvent)
- **Unenforceable:** No way to verify compliance
- **No industry adoption:** Lack of precedent

**Example problem:**

> "Your organization can have 25 users" - what does this mean?
>
> - 25 people building bots with our framework? ✅ Makes sense
> - 25 people using bots built with framework? ❌ Ridiculous (could be millions)

**Recommendation:** ❌ Avoid Fair Source - not applicable to frameworks

---

## Telegram Bot Frameworks Comparison

### Analysis of Competing Frameworks

| Framework               | License | Strategy         | Monetization          |
| ----------------------- | ------- | ---------------- | --------------------- |
| **python-telegram-bot** | LGPL v3 | Pure open-source | Donations only        |
| **aiogram**             | MIT     | Pure open-source | Donations, consulting |
| **pyTelegramBotAPI**    | GPL v2  | Pure open-source | None                  |
| **grammy** (JS)         | MIT     | Pure open-source | Donations             |
| **Telethon**            | MIT     | Pure open-source | None                  |
| **Pyrogram**            | LGPL v3 | Pure open-source | None                  |

### Key Findings

1. **All major frameworks use permissive/copyleft OSS licenses**

   - No commercial licensing in this space
   - No source-available licenses
   - Community-driven, donation-based

2. **No successful commercial Telegram bot frameworks**

   - Market is dominated by free/open-source
   - Commercial offerings exist (e.g., Chatfuel) but are hosted platforms, not frameworks

3. **Monetization is challenging**
   - Most rely on donations (GitHub Sponsors, Patreon)
   - Some authors offer consulting
   - No examples of dual-licensing or paid tiers

### Implications for telegram-bot-stack

**Opportunity:** We could be **first commercial-friendly framework** in this space.

**Risk:** Market expects free frameworks - commercial restrictions could hurt adoption.

**Strategy considerations:**

| Approach                           | Outcome                                                 |
| ---------------------------------- | ------------------------------------------------------- |
| **Pure OSS (MIT/Apache)**          | Maximum adoption, zero monetization, compete on quality |
| **Source-available (BSL/ELv2)**    | Moderate adoption, future monetization, differentiation |
| **Dual-license (AGPL+Commercial)** | Lower adoption, immediate monetization, niche market    |

**Recommendation:**

Given the competitive landscape, we have two strategic options:

1. **Play the long game (BSL):**

   - Be open now (build community, adoption)
   - Protect commercial rights for 3-4 years
   - Convert to Apache 2.0 once established
   - Monetize through services/hosting, not licenses

2. **Compete on openness (Apache 2.0):**
   - Go full open-source immediately
   - Compete with existing frameworks on quality/features
   - Build reputation and trust
   - Monetize through:
     - Managed hosting (telegram-bot-stack Cloud)
     - Enterprise support/SLA
     - Training/consulting
     - Premium templates/plugins

---

## Legal & Business Considerations

### Contributor License Agreement (CLA)

**Required for:** Dual-licensing, future license changes

**What it does:**

- Contributors grant you rights to use their code commercially
- You (project owner) retain ability to change license or sell commercial licenses
- Contributors keep their rights (non-exclusive grant)

**Examples:**

- **Google CLA:** Used by Go, Android, etc.
- **Apache ICLA:** Individual Contributor License Agreement
- **CLA Assistant:** Automated GitHub integration

**Pros:**

- Legal clarity for commercial licensing
- Ability to change license in future
- Protection against contributor lawsuits

**Cons:**

- Reduces contributions (friction in process)
- Requires legal review by contributors
- Perceived as "corporate" (less community-friendly)

**Do we need it?**

| License Choice           | CLA Required?                         |
| ------------------------ | ------------------------------------- |
| MIT/Apache (pure OSS)    | ❌ No                                 |
| BSL 1.1                  | ❌ No (all contributors get same BSL) |
| Elastic License 2.0      | ❌ No                                 |
| SSPL                     | ❌ No                                 |
| Dual (AGPL + Commercial) | ✅ **YES** (essential)                |
| Commons Clause           | ⚠️ Recommended                        |
| Fair Source              | ⚠️ Recommended                        |

### Copyright Ownership

**Current status:**

```
Copyright (c) 2024 telegram-bot-stack contributors
```

This means:

- All contributors own copyright to their contributions
- Cannot change license without permission from all contributors
- Cannot do dual-licensing without CLA

**Options:**

1. **Keep distributed copyright** (current)

   - Pro: Community-friendly
   - Con: Cannot change license or dual-license later

2. **Require copyright assignment**

   - Pro: Full control over licensing
   - Con: Major contributor deterrent (e.g., FSF requires this, gets fewer contributions)

3. **Use CLA (license grant, not assignment)**
   - Pro: Balance between control and community
   - Con: Still adds friction

**Recommendation:**

- If choosing MIT/Apache/BSL/ELv2: **Keep distributed copyright** ✅
- If choosing Dual-licensing: **Require CLA** ✅

### Trademark Protection

**Regardless of code license, protect the name:**

1. **Register trademark:** "telegram-bot-stack" (if not already done)
2. **Trademark policy:** Similar to Mozilla, Linux Foundation
   - Can use code freely
   - Cannot use name without permission
   - Prevents "telegram-bot-stack Pro" competitors

**Example:**

> "You may use and modify telegram-bot-stack code under [LICENSE], but you may not use the telegram-bot-stack name or logo without written permission."

**Benefits:**

- Protects brand regardless of code license
- Prevents confusing forks/derivatives
- Maintains market position

### Legal Entity

**Do we need a company/LLC?**

| License Choice              | Legal Entity Needed?            |
| --------------------------- | ------------------------------- |
| MIT/Apache (pure OSS)       | ❌ No (can be individual)       |
| BSL/ELv2 (source-available) | ⚠️ Recommended (for clarity)    |
| Dual-license                | ✅ **YES** (must sell licenses) |

**If monetizing, eventually need:**

- LLC or Corporation (liability protection)
- Business bank account
- Accounting/tax setup
- Commercial licensing infrastructure

---

## Final Recommendation

### Recommended License: **Business Source License 1.1**

**Why BSL is the best fit:**

1. ✅ **Balances all requirements:**

   - Public repository ✅
   - External contributions ✅
   - Commercial protection ✅ (for 3-4 years)
   - Future monetization ✅
   - Eventually open-source ✅

2. ✅ **Proven track record:**

   - Used by respected companies (MariaDB, CockroachDB, Sentry)
   - Stable legal framework
   - Community acceptance (better than SSPL or Commons Clause)

3. ✅ **Practical for our stage:**

   - We're pre-revenue, so dual-licensing overhead not needed yet
   - Protects our competitive position during critical growth (3-4 years)
   - Allows free use for personal/educational (builds community)
   - Converts to Apache 2.0 eventually (removes barriers after maturity)

4. ✅ **Low friction:**

   - No CLA required (unlike dual-licensing)
   - Clear, simple terms (unlike SSPL or Commons Clause)
   - Contributor-friendly (code will be Apache 2.0 in future)

5. ✅ **Strategic flexibility:**
   - Can still monetize through hosting, support, enterprise features
   - Prevents competitors from freeloading during our growth phase
   - After 4 years, if we're established, Apache 2.0 helps ecosystem growth

### Proposed BSL Parameters

```markdown
License: Business Source License 1.1
Licensor: telegram-bot-stack contributors
Licensed Work: telegram-bot-stack v2.0.0 and later
Change Date: 2029-01-01 (4 years from v2.0.0 release)
Change License: Apache License 2.0

Additional Use Grant:

You may use the Licensed Work for:

1. Personal, non-commercial purposes
2. Educational purposes (teaching, learning, research)
3. Evaluation and testing
4. Internal business use (up to 10 deployed bots)
5. Open-source projects

You may NOT use the Licensed Work for:

1. Providing the Licensed Work, or derivatives, as a hosted or
   managed service to third parties
2. Competing directly with telegram-bot-stack or its commercial
   offerings
3. Removing or obscuring licensing or attribution notices
```

**Rationale:**

- **4-year period:** Long enough to establish position, not too long to alienate community
- **Apache 2.0 conversion:** Most permissive OSS license (maximum adoption after maturity)
- **"Up to 10 bots":** Allows small business use (good for adoption), requires license for scale
- **Competing directly:** Prevents "telegram-bot-stack Pro" clones

### Alternative: Apache 2.0 (Pure Open Source)

**If we prioritize community growth over monetization protection:**

**Pros:**

- Maximum adoption and trust
- No contributor friction
- Compete with existing frameworks on equal terms
- Simple, well-known license

**Cons:**

- Zero protection against commercial exploitation
- Competitors can freely use our work
- Monetization only through services (hosting, support)

**When to choose Apache 2.0:**

- If we're confident in monetizing through hosted services
- If we prioritize becoming the "standard" framework over short-term protection
- If we want to compete directly with python-telegram-bot, aiogram

**Strategic difference:**

| Metric                    | BSL 1.1                     | Apache 2.0            |
| ------------------------- | --------------------------- | --------------------- |
| **Adoption rate**         | Moderate (some hesitation)  | Maximum               |
| **Contributor growth**    | Good                        | Excellent             |
| **Commercial protection** | Strong (4 years)            | None                  |
| **Monetization**          | Services + future licensing | Services only         |
| **Competitive position**  | Protected niche             | Open competition      |
| **Long-term (4+ years)**  | Becomes Apache 2.0 anyway   | Apache 2.0 from start |

### Recommendation for v2.0.0

**Phase 1 (Now - v2.0.0 release):**

Choose **Business Source License 1.1** because:

- We're not yet established (need protection during growth)
- Competitive market (python-telegram-bot, aiogram are strong)
- Differentiation needed (killer features + business model)
- Can always relax later (can't tighten once released under permissive license)

**Phase 2 (After v2.0.0 success):**

Monitor and adapt:

- If BSL hurts adoption significantly → early conversion to Apache 2.0
- If BSL works well → maintain until 2029, then convert
- If demand for commercial licenses → consider dual-licensing in v2.1.0+

**Safety valve:** BSL allows us to convert early to Apache 2.0 if needed, but we can't go the other direction with Apache 2.0.

---

## Implementation Plan

### Phase 1: Legal Preparation (Week 1-2)

**Tasks:**

1. ✅ Research complete (this document)
2. ⏳ **Legal review (if budget allows):**

   - Consult with open-source attorney
   - Review BSL parameters
   - Confirm "Additional Use Grant" wording
   - Estimated cost: $500-1500 USD

3. ⏳ **Finalize license parameters:**

   - Change Date: January 1, 2029 (4 years)
   - Change License: Apache License 2.0
   - Additional Use Grant: (see above)

4. ⏳ **Trademark planning:**
   - Research trademark availability
   - Draft trademark policy
   - Consider registration (optional for v2.0.0)

### Phase 2: Documentation (Week 2)

**Tasks:**

1. ⏳ **Create LICENSE file:**

   ```
   /LICENSE
   ├── Business Source License 1.1
   ├── Parameters section
   └── Additional Use Grant
   ```

2. ⏳ **Update CONTRIBUTING.md:**

   - Explain licensing to contributors
   - Clarify that contributions will become Apache 2.0 in 2029
   - No CLA required
   - Copyright attribution

3. ⏳ **Add license headers to source files:**

   ```python
   # Copyright (c) 2024-present telegram-bot-stack contributors
   # Licensed under the Business Source License 1.1
   # See LICENSE file for details
   ```

4. ⏳ **Update README.md:**

   - Add license badge
   - Brief explanation of BSL
   - Link to LICENSE file
   - FAQ about licensing

5. ⏳ **Update pyproject.toml:**
   ```toml
   [project]
   license = {text = "Business Source License 1.1"}
   ```

### Phase 3: Communication (Week 3)

**Tasks:**

1. ⏳ **CHANGELOG.md entry:**

   ```markdown
   ## [2.0.0] - 2025-12-XX

   ### Changed

   - **BREAKING:** License changed from MIT to Business Source License 1.1
     - Effective date: December XX, 2025
     - Conversion to Apache 2.0: January 1, 2029
     - See LICENSE file for full details
     - Personal, educational, and small business use remain free
     - Commercial/enterprise use restrictions apply (see Additional Use Grant)
     - Rationale: Protect framework development during growth phase while
       ensuring eventual full open-source status
   ```

2. ⏳ **Create FAQ document:**

   - "Why did you change from MIT to BSL?"
   - "Can I still use telegram-bot-stack for free?"
   - "What happens in 2029?"
   - "Do I need a commercial license?"
   - "How does this affect contributors?"

3. ⏳ **Announcement (if public community exists):**
   - Blog post explaining decision
   - GitHub Discussions thread
   - Transparency about goals and reasoning

### Phase 4: Repository Updates (Week 3)

**Tasks:**

1. ⏳ **Update all docs:**

   - Installation guide
   - Deployment guide
   - Quickstart
   - Architecture docs
   - Anywhere LICENSE is mentioned

2. ⏳ **Add license to PyPI:**

   - Update package metadata
   - Include LICENSE in package distribution

3. ⏳ **Update GitHub repository settings:**

   - License dropdown (will show "Other")
   - Add license to repo description

4. ⏳ **Create license automation:**
   - Pre-commit hook to check license headers
   - CI check for license compliance

### Phase 5: Legal Infrastructure (Post-v2.0.0)

**Optional/future tasks:**

1. 💡 **Commercial licensing system:**

   - Create commercial license agreement
   - Set up pricing tiers
   - Build purchase/licensing portal
   - (Only if demand exists)

2. 💡 **Trademark registration:**

   - Register "telegram-bot-stack" trademark
   - Create trademark usage policy
   - (Recommended within 6-12 months)

3. 💡 **Legal entity:**
   - Form LLC or corporation
   - (Required before selling commercial licenses)

### Success Criteria

- ✅ LICENSE file created and committed
- ✅ All source files have license headers
- ✅ Documentation updated (README, CONTRIBUTING, etc.)
- ✅ CHANGELOG entry explains change
- ✅ PyPI package includes license
- ✅ No legal ambiguities or questions
- ✅ Contributors understand licensing terms
- ✅ Users understand what's allowed/not allowed

### Timeline

**Estimated total:** 2-3 weeks

- Week 1: Research (✅ DONE), legal review
- Week 2: Documentation, file updates
- Week 3: Communication, final review

**Target:** Complete before v2.0.0 release (December 20, 2025)

---

## Conclusion

After comprehensive research, **Business Source License 1.1** is recommended for telegram-bot-stack v2.0.0 because it:

1. ✅ Achieves all stated goals (public repo, contributions, protection, monetization)
2. ✅ Provides commercial protection during critical growth phase (4 years)
3. ✅ Maintains community-friendly approach (free for personal/educational use)
4. ✅ Has proven track record (MariaDB, CockroachDB, Sentry)
5. ✅ Converts to Apache 2.0 (removes all restrictions after maturity)
6. ✅ Low implementation complexity (no CLA, no legal entity required yet)
7. ✅ Strategic flexibility (can monetize through multiple paths)

**Alternative considered:** Apache 2.0 (pure open source) if we prioritize maximum adoption over commercial protection.

**Next steps:**

1. Review this research document
2. Make final decision: BSL 1.1 or Apache 2.0
3. Execute implementation plan
4. Update issue #122 with decision

---

## References

### License Texts

- [Business Source License 1.1](https://mariadb.com/bsl11/)
- [Elastic License 2.0](https://www.elastic.co/licensing/elastic-license)
- [Server Side Public License](https://www.mongodb.com/licensing/server-side-public-license)
- [AGPL v3](https://www.gnu.org/licenses/agpl-3.0.en.html)
- [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0)
- [MIT License](https://opensource.org/licenses/MIT)
- [Commons Clause](https://commonsclause.com/)
- [Fair Source License](https://fair.io/)

### Further Reading

- [Choose a License](https://choosealicense.com/)
- [OSI Approved Licenses](https://opensource.org/licenses/)
- [tldrlegal.com](https://tldrlegal.com/) - License summaries
- [GitHub Licensing Guide](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository)

### Case Studies

- [CockroachDB: Why We're Relicensing](https://www.cockroachlabs.com/blog/oss-relicensing-cockroachdb/)
- [Elastic: Doubling Down on Open](https://www.elastic.co/blog/licensing-change)
- [MongoDB: SSPL FAQ](https://www.mongodb.com/licensing/server-side-public-license/faq)
- [MariaDB: BSL Announcement](https://mariadb.com/bsl-faq-mariadb/)

---

**Document Version:** 1.0  
**Last Updated:** 2025-11-30  
**Status:** Research complete, pending decision
