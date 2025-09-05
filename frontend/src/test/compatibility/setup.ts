import { vi } from 'vitest';

// Configuration des tests de compatibilité
export const compatibilityTestConfig = {
  timeout: 60000,
  retries: 1,
  setupFilesAfterEnv: ['<rootDir>/src/test/compatibility/setup.ts'],
  testEnvironment: 'jsdom',
  testMatch: ['**/*.compatibility.test.ts', '**/*.compatibility.spec.ts'],
};

// Types de tests de compatibilité
export enum CompatibilityTestType {
  BROWSER = 'BROWSER',
  DEVICE = 'DEVICE',
  OS = 'OS',
  FEATURE = 'FEATURE',
  API = 'API',
  POLYFILL = 'POLYFILL',
}

// Navigateurs supportés
export const supportedBrowsers = {
  chrome: {
    name: 'Chrome',
    versions: ['90+', '100+', '110+', '120+'],
    engine: 'Blink',
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  },
  firefox: {
    name: 'Firefox',
    versions: ['88+', '100+', '110+', '120+'],
    engine: 'Gecko',
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
  },
  safari: {
    name: 'Safari',
    versions: ['14+', '15+', '16+', '17+'],
    engine: 'WebKit',
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
  },
  edge: {
    name: 'Edge',
    versions: ['90+', '100+', '110+', '120+'],
    engine: 'Blink',
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
  },
  opera: {
    name: 'Opera',
    versions: ['76+', '90+', '100+'],
    engine: 'Blink',
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.0',
  },
};

// Systèmes d'exploitation supportés
export const supportedOperatingSystems = {
  windows: {
    name: 'Windows',
    versions: ['10', '11'],
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
  },
  macos: {
    name: 'macOS',
    versions: ['10.15', '11.0', '12.0', '13.0', '14.0'],
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
  },
  linux: {
    name: 'Linux',
    versions: ['Ubuntu 20.04+', 'CentOS 8+', 'Debian 11+'],
    userAgent: 'Mozilla/5.0 (X11; Linux x86_64)',
  },
  android: {
    name: 'Android',
    versions: ['8.0', '9.0', '10.0', '11.0', '12.0', '13.0', '14.0'],
    userAgent: 'Mozilla/5.0 (Linux; Android 13; SM-G991B)',
  },
  ios: {
    name: 'iOS',
    versions: ['14.0', '15.0', '16.0', '17.0'],
    userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)',
  },
};

// Types d'appareils supportés
export const supportedDevices = {
  desktop: {
    name: 'Desktop',
    resolutions: [
      { width: 1366, height: 768, name: 'HD' },
      { width: 1920, height: 1080, name: 'Full HD' },
      { width: 2560, height: 1440, name: '2K' },
      { width: 3840, height: 2160, name: '4K' },
    ],
    pixelRatio: 1,
  },
  laptop: {
    name: 'Laptop',
    resolutions: [
      { width: 1366, height: 768, name: 'HD' },
      { width: 1920, height: 1080, name: 'Full HD' },
      { width: 2560, height: 1600, name: 'Retina' },
    ],
    pixelRatio: 1,
  },
  tablet: {
    name: 'Tablet',
    resolutions: [
      { width: 768, height: 1024, name: 'iPad' },
      { width: 810, height: 1080, name: 'iPad Air' },
      { width: 834, height: 1194, name: 'iPad Pro' },
    ],
    pixelRatio: 2,
  },
  mobile: {
    name: 'Mobile',
    resolutions: [
      { width: 375, height: 667, name: 'iPhone SE' },
      { width: 390, height: 844, name: 'iPhone 12/13/14' },
      { width: 414, height: 896, name: 'iPhone 11/XR' },
      { width: 428, height: 926, name: 'iPhone 12/13/14 Pro Max' },
    ],
    pixelRatio: 2,
  },
};

// Fonctionnalités à tester
export const featuresToTest = {
  // JavaScript ES6+
  es6: {
    name: 'ES6+ Features',
    features: [
      'arrow functions',
      'template literals',
      'destructuring',
      'spread operator',
      'async/await',
      'modules',
      'classes',
    ],
    test: () => {
      // Test des fonctionnalités ES6+
      try {
        // Arrow functions
        const arrow = () => 'test';
        
        // Template literals
        const template = `test ${arrow()}`;
        
        // Destructuring
        const { test } = { test: 'value' };
        
        // Spread operator
        const spread = [...[1, 2, 3]];
        
        // Async/await
        const asyncTest = async () => 'test';
        
        // Modules (simulé)
        const moduleTest = true;
        
        // Classes
        class TestClass {
          constructor() {
            this.test = 'value';
          }
        }
        
        return true;
      } catch (error) {
        return false;
      }
    },
  },
  
  // CSS Grid
  cssGrid: {
    name: 'CSS Grid',
    test: () => {
      try {
        const div = document.createElement('div');
        div.style.display = 'grid';
        return div.style.display === 'grid';
      } catch (error) {
        return false;
      }
    },
  },
  
  // CSS Flexbox
  cssFlexbox: {
    name: 'CSS Flexbox',
    test: () => {
      try {
        const div = document.createElement('div');
        div.style.display = 'flex';
        return div.style.display === 'flex';
      } catch (error) {
        return false;
      }
    },
  },
  
  // CSS Custom Properties
  cssCustomProperties: {
    name: 'CSS Custom Properties',
    test: () => {
      try {
        const div = document.createElement('div');
        div.style.setProperty('--test', 'value');
        return div.style.getPropertyValue('--test') === 'value';
      } catch (error) {
        return false;
      }
    },
  },
  
  // Fetch API
  fetch: {
    name: 'Fetch API',
    test: () => {
      return typeof fetch !== 'undefined';
    },
  },
  
  // Local Storage
  localStorage: {
    name: 'Local Storage',
    test: () => {
      try {
        localStorage.setItem('test', 'value');
        const result = localStorage.getItem('test') === 'value';
        localStorage.removeItem('test');
        return result;
      } catch (error) {
        return false;
      }
    },
  },
  
  // Session Storage
  sessionStorage: {
    name: 'Session Storage',
    test: () => {
      try {
        sessionStorage.setItem('test', 'value');
        const result = sessionStorage.getItem('test') === 'value';
        sessionStorage.removeItem('test');
        return result;
      } catch (error) {
        return false;
      }
    },
  },
  
  // IndexedDB
  indexedDB: {
    name: 'IndexedDB',
    test: () => {
      return typeof indexedDB !== 'undefined';
    },
  },
  
  // Service Workers
  serviceWorkers: {
    name: 'Service Workers',
    test: () => {
      return 'serviceWorker' in navigator;
    },
  },
  
  // Push Notifications
  pushNotifications: {
    name: 'Push Notifications',
    test: () => {
      return 'Notification' in window;
    },
  },
  
  // Geolocation
  geolocation: {
    name: 'Geolocation',
    test: () => {
      return 'geolocation' in navigator;
    },
  },
  
  // Web Audio API
  webAudio: {
    name: 'Web Audio API',
    test: () => {
      return typeof AudioContext !== 'undefined' || typeof webkitAudioContext !== 'undefined';
    },
  },
  
  // Canvas 2D
  canvas2D: {
    name: 'Canvas 2D',
    test: () => {
      try {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        return ctx !== null;
      } catch (error) {
        return false;
      }
    },
  },
  
  // WebGL
  webgl: {
    name: 'WebGL',
    test: () => {
      try {
        const canvas = document.createElement('canvas');
        const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
        return gl !== null;
      } catch (error) {
        return false;
      }
    },
  },
  
  // Intersection Observer
  intersectionObserver: {
    name: 'Intersection Observer',
    test: () => {
      return 'IntersectionObserver' in window;
    },
  },
  
  // Resize Observer
  resizeObserver: {
    name: 'Resize Observer',
    test: () => {
      return 'ResizeObserver' in window;
    },
  },
  
  // Mutation Observer
  mutationObserver: {
    name: 'Mutation Observer',
    test: () => {
      return 'MutationObserver' in window;
    },
  },
  
  // Performance API
  performance: {
    name: 'Performance API',
    test: () => {
      return 'performance' in window;
    },
  },
  
  // Web Animations API
  webAnimations: {
    name: 'Web Animations API',
    test: () => {
      return 'animate' in Element.prototype;
    },
  },
  
  // CSS Animations
  cssAnimations: {
    name: 'CSS Animations',
    test: () => {
      try {
        const div = document.createElement('div');
        div.style.animation = 'test 1s';
        return div.style.animation.includes('test');
      } catch (error) {
        return false;
      }
    },
  },
  
  // CSS Transitions
  cssTransitions: {
    name: 'CSS Transitions',
    test: () => {
      try {
        const div = document.createElement('div');
        div.style.transition = 'all 1s';
        return div.style.transition.includes('all');
      } catch (error) {
        return false;
      }
    },
  },
  
  // CSS Transforms
  cssTransforms: {
    name: 'CSS Transforms',
    test: () => {
      try {
        const div = document.createElement('div');
        div.style.transform = 'translateX(10px)';
        return div.style.transform.includes('translateX');
      } catch (error) {
        return false;
      }
    },
  },
  
  // CSS Filters
  cssFilters: {
    name: 'CSS Filters',
    test: () => {
      try {
        const div = document.createElement('div');
        div.style.filter = 'blur(5px)';
        return div.style.filter.includes('blur');
      } catch (error) {
        return false;
      }
    },
  },
  
  // CSS Variables
  cssVariables: {
    name: 'CSS Variables',
    test: () => {
      try {
        const div = document.createElement('div');
        div.style.setProperty('--test', 'value');
        return div.style.getPropertyValue('--test') === 'value';
      } catch (error) {
        return false;
      }
    },
  },
  
  // CSS Media Queries
  cssMediaQueries: {
    name: 'CSS Media Queries',
    test: () => {
      return 'matchMedia' in window;
    },
  },
  
  // Touch Events
  touchEvents: {
    name: 'Touch Events',
    test: () => {
      return 'ontouchstart' in window;
    },
  },
  
  // Pointer Events
  pointerEvents: {
    name: 'Pointer Events',
    test: () => {
      return 'onpointerdown' in window;
    },
  },
  
  // Device Orientation
  deviceOrientation: {
    name: 'Device Orientation',
    test: () => {
      return 'ondeviceorientation' in window;
    },
  },
  
  // Device Motion
  deviceMotion: {
    name: 'Device Motion',
    test: () => {
      return 'ondevicemotion' in window;
    },
  },
  
  // Battery API
  batteryAPI: {
    name: 'Battery API',
    test: () => {
      return 'getBattery' in navigator;
    },
  },
  
  // Network Information API
  networkInfo: {
    name: 'Network Information API',
    test: () => {
      return 'connection' in navigator;
    },
  },
  
  // Vibration API
  vibration: {
    name: 'Vibration API',
    test: () => {
      return 'vibrate' in navigator;
    },
  },
  
  // Screen Orientation API
  screenOrientation: {
    name: 'Screen Orientation API',
    test: () => {
      return 'orientation' in screen;
    },
  },
  
  // Fullscreen API
  fullscreen: {
    name: 'Fullscreen API',
    test: () => {
      return 'requestFullscreen' in document.documentElement ||
             'webkitRequestFullscreen' in document.documentElement ||
             'mozRequestFullScreen' in document.documentElement ||
             'msRequestFullscreen' in document.documentElement;
    },
  },
  
  // Page Visibility API
  pageVisibility: {
    name: 'Page Visibility API',
    test: () => {
      return 'hidden' in document;
    },
  },
  
  // Online/Offline Events
  onlineOffline: {
    name: 'Online/Offline Events',
    test: () => {
      return 'ononline' in window && 'onoffline' in window;
    },
  },
  
  // History API
  history: {
    name: 'History API',
    test: () => {
      return 'pushState' in history;
    },
  },
  
  // File API
  fileAPI: {
    name: 'File API',
    test: () => {
      return 'File' in window && 'FileReader' in window;
    },
  },
  
  // Drag and Drop API
  dragAndDrop: {
    name: 'Drag and Drop API',
    test: () => {
      return 'ondragstart' in document.createElement('div');
    },
  },
  
  // Web Workers
  webWorkers: {
    name: 'Web Workers',
    test: () => {
      return 'Worker' in window;
    },
  },
  
  // Shared Workers
  sharedWorkers: {
    name: 'Shared Workers',
    test: () => {
      return 'SharedWorker' in window;
    },
  },
  
  // Web Sockets
  webSockets: {
    name: 'Web Sockets',
    test: () => {
      return 'WebSocket' in window;
    },
  },
  
  // Server-Sent Events
  serverSentEvents: {
    name: 'Server-Sent Events',
    test: () => {
      return 'EventSource' in window;
    },
  },
  
  // WebRTC
  webRTC: {
    name: 'WebRTC',
    test: () => {
      return 'RTCPeerConnection' in window;
    },
  },
  
  // Web Speech API
  webSpeech: {
    name: 'Web Speech API',
    test: () => {
      return 'speechSynthesis' in window;
    },
  },
  
  // Web Crypto API
  webCrypto: {
    name: 'Web Crypto API',
    test: () => {
      return 'crypto' in window && 'subtle' in crypto;
    },
  },
  
  // Web Storage
  webStorage: {
    name: 'Web Storage',
    test: () => {
      return 'localStorage' in window && 'sessionStorage' in window;
    },
  },
  
  // Web SQL Database
  webSQL: {
    name: 'Web SQL Database',
    test: () => {
      return 'openDatabase' in window;
    },
  },
  
  // Application Cache
  appCache: {
    name: 'Application Cache',
    test: () => {
      return 'applicationCache' in window;
    },
  },
};

// Configuration des tests de compatibilité
export interface CompatibilityTestConfig {
  browsers: string[];
  operatingSystems: string[];
  devices: string[];
  features: string[];
  polyfills: boolean;
  fallbacks: boolean;
}

// Configuration par défaut
export const defaultCompatibilityTestConfig: CompatibilityTestConfig = {
  browsers: Object.keys(supportedBrowsers),
  operatingSystems: Object.keys(supportedOperatingSystems),
  devices: Object.keys(supportedDevices),
  features: Object.keys(featuresToTest),
  polyfills: true,
  fallbacks: true,
};

// Utilitaires pour les tests de compatibilité
export const setUserAgent = (browser: string, os: string): void => {
  if (typeof navigator !== 'undefined') {
    const browserInfo = supportedBrowsers[browser as keyof typeof supportedBrowsers];
    const osInfo = supportedOperatingSystems[os as keyof typeof supportedOperatingSystems];
    
    if (browserInfo && osInfo) {
      const userAgent = `${osInfo.userAgent} ${browserInfo.userAgent}`;
      Object.defineProperty(navigator, 'userAgent', {
        writable: true,
        configurable: true,
        value: userAgent,
      });
    }
  }
};

export const setDevicePixelRatio = (ratio: number): void => {
  if (typeof window !== 'undefined') {
    Object.defineProperty(window, 'devicePixelRatio', {
      writable: true,
      configurable: true,
      value: ratio,
    });
  }
};

export const setViewport = (width: number, height: number): void => {
  if (typeof window !== 'undefined') {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: width,
    });
    
    Object.defineProperty(window, 'innerHeight', {
      writable: true,
      configurable: true,
      value: height,
    });
    
    Object.defineProperty(window, 'outerWidth', {
      writable: true,
      configurable: true,
      value: width,
    });
    
    Object.defineProperty(window, 'outerHeight', {
      writable: true,
      configurable: true,
      value: height,
    });
    
    // Déclencher l'événement resize
    window.dispatchEvent(new Event('resize'));
  }
};

export const testFeature = (featureName: string): boolean => {
  const feature = featuresToTest[featureName as keyof typeof featuresToTest];
  if (feature && feature.test) {
    return feature.test();
  }
  return false;
};

export const testAllFeatures = (): Record<string, boolean> => {
  const results: Record<string, boolean> = {};
  
  Object.keys(featuresToTest).forEach(featureName => {
    results[featureName] = testFeature(featureName);
  });
  
  return results;
};

export const generateCompatibilityReport = (
  testResults: Record<string, boolean>,
  config: CompatibilityTestConfig
): string => {
  const totalFeatures = Object.keys(testResults).length;
  const supportedFeatures = Object.values(testResults).filter(Boolean).length;
  const unsupportedFeatures = totalFeatures - supportedFeatures;
  
  let report = `# Rapport de Compatibilité\n\n`;
  report += `## Résumé\n`;
  report += `- Total des fonctionnalités testées: ${totalFeatures}\n`;
  report += `- Fonctionnalités supportées: ${supportedFeatures}\n`;
  report += `- Fonctionnalités non supportées: ${unsupportedFeatures}\n`;
  report += `- Taux de compatibilité: ${((supportedFeatures / totalFeatures) * 100).toFixed(1)}%\n\n`;
  
  if (unsupportedFeatures > 0) {
    report += `## Fonctionnalités Non Supportées\n\n`;
    Object.entries(testResults)
      .filter(([_, supported]) => !supported)
      .forEach(([featureName, _]) => {
        const feature = featuresToTest[featureName as keyof typeof featuresToTest];
        report += `### ${feature?.name || featureName}\n`;
        report += `- Statut: ❌ Non supporté\n`;
        report += `- Impact: À évaluer\n`;
        if (config.polyfills) {
          report += `- Recommandation: Implémenter un polyfill\n`;
        }
        report += `\n`;
      });
  }
  
  report += `## Fonctionnalités Supportées\n\n`;
  Object.entries(testResults)
    .filter(([_, supported]) => supported)
    .forEach(([featureName, _]) => {
      const feature = featuresToTest[featureName as keyof typeof featuresToTest];
      report += `### ${feature?.name || featureName}\n`;
      report += `- Statut: ✅ Supporté\n\n`;
    });
  
  report += `## Recommandations\n\n`;
  
  if (unsupportedFeatures > 0) {
    report += `### Amélioration de la Compatibilité\n`;
    report += `1. **Polyfills**: Implémenter des polyfills pour les fonctionnalités non supportées\n`;
    report += `2. **Fallbacks**: Fournir des alternatives pour les navigateurs anciens\n`;
    report += `3. **Détection**: Utiliser la détection de fonctionnalités pour adapter l'expérience\n`;
    report += `4. **Tests**: Tester régulièrement sur différents navigateurs et appareils\n\n`;
  }
  
  report += `### Maintenance\n`;
  report += `1. **Mise à jour**: Maintenir les polyfills et fallbacks à jour\n`;
  report += `2. **Monitoring**: Surveiller l'utilisation des navigateurs et appareils\n`;
  report += `3. **Documentation**: Maintenir une documentation de compatibilité\n`;
  report += `4. **CI/CD**: Intégrer les tests de compatibilité dans le pipeline CI/CD\n`;
  
  return report;
};

// Configuration des tests de compatibilité
export const setupCompatibilityTest = () => {
  // Configuration des timeouts
  vi.setConfig({
    testTimeout: 60000,
    hookTimeout: 30000,
  });
  
  // Configuration des retries
  vi.retry(1);
  
  // Mock des fonctionnalités non supportées pour les tests
  if (typeof window !== 'undefined') {
    // Mock de matchMedia
    Object.defineProperty(window, 'matchMedia', {
      value: vi.fn(() => ({
        matches: false,
        media: '',
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })),
      writable: true,
    });
    
    // Mock de getComputedStyle
    Object.defineProperty(window, 'getComputedStyle', {
      value: vi.fn(() => ({
        getPropertyValue: vi.fn(() => ''),
        setProperty: vi.fn(),
        removeProperty: vi.fn(),
      })),
      writable: true,
    });
  }
  
  // Mock de navigator
  if (typeof navigator !== 'undefined') {
    Object.defineProperty(navigator, 'userAgent', {
      writable: true,
      configurable: true,
      value: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    });
    
    Object.defineProperty(navigator, 'onLine', {
      writable: true,
      configurable: true,
      value: true,
    });
  }
  
  // Mock de performance
  if (typeof performance !== 'undefined') {
    Object.defineProperty(performance, 'now', {
      value: vi.fn(() => Date.now()),
      writable: true,
    });
  }
};
