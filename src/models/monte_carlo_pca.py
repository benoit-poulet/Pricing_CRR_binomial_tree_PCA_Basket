"""
Description : Moteur de pricing de Basket Options par simulation de Monte Carlo Multi-Facteurs.
Utilise les vecteurs propres et valeurs propres de la PCA pour simuler des chocs orthogonaux.
"""

import numpy as np

def monte_carlo_pca_pricing(
    S0_list: np.ndarray,
    eigenvalues: np.ndarray,
    eigenvectors: np.ndarray,
    rate: float,
    div_list: np.ndarray,
    T: float,
    K: float,
    n_simulations: int = 100_000,
    is_put: bool = True
) -> tuple:
    """
    Évalue une Basket Option Européenne via Monte Carlo en utilisant les composantes de la PCA.

    Arguments :
    - S0_list : Array des prix spots initiaux (Généralement des bases 100 pour un indice)
    - eigenvalues : Array des valeurs propres annualisées des K composantes retenues
    - eigenvectors : Matrice des vecteurs propres (Taille: N_actifs x K_composantes)
    - rate : Taux sans risque continu
    - div_list : Array des taux de dividende pour chaque actif
    - T : Maturité en années
    - K : Strike de l'option sur le panier
    - n_simulations : Nombre de trajectoires Monte Carlo
    - is_put : True pour Put, False pour Call

    Retourne :
    - prix : Prix estimé de l'option
    - standard_error : Erreur type de l'estimation (précision du Monte Carlo)
    """
    n_assets = len(S0_list)
    n_components = len(eigenvalues)
    
    # 1. Calcul de la variance spécifique de chaque actif induite par les facteurs retenus
    # sigma_i^2 = Somme( V_{i,k}^2 * lambda_k )
    # C'est la part de variance de l'actif capturée par notre modèle réduit
    implied_variances = np.sum((eigenvectors ** 2) * eigenvalues, axis=1)
    
    # 2. Terme de dérive (Drift) du Mouvement Brownien pour le saut direct à T
    # drift_i = (r - q_i - 0.5 * sigma_i^2) * T
    drifts = (rate - div_list - 0.5 * implied_variances) * T
    
    # Redimensionnement pour le calcul matriciel (n_assets, 1)
    drifts = drifts[:, np.newaxis]
    S0_col = S0_list[:, np.newaxis]
    
    # 3. Simulation des chocs orthogonaux (Les facteurs de la PCA)
    # Z est une matrice (n_components, n_simulations) de lois normales N(0,1)
    Z = np.random.standard_normal((n_components, n_simulations))
    
    # 4. Recombinaison matricielle (Le cœur de la modélisation)
    # On multiplie les chocs Z par les volatilités des facteurs (sqrt(lambda))
    # puis on les projette sur les actifs via les vecteurs propres (V)
    # Matrice des chocs (n_assets, n_simulations)
    scaled_Z = np.diag(np.sqrt(eigenvalues)) @ Z
    shocks = eigenvectors @ scaled_Z * np.sqrt(T)
    
    # 5. Calcul des prix à maturité T (Saut direct exact)
    S_T = S0_col * np.exp(drifts + shocks)
    
    # 6. Évaluation du Panier (Basket) à maturité
    # On suppose un panier équipondéré où le "Spot" de l'indice est la moyenne des cours
    basket_T = np.mean(S_T, axis=0)
    
    # 7. Payoff de l'option
    mult = -1.0 if is_put else 1.0
    payoffs = np.maximum(mult * (basket_T - K), 0.0)
    
    # 8. Actualisation et Statistiques
    discount_factor = np.exp(-rate * T)
    present_values = payoffs * discount_factor
    
    price = np.mean(present_values)
    standard_error = np.std(present_values) / np.sqrt(n_simulations)
    
    return float(price), float(standard_error)
