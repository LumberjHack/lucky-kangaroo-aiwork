-- Script d'initialisation de la base de données Lucky Kangaroo

-- Activer les extensions PostgreSQL
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "pgvector";

-- Créer les catégories par défaut
INSERT INTO listing_categories (id, name, slug, description, icon, sort_order, is_active, created_at) VALUES
(uuid_generate_v4(), 'Électronique', 'electronique', 'Appareils électroniques et technologie', 'smartphone', 1, true, NOW()),
(uuid_generate_v4(), 'Véhicules', 'vehicules', 'Voitures, motos, vélos et accessoires', 'car', 2, true, NOW()),
(uuid_generate_v4(), 'Maison & Jardin', 'maison-jardin', 'Meubles, décoration, outils de jardinage', 'home', 3, true, NOW()),
(uuid_generate_v4(), 'Mode & Beauté', 'mode-beaute', 'Vêtements, chaussures, cosmétiques', 'shirt', 4, true, NOW()),
(uuid_generate_v4(), 'Sports & Loisirs', 'sports-loisirs', 'Équipements sportifs et activités', 'activity', 5, true, NOW()),
(uuid_generate_v4(), 'Livres & Médias', 'livres-medias', 'Livres, films, musique, jeux', 'book', 6, true, NOW()),
(uuid_generate_v4(), 'Services', 'services', 'Services professionnels et personnels', 'briefcase', 7, true, NOW()),
(uuid_generate_v4(), 'Autres', 'autres', 'Autres objets et services', 'more-horizontal', 8, true, NOW());

-- Créer les badges par défaut
INSERT INTO badges (id, name, description, icon, color, badge_type, rarity, points_required, is_active, created_at) VALUES
(uuid_generate_v4(), 'Premier échange', 'Effectuez votre premier échange', 'star', '#FFD700', 'activity', 'common', 0, true, NOW()),
(uuid_generate_v4(), 'Éco-citoyen', 'Contribuez à l\'économie circulaire', 'leaf', '#00FF00', 'ecological', 'uncommon', 100, true, NOW()),
(uuid_generate_v4(), 'Membre actif', 'Utilisateur actif de la plateforme', 'users', '#0066CC', 'social', 'common', 50, true, NOW()),
(uuid_generate_v4(), 'Qualité garantie', 'Annonces de qualité', 'award', '#FF6600', 'quality', 'rare', 200, true, NOW());
