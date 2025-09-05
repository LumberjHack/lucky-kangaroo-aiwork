import { vi } from 'vitest';

// Configuration des tests de visualisation
export const visualTestConfig = {
  timeout: 60000,
  retries: 1,
  setupFilesAfterEnv: ['<rootDir>/src/test/visual/setup.ts'],
  testEnvironment: 'jsdom',
  testMatch: ['**/*.visual.test.ts', '**/*.visual.spec.ts'],
};

// Types de tests de visualisation
export enum VisualTestType {
  SCREENSHOT = 'SCREENSHOT',
  LAYOUT = 'LAYOUT',
  RESPONSIVE = 'RESPONSIVE',
  ANIMATION = 'ANIMATION',
  COLOR = 'COLOR',
  TYPOGRAPHY = 'TYPOGRAPHY',
  ACCESSIBILITY = 'ACCESSIBILITY',
}

// Résolutions d'écran à tester
export const screenResolutions = {
  mobile: { width: 375, height: 667, name: 'Mobile' },
  tablet: { width: 768, height: 1024, name: 'Tablet' },
  desktop: { width: 1920, height: 1080, name: 'Desktop' },
  large: { width: 2560, height: 1440, name: 'Large Desktop' },
};

// Navigateurs à simuler
export const browsers = {
  chrome: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
  firefox: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
  safari: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
  edge: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59',
};

// Configuration des tests de screenshot
export interface ScreenshotConfig {
  threshold: number; // Seuil de différence (0-1)
  ignoreRegions: Array<{ x: number; y: number; width: number; height: number }>;
  ignoreElements: string[]; // Sélecteurs CSS à ignorer
  fullPage: boolean;
  delay: number; // Délai avant capture (ms)
}

// Configuration des tests de layout
export interface LayoutConfig {
  checkAlignment: boolean;
  checkSpacing: boolean;
  checkOverflow: boolean;
  checkZIndex: boolean;
  tolerance: number; // Tolérance en pixels
}

// Configuration des tests responsifs
export interface ResponsiveConfig {
  breakpoints: number[];
  orientations: ('portrait' | 'landscape')[];
  checkContent: boolean;
  checkNavigation: boolean;
  checkImages: boolean;
}

// Configuration des tests d'animation
export interface AnimationConfig {
  checkDuration: boolean;
  checkEasing: boolean;
  checkKeyframes: boolean;
  checkPerformance: boolean;
  maxDuration: number; // Durée maximale en ms
}

// Configuration des tests de couleur
export interface ColorConfig {
  checkContrast: boolean;
  checkAccessibility: boolean;
  checkBranding: boolean;
  colorPalette: Record<string, string>;
  minContrastRatio: number;
}

// Configuration des tests de typographie
export interface TypographyConfig {
  checkFonts: boolean;
  checkSizes: boolean;
  checkLineHeight: boolean;
  checkReadability: boolean;
  fontStack: string[];
  minFontSize: number;
}

// Configuration complète des tests visuels
export interface VisualTestConfig {
  screenshot: ScreenshotConfig;
  layout: LayoutConfig;
  responsive: ResponsiveConfig;
  animation: AnimationConfig;
  color: ColorConfig;
  typography: TypographyConfig;
}

// Configuration par défaut
export const defaultVisualTestConfig: VisualTestConfig = {
  screenshot: {
    threshold: 0.1,
    ignoreRegions: [],
    ignoreElements: ['.ads', '.analytics', '.temporary'],
    fullPage: true,
    delay: 1000,
  },
  layout: {
    checkAlignment: true,
    checkSpacing: true,
    checkOverflow: true,
    checkZIndex: true,
    tolerance: 2,
  },
  responsive: {
    breakpoints: [375, 768, 1024, 1920],
    orientations: ['portrait', 'landscape'],
    checkContent: true,
    checkNavigation: true,
    checkImages: true,
  },
  animation: {
    checkDuration: true,
    checkEasing: true,
    checkKeyframes: true,
    checkPerformance: true,
    maxDuration: 1000,
  },
  color: {
    checkContrast: true,
    checkAccessibility: true,
    checkBranding: true,
    colorPalette: {
      primary: '#0ea5e9',
      secondary: '#d946ef',
      accent: '#eab308',
      success: '#22c55e',
      warning: '#f59e0b',
      error: '#ef4444',
    },
    minContrastRatio: 4.5,
  },
  typography: {
    checkFonts: true,
    checkSizes: true,
    checkLineHeight: true,
    checkReadability: true,
    fontStack: ['Inter', 'Poppins', 'system-ui', 'sans-serif'],
    minFontSize: 14,
  },
};

// Utilitaires pour les tests de visualisation
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

export const setUserAgent = (userAgent: string): void => {
  if (typeof navigator !== 'undefined') {
    Object.defineProperty(navigator, 'userAgent', {
      writable: true,
      configurable: true,
      value: userAgent,
    });
  }
};

export const waitForAnimation = async (duration: number = 1000): Promise<void> => {
  await new Promise(resolve => setTimeout(resolve, duration));
};

export const waitForImages = async (): Promise<void> => {
  const images = document.querySelectorAll('img');
  const imagePromises = Array.from(images).map(img => {
    return new Promise<void>((resolve) => {
      if (img.complete) {
        resolve();
      } else {
        img.onload = () => resolve();
        img.onerror = () => resolve();
      }
    });
  });
  
  await Promise.all(imagePromises);
};

export const waitForFonts = async (): Promise<void> => {
  if ('fonts' in document) {
    await document.fonts.ready;
  } else {
    // Fallback pour les navigateurs qui ne supportent pas Font Loading API
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
};

export const getElementBounds = (selector: string): DOMRect | null => {
  const element = document.querySelector(selector);
  if (element) {
    return element.getBoundingClientRect();
  }
  return null;
};

export const checkElementAlignment = (
  element1: string,
  element2: string,
  tolerance: number = 2
): boolean => {
  const bounds1 = getElementBounds(element1);
  const bounds2 = getElementBounds(element2);
  
  if (!bounds1 || !bounds2) {
    return false;
  }
  
  // Vérifier l'alignement vertical
  const verticalDiff = Math.abs(bounds1.top - bounds2.top);
  if (verticalDiff > tolerance) {
    return false;
  }
  
  // Vérifier l'alignement horizontal
  const horizontalDiff = Math.abs(bounds1.left - bounds2.left);
  if (horizontalDiff > tolerance) {
    return false;
  }
  
  return true;
};

export const checkElementSpacing = (
  element1: string,
  element2: string,
  expectedSpacing: number,
  tolerance: number = 2
): boolean => {
  const bounds1 = getElementBounds(element1);
  const bounds2 = getElementBounds(element2);
  
  if (!bounds1 || !bounds2) {
    return false;
  }
  
  // Calculer l'espacement vertical
  const verticalSpacing = bounds2.top - bounds1.bottom;
  const verticalDiff = Math.abs(verticalSpacing - expectedSpacing);
  
  if (verticalDiff > tolerance) {
    return false;
  }
  
  // Calculer l'espacement horizontal
  const horizontalSpacing = bounds2.left - bounds1.right;
  const horizontalDiff = Math.abs(horizontalSpacing - expectedSpacing);
  
  if (horizontalDiff > tolerance) {
    return false;
  }
  
  return true;
};

export const checkElementOverflow = (selector: string): boolean => {
  const element = document.querySelector(selector);
  if (!element) {
    return false;
  }
  
  const bounds = element.getBoundingClientRect();
  const computedStyle = window.getComputedStyle(element);
  
  // Vérifier si l'élément déborde de son conteneur
  const container = element.parentElement;
  if (container) {
    const containerBounds = container.getBoundingClientRect();
    
    if (bounds.left < containerBounds.left ||
        bounds.right > containerBounds.right ||
        bounds.top < containerBounds.top ||
        bounds.bottom > containerBounds.bottom) {
      return true; // Overflow détecté
    }
  }
  
  return false;
};

export const checkZIndex = (selector: string, expectedZIndex: number): boolean => {
  const element = document.querySelector(selector);
  if (!element) {
    return false;
  }
  
  const computedStyle = window.getComputedStyle(element);
  const zIndex = parseInt(computedStyle.zIndex);
  
  return zIndex === expectedZIndex;
};

export const checkResponsiveBreakpoint = (width: number): string => {
  if (width < 768) {
    return 'mobile';
  } else if (width < 1024) {
    return 'tablet';
  } else if (width < 1440) {
    return 'desktop';
  } else {
    return 'large';
  }
};

export const checkFontFamily = (selector: string, expectedFont: string): boolean => {
  const element = document.querySelector(selector);
  if (!element) {
    return false;
  }
  
  const computedStyle = window.getComputedStyle(element);
  const fontFamily = computedStyle.fontFamily.toLowerCase();
  
  return fontFamily.includes(expectedFont.toLowerCase());
};

export const checkFontSize = (selector: string, expectedSize: number): boolean => {
  const element = document.querySelector(selector);
  if (!element) {
    return false;
  }
  
  const computedStyle = window.getComputedStyle(element);
  const fontSize = parseFloat(computedStyle.fontSize);
  
  return Math.abs(fontSize - expectedSize) < 1;
};

export const checkLineHeight = (selector: string, expectedLineHeight: number): boolean => {
  const element = document.querySelector(selector);
  if (!element) {
    return false;
  }
  
  const computedStyle = window.getComputedStyle(element);
  const lineHeight = parseFloat(computedStyle.lineHeight);
  
  return Math.abs(lineHeight - expectedLineHeight) < 0.1;
};

export const checkColor = (selector: string, expectedColor: string): boolean => {
  const element = document.querySelector(selector);
  if (!element) {
    return false;
  }
  
  const computedStyle = window.getComputedStyle(element);
  const color = computedStyle.color;
  
  return color === expectedColor;
};

export const checkBackgroundColor = (selector: string, expectedColor: string): boolean => {
  const element = document.querySelector(selector);
  if (!element) {
    return false;
  }
  
  const computedStyle = window.getComputedStyle(element);
  const backgroundColor = computedStyle.backgroundColor;
  
  return backgroundColor === expectedColor;
};

export const checkAnimationDuration = (selector: string, expectedDuration: number): boolean => {
  const element = document.querySelector(selector);
  if (!element) {
    return false;
  }
  
  const computedStyle = window.getComputedStyle(element);
  const animationDuration = computedStyle.animationDuration;
  
  if (animationDuration === '0s') {
    return false;
  }
  
  const duration = parseFloat(animationDuration);
  return duration <= expectedDuration;
};

export const checkAnimationEasing = (selector: string, expectedEasing: string): boolean => {
  const element = document.querySelector(selector);
  if (!element) {
    return false;
  }
  
  const computedStyle = window.getComputedStyle(element);
  const animationTimingFunction = computedStyle.animationTimingFunction;
  
  return animationTimingFunction === expectedEasing;
};

export const checkKeyframes = (selector: string): boolean => {
  const element = document.querySelector(selector);
  if (!element) {
    return false;
  }
  
  const computedStyle = window.getComputedStyle(element);
  const animationName = computedStyle.animationName;
  
  return animationName !== 'none';
};

export const checkPerformance = (callback: () => void): number => {
  const start = performance.now();
  callback();
  const end = performance.now();
  
  return end - start;
};

export const generateVisualTestReport = (
  testResults: Array<{
    test: string;
    passed: boolean;
    details?: string;
    screenshot?: string;
  }>
): string => {
  const totalTests = testResults.length;
  const passedTests = testResults.filter(result => result.passed).length;
  const failedTests = totalTests - passedTests;
  
  let report = `# Rapport de Tests Visuels\n\n`;
  report += `## Résumé\n`;
  report += `- Total des tests: ${totalTests}\n`;
  report += `- Tests réussis: ${passedTests}\n`;
  report += `- Tests échoués: ${failedTests}\n`;
  report += `- Taux de réussite: ${((passedTests / totalTests) * 100).toFixed(1)}%\n\n`;
  
  if (failedTests > 0) {
    report += `## Tests Échoués\n\n`;
    testResults
      .filter(result => !result.passed)
      .forEach(result => {
        report += `### ${result.test}\n`;
        report += `- Statut: ❌ Échoué\n`;
        if (result.details) {
          report += `- Détails: ${result.details}\n`;
        }
        if (result.screenshot) {
          report += `- Screenshot: ${result.screenshot}\n`;
        }
        report += `\n`;
      });
  }
  
  report += `## Tests Réussis\n\n`;
  testResults
    .filter(result => result.passed)
    .forEach(result => {
      report += `### ${result.test}\n`;
      report += `- Statut: ✅ Réussi\n\n`;
    });
  
  return report;
};

// Configuration des tests de visualisation
export const setupVisualTest = () => {
  // Configuration des timeouts
  vi.setConfig({
    testTimeout: 60000,
    hookTimeout: 30000,
  });
  
  // Configuration des retries
  vi.retry(1);
  
  // Mock de window.getComputedStyle pour les tests
  if (typeof window !== 'undefined') {
    Object.defineProperty(window, 'getComputedStyle', {
      value: vi.fn((element) => ({
        zIndex: '1',
        animationDuration: '0.3s',
        animationTimingFunction: 'ease-in-out',
        animationName: 'fadeIn',
        fontFamily: 'Inter, system-ui, sans-serif',
        fontSize: '16px',
        lineHeight: '1.5',
        color: 'rgb(0, 0, 0)',
        backgroundColor: 'rgb(255, 255, 255)',
      })),
      writable: true,
    });
  }
  
  // Mock de performance.now pour les tests
  if (typeof performance !== 'undefined') {
    Object.defineProperty(performance, 'now', {
      value: vi.fn(() => Date.now()),
      writable: true,
    });
  }
  
  // Mock de document.fonts pour les tests
  if (typeof document !== 'undefined') {
    Object.defineProperty(document, 'fonts', {
      value: {
        ready: Promise.resolve(),
      },
      writable: true,
    });
  }
};
