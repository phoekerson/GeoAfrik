import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import folium
import webbrowser
import os
import json
from datetime import datetime, timedelta
import threading
import time
from PIL import Image, ImageTk
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class SuruwaApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SURUWA - Système de Prévention des Inondations")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f0f8ff")
        
        # Configuration des styles
        self.setup_styles()
        
        # Variables
        self.API_KEY = "bcfbca71e682918b20ab37cb390f581a"
        self.current_alerts = []
        self.weather_history = []
        self.user_preferences = {}
        
        # Base de données
        self.init_database()
        
        # Interface utilisateur
        self.create_interface()
        
        # Démarrage du système de monitoring
        self.start_monitoring()
        
    def setup_styles(self):
        """Configuration des styles visuels"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Style pour les boutons
        style.configure('Action.TButton', 
                       font=('Arial', 10, 'bold'),
                       padding=10)
        
        # Style pour les labels de titre
        style.configure('Title.TLabel',
                       font=('Arial', 16, 'bold'),
                       background='#f0f8ff')
        
        # Style pour les alertes
        style.configure('Alert.TLabel',
                       font=('Arial', 12, 'bold'),
                       foreground='red',
                       background='#fff0f0')
        
    def init_database(self):
        """Initialisation de la base de données SQLite"""
        self.conn = sqlite3.connect('suruwa.db')
        cursor = self.conn.cursor()
        
        # Table pour l'historique météo
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weather_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT,
                temperature REAL,
                humidity REAL,
                precipitation REAL,
                risk_level TEXT,
                timestamp DATETIME
            )
        ''')
        
        # Table pour les alertes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                zone TEXT,
                message TEXT,
                risk_level TEXT,
                timestamp DATETIME,
                status TEXT
            )
        ''')
        
        self.conn.commit()
        
    def create_interface(self):
        """Création de l'interface utilisateur"""
        # Menu principal
        self.create_menu()
        
        # Notebook avec onglets
        self.notebook = ttk.Notebook(self.root)
        
        # Onglets
        self.create_citizen_tab()
        self.create_admin_tab()
        self.create_monitoring_tab()
        self.create_analytics_tab()
        self.create_settings_tab()
        
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Barre de statut
        self.create_status_bar()
        
    def create_menu(self):
        """Création du menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Fichier
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Exporter données", command=self.export_data)
        file_menu.add_command(label="Importer données", command=self.import_data)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.root.quit)
        
        # Menu Aide
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aide", menu=help_menu)
        help_menu.add_command(label="Guide d'utilisation", command=self.show_help)
        help_menu.add_command(label="À propos", command=self.show_about)
        
    def create_citizen_tab(self):
        """Onglet Espace Citoyen"""
        self.citizen_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.citizen_frame, text="👥 Espace Citoyen")
        
        # Titre avec logo
        title_frame = tk.Frame(self.citizen_frame, bg="#2c5aa0")
        title_frame.pack(fill='x', pady=(0, 10))
        
        title_label = tk.Label(title_frame, 
                              text="🌊 SURUWA - Prévention des Inondations",
                              font=('Arial', 20, 'bold'),
                              fg='white', bg="#2c5aa0")
        title_label.pack(pady=15)
        
        # Frame principal
        main_frame = tk.Frame(self.citizen_frame)
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Section recherche
        search_frame = tk.LabelFrame(main_frame, text="📍 Recherche de Localité", 
                                   font=('Arial', 12, 'bold'), padx=10, pady=10)
        search_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(search_frame, text="Entrez votre ville ou coordonnées :").pack(anchor='w')
        
        search_input_frame = tk.Frame(search_frame)
        search_input_frame.pack(fill='x', pady=5)
        
        self.localite_entry = tk.Entry(search_input_frame, font=('Arial', 12), width=30)
        self.localite_entry.pack(side='left', padx=(0, 10))
        
        search_btn = tk.Button(search_input_frame, text="🔎 Analyser",
                              command=self.analyser_risque,
                              bg="#4CAF50", fg="white", font=('Arial', 10, 'bold'))
        search_btn.pack(side='left', padx=(0, 10))
        
        gps_btn = tk.Button(search_input_frame, text="📍 GPS",
                           command=self.get_gps_location,
                           bg="#2196F3", fg="white", font=('Arial', 10, 'bold'))
        gps_btn.pack(side='left')
        
        # Section résultats
        results_frame = tk.LabelFrame(main_frame, text="📊 Analyse des Risques", 
                                    font=('Arial', 12, 'bold'), padx=10, pady=10)
        results_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Informations météo
        weather_frame = tk.Frame(results_frame)
        weather_frame.pack(fill='x', pady=(0, 10))
        
        self.weather_label = tk.Label(weather_frame, text="Aucune donnée disponible",
                                     font=('Arial', 11), justify='left')
        self.weather_label.pack(anchor='w')
        
        # Indicateur de risque visuel
        risk_frame = tk.Frame(results_frame)
        risk_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(risk_frame, text="Niveau de Risque :", font=('Arial', 12, 'bold')).pack(side='left')
        
        self.risk_indicator = tk.Label(risk_frame, text="●", font=('Arial', 40), fg="gray")
        self.risk_indicator.pack(side='left', padx=10)
        
        self.risk_text = tk.Label(risk_frame, text="Non évalué", font=('Arial', 12, 'bold'))
        self.risk_text.pack(side='left', padx=10)
        
        # Boutons d'action
        action_frame = tk.Frame(results_frame)
        action_frame.pack(fill='x', pady=10)
        
        map_btn = tk.Button(action_frame, text="🗺️ Voir Carte",
                           command=self.show_map,
                           bg="#FF9800", fg="white", font=('Arial', 10, 'bold'))
        map_btn.pack(side='left', padx=(0, 10))
        
        history_btn = tk.Button(action_frame, text="📈 Historique",
                               command=self.show_history,
                               bg="#9C27B0", fg="white", font=('Arial', 10, 'bold'))
        history_btn.pack(side='left', padx=(0, 10))
        
        alert_btn = tk.Button(action_frame, text="⚠️ S'abonner aux alertes",
                             command=self.subscribe_alerts,
                             bg="#F44336", fg="white", font=('Arial', 10, 'bold'))
        alert_btn.pack(side='left')
        
        # Section conseils
        tips_frame = tk.LabelFrame(main_frame, text="💡 Conseils de Prévention", 
                                 font=('Arial', 12, 'bold'), padx=10, pady=10)
        tips_frame.pack(fill='x')
        
        self.tips_text = tk.Text(tips_frame, height=4, wrap='word', font=('Arial', 10))
        self.tips_text.pack(fill='x')
        self.tips_text.insert('1.0', "Conseils de sécurité adaptés à votre région apparaîtront ici après analyse...")
        
    def create_admin_tab(self):
        """Onglet Administrateur"""
        self.admin_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.admin_frame, text="🛠️ Administration")
        
        # Authentification
        auth_frame = tk.LabelFrame(self.admin_frame, text="🔐 Authentification", 
                                 font=('Arial', 12, 'bold'), padx=10, pady=10)
        auth_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(auth_frame, text="Nom d'utilisateur :").grid(row=0, column=0, sticky='w', pady=5)
        self.username_entry = tk.Entry(auth_frame, font=('Arial', 11))
        self.username_entry.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(auth_frame, text="Mot de passe :").grid(row=1, column=0, sticky='w', pady=5)
        self.password_entry = tk.Entry(auth_frame, show="*", font=('Arial', 11))
        self.password_entry.grid(row=1, column=1, padx=10, pady=5)
        
        login_btn = tk.Button(auth_frame, text="🔑 Se connecter",
                             command=self.admin_login,
                             bg="#4CAF50", fg="white", font=('Arial', 10, 'bold'))
        login_btn.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Section alerte (désactivée par défaut)
        self.alert_frame = tk.LabelFrame(self.admin_frame, text="⚠️ Gestion des Alertes", 
                                       font=('Arial', 12, 'bold'), padx=10, pady=10)
        self.alert_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Désactiver par défaut
        for widget in self.alert_frame.winfo_children():
            widget.configure(state='disabled')
        
        # Interface d'alerte
        tk.Label(self.alert_frame, text="Zone à alerter :").grid(row=0, column=0, sticky='w', pady=5)
        self.zone_entry = tk.Entry(self.alert_frame, font=('Arial', 11), width=30)
        self.zone_entry.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(self.alert_frame, text="Niveau de risque :").grid(row=1, column=0, sticky='w', pady=5)
        self.admin_risk = tk.StringVar(value="Faible")
        risk_combo = ttk.Combobox(self.alert_frame, textvariable=self.admin_risk, 
                                 values=["Faible", "Modéré", "Élevé", "Critique"])
        risk_combo.grid(row=1, column=1, padx=10, pady=5)
        
        tk.Label(self.alert_frame, text="Message d'alerte :").grid(row=2, column=0, sticky='nw', pady=5)
        self.message_text = tk.Text(self.alert_frame, width=50, height=5, font=('Arial', 10))
        self.message_text.grid(row=2, column=1, padx=10, pady=5)
        
        # Boutons d'action admin
        admin_buttons = tk.Frame(self.alert_frame)
        admin_buttons.grid(row=3, column=0, columnspan=2, pady=15)
        
        send_btn = tk.Button(admin_buttons, text="📤 Envoyer Alerte",
                            command=self.send_alert,
                            bg="#F44336", fg="white", font=('Arial', 10, 'bold'))
        send_btn.pack(side='left', padx=10)
        
        preview_btn = tk.Button(admin_buttons, text="👁️ Aperçu",
                               command=self.preview_alert,
                               bg="#2196F3", fg="white", font=('Arial', 10, 'bold'))
        preview_btn.pack(side='left', padx=10)
        
        # Liste des alertes actives
        alerts_list_frame = tk.LabelFrame(self.admin_frame, text="📋 Alertes Actives", 
                                        font=('Arial', 12, 'bold'), padx=10, pady=10)
        alerts_list_frame.pack(fill='both', expand=True, padx=20, pady=(0, 10))
        
        self.alerts_listbox = tk.Listbox(alerts_list_frame, font=('Arial', 10))
        self.alerts_listbox.pack(fill='both', expand=True)
        
    def create_monitoring_tab(self):
        """Onglet Monitoring en temps réel"""
        self.monitoring_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.monitoring_frame, text="📡 Monitoring")
        
        # Contrôles
        control_frame = tk.Frame(self.monitoring_frame)
        control_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(control_frame, text="Surveillance en temps réel", 
                font=('Arial', 16, 'bold')).pack(anchor='w')
        
        self.monitoring_status = tk.Label(control_frame, text="● Actif", 
                                        fg="green", font=('Arial', 12, 'bold'))
        self.monitoring_status.pack(anchor='w')
        
        # Zones surveillées
        zones_frame = tk.LabelFrame(self.monitoring_frame, text="🎯 Zones Surveillées", 
                                  font=('Arial', 12, 'bold'), padx=10, pady=10)
        zones_frame.pack(fill='both', expand=True, padx=20, pady=(0, 10))
        
        # Treeview pour les zones
        columns = ('Zone', 'Risque', 'Dernière MAJ', 'Statut')
        self.zones_tree = ttk.Treeview(zones_frame, columns=columns, show='headings')
        
        for col in columns:
            self.zones_tree.heading(col, text=col)
            self.zones_tree.column(col, width=150)
        
        self.zones_tree.pack(fill='both', expand=True)
        
        # Boutons de contrôle
        control_buttons = tk.Frame(self.monitoring_frame)
        control_buttons.pack(fill='x', padx=20, pady=10)
        
        add_zone_btn = tk.Button(control_buttons, text="➕ Ajouter Zone",
                               command=self.add_monitoring_zone,
                               bg="#4CAF50", fg="white", font=('Arial', 10, 'bold'))
        add_zone_btn.pack(side='left', padx=10)
        
        remove_zone_btn = tk.Button(control_buttons, text="➖ Supprimer Zone",
                                  command=self.remove_monitoring_zone,
                                  bg="#F44336", fg="white", font=('Arial', 10, 'bold'))
        remove_zone_btn.pack(side='left', padx=10)
        
    def create_analytics_tab(self):
        """Onglet Analytiques"""
        self.analytics_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.analytics_frame, text="📊 Analytiques")
        
        # Frame pour les graphiques
        graph_frame = tk.Frame(self.analytics_frame)
        graph_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Graphique des tendances
        self.create_analytics_chart(graph_frame)
        
    def create_settings_tab(self):
        """Onglet Paramètres"""
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="⚙️ Paramètres")
        
        # Paramètres généraux
        general_frame = tk.LabelFrame(self.settings_frame, text="🔧 Paramètres Généraux", 
                                    font=('Arial', 12, 'bold'), padx=10, pady=10)
        general_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(general_frame, text="Langue :").grid(row=0, column=0, sticky='w', pady=5)
        self.language_var = tk.StringVar(value="Français")
        language_combo = ttk.Combobox(general_frame, textvariable=self.language_var,
                                    values=["Français", "English", "العربية"])
        language_combo.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(general_frame, text="Notifications :").grid(row=1, column=0, sticky='w', pady=5)
        self.notifications_var = tk.BooleanVar(value=True)
        notifications_check = tk.Checkbutton(general_frame, variable=self.notifications_var,
                                           text="Activer les notifications")
        notifications_check.grid(row=1, column=1, padx=10, pady=5, sticky='w')
        
        # Seuils d'alerte
        thresholds_frame = tk.LabelFrame(self.settings_frame, text="🎚️ Seuils d'Alerte", 
                                       font=('Arial', 12, 'bold'), padx=10, pady=10)
        thresholds_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(thresholds_frame, text="Précipitations (mm/h) :").grid(row=0, column=0, sticky='w', pady=5)
        self.precip_threshold = tk.Scale(thresholds_frame, from_=0, to=100, orient='horizontal')
        self.precip_threshold.set(20)
        self.precip_threshold.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(thresholds_frame, text="Humidité (%) :").grid(row=1, column=0, sticky='w', pady=5)
        self.humidity_threshold = tk.Scale(thresholds_frame, from_=0, to=100, orient='horizontal')
        self.humidity_threshold.set(80)
        self.humidity_threshold.grid(row=1, column=1, padx=10, pady=5)
        
    def create_status_bar(self):
        """Barre de statut"""
        self.status_bar = tk.Label(self.root, 
                                  text="© 2025 SuruwaSoft - Système de Prévention des Inondations | Statut: Prêt",
                                  bd=1, relief=tk.SUNKEN, anchor=tk.W,
                                  font=('Arial', 9), bg='lightgray')
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def create_analytics_chart(self, parent):
        """Création du graphique d'analyse"""
        # Données exemple
        dates = [datetime.now() - timedelta(days=i) for i in range(30, 0, -1)]
        risks = np.random.choice(['Faible', 'Modéré', 'Élevé'], 30)
        
        fig, ax = plt.subplots(figsize=(8, 4))
        
        # Conversion des risques en valeurs numériques
        risk_values = [1 if r == 'Faible' else 2 if r == 'Modéré' else 3 for r in risks]
        
        ax.plot(dates, risk_values, marker='o', linewidth=2, markersize=4)
        ax.set_ylim(0, 4)
        ax.set_ylabel('Niveau de Risque')
        ax.set_title('Évolution du Risque d\'Inondation (30 derniers jours)')
        ax.grid(True, alpha=0.3)
        
        # Labels pour l'axe Y
        ax.set_yticks([1, 2, 3])
        ax.set_yticklabels(['Faible', 'Modéré', 'Élevé'])
        
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
        
    def get_weather_with_forecast(self, city):
        """Récupération météo avec prévisions"""
        try:
            # Météo actuelle
            current_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.API_KEY}&units=metric"
            current_res = requests.get(current_url).json()
            
            if current_res.get("cod") != 200:
                raise Exception("Ville introuvable")
            
            # Prévisions
            forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={self.API_KEY}&units=metric"
            forecast_res = requests.get(forecast_url).json()
            
            current_data = {
                'temp': current_res["main"]["temp"],
                'humidity': current_res["main"]["humidity"],
                'condition': current_res["weather"][0]["description"],
                'pressure': current_res["main"]["pressure"],
                'wind_speed': current_res["wind"]["speed"],
                'lat': current_res["coord"]["lat"],
                'lon': current_res["coord"]["lon"]
            }
            
            # Analyse des prévisions pour les 24h
            forecast_data = []
            for item in forecast_res["list"][:8]:  # 8 prévisions = 24h
                forecast_data.append({
                    'time': item["dt_txt"],
                    'temp': item["main"]["temp"],
                    'humidity': item["main"]["humidity"],
                    'precipitation': item.get("rain", {}).get("3h", 0)
                })
            
            return current_data, forecast_data
            
        except Exception as e:
            return None, str(e)
            
    def calculate_flood_risk(self, current_data, forecast_data):
        """Calcul du risque d'inondation basé sur l'IA"""
        if not current_data or not forecast_data:
            return "Indéterminé", "Données insuffisantes"
        
        risk_score = 0
        factors = []
        
        # Facteur humidité
        if current_data['humidity'] > 85:
            risk_score += 3
            factors.append("Humidité très élevée")
        elif current_data['humidity'] > 70:
            risk_score += 2
            factors.append("Humidité élevée")
        
        # Facteur précipitations prévues
        total_precip = sum(f['precipitation'] for f in forecast_data)
        if total_precip > 50:
            risk_score += 4
            factors.append("Fortes précipitations prévues")
        elif total_precip > 20:
            risk_score += 2
            factors.append("Précipitations modérées prévues")
        
        # Facteur pression atmosphérique
        if current_data['pressure'] < 1000:
            risk_score += 2
            factors.append("Basse pression")
        
        # Facteur vent
        if current_data['wind_speed'] > 15:
            risk_score += 1
            factors.append("Vents forts")
        
        # Détermination du niveau de risque
        if risk_score >= 7:
            return "Critique", factors
        elif risk_score >= 5:
            return "Élevé", factors
        elif risk_score >= 3:
            return "Modéré", factors
        else:
            return "Faible", factors
            
    def analyser_risque(self):
        """Analyse complète du risque"""
        city = self.localite_entry.get().strip()
        if not city:
            messagebox.showerror("Erreur", "Veuillez entrer une localité.")
            return
        
        self.update_status("Analyse en cours...")
        
        # Thread pour éviter le blocage de l'interface
        threading.Thread(target=self._analyze_risk_thread, args=(city,), daemon=True).start()
        
    def _analyze_risk_thread(self, city):
        """Thread d'analyse du risque"""
        current_data, forecast_data = self.get_weather_with_forecast(city)
        
        if isinstance(forecast_data, str):  # Erreur
            self.root.after(0, lambda: messagebox.showerror("Erreur", forecast_data))
            self.root.after(0, lambda: self.update_status("Prêt"))
            return
        
        # Calcul du risque
        risk_level, factors = self.calculate_flood_risk(current_data, forecast_data)
        
        # Mise à jour de l'interface
        self.root.after(0, lambda: self._update_risk_display(current_data, risk_level, factors))
        
        # Sauvegarde en base
        self.save_weather_data(city, current_data, risk_level)
        
        self.root.after(0, lambda: self.update_status(f"Analyse terminée pour {city}"))
        
    def _update_risk_display(self, current_data, risk_level, factors):
        """Mise à jour de l'affichage du risque"""
        # Informations météo
        weather_info = f"""🌡️ Température: {current_data['temp']:.1f}°C
💧 Humidité: {current_data['humidity']}%
🌥️ Condition: {current_data['condition'].capitalize()}
🌪️ Vent: {current_data['wind_speed']} m/s
📊 Pression: {current_data['pressure']} hPa"""
        
        self.weather_label.config(text=weather_info)
        
        # Indicateur de risque
        colors = {"Faible": "green", "Modéré": "orange", "Élevé": "red", "Critique": "darkred"}
        self.risk_indicator.config(fg=colors.get(risk_level, "gray"))
        self.risk_text.config(text=risk_level, fg=colors.get(risk_level, "gray"))
        
        # Conseils adaptés
        tips = self.get_safety_tips(risk_level, factors)
        self.tips_text.delete('1.0', tk.END)
        self.tips_text.insert('1.0', tips)
        
        # Stockage pour la carte
        self.current_location = (current_data['lat'], current_data['lon'])
        self.current_city = self.localite_entry.get()
        
    def get_safety_tips(self, risk_level, factors):
        """Génération de conseils de sécurité"""
        base_tips = "🔰 CONSEILS DE SÉCURITÉ:\n\n"
        
        if risk_level == "Faible":
            tips = base_tips + "• Restez informé des conditions météo\n• Vérifiez vos systèmes d'évacuation\n• Maintenez vos provisions d'urgence"
        elif risk_level == "Modéré":
            tips = base_tips + "• Surveillez les bulletins météo régulièrement\n• Préparez un kit d'urgence\n• Évitez les zones inondables\n• Informez votre famille"
        elif risk_level == "Élevé":
            tips = base_tips + "• ATTENTION: Risque d'inondation élevé\n• Évitez les déplacements non essentiels\n• Éloignez-vous des cours d'eau\n• Préparez-vous à évacuer si nécessaire"
        else:  # Critique
            tips = base_tips + "🚨 ALERTE MAXIMALE:\n• Évacuez immédiatement les zones à risque\n• Contactez les services d'urgence\n• Suivez les consignes des autorités\n• Ne traversez JAMAIS une route inondée"
        
        # Ajout des facteurs spécifiques
        if factors:
            tips += f"\n\n⚠️ FACTEURS DE RISQUE DÉTECTÉS:\n• " + "\n• ".join(factors)
        
        return tips
        
    def show_map(self):
        """Affichage de la carte interactive"""
        if not hasattr(self, 'current_location'):
            messagebox.showwarning("Attention", "Effectuez d'abord une analyse de risque.")
            return
        
        lat, lon = self.current_location
        
        # Création de la carte avec couches multiples
        m = folium.Map(location=[lat, lon], zoom_start=10)
        
        # Marqueur principal
        folium.Marker(
            [lat, lon],
            popup=f"📍 {self.current_city}\n🌊 Risque: {self.risk_text.cget('text')}",
            tooltip=f"Zone analysée: {self.current_city}",
            icon=folium.Icon(color='red' if self.risk_text.cget('text') in ['Élevé', 'Critique'] else 'green')
        ).add_to(m)
        
        # Couche des zones inondables (simulation)
        self.add_flood_zones(m, lat, lon)
        
        # Couche des points d'évacuation
        self.add_evacuation_points(m, lat, lon)
        
        # Sauvegarde et ouverture
        map_path = os.path.join(os.getcwd(), "suruwa_map.html")
        m.save(map_path)
        webbrowser.open(f"file://{map_path}")
        
    def add_flood_zones(self, map_obj, lat, lon):
        """Ajout des zones inondables à la carte"""
        # Simulation de zones inondables autour de la position
        import random
        
        for i in range(3):
            # Génération de coordonnées aléatoires dans un rayon
            offset_lat = random.uniform(-0.01, 0.01)
            offset_lon = random.uniform(-0.01, 0.01)
            
            zone_coords = [
                [lat + offset_lat, lon + offset_lon],
                [lat + offset_lat + 0.005, lon + offset_lon],
                [lat + offset_lat + 0.005, lon + offset_lon + 0.005],
                [lat + offset_lat, lon + offset_lon + 0.005]
            ]
            
            folium.Polygon(
                zone_coords,
                color='blue',
                fill=True,
                fillColor='lightblue',
                fillOpacity=0.3,
                popup=f"Zone inondable #{i+1}",
                tooltip="Zone à risque d'inondation"
            ).add_to(map_obj)
            
    def add_evacuation_points(self, map_obj, lat, lon):
        """Ajout des points d'évacuation"""
        evacuation_points = [
            (lat + 0.005, lon + 0.005, "École Primaire"),
            (lat - 0.005, lon + 0.005, "Centre Communautaire"),
            (lat + 0.005, lon - 0.005, "Hôpital Local")
        ]
        
        for e_lat, e_lon, name in evacuation_points:
            folium.Marker(
                [e_lat, e_lon],
                popup=f"🏥 Point d'évacuation\n{name}",
                tooltip=f"Refuge: {name}",
                icon=folium.Icon(color='green', icon='home')
            ).add_to(map_obj)
            
    def get_gps_location(self):
        """Simulation de récupération GPS"""
        # En réalité, on utiliserait une API de géolocalisation
        messagebox.showinfo("GPS", "Fonctionnalité GPS simulée.\nLocalisation: Lomé, Togo")
        self.localite_entry.delete(0, tk.END)
        self.localite_entry.insert(0, "Lomé")
        
    def show_history(self):
        """Affichage de l'historique"""
        history_window = tk.Toplevel(self.root)
        history_window.title("📈 Historique des Analyses")
        history_window.geometry("800x600")
        
        # Récupération des données
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT city, temperature, humidity, risk_level, timestamp 
            FROM weather_history 
            ORDER BY timestamp DESC 
            LIMIT 50
        """)
        
        data = cursor.fetchall()
        
        # Création du tableau
        columns = ('Ville', 'Temp (°C)', 'Humidité (%)', 'Risque', 'Date/Heure')
        tree = ttk.Treeview(history_window, columns=columns, show='headings')
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        
        for row in data:
            tree.insert('', 'end', values=row)
        
        tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Bouton export
        export_btn = tk.Button(history_window, text="💾 Exporter CSV",
                              command=lambda: self.export_history_csv(data),
                              bg="#4CAF50", fg="white")
        export_btn.pack(pady=10)
        
    def export_history_csv(self, data):
        """Export de l'historique en CSV"""
        import csv
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Ville', 'Température', 'Humidité', 'Risque', 'Date/Heure'])
                writer.writerows(data)
            
            messagebox.showinfo("Succès", f"Données exportées vers {filename}")
            
    def subscribe_alerts(self):
        """Abonnement aux alertes"""
        alert_window = tk.Toplevel(self.root)
        alert_window.title("⚠️ Abonnement aux Alertes")
        alert_window.geometry("500x400")
        
        tk.Label(alert_window, text="Configuration des Alertes", 
                font=('Arial', 16, 'bold')).pack(pady=10)
        
        # Email
        tk.Label(alert_window, text="Email :").pack(anchor='w', padx=20)
        email_entry = tk.Entry(alert_window, width=40, font=('Arial', 11))
        email_entry.pack(pady=5)
        
        # Téléphone
        tk.Label(alert_window, text="Téléphone :").pack(anchor='w', padx=20)
        phone_entry = tk.Entry(alert_window, width=40, font=('Arial', 11))
        phone_entry.pack(pady=5)
        
        # Types d'alertes
        tk.Label(alert_window, text="Types d'alertes :").pack(anchor='w', padx=20, pady=(10, 0))
        
        alert_types = tk.Frame(alert_window)
        alert_types.pack(fill='x', padx=20, pady=5)
        
        flood_var = tk.BooleanVar(value=True)
        weather_var = tk.BooleanVar(value=True)
        emergency_var = tk.BooleanVar(value=True)
        
        tk.Checkbutton(alert_types, text="🌊 Alertes inondation", variable=flood_var).pack(anchor='w')
        tk.Checkbutton(alert_types, text="🌦️ Alertes météo", variable=weather_var).pack(anchor='w')
        tk.Checkbutton(alert_types, text="🚨 Alertes urgence", variable=emergency_var).pack(anchor='w')
        
        def save_subscription():
            email = email_entry.get()
            phone = phone_entry.get()
            
            if email or phone:
                # Simulation de sauvegarde
                self.user_preferences.update({
                    'email': email,
                    'phone': phone,
                    'flood_alerts': flood_var.get(),
                    'weather_alerts': weather_var.get(),
                    'emergency_alerts': emergency_var.get()
                })
                
                messagebox.showinfo("Succès", "Abonnement enregistré avec succès!")
                alert_window.destroy()
            else:
                messagebox.showerror("Erreur", "Veuillez renseigner au moins un moyen de contact.")
        
        tk.Button(alert_window, text="💾 Enregistrer",
                 command=save_subscription,
                 bg="#4CAF50", fg="white", font=('Arial', 11, 'bold')).pack(pady=20)
        
    def admin_login(self):
        """Connexion administrateur"""
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        # Authentification simple (en production, utiliser un système sécurisé)
        if username == "admin" and password == "suruwa2025":
            messagebox.showinfo("Succès", "Connexion réussie!")
            self.enable_admin_features()
        else:
            messagebox.showerror("Erreur", "Identifiants incorrects.")
            
    def enable_admin_features(self):
        """Activation des fonctionnalités admin"""
        for widget in self.alert_frame.winfo_children():
            if isinstance(widget, (tk.Entry, tk.Text, ttk.Combobox, tk.Button)):
                widget.configure(state='normal')
        
        # Chargement des alertes existantes
        self.load_active_alerts()
        
    def send_alert(self):
        """Envoi d'une alerte"""
        zone = self.zone_entry.get()
        risk = self.admin_risk.get()
        message = self.message_text.get("1.0", tk.END).strip()
        
        if not zone or not message:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")
            return
        
        # Sauvegarde en base
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO alerts (zone, message, risk_level, timestamp, status)
            VALUES (?, ?, ?, ?, ?)
        """, (zone, message, risk, datetime.now(), "Actif"))
        
        self.conn.commit()
        
        # Simulation d'envoi
        self.simulate_alert_sending(zone, risk, message)
        
        # Mise à jour de la liste
        self.load_active_alerts()
        
        messagebox.showinfo("Succès", f"Alerte envoyée à {zone}!")
        
    def simulate_alert_sending(self, zone, risk, message):
        """Simulation d'envoi d'alerte"""
        # En production, ceci enverrait des SMS, emails, etc.
        print(f"📱 SMS envoyé à {zone}")
        print(f"📧 Email envoyé à {zone}")
        print(f"📻 Diffusion radio: {message}")
        
        # Notification dans l'interface
        self.update_status(f"Alerte {risk} envoyée à {zone}")
        
    def preview_alert(self):
        """Aperçu de l'alerte"""
        zone = self.zone_entry.get()
        risk = self.admin_risk.get()
        message = self.message_text.get("1.0", tk.END).strip()
        
        if not zone or not message:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")
            return
        
        preview_text = f"""
🚨 ALERTE SURUWA 🚨

Zone: {zone}
Niveau: {risk}
Heure: {datetime.now().strftime('%d/%m/%Y %H:%M')}

Message:
{message}

---
Restez en sécurité!
SURUWA Team
        """
        
        preview_window = tk.Toplevel(self.root)
        preview_window.title("👁️ Aperçu de l'Alerte")
        preview_window.geometry("400x300")
        
        text_widget = tk.Text(preview_window, wrap='word', font=('Arial', 10))
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)
        text_widget.insert('1.0', preview_text)
        text_widget.config(state='disabled')
        
    def load_active_alerts(self):
        """Chargement des alertes actives"""
        self.alerts_listbox.delete(0, tk.END)
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT zone, risk_level, timestamp, message
            FROM alerts 
            WHERE status = 'Actif'
            ORDER BY timestamp DESC
        """)
        
        for row in cursor.fetchall():
            zone, risk, timestamp, message = row
            display_text = f"{zone} - {risk} - {timestamp[:16]}"
            self.alerts_listbox.insert(tk.END, display_text)
            
    def add_monitoring_zone(self):
        """Ajout d'une zone à surveiller"""
        zone_window = tk.Toplevel(self.root)
        zone_window.title("➕ Ajouter Zone de Surveillance")
        zone_window.geometry("400x200")
        
        tk.Label(zone_window, text="Nom de la zone :").pack(pady=5)
        zone_entry = tk.Entry(zone_window, width=30, font=('Arial', 11))
        zone_entry.pack(pady=5)
        
        tk.Label(zone_window, text="Fréquence de vérification (minutes) :").pack(pady=5)
        freq_entry = tk.Entry(zone_window, width=30, font=('Arial', 11))
        freq_entry.pack(pady=5)
        freq_entry.insert(0, "30")
        
        def add_zone():
            zone = zone_entry.get()
            frequency = freq_entry.get()
            
            if zone and frequency:
                # Ajout à la liste de surveillance
                self.zones_tree.insert('', 'end', values=(
                    zone, 
                    "En attente...", 
                    "Jamais", 
                    "Actif"
                ))
                
                messagebox.showinfo("Succès", f"Zone {zone} ajoutée à la surveillance!")
                zone_window.destroy()
            else:
                messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")
        
        tk.Button(zone_window, text="➕ Ajouter",
                 command=add_zone,
                 bg="#4CAF50", fg="white").pack(pady=20)
        
    def remove_monitoring_zone(self):
        """Suppression d'une zone surveillée"""
        selected = self.zones_tree.selection()
        if selected:
            self.zones_tree.delete(selected)
            messagebox.showinfo("Succès", "Zone supprimée de la surveillance.")
        else:
            messagebox.showwarning("Attention", "Veuillez sélectionner une zone à supprimer.")
            
    def start_monitoring(self):
        """Démarrage du système de monitoring"""
        def monitor_loop():
            while True:
                time.sleep(60)  # Vérification toutes les minutes
                # Mise à jour du statut des zones surveillées
                self.update_monitoring_status()
        
        threading.Thread(target=monitor_loop, daemon=True).start()
        
    def update_monitoring_status(self):
        """Mise à jour du statut de monitoring"""
        # Cette fonction serait appelée périodiquement
        pass
        
    def save_weather_data(self, city, data, risk_level):
        """Sauvegarde des données météo"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO weather_history (city, temperature, humidity, precipitation, risk_level, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (city, data['temp'], data['humidity'], 0, risk_level, datetime.now()))
        
        self.conn.commit()
        
    def update_status(self, message):
        """Mise à jour de la barre de statut"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_bar.config(text=f"© 2025 SuruwaSoft | {timestamp} - {message}")
        
    def export_data(self):
        """Export des données"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            # Export des données en JSON
            export_data = {
                'preferences': self.user_preferences,
                'alerts': self.current_alerts,
                'timestamp': datetime.now().isoformat()
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("Succès", f"Données exportées vers {filename}")
            
    def import_data(self):
        """Import des données"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Restauration des préférences
                if 'preferences' in data:
                    self.user_preferences.update(data['preferences'])
                
                messagebox.showinfo("Succès", f"Données importées depuis {filename}")
                
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'import: {str(e)}")
                
    def show_help(self):
        """Affichage de l'aide"""
        help_window = tk.Toplevel(self.root)
        help_window.title("📚 Guide d'Utilisation")
        help_window.geometry("600x500")
        
        help_text = """
🌊 GUIDE D'UTILISATION SURUWA 🌊

1. ESPACE CITOYEN
   • Entrez votre ville dans le champ de recherche
   • Cliquez sur "Analyser" pour obtenir l'évaluation des risques
   • Consultez les conseils de sécurité adaptés
   • Visualisez la carte des zones à risque
   • Abonnez-vous aux alertes

2. ESPACE ADMINISTRATEUR
   • Connectez-vous avec vos identifiants
   • Créez et envoyez des alertes aux citoyens
   • Surveillez les zones à risque
   • Gérez les notifications d'urgence

3. MONITORING
   • Ajoutez des zones de surveillance
   • Configurez la fréquence de vérification
   • Suivez l'évolution des risques en temps réel

4. ANALYTIQUES
   • Consultez les graphiques d'évolution
   • Analysez les tendances historiques
   • Exportez les données pour analyse

5. PARAMÈTRES
   • Configurez vos préférences
   • Ajustez les seuils d'alerte
   • Personnalisez les notifications

📞 CONTACTS D'URGENCE
• Pompiers: 118
• Police: 117
• SAMU: 15
• Numéro européen: 112

⚠️ EN CAS D'URGENCE
• Évacuez immédiatement les zones inondées
• Suivez les consignes des autorités
• Ne traversez jamais une route inondée
• Restez informé via les médias officiels
        """
        
        text_widget = tk.Text(help_window, wrap='word', font=('Arial', 10))
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)
        text_widget.insert('1.0', help_text)
        text_widget.config(state='disabled')
        
    def show_about(self):
        """Affichage des informations sur l'application"""
        about_text = """
🌊 SURUWA - Système de Prévention des Inondations 🌊

Version: 2.0
Développé par: SuruwaSoft
Année: 2025

🎯 MISSION
Protéger les communautés africaines contre les risques d'inondation
grâce à un système d'alerte précoce intelligent et accessible.

🚀 FONCTIONNALITÉS
• Analyse météorologique en temps réel
• Calcul intelligent des risques d'inondation
• Système d'alerte multi-canal
• Cartographie interactive des zones à risque
• Monitoring automatisé
• Analytiques avancées

🌍 IMPACT
SURUWA contribue à la résilience climatique en Afrique
en fournissant des outils de prévention accessibles à tous.

📧 Contact: contact@suruwasoft.com
🌐 Web: www.suruwasoft.com
        """
        
        messagebox.showinfo("À Propos", about_text)
        
    def run(self):
        """Lancement de l'application"""
        self.root.mainloop()
        
    def __del__(self):
        """Nettoyage lors de la fermeture"""
        if hasattr(self, 'conn'):
            self.conn.close()

# Lancement de l'application
if __name__ == "__main__":
    app = SuruwaApp()
    app.run()