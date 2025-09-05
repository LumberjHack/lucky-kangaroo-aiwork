import { vi } from 'vitest';
import { cleanup } from '@testing-library/react';

// Configuration des tests d'intégration
beforeEach(() => {
  // Reset des mocks
  vi.clearAllMocks();
  
  // Reset du DOM
  cleanup();
  
  // Reset des événements
  window.history.pushState({}, '', '/');
});

afterEach(() => {
  // Nettoyage après chaque test
  cleanup();
  
  // Reset des timers
  vi.clearAllTimers();
});

// Configuration globale pour les tests d'intégration
export const integrationTestConfig = {
  timeout: 10000,
  retries: 2,
  setupFilesAfterEnv: ['<rootDir>/src/test/integration/setup.ts'],
};
