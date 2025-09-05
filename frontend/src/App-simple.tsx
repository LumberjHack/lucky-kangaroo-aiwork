import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

function HomePage() {
  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>🚀 Lucky Kangaroo</h1>
      <p>Plateforme d'échange collaborative</p>
      <div style={{ marginTop: '20px' }}>
        <h2>✅ Backend fonctionnel</h2>
        <p>API disponible sur : <a href="http://localhost:5000/api/v1">http://localhost:5000/api/v1</a></p>
        
        <h2>🔧 Fonctionnalités disponibles :</h2>
        <ul>
          <li>✅ Authentification (JWT)</li>
          <li>✅ Gestion des annonces</li>
          <li>✅ Recherche avancée</li>
          <li>✅ Chat temps réel</li>
          <li>✅ Services IA</li>
          <li>✅ Moteur de matching</li>
        </ul>
        
        <h2>📱 Test de l'API :</h2>
        <button onClick={() => {
          fetch('http://localhost:5000/api/v1/')
            .then(res => res.json())
            .then(data => alert('API Response: ' + JSON.stringify(data)))
            .catch(err => alert('Erreur: ' + err.message));
        }}>
          Tester l'API
        </button>
      </div>
    </div>
  );
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
      </Routes>
    </Router>
  );
}

export default App;
