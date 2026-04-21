"""
Description : Pricer vectorisé basé sur le modèle binomial de Cox-Ross-Rubinstein (CRR).
"""

import numpy as np

def crr_pricing(
    S: float, 
    K: float, 
    vol: float, 
    rate: float, 
    div: float, 
    T: float, 
    n_steps: int, 
    is_put: bool = False, 
    is_american: bool = True
) -> float:
    """
    Évalue une option (Européenne ou Américaine) via un arbre binomial CRR vectorisé.

    Arguments :
    - S : Prix Spot du sous-jacent ou du portefeuille synthétique
    - K : Prix d'exercice (Strike)
    - vol : Volatilité annualisée (σ)
    - rate : Taux sans risque continu (r)
    - div : Taux de dividende continu (q)
    - T : Maturité en années
    - n_steps : Nombre de pas de temps dans l'arbre (N)
    - is_put : True pour un Put, False pour un Call
    - is_american : True pour une option Américaine, False pour une Européenne

    Retourne :
    - Prix de l'option à t=0
    """
    if T <= 0 or n_steps <= 0:
        return max(0.0, (K - S) if is_put else (S - K))

    # 1. Paramètres de l'arbre CRR
    dt = T / n_steps
    u = np.exp(vol * np.sqrt(dt))
    d = 1.0 / u
    
    # Probabilité risque-neutre
    p = (np.exp((rate - div) * dt) - d) / (u - d)
    
    # Sécurité numérique : s'assurer que p est une vraie probabilité [0, 1]
    # Si la volatilité est trop faible par rapport aux taux, la condition d'arbitrage peut sauter
    p = max(0.0, min(1.0, p)) 
    
    discount = np.exp(-rate * dt)
    mult = -1.0 if is_put else 1.0

    # 2. Initialisation des prix du sous-jacent à maturité (t = T)
    # j représente le nombre de mouvements à la hausse (de 0 à n_steps)
    j = np.arange(0, n_steps + 1)
    S_T = S * (u ** j) * (d ** (n_steps - j))

    # 3. Valeurs intrinsèques de l'option à maturité (Payoff terminal)
    V = np.maximum(mult * (S_T - K), 0.0)

    # 4. Récurrence Arrière (Backward Induction vectorisée)
    for i in range(n_steps - 1, -1, -1):
        # Espérance actualisée pour le pas précédent (vectorisation de tout l'étage)
        # V[1:] correspond aux nœuds "Up" et V[:-1] aux nœuds "Down"
        V_cont = discount * (p * V[1:] + (1.0 - p) * V[:-1])
        
        if is_american:
            # Reconstitution vectorisée des prix du sous-jacent à l'étape i
            j_actuel = np.arange(0, i + 1)
            S_i = S * (u ** j_actuel) * (d ** (i - j_actuel))
            
            # Valeur d'exercice immédiat
            V_exercise = np.maximum(mult * (S_i - K), 0.0)
            
            # L'option américaine est le max entre continuation et exercice
            V = np.maximum(V_exercise, V_cont)
        else:
            V = V_cont

    # Le premier élément du tableau final est la valeur à t=0 (nœud racine)
    return float(V[0])
