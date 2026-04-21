# Réduction de Dimension en Finance : L'Analyse en Composantes Principales (PCA)

## 1. Introduction au Problème

Dans le cadre de la valorisation d'options, le modèle binomial de Cox-Ross-Rubinstein (CRR) est parfait pour modéliser la dynamique d'un seul actif (dimension 1). Cependant, de nombreux produits financiers exotiques (comme les *Basket Options*) dépendent de l'évolution simultanée d'un panier de $N$ actifs.

### 1.1 La Malédiction de la Dimensionnalité
Pour un panier de $N$ actifs, un arbre binomial standard exige la construction de $2^N$ branches à chaque nœud pour capturer toutes les combinaisons de hausses et de baisses possibles. 
- Pour 1 actif : 2 branches.
- Pour 2 actifs : 4 branches.
- Pour 5 actifs : 32 branches par nœud.
- Pour le CAC 40 (40 actifs) : $1.09 \times 10^{12}$ branches par nœud.

Le calcul devient rapidement impossible en termes de mémoire (RAM) et de temps d'exécution. Pour pricer ce type de produit de manière déterministe, il est impératif de réduire la dimension du problème. L'**Analyse en Composantes Principales (PCA)** est la solution de référence en ingénierie quantitative pour contourner ce mur dimensionnel.

---

## 2. Fondements Mathématiques de la PCA

L'objectif de la PCA est de projeter la dynamique multidimensionnelle du panier sur un espace de dimension fortement réduite (généralement 1D ou 2D), tout en conservant la majorité de l'information (la variance totale du système).

### 2.1 Matrice des Rendements et Covariance
Soit un panier de $N$ actifs observés sur $M$ périodes (ex: jours). 
On note $R$ la matrice de taille $(M \times N)$ des rendements logarithmiques :
$$R_{t, i} = \ln\left(\frac{S_{t, i}}{S_{t-1, i}}\right)$$

L'information sur la dépendance (corrélation) et le risque (volatilité) de ces actifs est contenue dans la **matrice de covariance** empirique $\Sigma$ (de taille $N \times N$) :
$$\Sigma = \frac{1}{M-1} R^T R$$
*(En supposant que les rendements ont été préalablement centrés).*

### 2.2 Décomposition en Éléments Propres (Eigendecomposition)
La PCA consiste à trouver des combinaisons linéaires des actifs d'origine qui soient **strictement orthogonales** (non corrélées entre elles) et qui maximisent la variance expliquée. 

Mathématiquement, cela revient à résoudre l'équation aux valeurs propres pour la matrice de covariance $\Sigma$ :
$$\Sigma \mathbf{w}_k = \lambda_k \mathbf{w}_k$$

Où :
- $\mathbf{w}_k$ est le $k$-ème **vecteur propre** (eigenvector) de taille $N \times 1$. En finance, les composantes de ce vecteur s'interprètent comme les *poids* d'un portefeuille synthétique (une Composante Principale).
- $\lambda_k$ est la **valeur propre** (eigenvalue) scalaire associée. Elle représente exactement la variance (le risque) capturée par ce vecteur propre.

---

## 3. Interprétation Financière des Composantes

Une fois les $N$ valeurs propres calculées, on les trie par ordre décroissant : 
$$\lambda_1 \ge \lambda_2 \ge \dots \ge \lambda_N$$

### 3.1 Le Facteur Marché (PC1)
Le premier composant principal (PC1), associé à la plus grande valeur propre $\lambda_1$, est l'axe qui explique la plus grande part des mouvements conjoints du panier. 

Sur le marché des actions, **PC1 est universellement interprété comme le "Facteur Marché"** (ou risque systématique). Il capture la tendance macroéconomique globale qui pousse la majorité des actions dans le même sens lors d'une séance boursière.

Le pourcentage de variance expliquée par ce seul facteur est donné par :
$$\text{Variance Expliquée (PC1)} = \frac{\lambda_1}{\sum_{i=1}^{N} \lambda_i}$$
Pour un panier d'actions du même secteur (ex: la Tech américaine), le PC1 explique couramment entre 70% et 90% de la variance totale.

---

## 4. Application au Pricing d'Options (Le Pont vers CRR)

C'est ici que s'opère la réduction de dimension pour notre pricer. Plutôt que de modéliser $N$ actifs intriqués, nous allons évaluer l'option comme si elle portait sur un actif unique (le "Panier") dont la dynamique est entièrement dictée par le Facteur Marché (PC1).

### 4.1 Volatilité Synthétique du Panier
Puisque $\lambda_1$ représente la variance (souvent journalière) du portefeuille synthétique principal, nous pouvons en déduire la **volatilité annualisée** du panier $\sigma_{PCA}$ :
$$\sigma_{PCA} = \sqrt{\lambda_1 \times 252}$$

### 4.2 Construction de l'Arbre 1D
Cette volatilité synthétique $\sigma_{PCA}$ est ensuite injectée directement dans les équations standard du modèle de Cox-Ross-Rubinstein pour calculer les facteurs de diffusion d'un arbre en **dimension 1** :
$$u = e^{\sigma_{PCA} \sqrt{\Delta t}} \quad \text{et} \quad d = e^{-\sigma_{PCA} \sqrt{\Delta t}}$$

Grâce à cette approximation, le temps de calcul passe de plusieurs années (pour un arbre multidimensionnel) à quelques millisecondes, rendant le pricing des *Basket Options* opérationnel.

---

## 5. Limites et Risques de l'Approche

Bien que cette méthode soit le standard industriel pour l'approximation des paniers, le quant doit garder à l'esprit ses limites structurelles :

1. **Perte du risque idiosyncratique** : En ignorant les composants suivants ($\lambda_2 \dots \lambda_N$), le modèle efface le risque spécifique de chaque entreprise (ex: une fraude comptable isolée). Le prix de l'option calculé via la PCA sera donc structurellement une borne inférieure du risque réel.
2. **Hypothèse de linéarité** : La matrice de covariance ne capture que les dépendances linéaires. Elle échoue à modéliser les dépendances de queue (les krachs boursiers où la corrélation devient soudainement non linéaire).
3. **Instabilité temporelle** : Les vecteurs propres (les poids du panier synthétique) sont calibrés sur l'historique et peuvent changer radicalement de régime (Changement de régime de volatilité), nécessitant une recalibration quotidienne de la PCA.

---

## 6. Références

1. **Jolliffe, I. T. (2002)**. *Principal Component Analysis* (2nd ed.). Springer Series in Statistics.
2. **Avellaneda, M., & Lee, J. H. (2010)**. *Statistical arbitrage in the US equities market*. Quantitative Finance, 10(7), 761-782. (Pour l'interprétation financière des composantes principales).