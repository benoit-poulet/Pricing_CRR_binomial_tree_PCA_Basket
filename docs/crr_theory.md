# Étude Théorique du Modèle Binomial de Cox-Ross-Rubinstein (CRR)

## 1. Introduction

Introduit en 1979 par John C. Cox, Stephen A. Ross et Mark Rubinstein, le modèle binomial est une méthode numérique d'évaluation d'options en temps discret. Contrairement au modèle de Black-Scholes qui repose sur une équation aux dérivées partielles en temps continu, le modèle CRR modélise l'évolution du prix de l'actif sous-jacent par un arbre, ou treillis, recombinant.

C'est l'une des méthodes les plus robustes et intuitives pour valoriser les options américaines, car elle permet de vérifier la condition d'exercice optimal à chaque étape de la vie de l'option.

---

## 2. Construction de l'Arbre (Dynamique du Sous-jacent)

Le temps jusqu'à l'échéance de l'option $T$ est divisé en $N$ intervalles de temps égaux, de longueur $\Delta t$ :
$$\Delta t = \frac{T}{N}$$

À chaque pas de temps, le prix de l'actif $S$ peut évoluer vers deux états possibles :
- **Un mouvement à la hausse** par un facteur $u$ (up)
- **Un mouvement à la baisse** par un facteur $d$ (down)

Pour que la variance de l'arbre corresponde à la variance de l'actif sous-jacent modélisé par un Mouvement Brownien Géométrique avec une volatilité $\sigma$, les facteurs sont définis ainsi :
$$u = e^{\sigma \sqrt{\Delta t}}$$
$$d = e^{-\sigma \sqrt{\Delta t}} = \frac{1}{u}$$

L'arbre est dit **recombinant** car un mouvement à la hausse suivi d'une baisse donne le même prix qu'une baisse suivie d'une hausse ($S \cdot u \cdot d = S \cdot d \cdot u = S$).

---

## 3. Probabilité Risque-Neutre

Dans un cadre d'évaluation risque-neutre, le rendement espéré de l'actif sous-jacent doit être égal au taux sans risque $r$, ajusté du taux de dividende continu $q$. 

La probabilité risque-neutre $p$ d'un mouvement à la hausse est calculée pour satisfaire cette condition d'absence d'opportunité d'arbitrage :
$$p = \frac{e^{(r-q)\Delta t} - d}{u - d}$$

La probabilité d'un mouvement à la baisse est simplement $1 - p$.

---

## 4. Algorithme de Valorisation (Backward Induction)

L'évaluation de l'option se fait en deux grandes étapes : la construction des valeurs finales (à maturité), puis la remontée de l'arbre jusqu'à l'instant $t=0$.

### 4.1 Condition Terminale ($t=T$)

Aux nœuds finaux de l'arbre, la valeur de l'option est exactement sa valeur intrinsèque (Payoff). Pour un nœud $j$ (nombre de hausses) sur $N$ pas :
$$S_{N,j} = S_0 \cdot u^j \cdot d^{N-j}$$

La valeur de l'option $V$ à ce nœud est :
- **Call** : $V_{N,j} = \max(S_{N,j} - K, 0)$
- **Put** : $V_{N,j} = \max(K - S_{N,j}, 0)$

### 4.2 Récurrence Arrière ($t < T$)

Pour chaque nœud précédent, la valeur de l'option dépend de son type (Européenne ou Américaine).

#### Option Européenne (Valeur de Continuation)
La valeur de l'option est l'espérance mathématique de sa valeur future sous la probabilité risque-neutre, actualisée au taux sans risque :
$$V_{i,j} = e^{-r \Delta t} [p \cdot V_{i+1, j+1} + (1-p) \cdot V_{i+1, j}]$$

#### Option Américaine (Décision d'Exercice)
À chaque nœud, le détenteur peut choisir d'exercer l'option. La valeur de l'option est donc le maximum entre la valeur d'exercice immédiat et la valeur de continuation espérée :
$$V_{i,j} = \max\left( \text{Payoff}(S_{i,j}), e^{-r \Delta t} [p \cdot V_{i+1, j+1} + (1-p) \cdot V_{i+1, j}] \right)$$

C'est cette simple fonction $\max()$ intégrée dans la boucle de récurrence qui capture la **prime d'exercice anticipé**.

---

## 5. Propriétés et Limites du Modèle

### 5.1 Avantages
- **Exactitude pour les Américaines** : Contrairement à Longstaff-Schwartz qui est une approximation polynomiale générant une borne inférieure, le modèle binomial converge vers le "vrai" prix de l'option américaine lorsque $N \to \infty$.
- **Transparence** : L'arbre génère une grille de prix explicite, permettant d'extraire facilement les Grecs (Delta, Gamma) par différences finies entre les nœuds.

### 5.2 Limites
- **Lenteur (Complexité Spatiale/Temporelle)** : Le nombre de nœuds finaux est $N+1$. Le temps de calcul croît en $O(N^2)$. Un arbre de 10 000 pas est très gourmand.
- **Malédiction de la Dimension** : Inutilisable pour pricer des options sur panier (plusieurs actifs sous-jacents simultanément). Un arbre binaire en dimension $D$ devient un arbre à $2^D$ branches à chaque nœud.
- **Oscillations Numériques** : Si le strike $K$ tombe exactement entre deux nœuds terminaux, le modèle peut subir des oscillations de convergence (un phénomène que les arbres de type Trinomial ou de Leisen-Reimer corrigent).

---

## 6. Extension : Réduction de Dimension via PCA (Analyse en Composantes Principales)

Lors de la valorisation d'options sur paniers d'actifs (Basket Options), la limite dimensionnelle du modèle binomial devient bloquante. L'utilisation de la PCA (Analyse en Composantes Principales) permet de contourner ce problème en réduisant le nombre de variables d'état.

### 6.1 Principe
La PCA transforme un ensemble d'actifs corrélés (via leur matrice de covariance) en un ensemble de facteurs non corrélés appelés **Composantes Principales**. En pratique, sur un panier d'actions, les 3 premiers composants (souvent interprétés comme le facteur "Marché", le facteur "Secteur", etc.) expliquent plus de 90% de la variance totale.

### 6.2 Avantages et Défauts de l'approche PCA

| Avantages | Défauts |
| :--- | :--- |
| **Faisabilité numérique** : Permet de ramener un problème de dimension 50 à un arbre en dimension 1 ou 2 basé sur la composante principale, rendant le calcul possible. | **Perte d'information** : En ignorant les derniers composants, on élimine le risque "idiosyncratique" (le risque spécifique d'une seule entreprise du panier). |
| **Filtrage du Bruit** : En ne gardant que les signaux forts (PC1, PC2), on évite le sur-apprentissage des mouvements stochastiques mineurs. | **Hypothèse de Linéarité** : La PCA repose sur des corrélations linéaires et capture mal les dépendances extrêmes (ex: krach boursier où tout se corrèle à 1). |

---

## 7. Comparatif Méthodologique

| Caractéristique | Black-Scholes | Cox-Ross-Rubinstein | Longstaff-Schwartz |
| :--- | :--- | :--- | :--- |
| **Type mathématique** | Équation différentielle | Arbre (Treillis discret) | Monte Carlo (Stochastique) |
| **Options Américaines** | ❌ Impossible | ✅ Exact (en 1D) | ✅ Approximé (très bon en nD) |
| **Temps de calcul** | Instantané | Lent (dépend de $N^2$) | Lent (dépend des trajectoires $N$) |
| **Facilité sur paniers**| ❌ Impossible | ❌ Trop lourd sans PCA | ✅ Idéal |

---

## 8. Références

1. **Cox, J. C., Ross, S. A., & Rubinstein, M. (1979)**. *Option Pricing: A Simplified Approach*. Journal of Financial Economics.
2. **Hull, J. C.** Options, Futures, and Other Derivatives. Pearson.
3. **Jolliffe, I. T. (2002)**. *Principal Component Analysis*. Springer (pour les fondements théoriques de la réduction de dimension).