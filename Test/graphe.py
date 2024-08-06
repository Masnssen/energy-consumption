import matplotlib.pyplot as plt

# Données
time = ["0:00", "1:00", "2:00", "3:00", "4:00", "5:00", "6:00", "7:00", "8:00", "9:00", 
        "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", 
        "19:00", "20:00", "21:00", "22:00", "23:00"]
consumption = [0.095, 0.035, 0.008, 0.007, 0.003, 0.003, 0.004, 0.004, 0.004, 0.004, 
               0.026, 0.047, 0.026, 0.020, 0.020, 0.018, 0.018, 0.018, 0.018, 0.019, 
               0.018, 0.018, 0.018, 0.040]

# Créer le graphique à barres
plt.figure(figsize=(10, 6))
plt.bar(time, consumption, color='blue', width=0.8)

# Ajouter les titres et les étiquettes
plt.title('Consommation d\'énergie en KWh')
plt.xlabel('Heure')
plt.ylabel('Consommation (KW)')
plt.grid(axis='y')

# Tourner les étiquettes de l'axe des x pour une meilleure lisibilité
plt.xticks(rotation=45)

# Afficher le graphique
plt.tight_layout()
plt.show()
