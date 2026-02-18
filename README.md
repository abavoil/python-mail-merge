# Python Mail Merger

Ce script permet d'envoyer des emails personnalisés en masse à partir d'un fichier **CSV** et d'un template **HTML**. Il supporte l'injection de données variables (colonnes du CSV) et de données constantes (liens, noms d'établissement, etc.) définies dans un fichier de configuration.

## 🚀 Fonctionnement

Le script effectue une fusion (merge) entre trois éléments :
1. **Un template HTML** : Contient le design et des balises du type `<<NomDuChamp>>`.
2. **Un fichier CSV** : Contient les données qui varient pour chaque destinataire (une ligne = un email).
3. **Un fichier JSON de configuration** : Gère les accès SMTP et les données constantes communes à tous les emails.

Le script utilise la méthode `.replace()` pour l'injection des données, ce qui permet d'utiliser des balises `<style>` complexes dans votre HTML sans conflit avec la syntaxe Python.

---

## 📁 Structure des fichiers

- `main.py` : Le script d'exécution.
- `default-config.json` : Configuration par défaut.
- `config.json` : Configuration locale (exclue du versioning, contient vos mots de passe).
- `template.html` : Le corps de l'email.
- `data.csv` : La base de données.

---

## 📖 Exemple Simplissime

Voici comment configurer un envoi rapide :

### 1. Le Template (`template.html`)
```html
<style>
    .card { font-family: sans-serif; border: 1px solid #ddd; padding: 20px; }
    .highlight { color: #27ae60; font-weight: bold; }
</style>

<div class="card">
    <p>Bonjour <<prenom>>,</p>
    <p>Tu as obtenu la note de <span class="highlight"><<note>>/20</span>.</p>
    <p>Merci de ta participation à <strong><<nom_ecole>></strong>.</p>
</div>
```

### 2. Les Données (`data.csv`)
```csv
prenom,email,note
Alice,alice@example.com,18
Bob,bob@example.com,14
```

### 3. La Configuration (`config.json`)
```json
{
    "sender_email": "votre.email@gmail.com",
    "password": "votre-mot-de-passe-application",
    "email_column": "email",
    "email_subject": "Résultat de <<prenom>>",
    "constants": {
        "nom_ecole": "Lycée Saint-Exupéry"
    }
}
```

---

## ⚙️ Configuration Avancée

### Gestion des fichiers JSON
Le script fusionne `default-config.json` et `config.json`. Cela permet de :
- Garder les paramètres génériques dans le fichier par défaut.
- Surcharger uniquement les informations sensibles (mot de passe, emails) dans le fichier local.

### Sécurité SMTP (Gmail)
Si vous utilisez Gmail, vous ne pouvez pas utiliser votre mot de passe habituel. Vous devez :
1. Activer la validation en deux étapes sur votre compte Google.
2. Générer un **Mot de passe d'application** (Sécurité > Connexion à Google).
3. Utiliser ce code de 16 caractères dans votre fichier `config.json`.

### Balises de remplacement
Les balises dans le HTML et dans l'objet de l'email doivent être entourées de `<< >>`.
- Si le script trouve `<<nom>>`, il cherchera d'abord une colonne `nom` dans le CSV.
- S'il ne la trouve pas, il cherchera une clé `nom` dans le dictionnaire `constants` du fichier JSON.

---

## 🛠 Installation et Exécution

1. Assurez-vous d'avoir Python 3 installé.
2. Placez vos fichiers dans le même dossier.
3. Exécutez le script :
   ```bash
   python main.py
   ```

---

## ⚠️ Points d'attention importants

- **Limite d'envoi** : Les serveurs SMTP (comme Gmail ou Outlook) ont des quotas quotidiens d'envoi d'emails (généralement entre 500 et 2000 par jour).
- **Encodage** : Enregistrez toujours votre fichier CSV en **UTF-8** pour éviter les problèmes d'accents.
- **Headers CSV** : Les noms des colonnes dans votre CSV ne doivent pas contenir d'espaces ou de caractères spéciaux complexes pour faciliter le remplacement.
- **Testez d'abord** : Avant d'envoyer à 200 personnes, créez un fichier CSV de test avec uniquement votre propre adresse email.