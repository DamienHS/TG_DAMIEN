# WasteGraph – Système d'Optimisation de Collecte des Déchets

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13%2B-316192)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📋 Table des Matières

- [Vue d'ensemble](#-vue-densemble)
- [Architecture du Projet](#-architecture-du-projet)
- [Algorithmes Implémentés](#-algorithmes-implémentés)
- [Prérequis](#-prérequis)
- [Installation](#-installation)
- [Configuration de la Base de Données](#-configuration-de-la-base-de-données)
- [Utilisation](#-utilisation)
- [Structure du Projet](#-structure-du-projet)
- [API Reference](#-api-reference)
- [Interface Utilisateur](#-interface-utilisateur)
- [Exemples d'Utilisation](#-exemples-dutilisation)
- [Contributions](#-contributions)
- [Auteurs](#-auteurs)
- [Licence](#-licence)

## 🎯 Vue d'ensemble

**WasteGraph** est une application web de visualisation et d'optimisation de routes de collecte des déchets, développée dans le cadre d'un projet universitaire de théorie des graphes. Le système utilise des algorithmes classiques de la théorie des graphes pour résoudre des problèmes d'optimisation réels dans le domaine de la gestion des déchets urbains.

### Problématique

La collecte des déchets en milieu urbain pose plusieurs défis d'optimisation :
- **Planification des tournées** : Minimiser la distance totale parcourue
- **Répartition des équipes** : Assigner efficacement les zones de collecte
- **Gestion des contraintes** : Respecter les capacités des véhicules et les contraintes temporelles

### Solution Proposée

WasteGraph offre une interface interactive permettant de :
- Visualiser le réseau de collecte sous forme de graphe
- Calculer les chemins optimaux entre plusieurs points (problème du voyageur de commerce)
- Assigner des équipes/jours de collecte via un algorithme de coloration de graphe
- Modifier dynamiquement les contraintes du réseau

## 🏗️ Architecture du Projet

Le projet suit une architecture client-serveur classique :

```
┌─────────────────┐         HTTP/REST          ┌──────────────────┐
│                 │ ◄──────────────────────────► │                  │
│  Frontend (JS)  │         JSON API            │  Backend (Python)│
│   + SVG Canvas  │ ──────────────────────────► │   + Algorithmes  │
│                 │                              │                  │
└─────────────────┘                              └────────┬─────────┘
                                                          │
                                                          │ SQL
                                                          ▼
                                                 ┌─────────────────┐
                                                 │   PostgreSQL    │
                                                 │   (wastegraph)  │
                                                 └─────────────────┘
```

### Technologies Utilisées

**Backend**
- Python 3.8+
- `http.server` (serveur HTTP intégré)
- `psycopg2` (connecteur PostgreSQL)
- `heapq` (file de priorité pour Dijkstra)

**Frontend**
- HTML5 / CSS3
- JavaScript Vanilla
- SVG pour la visualisation du graphe

**Base de données**
- PostgreSQL 13+

## 🧮 Algorithmes Implémentés

### 1. Algorithme de Dijkstra (Chemin le Plus Court)

**Complexité** : O((V + E) log V) avec une file de priorité

**Application** : Calcul du chemin optimal entre un dépôt et plusieurs points de collecte.

```python
# Pseudo-code simplifié
def dijkstra(graph, source, destination):
    distances = {node: ∞ for node in graph}
    distances[source] = 0
    priority_queue = [(0, source)]
    
    while priority_queue:
        current_dist, current_node = extract_min(priority_queue)
        
        for neighbor, weight in graph.neighbors(current_node):
            new_dist = current_dist + weight
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                insert(priority_queue, (new_dist, neighbor))
    
    return reconstruct_path(destination)
```

**Extension Multi-cibles** : Notre implémentation résout une variante du problème en chaînant plusieurs appels de Dijkstra pour visiter séquentiellement N points.

### 2. Coloration de Graphe (Algorithme Glouton)

**Complexité** : O(V + E)

**Application** : Attribution de jours/équipes de collecte en évitant les conflits entre zones adjacentes.

```python
# Pseudo-code simplifié
def greedy_coloring(graph):
    colors = {}
    
    for node in graph.nodes:
        # Trouver les couleurs des voisins
        neighbor_colors = {colors[neighbor] for neighbor in graph.neighbors(node)}
        
        # Assigner la plus petite couleur disponible
        color = 0
        while color in neighbor_colors:
            color += 1
        
        colors[node] = color
    
    return colors
```

**Propriété** : L'algorithme garantit une coloration valide avec au maximum Δ + 1 couleurs (où Δ est le degré maximal du graphe).

## 📦 Prérequis

- **Python** 3.8 ou supérieur
- **PostgreSQL** 13 ou supérieur
- **pip** (gestionnaire de paquets Python)
- Un navigateur web moderne (Chrome, Firefox, Safari)

## 🚀 Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/votre-username/wastegraph.git
cd wastegraph
```

### 2. Installer les dépendances Python

```bash
pip install psycopg2-binary
```

Ou si vous avez un fichier `requirements.txt` :

```bash
pip install -r requirements.txt
```

### 3. Vérifier l'installation de PostgreSQL

```bash
psql --version
```

Si PostgreSQL n'est pas installé :

**macOS** :
```bash
brew install postgresql
brew services start postgresql
```

**Linux** :
```bash
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

## 🗄️ Configuration de la Base de Données

### 1. Créer la base de données

```bash
psql -U postgres
```

```sql
CREATE DATABASE wastegraph;
\c wastegraph
```

### 2. Créer les tables

```sql
-- Table des nœuds (points de collecte)
CREATE TABLE nodes (
    id VARCHAR(10) PRIMARY KEY,
    x INTEGER NOT NULL,
    y INTEGER NOT NULL,
    capacity INTEGER
);

-- Table des arêtes (routes)
CREATE TABLE edges (
    id SERIAL PRIMARY KEY,
    src VARCHAR(10) REFERENCES nodes(id) ON DELETE CASCADE,
    dst VARCHAR(10) REFERENCES nodes(id) ON DELETE CASCADE,
    weight FLOAT NOT NULL,
    CONSTRAINT unique_edge UNIQUE(src, dst)
);

-- Index pour améliorer les performances
CREATE INDEX idx_edges_src ON edges(src);
CREATE INDEX idx_edges_dst ON edges(dst);
```

### 3. Configuration des identifiants

Modifiez le fichier `server.py` ligne 12-18 selon vos paramètres PostgreSQL :

```python
conn = psycopg2.connect(
    dbname="wastegraph",
    user="postgres",          # Votre utilisateur PostgreSQL
    password="MDP",          # Votre mot de passe
    host="localhost",
    port=5432
)
```

### 4. Charger les données initiales

```bash
python load_data_raw.py
```

Ce script initialise le graphe avec un réseau de test comprenant :
- 8 nœuds (DEPOT, A, B, C, D, E, F, G)
- 10 arêtes avec des poids représentant des distances en km

## 🎮 Utilisation

### 1. Démarrer le serveur backend

```bash
python server.py
```

Le serveur démarre sur `http://localhost:8000`

### 2. Ouvrir l'interface web

Ouvrez `index.html` dans votre navigateur, ou utilisez un serveur local :

```bash
# Option 1 : Ouvrir directement
open index.html

# Option 2 : Serveur Python simple (recommandé)
python -m http.server 3000
# Puis ouvrez http://localhost:3000
```

### 3. Utiliser l'application

L'interface permet de :

1. **Visualiser le graphe** : Affichage SVG interactif avec nœuds et arêtes
2. **Calculer un itinéraire optimal** :
   - Sélectionner un point de départ (source)
   - Sélectionner plusieurs destinations
   - Cliquer sur "Dijkstra (multi)"
3. **Assigner des équipes** :
   - Cliquer sur "Colorier (jours/équipes)"
   - Observer la coloration du graphe
4. **Modifier le réseau** :
   - Ajouter/supprimer des nœuds
   - Ajouter/supprimer des arêtes
   - Modifier le poids d'une arête

## 📁 Structure du Projet

```
wastegraph/
│
├── index.html              # Interface utilisateur principale
├── styles.css              # Feuille de style
├── app.js                  # Logique frontend (fetch API, SVG)
│
├── server.py               # Serveur HTTP + endpoints REST
├── graph.py                # Classe Graph (structure de données)
├── dijkstra.py             # Implémentation de l'algorithme de Dijkstra
├── coloring.py             # Implémentation du coloring glouton
├── load_data_raw.py        # Script d'initialisation des données
│
├── README.md               # Documentation (ce fichier)
└── requirements.txt        # Dépendances Python
```

## 🔌 API Reference

### Récupérer le graphe

```http
GET /graph
```

**Réponse** :
```json
{
  "nodes": {
    "A": {"x": 140, "y": 330},
    "B": {"x": 250, "y": 100}
  },
  "edges": {
    "A": [["B", 2.3, 1]],
    "B": [["A", 2.3, 1]]
  }
}
```

### Algorithme de Dijkstra (simple)

```http
GET /algo/dijkstra?src=A&dst=B
```

**Réponse** :
```json
{
  "result": [["A", "D", "B"], 4.5]
}
```

### Algorithme de Dijkstra (multi-cibles)

```http
GET /algo/dijkstra/multi?src=DEPOT&targets=A,C,F
```

**Réponse** :
```json
{
  "path": ["DEPOT", "A", "E", "D", "C", "F"],
  "points_to_visit": ["A", "C", "F"],
  "total_distance": 11.4
}
```

### Coloration de graphe

```http
GET /algo/coloring
```

**Réponse** :
```json
{
  "colors": {
    "DEPOT": 0,
    "A": 1,
    "B": 1,
    "C": 2,
    "D": 0
  }
}
```

### Ajouter un nœud

```http
POST /graph/node
Content-Type: application/json

{
  "id": "H",
  "x": 500,
  "y": 400
}
```

### Ajouter une arête

```http
POST /graph/edge
Content-Type: application/json

{
  "u": "A",
  "v": "H",
  "weight": 3.5
}
```

### Modifier le poids d'une arête

```http
POST /graph/edge/update
Content-Type: application/json

{
  "id": 5,
  "weight": 2.8
}
```

### Supprimer un nœud

```http
DELETE /graph/node?id=H
```

### Supprimer une arête

```http
DELETE /graph/edge?id=5
```

## 🖥️ Interface Utilisateur

### Composants Principaux

1. **Canvas SVG** : Zone de dessin du graphe (650×550px)
   - Nœuds représentés par des cercles avec labels
   - Arêtes avec poids affichés au milieu
   - Coloration dynamique selon les algorithmes

2. **Panneau de contrôle** (en haut)
   - Bouton "Colorier"
   - Sélecteur de source
   - Sélecteur multi-cibles
   - Bouton "Dijkstra (multi)"

3. **Sidebar droite**
   - Légende des couleurs
   - Résultats des algorithmes
   - Formulaires de gestion du graphe

### Codes Couleur

| Couleur | Signification |
|---------|---------------|
| Blanc | Nœud standard |
| Jaune clair (#fff5a3) | Nœud sur le chemin calculé |
| Bleu (#add8e6) | Équipe/Jour 0 |
| Jaune (#ffe599) | Équipe/Jour 1 |
| Vert (#b6d7a8) | Équipe/Jour 2 |
| ... | Autres équipes (jusqu'à 10 couleurs prédéfinies) |

## 💡 Exemples d'Utilisation

### Cas d'usage 1 : Planification d'une tournée

**Objectif** : Un camion doit partir du DEPOT et collecter aux points A, C et F.

**Étapes** :
1. Sélectionner "DEPOT" comme source
2. Maintenir Cmd (Mac) ou Ctrl (Windows/Linux) et sélectionner A, C, F dans la liste
3. Cliquer sur "Dijkstra (multi)"

**Résultat** :
```
Chemin obtenu : DEPOT → A → E → D → C → F
Distance totale : 11.4 km
```

### Cas d'usage 2 : Répartition des équipes

**Objectif** : Assigner des jours de collecte pour éviter que deux zones adjacentes soient collectées le même jour.

**Étapes** :
1. Cliquer sur "Colorier (jours/équipes)"

**Résultat** :
- Le graphe se colorie
- La légende indique le nombre de jours nécessaires (généralement 3-4)
- Les zones adjacentes ont des couleurs différentes

### Cas d'usage 3 : Simulation de fermeture de route

**Objectif** : Une route est en travaux, augmenter artificiellement son poids.

**Étapes** :
1. Dans "Modifier le poids d'une arête", sélectionner par exemple "A → E (actuel: 3.0)"
2. Entrer un nouveau poids élevé : 50
3. Cliquer sur "Modifier"
4. Refaire un calcul Dijkstra → le chemin évite maintenant cette arête

## 🤝 Contributions

Les contributions sont les bienvenues ! Pour contribuer :

1. Forkez le projet
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/NouvelleFonctionnalite`)
3. Committez vos changements (`git commit -m 'Ajout d'une nouvelle fonctionnalité'`)
4. Poussez vers la branche (`git push origin feature/NouvelleFonctionnalite`)
5. Ouvrez une Pull Request

### Améliorations Futures

- [ ] Algorithme de Bellman-Ford pour les poids négatifs
- [ ] Algorithme de Kruskal/Prim pour l'arbre couvrant minimal
- [ ] Export des résultats en PDF/CSV
- [ ] Authentification utilisateur
- [ ] Mode multi-utilisateurs avec WebSockets
- [ ] Intégration de cartes réelles (OpenStreetMap)
- [ ] Optimisation avec contraintes de capacité (CVRP)

## 👥 Auteur

- **DAMIEN SALAMERO**

Projet réalisé dans le cadre du cours de **Théorie des Graphes** (année universitaire 2025-2026).


---

## 📚 Références Académiques

1. **Dijkstra, E. W.** (1959). "A note on two problems in connexion with graphs". *Numerische Mathematik*, 1(1), 269-271.

2. **Welch, T. A.** (1967). "An upper bound for the chromatic number of a graph and its application to timetabling problems". *The Computer Journal*, 10(1), 85-86.

3. **Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C.** (2009). *Introduction to Algorithms* (3rd ed.). MIT Press.

4. **Toth, P., & Vigo, D.** (2014). *Vehicle Routing: Problems, Methods, and Applications* (2nd ed.). SIAM.

---

## 🐛 Signaler un Bug

Si vous trouvez un bug, veuillez ouvrir une [issue](https://github.com/votre-username/wastegraph/issues) avec :
- Une description claire du problème
- Les étapes pour reproduire
- Le comportement attendu vs observé
- Captures d'écran si pertinent

---

**Développé avec ❤️ pour optimiser la gestion des déchets urbains**
