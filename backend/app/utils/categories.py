"""
Configuration des catégories pour Lucky Kangaroo
Basé sur le cahier des charges avec catégories étendues
"""

# Catégories principales d'objets
OBJECT_CATEGORIES = {
    "antiques": {
        "name": "Antiquités & objets de collection",
        "icon": "🏺",
        "subcategories": [
            "Mobilier ancien",
            "Objets d'art",
            "Livres anciens",
            "Monnaies & timbres",
            "Vintage & rétro"
        ]
    },
    "appliances": {
        "name": "Appareils électroménagers & petit ménager",
        "icon": "🏠",
        "subcategories": [
            "Gros électroménager",
            "Petit électroménager",
            "Cuisine & salle de bain",
            "Nettoyage & entretien"
        ]
    },
    "art_crafts": {
        "name": "Art, artisanat & loisirs créatifs",
        "icon": "🎨",
        "subcategories": [
            "Peinture & dessin",
            "Sculpture",
            "Artisanat",
            "Fournitures créatives",
            "Instruments d'art"
        ]
    },
    "recreational_vehicles": {
        "name": "Véhicules récréatifs",
        "icon": "🏍️",
        "subcategories": [
            "Quads & motoneiges",
            "Caravanes & camping-cars",
            "Bateaux de plaisance",
            "Véhicules tout-terrain"
        ]
    },
    "auto_parts": {
        "name": "Pièces auto & accessoires",
        "icon": "🔧",
        "subcategories": [
            "Pièces détachées",
            "Accessoires auto",
            "Outillage auto",
            "Pneus & jantes"
        ]
    },
    "aviation": {
        "name": "Aviation & sports aériens",
        "icon": "✈️",
        "subcategories": [
            "Avions & hélicoptères",
            "Parapente & deltaplane",
            "Simulateurs de vol",
            "Équipements aéronautiques"
        ]
    },
    "baby_kids": {
        "name": "Articles pour bébés & enfants",
        "icon": "👶",
        "subcategories": [
            "Poussettes & sièges auto",
            "Vêtements bébé/enfant",
            "Jouets & jeux",
            "Mobilier enfant",
            "Équipements bébé"
        ]
    },
    "barter": {
        "name": "Barter & troc",
        "icon": "🔄",
        "subcategories": [
            "Échanges divers",
            "Wanted (recherché)",
            "Services contre objets",
            "Troc spécialisé"
        ]
    },
    "beauty_health": {
        "name": "Beauté, santé & bien-être",
        "icon": "💄",
        "subcategories": [
            "Cosmétiques & parfums",
            "Équipements fitness",
            "Produits de bien-être",
            "Accessoires beauté"
        ]
    },
    "bicycles": {
        "name": "Vélos & pièces de vélo",
        "icon": "🚲",
        "subcategories": [
            "Vélos complets",
            "Pièces détachées",
            "Accessoires vélo",
            "Équipements cyclistes"
        ]
    },
    "boats": {
        "name": "Bateaux & pièces de bateau",
        "icon": "⛵",
        "subcategories": [
            "Bateaux de plaisance",
            "Voiliers",
            "Moteurs marins",
            "Équipements nautiques"
        ]
    },
    "books_media": {
        "name": "Livres, BD, CD, DVD",
        "icon": "📚",
        "subcategories": [
            "Livres & BD",
            "CD & vinyles",
            "DVD & Blu-ray",
            "Jeux vidéo",
            "Médias numériques"
        ]
    },
    "professional": {
        "name": "Matériel professionnel & industriel",
        "icon": "🏭",
        "subcategories": [
            "Outillage professionnel",
            "Machines industrielles",
            "Équipements de chantier",
            "Matériel médical"
        ]
    },
    "vehicles": {
        "name": "Voitures, motos, scooters, utilitaires",
        "icon": "🚗",
        "subcategories": [
            "Voitures particulières",
            "Motos & scooters",
            "Utilitaires & camions",
            "Véhicules de collection"
        ]
    },
    "mobile_tablets": {
        "name": "Téléphones mobiles & tablettes",
        "icon": "📱",
        "subcategories": [
            "Smartphones",
            "Tablettes",
            "Accessoires mobiles",
            "Objets connectés"
        ]
    },
    "clothing": {
        "name": "Vêtements, chaussures & accessoires",
        "icon": "👕",
        "subcategories": [
            "Vêtements homme",
            "Vêtements femme",
            "Vêtements enfant",
            "Chaussures",
            "Accessoires mode"
        ]
    },
    "computers": {
        "name": "Ordinateurs & périphériques",
        "icon": "💻",
        "subcategories": [
            "Ordinateurs portables",
            "Ordinateurs de bureau",
            "Périphériques",
            "Composants informatiques"
        ]
    },
    "electronics": {
        "name": "Électronique grand public",
        "icon": "📺",
        "subcategories": [
            "TV & home cinéma",
            "Audio & hi-fi",
            "Jeux vidéo & consoles",
            "Photo & vidéo"
        ]
    },
    "agricultural": {
        "name": "Équipement agricole, ferme & jardin",
        "icon": "🚜",
        "subcategories": [
            "Machines agricoles",
            "Outillage jardin",
            "Équipements ferme",
            "Produits agricoles"
        ]
    },
    "furniture": {
        "name": "Meubles & décoration",
        "icon": "🪑",
        "subcategories": [
            "Mobilier salon",
            "Mobilier chambre",
            "Mobilier cuisine",
            "Décoration & art"
        ]
    },
    "garage_sales": {
        "name": "Ventes de garage & \"free stuff\"",
        "icon": "🏪",
        "subcategories": [
            "Ventes de garage",
            "Objets gratuits",
            "Dons & échanges",
            "Brocante"
        ]
    },
    "general": {
        "name": "Articles généraux",
        "icon": "📦",
        "subcategories": [
            "Objets divers",
            "Gadgets & curiosités",
            "Articles insolites",
            "Autres"
        ]
    },
    "heavy_machinery": {
        "name": "Engins & matériel lourd",
        "icon": "🚛",
        "subcategories": [
            "Engins de chantier",
            "Matériel lourd",
            "Machines industrielles",
            "Équipements spécialisés"
        ]
    },
    "jewelry": {
        "name": "Bijoux & montres",
        "icon": "💍",
        "subcategories": [
            "Bijoux précieux",
            "Montres",
            "Accessoires bijoux",
            "Bijoux fantaisie"
        ]
    },
    "materials": {
        "name": "Matériaux & bricolage",
        "icon": "🔨",
        "subcategories": [
            "Bois & matériaux",
            "Carrelage & revêtements",
            "Peinture & finitions",
            "Outillage bricolage"
        ]
    },
    "motorcycle_parts": {
        "name": "Pièces & accessoires moto",
        "icon": "🏍️",
        "subcategories": [
            "Pièces détachées moto",
            "Accessoires moto",
            "Équipements motard",
            "Outillage moto"
        ]
    },
    "music": {
        "name": "Instruments de musique",
        "icon": "🎵",
        "subcategories": [
            "Instruments à cordes",
            "Instruments à vent",
            "Percussions",
            "Équipements audio"
        ]
    },
    "photo_video": {
        "name": "Photo & vidéo",
        "icon": "📷",
        "subcategories": [
            "Appareils photo",
            "Objectifs & accessoires",
            "Équipements vidéo",
            "Éclairage & studio"
        ]
    },
    "camping": {
        "name": "Camping & plein air",
        "icon": "⛺",
        "subcategories": [
            "Tentes & abris",
            "Sacs de couchage",
            "Équipements randonnée",
            "Matériel camping"
        ]
    },
    "sports": {
        "name": "Articles de sport & fitness",
        "icon": "⚽",
        "subcategories": [
            "Équipements sportifs",
            "Fitness & musculation",
            "Sports d'hiver",
            "Sports nautiques"
        ]
    },
    "tickets": {
        "name": "Billetterie & événements",
        "icon": "🎫",
        "subcategories": [
            "Billets concerts",
            "Billets sport",
            "Billets théâtre",
            "Événements divers"
        ]
    },
    "toys": {
        "name": "Jeux & jouets",
        "icon": "🧸",
        "subcategories": [
            "Jouets enfants",
            "Jeux de société",
            "Puzzles & casse-têtes",
            "Jouets éducatifs"
        ]
    },
    "gaming": {
        "name": "Jeux vidéo & consoles",
        "icon": "🎮",
        "subcategories": [
            "Consoles de jeux",
            "Jeux vidéo",
            "Accessoires gaming",
            "PC gaming"
        ]
    },
    "tires": {
        "name": "Jantes & pneus",
        "icon": "🛞",
        "subcategories": [
            "Pneus auto",
            "Pneus moto",
            "Jantes & roues",
            "Accessoires roues"
        ]
    },
    "animals": {
        "name": "Animaux & accessoires",
        "icon": "🐕",
        "subcategories": [
            "Accessoires animaux",
            "Nourriture animaux",
            "Équipements vétérinaires",
            "Adoption (respect des lois)"
        ]
    },
    "real_estate": {
        "name": "Immobilier & hébergement",
        "icon": "🏠",
        "subcategories": [
            "Locations",
            "Ventes immobilières",
            "Sous-locations",
            "Parkings & garages"
        ]
    }
}

# Catégories de services
SERVICE_CATEGORIES = {
    "automotive": {
        "name": "Automobile",
        "icon": "🚗",
        "subcategories": [
            "Réparation & entretien",
            "Lavage & détailing",
            "Dépannage",
            "Conseils auto"
        ]
    },
    "beauty_wellness": {
        "name": "Beauté, bien-être & soins",
        "icon": "💄",
        "subcategories": [
            "Coiffure & esthétique",
            "Massages & bien-être",
            "Soins du corps",
            "Conseils beauté"
        ]
    },
    "it_mobile": {
        "name": "Informatique & mobile",
        "icon": "💻",
        "subcategories": [
            "Réparation informatique",
            "Installation & configuration",
            "Conseils IT",
            "Support technique"
        ]
    },
    "creative": {
        "name": "Créatifs",
        "icon": "🎨",
        "subcategories": [
            "Graphisme & design",
            "Photographie",
            "Musique & audio",
            "Rédaction & traduction"
        ]
    },
    "events": {
        "name": "Événementiel",
        "icon": "🎉",
        "subcategories": [
            "Organisation d'événements",
            "Sonorisation",
            "Location de matériel",
            "Animation & DJ"
        ]
    },
    "agricultural_garden": {
        "name": "Agricole & jardinage",
        "icon": "🌱",
        "subcategories": [
            "Paysagistes",
            "Entretien jardin",
            "Tonte & taille",
            "Conseils jardinage"
        ]
    },
    "financial_legal": {
        "name": "Financier & juridique",
        "icon": "⚖️",
        "subcategories": [
            "Comptabilité",
            "Assurances",
            "Conseils juridiques",
            "Gestion financière"
        ]
    },
    "health_wellness": {
        "name": "Santé & bien-être non médicaux",
        "icon": "🏃",
        "subcategories": [
            "Coach sportif",
            "Diététique & nutrition",
            "Bien-être mental",
            "Thérapies alternatives"
        ]
    },
    "home_household": {
        "name": "Maison & ménage",
        "icon": "🏠",
        "subcategories": [
            "Nettoyage & ménage",
            "Déménagement",
            "Bricolage & réparations",
            "Garde d'enfants"
        ]
    },
    "education": {
        "name": "Cours & formation",
        "icon": "📚",
        "subcategories": [
            "Soutien scolaire",
            "Cours de langues",
            "Cours de musique",
            "Formation professionnelle"
        ]
    },
    "marine": {
        "name": "Marine & nautique",
        "icon": "⛵",
        "subcategories": [
            "Entretien bateaux",
            "Hivernage",
            "Conseils nautiques",
            "Réparations marines"
        ]
    },
    "handyman": {
        "name": "Petits travaux & artisanat",
        "icon": "🔧",
        "subcategories": [
            "Plomberie",
            "Électricité",
            "Menuiserie",
            "Peinture & finitions"
        ]
    },
    "travel_tourism": {
        "name": "Voyages & tourisme",
        "icon": "✈️",
        "subcategories": [
            "Guides touristiques",
            "Transport & chauffeur",
            "Hébergement",
            "Conseils voyage"
        ]
    },
    "animal_services": {
        "name": "Services animaliers",
        "icon": "🐕",
        "subcategories": [
            "Garde d'animaux",
            "Toilettage",
            "Éducation animale",
            "Promenade & sorties"
        ]
    },
    "marketing": {
        "name": "Publicité, marketing & services pro",
        "icon": "📢",
        "subcategories": [
            "Marketing digital",
            "Publicité",
            "Conseils business",
            "Services professionnels"
        ]
    },
    "medical": {
        "name": "Services médicaux & paramédicaux",
        "icon": "🏥",
        "subcategories": [
            "Soins dentaires",
            "Kinésithérapie",
            "Conseils médicaux",
            "Services paramédicaux"
        ],
        "note": "Sous réserve de conformité aux lois et à la déontologie en vigueur"
    }
}

# Toutes les catégories combinées
ALL_CATEGORIES = {**OBJECT_CATEGORIES, **SERVICE_CATEGORIES}

# États des objets
OBJECT_CONDITIONS = [
    {"value": "new", "label": "Neuf", "description": "Jamais utilisé, avec emballage d'origine"},
    {"value": "excellent", "label": "Excellent", "description": "Très bon état, utilisation minimale"},
    {"value": "good", "label": "Bon", "description": "Bon état général, quelques signes d'usage"},
    {"value": "fair", "label": "Correct", "description": "État correct, signes d'usage visibles"},
    {"value": "poor", "label": "Moyen", "description": "Fonctionnel mais état d'usage marqué"}
]

# Types d'échange
EXCHANGE_TYPES = [
    {"value": "barter", "label": "Troc", "description": "Échange d'objet contre objet"},
    {"value": "service_exchange", "label": "Service contre objet", "description": "Échange d'un service contre un objet"},
    {"value": "free", "label": "Gratuit", "description": "Don ou objet gratuit"},
    {"value": "donation", "label": "Don", "description": "Don à une association ou personne"},
    {"value": "sale", "label": "Vente", "description": "Vente avec paiement"}
]

# Devises supportées
SUPPORTED_CURRENCIES = [
    {"code": "CHF", "name": "Franc suisse", "symbol": "CHF", "default": True},
    {"code": "EUR", "name": "Euro", "symbol": "€"},
    {"code": "USD", "name": "Dollar américain", "symbol": "$"},
    {"code": "GBP", "name": "Livre sterling", "symbol": "£"},
    {"code": "CAD", "name": "Dollar canadien", "symbol": "C$"},
    {"code": "JPY", "name": "Yen japonais", "symbol": "¥"}
]

# Langues supportées
SUPPORTED_LANGUAGES = [
    {"code": "fr", "name": "Français", "flag": "🇫🇷", "default": True},
    {"code": "en", "name": "English", "flag": "🇬🇧"},
    {"code": "de", "name": "Deutsch", "flag": "🇩🇪"},
    {"code": "it", "name": "Italiano", "flag": "🇮🇹"},
    {"code": "es", "name": "Español", "flag": "🇪🇸"},
    {"code": "pt", "name": "Português", "flag": "🇵🇹"},
    {"code": "ru", "name": "Русский", "flag": "🇷🇺"},
    {"code": "zh", "name": "中文", "flag": "🇨🇳"}
]

def get_category_by_id(category_id):
    """Récupère une catégorie par son ID"""
    return ALL_CATEGORIES.get(category_id)

def get_categories_by_type(category_type="all"):
    """Récupère les catégories par type"""
    if category_type == "objects":
        return OBJECT_CATEGORIES
    elif category_type == "services":
        return SERVICE_CATEGORIES
    else:
        return ALL_CATEGORIES

def search_categories(query):
    """Recherche dans les catégories"""
    results = {}
    query_lower = query.lower()
    
    for cat_id, cat_data in ALL_CATEGORIES.items():
        if (query_lower in cat_data["name"].lower() or 
            any(query_lower in sub.lower() for sub in cat_data.get("subcategories", []))):
            results[cat_id] = cat_data
    
    return results
