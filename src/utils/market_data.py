"""
Description : Pipeline de données de marché. 
Inclut l'extraction yfinance, la courbe des taux OAT, et la réduction de dimension PCA pour les paniers d'actifs.
"""

import yfinance as yf
import numpy as np
import pandas as pd
from typing import Tuple, List

def fetch_single_asset(ticker: str, period: str = "1y") -> Tuple[float, float, float]:
    """
    Récupère les données de marché pour un actif unique.
    
    Retourne :
    - spot : Dernier prix de clôture
    - vol : Volatilité historique annualisée
    - q : Taux de dividende continu
    """
    print(f"Téléchargement des données pour {ticker}...")
    stock = yf.Ticker(ticker)
    
    try:
        hist = stock.history(period=period)
        if hist.empty:
            raise ValueError(f"Aucune donnée trouvée pour {ticker}.")
            
        # Calcul de la volatilité historique
        log_returns = np.log(hist['Close'] / hist['Close'].shift(1)).dropna()
        vol = log_returns.std() * np.sqrt(252)
        spot = float(hist['Close'].iloc[-1])
        
    except Exception as e:
        print(f"Erreur sur {ticker} : {e}. Utilisation de valeurs par défaut.")
        return 100.0, 0.20, 0.0

    # Calcul du taux de dividende
    div = stock.info.get('dividendRate', None)
    if div is not None and spot > 0:
        q = div / spot
    else:
        q = 0.0

    # Normalisation au cas où l'API renvoie un pourcentage > 1
    if q > 1: 
        q = q / 100.0 
    
    print(f"{ticker} -> Spot : {spot:.2f} € | Vol : {vol*100:.2f}% | Div : {q*100:.2f}%")
    return spot, vol, q


def fetch_basket_pca(tickers: List[str], period: str = "1y") -> Tuple[float, float, float, float]:
    """
    Applique une Analyse en Composantes Principales (PCA) sur un panier d'actifs.
    Objectif : Extraire le Facteur Principal (PC1) pour réduire la dimensionnalité à 1D.
    
    Retourne :
    - spot_synthetique : Toujours 100.0 (Base 100 pour l'indice synthétique)
    - vol_pca : Volatilité annualisée du Facteur Principal
    - variance_expliquee : % de variance capturé par PC1
    - q_moyen : Taux de dividende moyen du panier
    """
    print(f"\nLancement de l'algorithme PCA sur le panier : {tickers}")
    
    # 1. Extraction synchronisée des prix de clôture
    data = yf.download(tickers, period=period, progress=False, auto_adjust=False)['Close']
    data = data.dropna()
    
    # 2. Calcul de la matrice des rendements logarithmiques journaliers
    log_returns = np.log(data / data.shift(1)).dropna()
    
    # 3. Matrice de Covariance (La structure de dépendance du panier)
    cov_matrix = log_returns.cov().values
    
    # 4. Décomposition en éléments propres (Eigendecomposition)
    eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)
    max_eigenvalue = eigenvalues[-1]
    
    # 5. Calcul de la Volatilité Synthétique (Correction Financière)
    # On extrait le vecteur propre principal (les "poids" mathématiques)
    pc1_vector = eigenvectors[:, -1]
    
    # Normalisation financière : on force la somme des poids du portefeuille à faire 1 (100%)
    weights = pc1_vector / np.sum(pc1_vector)
    
    # Variance du portefeuille synthétique : w.T * Cov * w
    portfolio_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
    
    # Volatilité annualisée
    vol_pca = np.sqrt(portfolio_variance) * np.sqrt(252)
    
    # Métrique de qualité
    variance_expliquee = max_eigenvalue / np.sum(eigenvalues)
    
    # 6. Extraction du dividende moyen (simplification pour le pricing)
    divs = []
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        d = stock.info.get('dividendRate', None)
        s = float(data[ticker].iloc[-1])
        if d is not None and s > 0:
            divs.append(d / s)
        else:
            divs.append(0.0)
    q_moyen = np.mean([d / 100.0 if d > 1 else d for d in divs])

    print(f"PCA Terminée ! PC1 capture {variance_expliquee*100:.2f}% de la variance totale du panier.")
    print(f"   ▶ Volatilité du Panier Synthétique : {vol_pca*100:.2f}%")
    print(f"   ▶ Dividende moyen estimé : {q_moyen*100:.2f}%")
    
    # On renvoie 100.0 comme Spot synthétique de base.
    return 100.0, vol_pca, variance_expliquee, q_moyen

def fetch_multi_pca(tickers: List[str], period: str = "1y", n_components: int = 3) -> Tuple[np.ndarray, np.ndarray, np.ndarray, float, np.ndarray]:
    """
    Applique une PCA et extrait les K premières composantes principales pour le pricing Multi-Facteurs.
    
    Arguments:
    - tickers : Liste des actions du panier.
    - period : Historique (ex: "1y").
    - n_components : Nombre de facteurs à retenir (K).
    
    Retourne :
    - spots : Array des prix actuels des actions.
    - ann_eigenvalues : Array des valeurs propres (variances) annualisées des K facteurs.
    - top_eigenvectors : Matrice (N_actifs x K_facteurs) des vecteurs propres bruts.
    - variance_expliquee : % de variance totale capturée par les K facteurs.
    - div_list : Array des taux de dividende des actions.
    """
    print(f"\nLancement de la PCA Multi-Facteurs ({n_components} composantes) sur : {tickers}")
    
    # 1. Extraction des données
    data = yf.download(tickers, period=period, progress=False, auto_adjust=False)['Close']
    data = data.dropna()
    
    # Spots initiaux
    spots = data.iloc[-1].values
    
    # 2. Matrice de Covariance des rendements journaliers
    log_returns = np.log(data / data.shift(1)).dropna()
    cov_matrix = log_returns.cov().values
    
    # 3. Décomposition spectrale (Eigendecomposition)
    eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)
    
    # np.linalg.eigh trie du plus petit au plus grand. On inverse pour avoir PC1 en premier.
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]
    
    # 4. Sélection des K premières composantes
    # On s'assure de ne pas demander plus de composants qu'il n'y a d'actifs
    k = min(n_components, len(tickers))
    top_eigenvalues = eigenvalues[:k]
    top_eigenvectors = eigenvectors[:, :k]
    
    # Annualisation de la variance (Les valeurs propres sont des variances journalières)
    ann_eigenvalues = top_eigenvalues * 252
    
    # Qualité du modèle
    variance_expliquee = np.sum(top_eigenvalues) / np.sum(eigenvalues)
    
    # 5. Extraction des dividendes vectorisés
    divs = []
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        d = stock.info.get('dividendRate', None)
        s = float(data[ticker].iloc[-1])
        divs.append(d / s if d is not None and s > 0 else 0.0)
    
    div_list = np.array([d / 100.0 if d > 1 else d for d in divs])

    print(f"PCA Multi-Facteurs Terminée !")
    print(f"   ▶ {k} composants capturent {variance_expliquee*100:.2f}% de la variance totale.")
    for i in range(k):
        # Volatilité annualisée du facteur = racine(variance annualisée)
        print(f"   ▶ PC{i+1} Volatilité implicite : {np.sqrt(ann_eigenvalues[i])*100:.2f}%")
        
    return spots, ann_eigenvalues, top_eigenvectors, variance_expliquee, div_list

def get_oat_rate(maturity_years: float) -> float:
    """
    Renvoie le taux d'intérêt sans risque (OAT française) en fonction de la maturité.
    """
    if maturity_years <= 1.0: return 0.0212
    elif maturity_years <= 2.0: return 0.0221
    elif maturity_years <= 3.0: return 0.0238
    elif maturity_years <= 5.0: return 0.0268
    elif maturity_years <= 7.0: return 0.0301
    elif maturity_years <= 10.0: return 0.0341
    elif maturity_years <= 15.0: return 0.0382
    else: return 0.0410

