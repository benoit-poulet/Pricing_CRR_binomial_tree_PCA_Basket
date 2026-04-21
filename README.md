# Pricing d'Options : Modèle Binomial CRR & Réduction PCA pour Paniers d'Actifs 

## Description du Projet

**Dates de réalisation :** 10 Décembre 2025 – 13 Décembre 2025

### English Version
After coding the American and European options pricer with Monte Carlo and Longstaff-Schwartz methods, I implemented the Cox-Ross-Rubinstein (CRR) binomial tree pricing method. To overcome the "curse of dimensionality" when pricing Basket Options (options on multiple underlying assets), I integrated a Machine Learning layer using Principal Component Analysis (PCA). This allows the extraction of the main market risk factor, reducing an $N$-dimensional problem into a solvable 1D binomial tree.

### Version Française
Faisant suite à mon implémentation des méthodes de Monte Carlo et de Longstaff-Schwartz, ce projet introduit le modèle binomial de Cox-Ross-Rubinstein (1979). Contrairement à Monte Carlo qui est un estimateur statistique, l'arbre binomial fournit une solution numérique exacte, idéale pour capturer la frontière d'exercice optimal des options américaines.

Pour surmonter la "malédiction de la dimensionnalité" inhérente aux arbres lors du pricing d'options sur paniers (Basket Options), une couche d'Analyse en Composantes Principales (PCA) a été développée. Elle permet de synthétiser la matrice de covariance d'un portefeuille d'actifs réels en un facteur de risque principal, rendant le pricing multidimensionnel possible et instantané.

---

## Concepts Théoriques Clés

### 1. La Dynamique de l'Arbre (CRR)
Le modèle divise la maturité $T$ en pas de temps $\Delta t$. À chaque étape, le sous-jacent peut monter ou descendre :
$$u = e^{\sigma \sqrt{\Delta t}} \quad \text{et} \quad d = e^{-\sigma \sqrt{\Delta t}}$$

### 2. Probabilité Risque-Neutre
Calculée pour garantir l'absence d'opportunité d'arbitrage (en incluant le taux sans risque $r$ et les dividendes $q$) :
$$p = \frac{e^{(r-q)\Delta t} - d}{u - d}$$

### 3. Réduction de Dimension (PCA) & Modélisation Multi-Facteurs
Pour un panier de $N$ actifs, la matrice de covariance empirique est décomposée en valeurs et vecteurs propres afin d'extraire des facteurs de risque orthogonaux (indépendants) :

* **PC1 (Le Facteur Marché / Systémique) :** Associé à la plus grande valeur propre, il capture la tendance globale du panier (lorsque tous les actifs bougent ensemble). Pour un panier hautement corrélé (ex: Banques), PC1 suffit à capturer plus de 80% de la variance. La volatilité de ce portefeuille synthétique est alors injectée dans un arbre binomial 1D ultra-rapide.
* **PC2 & PC3 (Facteurs Sectoriels / Divergences) :** Capturent les dynamiques secondaires (les oppositions de styles, les risques idiosyncratiques spécifiques à certains sous-groupes d'actifs). 

**Le mur de la corrélation :** Lorsque le panier présente une corrélation plus faible (ex: secteur Tech, où PC1 ne capture que ~60% de la variance), pricer uniquement avec PC1 revient à amputer le modèle de 40% de son risque, sous-évaluant drastiquement l'option. Le projet introduit alors une extension **Multi-Facteurs via Monte Carlo**, simulant conjointement PC1, PC2 et PC3 pour reconstituer fidèlement la dimensionnalité du risque, là où l'arbre binomial atteindrait ses limites spatiales (RAM).

---

## Outils et Technologies

- **numpy / pandas** : Calcul vectoriel intensif et algèbre linéaire (Décomposition matricielle propre `np.linalg.eigh`).
- **yfinance** : Extraction automatisée des historiques de prix et matrices de corrélation de marché.
- **matplotlib / seaborn** : Visualisation de la convergence et de l'impact de l'exercice anticipé.
- **Jupyter** : Environnement de recherche et d'analyse.

---

## Architecture du Projet

```
Pricing_Cox_Ross_Rubinstein_PCA/
│
├── docs/
│   ├── crr_theory.md               # Dérivations mathématiques du modèle et PCA
│   ├── pca_theory.md               # Algorithme PCA expliqué et adaptation aux Baskets
│   └── monte_carlo_pca.md          # Théorie : Arbre vs Monte Carlo en dimension N
│
├── src/
│   ├── models/
│   │   ├── binomial_tree.py        # Algorithme CRR (Européen et Américain) vectorisé
│   │   └── monte_carlo_pca.py      # Moteur de simulation multi-facteurs (PC1, PC2, PC3...)
│   └── utils/
│       └── market_data.py          # API yfinance, Courbe OAT et Algorithme PCA
│
├── notebooks/
│   ├── 01_crr_theoretical.ipynb        # Validation mathématique (Benchmark avec Black-Scholes)
│   ├── 02_crr_basket_pca.ipynb         # Pricing d'un panier d'actions (Tech/Luxe) via PCA
│   └── 03_multi_factor_pricing.ipynb   # Le test de robustesse sur la Tech (PC1 vs PC1+PC2+PC3)
│
├── requirements.txt                # Dépendances Python
└── README.md
```

---

## Références Académiques

1. **Cox, J. C., Ross, S. A., & Rubinstein, M. (1979)**. *Option Pricing: A Simplified Approach*. Journal of Financial Economics, 7(3), 229-263.
2. **Hull, J. C. (2018)**. *Options, Futures, and Other Derivatives*. Pearson.
3. **Jolliffe, I. T. (2002)**. *Principal Component Analysis*. Springer Series in Statistics.
4. **API de marché** : [yfinance Documentation](https://pypi.org/project/yfinance/)