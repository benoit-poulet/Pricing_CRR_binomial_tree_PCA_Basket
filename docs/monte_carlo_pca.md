# Pricing Multi-Facteurs : Monte Carlo sur Composantes Principales

## 1. Les Limites de l'Arbre Binomial (Le Mur Dimensionnel)

L'arbre de Cox-Ross-Rubinstein (CRR) est une méthode numérique extrêmement puissante en dimension 1, car elle permet de capturer la prime d'exercice anticipé des options américaines. Grâce à notre première réduction PCA, nous avons pu écraser la dimension d'un panier d'actifs ($N$) en un seul facteur principal (PC1), permettant d'utiliser un arbre 1D.

Cependant, lorsque les actifs du panier sont faiblement corrélés (comme dans le secteur de la Tech), le PC1 ne capture qu'une fraction de la variance totale (ex: 60%). Pour obtenir un pricing robuste, il devient impératif de réintégrer les dynamiques secondaires : **PC2 et PC3**.

**Pourquoi ne pas faire un arbre binomial en 3D ?**
Dans un arbre binomial standard, à chaque pas de temps, l'actif évolue vers 2 états (Hausse ou Baisse). 
Pour un modèle à $D$ dimensions, chaque nœud se sépare en $2^D$ branches :
- Dimension 1 (PC1) : $2^1 = 2$ branches par nœud.
- Dimension 2 (PC1, PC2) : $2^2 = 4$ branches par nœud.
- Dimension 3 (PC1, PC2, PC3) : $2^3 = 8$ branches par nœud.

Pour un arbre de 1000 pas en dimension 3, le nombre de nœuds terminaux devient astronomique. La complexité spatiale (RAM) et temporelle sature instantanément les capacités de calcul standard.

---

## 2. La Solution : Monte Carlo Multi-Facteurs

Pour briser la "malédiction de la dimensionnalité", la méthode standard de l'industrie quantitative est la **Simulation de Monte Carlo**. L'avantage de Monte Carlo est que son taux de convergence en $\mathcal{O}(1/\sqrt{M})$ (où $M$ est le nombre de trajectoires) est indépendant de la dimension du problème.

L'utilisation conjointe de la **PCA** et de **Monte Carlo** est particulièrement élégante, car la PCA fournit par définition des facteurs de risque *strictement orthogonaux* (indépendants). 

---

## 3. Modélisation Mathématique

L'objectif est de simuler les trajectoires de $N$ actifs d'un panier en utilisant seulement $K$ composantes principales ($K \ll N$, par exemple $K=3$ pour un panier de 10 actions).

### 3.1 Décomposition du Risque
Soit $\Sigma$ la matrice de covariance des rendements du panier. La PCA effectue la décomposition spectrale :
$$\Sigma \approx V_K \Lambda_K V_K^T$$
Où :
- $\Lambda_K$ est la matrice diagonale des $K$ plus grandes valeurs propres.
- $V_K$ est la matrice des $K$ vecteurs propres associés (de taille $N \times K$).

### 3.2 Simulation des Chocs Indépendants
Puisque les composantes principales sont non corrélées, nous pouvons simuler $K$ variables aléatoires indépendantes tirées d'une loi normale centrée réduite pour chaque pas de temps :
$$Z = [Z_1, Z_2, \dots, Z_K]^T \sim \mathcal{N}(0, I_K)$$

### 3.3 Recombinaison des Actifs
Le vecteur des chocs corrélés $W$ pour les $N$ actions du panier est reconstitué en multipliant les chocs indépendants par les pondérations de la PCA :
$$W = V_K \sqrt{\Lambda_K} Z$$

Ainsi, pour un actif $i$, le prix à maturité $T$ sous l'hypothèse d'un Mouvement Brownien Géométrique risque-neutre s'écrit :
$$S_i(T) = S_i(0) \exp\left( \left(r - q_i - \frac{\sigma_i^2}{2}\right)T + \sqrt{T} \sum_{k=1}^K V_{i,k} \sqrt{\lambda_k} Z_k \right)$$

---

## 4. Application aux Options sur Panier (Basket Options)

Une fois les trajectoires des $N$ actifs simulées simultanément jusqu'à la maturité $T$, le prix de l'indice synthétique (le Panier) est calculé. 
Pour un panier équipondéré :
$$Basket_m(T) = \frac{1}{N} \sum_{i=1}^N \frac{S_{i,m}(T)}{S_i(0)}$$
*(où $m$ représente la $m$-ième trajectoire simulée).*

Le prix de l'option Européenne (ex: un Put) est l'espérance actualisée de tous les payoffs terminaux simulés :
$$V_0 = e^{-rT} \frac{1}{M} \sum_{m=1}^M \max(K - Basket_m(T), 0)$$

---

## 5. Comparatif des Approches

| Caractéristique | Arbre Binomial (CRR 1D sur PC1) | Monte Carlo (PC1 + PC2 + PC3) |
| :--- | :--- | :--- |
| **Précision du Risque** | Faible si corrélation < 70% | Excellente (Capture > 90% de la variance) |
| **Type d'Options** | Européennes et **Américaines** | Européennes (nécessite Longstaff-Schwartz pour les Américaines) |
| **Temps de Calcul** | Instantané ($\approx 10$ ms) | Très rapide ($\approx 2$ secondes pour $10^5$ trajectoires) |
| **Dimension maximale**| $D = 1$ (voire $D=2$ avec difficulté) | $D = 100+$ sans difficulté technique |

**Conclusion :** Le modèle CRR couplé au PC1 est un outil pédagogique et rapide pour évaluer la prime d'exercice anticipé sur des secteurs très corrélés. Pour un pricing industriel de haute précision sur des paniers complexes, le Monte Carlo Multi-Facteurs prend le relais.