import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configuration de la page
st.set_page_config(
    page_title="Simulateur d'investissement en crypto",
    layout="wide"
)

# Titre de l'application
st.title("Simulateur d'investissement en crypto")

# Fonctions utiles
def get_crypto_price_history(crypto_id, days):
    """Récupère l'historique des prix d'une crypto via l'API CoinGecko"""
    # Pour la version pro, décommentez ces lignes et ajoutez votre clé
    # api_key = st.secrets["COINGECKO_API_KEY"]
    # headers = {"X-Cg-Pro-Api-Key": api_key}
    
    url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart"
    params = {
        "vs_currency": "eur",
        "days": days,
        "interval": "daily"
    }
    # Pour la version pro, ajoutez headers=headers dans la requête
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        prices = pd.DataFrame(data["prices"], columns=["date", "price"])
        prices["date"] = pd.to_datetime(prices["date"], unit="ms")
        return prices
    else:
        st.error("Erreur lors de la récupération des données")
        return None

# Interface utilisateur
col1, col2 = st.columns(2)

with col1:
    # Sélection de la crypto
    crypto_list = {
        "Bitcoin": "bitcoin",
        "Ethereum": "ethereum",
        "Solana": "solana"
    }
    crypto = st.selectbox("Sélectionnez une crypto-monnaie", options=list(crypto_list.keys()))
    
    # Paramètres d'investissement
    epargne_mensuelle = st.number_input("Épargne mensuelle (€)", min_value=0, value=100)
    horizon = st.number_input("Horizon de placement (mois)", min_value=1, max_value=12, value=6)

# Calcul et affichage
if st.button("Simuler l'investissement"):
    # Récupération des données historiques
    crypto_id = crypto_list[crypto]
    days = horizon * 30  # Conversion des mois en jours
    df_prices = get_crypto_price_history(crypto_id, days)
    
    if df_prices is not None:
        # Création des données de simulation
        dates = pd.date_range(start=datetime.now(), periods=len(df_prices), freq='D')
        montant_investi = np.arange(len(df_prices)) // 30 * epargne_mensuelle
        
        # Simulation de la valeur du portefeuille
        prix_initial = df_prices['price'].iloc[0]  # Prix au début de la période
        variation_prix = df_prices['price'] / prix_initial
        valeur_portefeuille = montant_investi * variation_prix

        # Création du graphique
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Courbe du montant investi
        fig.add_trace(
            go.Scatter(x=dates, y=montant_investi, name="Montant investi"),
            secondary_y=False
        )

        # Courbe de la valeur du portefeuille
        fig.add_trace(
            go.Scatter(x=dates, y=valeur_portefeuille, name="Valeur du portefeuille"),
            secondary_y=False
        )

        # Mise en forme du graphique
        fig.update_layout(
            title=f"Simulation d'investissement en {crypto}",
            xaxis_title="Date",
            yaxis_title="Valeur (€)"
        )

        # Affichage du graphique
        st.plotly_chart(fig, use_container_width=True)
        
        # Affichage des métriques
        col1, col2, col3, col4 = st.columns(4)
        
        # Montant total investi
        montant_total = montant_investi.iloc[-1] if isinstance(montant_investi, pd.Series) else montant_investi[-1]
        with col1:
            st.metric(
                label="Montant total investi",
                value=f"{montant_total:.2f} €"
            )
        
        # Valeur finale du portefeuille
        valeur_finale = valeur_portefeuille.iloc[-1] if isinstance(valeur_portefeuille, pd.Series) else valeur_portefeuille[-1]
        with col2:
            st.metric(
                label="Valeur finale du portefeuille",
                value=f"{valeur_finale:.2f} €"
            )
        
        # Plus/moins-value
        plus_moins_value = valeur_finale - montant_total
        with col3:
            st.metric(
                label="Plus/moins-value",
                value=f"{plus_moins_value:.2f} €",
                delta=f"{(plus_moins_value/montant_total*100):.1f}%"
            )
        
        # Performance du crypto sur la période
        perf_crypto = (df_prices['price'].iloc[-1] / df_prices['price'].iloc[0] - 1) * 100
        with col4:
            st.metric(
                label=f"Performance {crypto}",
                value=f"{perf_crypto:.1f}%",
                delta=f"{perf_crypto:.1f}%"
            )
