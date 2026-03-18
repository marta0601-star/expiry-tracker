# 📦 Expiry Tracker

.Sledujte dátumy spotreby produktov. Odfotíte produkt → appka rozpozná dátum → automaticky vám príde email keď sa blíži expirácia.

## Ako to funguje

1. **Webová appka** (GitHub Pages) — skenujete produkty fotoaparátom, AI rozpozná dátum spotreby
2. **Automatický email** (GitHub Actions) — každý deň ráno skript skontroluje produkty a pošle vám email ak niečo expiruje do 30 dní

## 🚀 Nastavenie (krok za krokom)

### 1. Vytvorte GitHub repozitár

1. Choďte na [github.com/new](https://github.com/new)
2. Názov: `expiry-tracker`
3. Nastavte ako **Public** (potrebné pre GitHub Pages)
4. Kliknite **Create repository**
5. Nahrajte všetky súbory z tohto projektu do repozitára

### 2. Zapnite GitHub Pages

1. V repozitári choďte do **Settings → Pages**
2. Source: **Deploy from a branch**
3. Branch: **main**, folder: **/ (root)**
4. Kliknite **Save**
5. Po pár minútach bude appka na: `https://vasemeno.github.io/expiry-tracker/`

### 3. Získajte Anthropic API kľúč (pre rozpoznávanie produktov)

1. Choďte na [console.anthropic.com](https://console.anthropic.com)
2. Vytvorte účet a vygenerujte API kľúč
3. Kľúč si uložte (začína na `sk-ant-...`)

### 4. Nastavte Gmail pre automatický email

Pre odosielanie emailov cez Gmail potrebujete **App Password**:

1. Choďte na [myaccount.google.com/security](https://myaccount.google.com/security)
2. Zapnite **2-Step Verification** (ak nemáte)
3. Choďte do **App passwords** (alebo hľadajte "app passwords" vo vyhľadávaní)
4. Vytvorte nové heslo pre "Mail" — skopírujte 16-znakový kód

### 5. Pridajte GitHub Secrets

V repozitári choďte do **Settings → Secrets and variables → Actions** a pridajte:

| Secret | Hodnota | Príklad |
|--------|---------|---------|
| `EMAIL_TO` | Váš email kam majú chodiť upozornenia | `jan@gmail.com` |
| `SMTP_SERVER` | SMTP server | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP port | `587` |
| `SMTP_USER` | Gmail adresa | `jan@gmail.com` |
| `SMTP_PASSWORD` | App Password z kroku 4 | `abcd efgh ijkl mnop` |

### 6. Vytvorte GitHub Personal Access Token (pre sync z appky)

1. Choďte na [github.com/settings/tokens](https://github.com/settings/tokens)
2. **Generate new token (classic)**
3. Zaškrtnite scope: **repo**
4. Kliknite Generate a skopírujte token

### 7. Nastavte appku

1. Otvorte appku v prehliadači (`vasemeno.github.io/expiry-tracker`)
2. Choďte do **Nastavenia**
3. Zadajte:
   - Anthropic API kľúč
   - Váš email
   - GitHub Token
   - GitHub Repo (`vasemeno/expiry-tracker`)
4. Kliknite **Uložiť**

### 8. Pridajte appku na plochu telefónu

- **iPhone**: Safari → Zdieľať → Pridať na plochu
- **Android**: Chrome → Menu (⋮) → Pridať na plochu

## ✅ Hotovo!

Teraz môžete:
- 📷 Fotiť produkty a automaticky rozpoznávať dátumy
- 📧 Každé ráno dostanete email ak niečo expiruje
- 📱 Appka funguje ako natívna appka na telefóne

## 📁 Štruktúra projektu

```
expiry-tracker/
├── index.html                    # Webová appka
├── manifest.json                 # PWA manifest
├── products.json                 # Databáza produktov (sync z appky)
├── check_expiry.py               # Skript pre dennú kontrolu
├── README.md                     # Tento súbor
└── .github/
    └── workflows/
        └── daily-check.yml       # GitHub Actions — denný cron
```

## ❓ FAQ

**Koľko to stojí?**
- GitHub Pages + Actions = zadarmo
- Anthropic API = cca $0.003 za jedno skenovanie (veľmi lacné)

**Môžem zmeniť čas emailu?**
Áno, v `.github/workflows/daily-check.yml` upravte cron výraz. Napr. `0 5 * * *` = 7:00 CEST.

**Čo ak nemám Gmail?**
Zmeňte `SMTP_SERVER` a `SMTP_PORT` na váš email provider (napr. Outlook: `smtp.office365.com:587`).

**Dáta sú bezpečné?**
Produkty sú uložené vo vašom privátnom repozitári. API kľúče sú v GitHub Secrets (šifrované).
