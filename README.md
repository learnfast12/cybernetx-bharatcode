# CyberNetX: Detect. Trace. Neutralize.

One consent-first pipeline that blocks AI-written UPI scams on the phone, groups lures into campaigns, and traces the stolen money back to its collector, with human review before any hold or freeze.

**Powered by BharatCode (Qwen 3.8 27B):** every ShieldNetX verdict comes with a plain-language explanation, so users and analysts see *why* something was flagged.

![ShieldNetX app](assets/shieldnetx-app.png)

## The problem
Most UPI fraud in India starts with a link or APK on WhatsApp or SMS. The link opens a fresh clone of a bank page, and the money is gone in minutes. Link checkers need the user to copy and paste, and they mostly catch links already known to be bad. Bank tools freeze one mule account at a time and don't explain why.

## How it works
**ShieldNetX (Detect).** Automatic link interception through a Chrome extension and an Android Accessibility Service. Unknown links are opened in an isolated Ghost Sandbox and scored on behaviour, page forensics, visual brand match (CLIP), domain/TLS/kit fingerprints, and crowd signals. A link is blocked only when 2+ independent signal families agree.

**TraceNetX (Trace).** A Neo4j graph and ML ensemble (XGBoost, LightGBM, Random Forest, LSTM, SHAP) that traces money backwards to the dealer in about 3-4 hops, separates victims from willing participants, and produces an evidence package.

**Bridge.** Payee details (UPI ID, account, phone, domain, IP) extracted from blocked scam pages are sent to TraceNetX as seed nodes via `POST /api/investigate`.

## BharatCode integration
`shieldnetx/sentinel-backend/bharatcode_client.py` calls the BharatCode API (`qwen-3.8-27b`). `POST /scan` returns a `bharatcode_explanation` field with the reasons behind the verdict, built only from the signals that triggered. Without an API key, it falls back to template text.

```bash
cd shieldnetx/sentinel-backend
pip install -r requirements.txt
export BHARATCODE_API_KEY="your-key"   # see .env.example; never commit it
python3 main.py                         # http://localhost:8000
curl -s -X POST localhost:8000/scan -H "Content-Type: application/json" \
  -d '{"url":"http://sbi-kyc-verify.xyz/login"}'
```

## TraceNetX
```bash
docker start neo4j   # wait ~15 s
./tracenetx/start-tracenetx-v2.sh
```

| Spider Map | Dashboard |
|---|---|
| ![Spider map](assets/spider-map.png) | ![Dashboard](assets/dashboard.png) |
| **City Map** | **Evidence package** |
| ![City map](assets/city-map.png) | ![Evidence](assets/evidence-package.png) |

## Safety and responsible AI
- Never collects message bodies, contacts, keystrokes, PINs, OTPs, or precise location.
- No block on a single weak signal; a "Not a scam" button triggers a re-scan.
- Humans approve every hold or freeze, with an appeal path.
- The demo uses synthetic data only.

## Limitations
The demo network is small (21 accounts, 42 transactions), so ML scores can vary. All performance figures in our plans are targets, not results. The Android Accessibility permission is restricted by store policy, so the pilot is an opt-in install.

## Team
Team OMEGA 404, Sri Sairam Engineering College, Chennai: Shravan Khanal, Rithwik, Kirthik, Anisha.

---

# Original documentation
<div align="center">

# CyberNetX

### Detect. Trace. Neutralize.

**An end-to-end financial-fraud defense platform: stop scams before they reach the customer, and trace the money if they don't.**

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Neo4j](https://img.shields.io/badge/Neo4j-008CC1?style=for-the-badge&logo=neo4j&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![Flutter](https://img.shields.io/badge/Flutter-02569B?style=for-the-badge&logo=flutter&logoColor=white)
![XGBoost](https://img.shields.io/badge/XGBoost-EB5E28?style=for-the-badge)

</div>

---

## Overview

Online fraud is a two-sided problem. Victims get phished, and the stolen money disappears through layers of disposable mule accounts. Most tools cover only one side, and most are black boxes that block something without saying why.

**CyberNetX** closes both sides with two cooperating systems:

| Module | Role | What it does |
|---|---|---|
| **[ShieldNetX](./shieldnetx)** | Customer Shield | Real-time phishing and smishing detection that intercepts malicious links before they open |
| **[TraceNetX](./tracenetx)** | Bank Shield | AML mule-account detection and money-trail tracing using graph intelligence and an ML ensemble |

Threat intelligence flows from ShieldNetX into TraceNetX, so a scam blocked on one phone becomes a lead against the accounts behind it.

---

## Screenshots

<p align="center">
  <img src="assets/spider-map.png" width="100%" alt="TraceNetX Spider Map"/><br/>
  <b>Spider Map</b>: layered money-flow graph with role-colored nodes, tracing mule chains back to the dealer
</p>

<table>
  <tr>
    <td align="center" width="50%">
      <img src="assets/dashboard.png" alt="Risk Intelligence Dashboard"/><br/>
      <b>Risk Intelligence Dashboard</b><br/>Account risk scores, city and volume analytics
    </td>
    <td align="center" width="50%">
      <img src="assets/city-map.png" alt="India Money Flow Map"/><br/>
      <b>City Map</b><br/>Geospatial view of fund movement across India
    </td>
  </tr>
  <tr>
    <td align="center" width="50%">
      <img src="assets/evidence-package.png" alt="Evidence Package"/><br/>
      <b>Evidence Package</b><br/>SHAP-explained, regulator-ready case file
    </td>
    <td align="center" width="50%">
      <img src="assets/shieldnetx-app.png" width="45%" alt="ShieldNetX Android app"/><br/>
      <b>ShieldNetX Android App</b><br/>Link scanner and accessibility-service protection
    </td>
  </tr>
</table>

---

## Architecture

```mermaid
flowchart LR
    U["User devices<br/>Browser extension · Android app"] --> S["ShieldNetX<br/>Multi-signal threat engine"]
    S -->|"block · warn · ban"| U
    S -->|"POST /api/investigate<br/>payee intel (UPI, account, phone, domain, IP)"| T["TraceNetX<br/>Graph + ML intelligence"]
    B["Bank transaction data"] --> T
    R["Victim / complaint reports"] --> T
    T --> E["Evidence package<br/>Risk-scored accounts"]
    T -->|"pre-transfer warnings / holds"| BK["Banks"]
```

TraceNetX runs standalone and accepts three intake paths: bank-side behavioral detection, victim reports as seed nodes, and ShieldNetX payee intelligence. Flagged accounts can be pushed to banks, so people who never installed ShieldNetX are still protected.

---

## ShieldNetX: Customer Shield

Detects phishing in real time, on the device, before the user is exposed.

**Detection engine, six signals fused into one explainable risk score**

| Signal | What it looks at |
|---|---|
| Click Velocity | How fast and how widely a link is spreading |
| Dwell Time | How quickly people open a page and bail out, a strong tell for fake pages |
| Geo Velocity | Impossible or anomalous geographic travel of a link |
| HTML Analysis | Structure and content of the page source |
| JS Analysis | Obfuscation and malicious behavior in page scripts |
| Sender Trust | Reputation and context of the sender |

**Ghost Sandbox:** inspects live page behavior in a sandboxed browser and returns a verdict in under 3 seconds.

**Delivery surfaces**
- **Chrome extension** for in-browser protection
- **Android app** (Flutter) with a **Kotlin Accessibility Service** bridge that intercepts links system-wide, before any browser opens
- **FastAPI sentinel backend** for scoring and orchestration
- **Zero configuration** for the end user

**Automatic response on risky links:** block (warning screen with top reasons), warn (proceed-anyway option), ban (confirmed phishing domains, URLs and IPs go to a shared blocklist so repeats are stopped instantly), and report (payee details sent to TraceNetX).

Unlike copy-paste checkers that only know already-registered bad links, ShieldNetX analyzes behavior, so brand-new links don't slip through. It is built for everyone, not just bank customers.

---

## TraceNetX: Bank Shield

Most tools catch the criminal at the end of the chain. TraceNetX finds the **dealer**, the convergence point that mule accounts feed into. Mule accounts are disposable, but the dealer can't hide.

**Layer 1, DETECT.** Ensemble classification with XGBoost, LightGBM and Random Forest, with Isolation Forest as an independent anomaly signal. Class imbalance is handled with SMOTE, and every score is explained with **SHAP**.

**Layer 2, INVESTIGATE.** Neo4j graph intelligence:
- Forward traversal (**Spider Map**) and **reverse chain analysis**, tracing backward from the exit point to the coordinator
- Community detection, batch-recruitment detection (shared IP clusters), coordination and convergence analysis
- Pattern detectors for hawala-broker signatures, shell companies, crypto-gateway exposure and cross-border layering
- **City Map** geospatial view of fund movement
- Roles are derived from graph structure and behavior, never from account names

**Layer 3, ACT.** Graduated response instead of a binary flag:

| Level | Score | Response |
|---|---|---|
| CRITICAL | 85–100 | Immediate action |
| HIGH | 70–84 | Escalate |
| MEDIUM | 50–69 | Enhanced monitoring |
| LOW | 30–49 | Watchlist |
| CLEAR | 0–29 | No action |

- One-click **Evidence Package** with fund-flow chains, flagged-account details and a regulator-ready summary (STR / FIR style)
- CSV export of flagged accounts with risk scores and graph flags
- **Plug-and-play datasets:** upload any dataset and every view (Spider Map, City Map, Dashboard, Intelligence, Temporal, ML Analysis) rebuilds from it automatically

---

## Tech Stack

| Layer | Technologies |
|---|---|
| ML / Data | XGBoost, LightGBM, scikit-learn, TensorFlow/Keras, SHAP, imbalanced-learn, Pandas, NumPy |
| Graph | Neo4j, NetworkX |
| Backend | Python, FastAPI, Uvicorn |
| Frontend | React, Cytoscape.js |
| Mobile | Flutter, Kotlin (Accessibility Service) |
| Browser | Chrome Extension (Manifest V3) |
| Infra | Docker |

---

## Repository Structure

```
cybernetx/
├── shieldnetx/     # Phishing detection: extension, Android app, backend
├── tracenetx/      # Fraud graph platform: backend, frontend, docs
└── README.md
```

---

## Getting Started

### TraceNetX (local)

```bash
# 1. Graph database
docker run -d --name neo4j -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/<your-password> neo4j:latest

# 2. Backend (wait ~15s after Neo4j starts)
cd tracenetx/backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --port 8001

# 3. Frontend
cd ../frontend/tracenetx-ui
npm install && npm start
```

### ShieldNetX

Each ShieldNetX component (extension, Android app, backend) has its own setup instructions in the [`shieldnetx/`](./shieldnetx) directory.


> Make sure the Neo4j credentials in your environment match the backend configuration. Never commit credentials to the repository.

---

## Roadmap

- [ ] APK-link analysis: static analysis, sandbox execution and GenAI code interpretation
- [ ] Visual brand-impersonation detection (CLIP-based) and page fingerprinting (logo hash, DOM/phishing-kit hash, favicon hash, TLS server fingerprint)
- [ ] URL and domain intelligence: domain age, fresh certificates, typosquatting and punycode, redirect depth, ASN/TLD reputation
- [ ] LSTM lifecycle modeling, and victim-vs-criminal account classification
- [ ] Kafka streaming for real-time ingestion
- [ ] Regulator feed integration (I4C, NCRP, FIU-IND)
- [ ] Hardware: ESP32 desk appliance and router plug for network-wide protection

---

## Team

Built by **Team OMEGA 404**, Sri Sairam Engineering College, Chennai, in association with **OWASP Sri Sairam**.

**Lead:** [Shravan Khanal](https://github.com/learnfast12)

---

<div align="center">

**CyberNetX: Detect. Trace. Neutralize.**

</div>
