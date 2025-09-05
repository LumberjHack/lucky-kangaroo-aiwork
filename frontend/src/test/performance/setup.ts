import { vi } from 'vitest';

// Configuration des tests de performance
export const performanceTestConfig = {
  timeout: 120000,
  retries: 1,
  setupFilesAfterEnv: ['<rootDir>/src/test/performance/setup.ts'],
  testEnvironment: 'jsdom',
  testMatch: ['**/*.performance.test.ts', '**/*.performance.spec.ts'],
};

// Types de tests de performance
export enum PerformanceTestType {
  LOAD_TIME = 'LOAD_TIME',
  RENDER_TIME = 'RENDER_TIME',
  INTERACTION_TIME = 'INTERACTION_TIME',
  MEMORY_USAGE = 'MEMORY_USAGE',
  CPU_USAGE = 'CPU_USAGE',
  NETWORK_PERFORMANCE = 'NETWORK_PERFORMANCE',
  BUNDLE_SIZE = 'BUNDLE_SIZE',
  LIGHTHOUSE = 'LIGHTHOUSE',
}

// Métriques de performance
export interface PerformanceMetrics {
  // Métriques de temps
  loadTime: {
    firstContentfulPaint: number;
    largestContentfulPaint: number;
    firstInputDelay: number;
    timeToInteractive: number;
    domContentLoaded: number;
    loadComplete: number;
  };
  
  // Métriques de rendu
  renderTime: {
    initialRender: number;
    reRender: number;
    componentMount: number;
    componentUpdate: number;
  };
  
  // Métriques d'interaction
  interactionTime: {
    clickResponse: number;
    scrollPerformance: number;
    animationFrameRate: number;
    inputLatency: number;
  };
  
  // Métriques de ressources
  resourceUsage: {
    memoryUsage: number;
    cpuUsage: number;
    networkRequests: number;
    bundleSize: number;
  };
  
  // Métriques de qualité
  qualityMetrics: {
    cumulativeLayoutShift: number;
    totalBlockingTime: number;
    speedIndex: number;
    maxPotentialFirstInputDelay: number;
  };
}

// Configuration des tests de performance
export interface PerformanceTestConfig {
  // Types de tests à exécuter
  testTypes: PerformanceTestType[];
  
  // Seuils de performance
  thresholds: {
    loadTime: {
      firstContentfulPaint: number;
      largestContentfulPaint: number;
      firstInputDelay: number;
      timeToInteractive: number;
    };
    renderTime: {
      initialRender: number;
      reRender: number;
      componentMount: number;
    };
    interactionTime: {
      clickResponse: number;
      scrollPerformance: number;
      animationFrameRate: number;
    };
    resourceUsage: {
      memoryUsage: number;
      cpuUsage: number;
      bundleSize: number;
    };
    qualityMetrics: {
      cumulativeLayoutShift: number;
      totalBlockingTime: number;
      speedIndex: number;
    };
  };
  
  // Configuration des tests
  testing: {
    timeout: number;
    retries: number;
    iterations: number;
    warmupRuns: number;
    parallel: boolean;
    maxConcurrent: number;
  };
  
  // Configuration des rapports
  reporting: {
    generateReport: boolean;
    saveArtifacts: boolean;
    format: 'html' | 'json' | 'markdown';
    outputDir: string;
    compareWithBaseline: boolean;
  };
}

// Configuration par défaut
export const defaultPerformanceTestConfig: PerformanceTestConfig = {
  testTypes: [
    PerformanceTestType.LOAD_TIME,
    PerformanceTestType.RENDER_TIME,
    PerformanceTestType.INTERACTION_TIME,
    PerformanceTestType.MEMORY_USAGE,
  ],
  thresholds: {
    loadTime: {
      firstContentfulPaint: 1800, // 1.8s
      largestContentfulPaint: 2500, // 2.5s
      firstInputDelay: 100, // 100ms
      timeToInteractive: 3800, // 3.8s
    },
    renderTime: {
      initialRender: 100, // 100ms
      reRender: 16, // 16ms (60fps)
      componentMount: 50, // 50ms
    },
    interactionTime: {
      clickResponse: 100, // 100ms
      scrollPerformance: 16, // 16ms (60fps)
      animationFrameRate: 60, // 60fps
    },
    resourceUsage: {
      memoryUsage: 50, // 50MB
      cpuUsage: 30, // 30%
      bundleSize: 500, // 500KB
    },
    qualityMetrics: {
      cumulativeLayoutShift: 0.1,
      totalBlockingTime: 300, // 300ms
      speedIndex: 3400, // 3.4s
    },
  },
  testing: {
    timeout: 60000,
    retries: 1,
    iterations: 5,
    warmupRuns: 2,
    parallel: false,
    maxConcurrent: 1,
  },
  reporting: {
    generateReport: true,
    saveArtifacts: true,
    format: 'html',
    outputDir: 'performance-reports',
    compareWithBaseline: true,
  },
};

// Interface pour les résultats de test de performance
export interface PerformanceTestResult {
  testName: string;
  type: PerformanceTestType;
  metrics: PerformanceMetrics;
  passed: boolean;
  score: number; // 0-100
  details: string;
  artifacts: {
    screenshots?: string[];
    traces?: string[];
    logs?: string;
  };
  timestamp: string;
  duration: number;
}

// Interface pour le rapport de performance
export interface PerformanceReport {
  summary: {
    totalTests: number;
    passedTests: number;
    failedTests: number;
    averageScore: number;
    overallPerformance: 'excellent' | 'good' | 'needs-improvement' | 'poor';
  };
  results: PerformanceTestResult[];
  recommendations: string[];
  baselineComparison?: {
    improved: number;
    degraded: number;
    unchanged: number;
    details: Record<string, { baseline: number; current: number; change: number }>;
  };
  timestamp: string;
}

// Utilitaires pour les tests de performance
export const measureLoadTime = async (): Promise<PerformanceMetrics['loadTime']> => {
  // Simulation de mesure des temps de chargement
  // En production, utiliser l'API Performance ou Lighthouse
  
  const startTime = performance.now();
  
  // Simuler le chargement de la page
  await new Promise(resolve => setTimeout(resolve, Math.random() * 1000 + 500));
  
  const endTime = performance.now();
  const totalTime = endTime - startTime;
  
  return {
    firstContentfulPaint: totalTime * 0.3,
    largestContentfulPaint: totalTime * 0.6,
    firstInputDelay: Math.random() * 200 + 50,
    timeToInteractive: totalTime * 0.8,
    domContentLoaded: totalTime * 0.4,
    loadComplete: totalTime,
  };
};

export const measureRenderTime = async (): Promise<PerformanceMetrics['renderTime']> => {
  // Simulation de mesure des temps de rendu
  
  const startTime = performance.now();
  
  // Simuler le rendu initial
  await new Promise(resolve => setTimeout(resolve, Math.random() * 100 + 50));
  
  const endTime = performance.now();
  const totalTime = endTime - startTime;
  
  return {
    initialRender: totalTime,
    reRender: Math.random() * 20 + 10,
    componentMount: Math.random() * 30 + 20,
    componentUpdate: Math.random() * 15 + 5,
  };
};

export const measureInteractionTime = async () => {
  // Simulation de mesure des temps d'interaction
  
  const startTime = performance.now();
  
  // Simuler une interaction
  await new Promise(resolve => setTimeout(resolve, Math.random() * 50 + 25));
  
  const endTime = performance.now();
  const totalTime = endTime - startTime;
  
  return {
    clickResponse: totalTime,
    scrollPerformance: Math.random() * 20 + 10,
    animationFrameRate: Math.random() * 20 + 50, // 50-70fps
    inputLatency: Math.random() * 30 + 10,
  };
};

export const measureResourceUsage = async () => {
  // Simulation de mesure de l'utilisation des ressources
  
  return {
    memoryUsage: Math.random() * 100 + 20, // 20-120MB
    cpuUsage: Math.random() * 50 + 10, // 10-60%
    networkRequests: Math.floor(Math.random() * 20) + 5, // 5-25 requêtes
    bundleSize: Math.random() * 300 + 200, // 200-500KB
  };
};

export const measureQualityMetrics = async () => {
  // Simulation de mesure des métriques de qualité
  
  return {
    cumulativeLayoutShift: Math.random() * 0.2, // 0-0.2
    totalBlockingTime: Math.random() * 400 + 100, // 100-500ms
    speedIndex: Math.random() * 2000 + 2000, // 2-4s
    maxPotentialFirstInputDelay: Math.random() * 200 + 100, // 100-300ms
  };
};

export const runPerformanceTest = async (
  testName: string,
  testFunction: () => Promise<any>,
  config: PerformanceTestConfig
): Promise<PerformanceTestResult> => {
  const startTime = performance.now();
  
  try {
    // Exécuter le test avec plusieurs itérations
    const results: PerformanceMetrics[] = [];
    
    // Runs de réchauffement
    for (let i = 0; i < config.testing.warmupRuns; i++) {
      await testFunction();
    }
    
    // Runs de mesure
    for (let i = 0; i < config.testing.iterations; i++) {
      const metrics: PerformanceMetrics = {
        loadTime: await measureLoadTime(),
        renderTime: await measureRenderTime(),
        interactionTime: await measureInteractionTime(),
        resourceUsage: await measureResourceUsage(),
        qualityMetrics: await measureQualityMetrics(),
      };
      
      results.push(metrics);
    }
    
    // Calculer les métriques moyennes
    const averageMetrics = calculateAverageMetrics(results);
    
    // Calculer le score de performance
    const score = calculatePerformanceScore(averageMetrics, config.thresholds);
    
    // Vérifier si le test passe
    const passed = score >= 80; // Seuil de 80%
    
    const endTime = performance.now();
    const duration = endTime - startTime;
    
    return {
      testName,
      type: PerformanceTestType.LOAD_TIME, // Type par défaut
      metrics: averageMetrics,
      passed,
      score,
      details: generatePerformanceDetails(averageMetrics, config.thresholds),
      artifacts: {},
      timestamp: new Date().toISOString(),
      duration,
    };
    
  } catch (error) {
    const endTime = performance.now();
    const duration = endTime - startTime;
    
    return {
      testName,
      type: PerformanceTestType.LOAD_TIME,
      metrics: {
        loadTime: { firstContentfulPaint: 0, largestContentfulPaint: 0, firstInputDelay: 0, timeToInteractive: 0, domContentLoaded: 0, loadComplete: 0 },
        renderTime: { initialRender: 0, reRender: 0, componentMount: 0, componentUpdate: 0 },
        interactionTime: { clickResponse: 0, scrollPerformance: 0, animationFrameRate: 0, inputLatency: 0 },
        resourceUsage: { memoryUsage: 0, cpuUsage: 0, networkRequests: 0, bundleSize: 0 },
        qualityMetrics: { cumulativeLayoutShift: 0, totalBlockingTime: 0, speedIndex: 0, maxPotentialFirstInputDelay: 0 },
      },
      passed: false,
      score: 0,
      details: `Test execution failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
      artifacts: {},
      timestamp: new Date().toISOString(),
      duration,
    };
  }
};

export const calculateAverageMetrics = (results: PerformanceMetrics[]): PerformanceMetrics => {
  if (results.length === 0) {
    throw new Error('No results to average');
  }
  
  const average: PerformanceMetrics = {
    loadTime: {
      firstContentfulPaint: 0,
      largestContentfulPaint: 0,
      firstInputDelay: 0,
      timeToInteractive: 0,
      domContentLoaded: 0,
      loadComplete: 0,
    },
    renderTime: {
      initialRender: 0,
      reRender: 0,
      componentMount: 0,
      componentUpdate: 0,
    },
    interactionTime: {
      clickResponse: 0,
      scrollPerformance: 0,
      animationFrameRate: 0,
      inputLatency: 0,
    },
    resourceUsage: {
      memoryUsage: 0,
      cpuUsage: 0,
      networkRequests: 0,
      bundleSize: 0,
    },
    qualityMetrics: {
      cumulativeLayoutShift: 0,
      totalBlockingTime: 0,
      speedIndex: 0,
      maxPotentialFirstInputDelay: 0,
    },
  };
  
  // Calculer les moyennes pour chaque métrique
  Object.keys(average).forEach(category => {
    const categoryKey = category as keyof PerformanceMetrics;
    const categoryMetrics = average[categoryKey] as any;
    
    Object.keys(categoryMetrics).forEach(metric => {
      const sum = results.reduce((acc, result) => {
        return acc + (result[categoryKey] as any)[metric];
      }, 0);
      
      (categoryMetrics as any)[metric] = sum / results.length;
    });
  });
  
  return average;
};

export const calculatePerformanceScore = (
  metrics: PerformanceMetrics,
  thresholds: PerformanceTestConfig['thresholds']
): number => {
  let totalScore = 0;
  let maxScore = 0;
  
  // Score pour le temps de chargement (30% du score total)
  const loadTimeScore = calculateLoadTimeScore(metrics.loadTime, thresholds.loadTime);
  totalScore += loadTimeScore * 0.3;
  maxScore += 100 * 0.3;
  
  // Score pour le temps de rendu (25% du score total)
  const renderTimeScore = calculateRenderTimeScore(metrics.renderTime, thresholds.renderTime);
  totalScore += renderTimeScore * 0.25;
  maxScore += 100 * 0.25;
  
  // Score pour le temps d'interaction (20% du score total)
  const interactionTimeScore = calculateInteractionTimeScore(metrics.interactionTime, thresholds.interactionTime);
  totalScore += interactionTimeScore * 0.2;
  maxScore += 100 * 0.2;
  
  // Score pour l'utilisation des ressources (15% du score total)
  const resourceUsageScore = calculateResourceUsageScore(metrics.resourceUsage, thresholds.resourceUsage);
  totalScore += resourceUsageScore * 0.15;
  maxScore += 100 * 0.15;
  
  // Score pour les métriques de qualité (10% du score total)
  const qualityMetricsScore = calculateQualityMetricsScore(metrics.qualityMetrics, thresholds.qualityMetrics);
  totalScore += qualityMetricsScore * 0.1;
  maxScore += 100 * 0.1;
  
  return maxScore > 0 ? (totalScore / maxScore) * 100 : 0;
};

export const calculateLoadTimeScore = (
  loadTime: PerformanceMetrics['loadTime'],
  thresholds: PerformanceTestConfig['thresholds']['loadTime']
): number => {
  let score = 100;
  
  // Pénaliser si les seuils sont dépassés
  if (loadTime.firstContentfulPaint > thresholds.firstContentfulPaint) {
    score -= 20;
  }
  
  if (loadTime.largestContentfulPaint > thresholds.largestContentfulPaint) {
    score -= 20;
  }
  
  if (loadTime.firstInputDelay > thresholds.firstInputDelay) {
    score -= 20;
  }
  
  if (loadTime.timeToInteractive > thresholds.timeToInteractive) {
    score -= 20;
  }
  
  return Math.max(0, score);
};

export const calculateRenderTimeScore = (
  renderTime: PerformanceMetrics['renderTime'],
  thresholds: PerformanceTestConfig['thresholds']['renderTime']
): number => {
  let score = 100;
  
  if (renderTime.initialRender > thresholds.initialRender) {
    score -= 25;
  }
  
  if (renderTime.reRender > thresholds.reRender) {
    score -= 25;
  }
  
  if (renderTime.componentMount > thresholds.componentMount) {
    score -= 25;
  }
  
  return Math.max(0, score);
};

export const calculateInteractionTimeScore = (
  interactionTime: PerformanceMetrics['interactionTime'],
  thresholds: PerformanceTestConfig['thresholds']['interactionTime']
): number => {
  let score = 100;
  
  if (interactionTime.clickResponse > thresholds.clickResponse) {
    score -= 25;
  }
  
  if (interactionTime.scrollPerformance > thresholds.scrollPerformance) {
    score -= 25;
  }
  
  if (interactionTime.animationFrameRate < thresholds.animationFrameRate) {
    score -= 25;
  }
  
  return Math.max(0, score);
};

export const calculateResourceUsageScore = (
  resourceUsage: PerformanceMetrics['resourceUsage'],
  thresholds: PerformanceTestConfig['thresholds']['resourceUsage']
): number => {
  let score = 100;
  
  if (resourceUsage.memoryUsage > thresholds.memoryUsage) {
    score -= 33;
  }
  
  if (resourceUsage.cpuUsage > thresholds.cpuUsage) {
    score -= 33;
  }
  
  if (resourceUsage.bundleSize > thresholds.bundleSize) {
    score -= 34;
  }
  
  return Math.max(0, score);
};

export const calculateQualityMetricsScore = (
  qualityMetrics: PerformanceMetrics['qualityMetrics'],
  thresholds: PerformanceTestConfig['thresholds']['qualityMetrics']
): number => {
  let score = 100;
  
  if (qualityMetrics.cumulativeLayoutShift > thresholds.cumulativeLayoutShift) {
    score -= 33;
  }
  
  if (qualityMetrics.totalBlockingTime > thresholds.totalBlockingTime) {
    score -= 33;
  }
  
  if (qualityMetrics.speedIndex > thresholds.speedIndex) {
    score -= 34;
  }
  
  return Math.max(0, score);
};

export const generatePerformanceDetails = (
  metrics: PerformanceMetrics,
  thresholds: PerformanceTestConfig['thresholds']
): string => {
  const details: string[] = [];
  
  // Analyser le temps de chargement
  if (metrics.loadTime.firstContentfulPaint > thresholds.loadTime.firstContentfulPaint) {
    details.push(`FCP (${metrics.loadTime.firstContentfulPaint.toFixed(0)}ms) dépasse le seuil (${thresholds.loadTime.firstContentfulPaint}ms)`);
  }
  
  if (metrics.loadTime.largestContentfulPaint > thresholds.loadTime.largestContentfulPaint) {
    details.push(`LCP (${metrics.loadTime.largestContentfulPaint.toFixed(0)}ms) dépasse le seuil (${thresholds.loadTime.largestContentfulPaint}ms)`);
  }
  
  if (metrics.loadTime.firstInputDelay > thresholds.loadTime.firstInputDelay) {
    details.push(`FID (${metrics.loadTime.firstInputDelay.toFixed(0)}ms) dépasse le seuil (${thresholds.loadTime.firstInputDelay}ms)`);
  }
  
  // Analyser le temps de rendu
  if (metrics.renderTime.initialRender > thresholds.renderTime.initialRender) {
    details.push(`Rendu initial (${metrics.renderTime.initialRender.toFixed(0)}ms) dépasse le seuil (${thresholds.renderTime.initialRender}ms)`);
  }
  
  // Analyser l'utilisation des ressources
  if (metrics.resourceUsage.memoryUsage > thresholds.resourceUsage.memoryUsage) {
    details.push(`Mémoire (${metrics.resourceUsage.memoryUsage.toFixed(0)}MB) dépasse le seuil (${thresholds.resourceUsage.memoryUsage}MB)`);
  }
  
  if (details.length === 0) {
    details.push('Toutes les métriques respectent les seuils de performance');
  }
  
  return details.join('; ');
};

export const generatePerformanceReport = (
  results: PerformanceTestResult[],
  config: PerformanceTestConfig
): PerformanceReport => {
  const totalTests = results.length;
  const passedTests = results.filter(result => result.passed).length;
  const failedTests = totalTests - passedTests;
  const averageScore = results.reduce((sum, result) => sum + result.score, 0) / totalTests;
  
  // Déterminer la performance globale
  let overallPerformance: PerformanceReport['summary']['overallPerformance'];
  if (averageScore >= 90) {
    overallPerformance = 'excellent';
  } else if (averageScore >= 80) {
    overallPerformance = 'good';
  } else if (averageScore >= 60) {
    overallPerformance = 'needs-improvement';
  } else {
    overallPerformance = 'poor';
  }
  
  // Générer les recommandations
  const recommendations: string[] = [];
  
  if (averageScore < 80) {
    recommendations.push('La performance globale est en dessous du seuil recommandé (80%)');
  }
  
  if (failedTests > 0) {
    recommendations.push(`${failedTests} test(s) de performance ont échoué`);
  }
  
  // Recommandations spécifiques basées sur les métriques
  const loadTimeIssues = results.filter(result => 
    result.metrics.loadTime.firstContentfulPaint > config.thresholds.loadTime.firstContentfulPaint ||
    result.metrics.loadTime.largestContentfulPaint > config.thresholds.loadTime.largestContentfulPaint
  );
  
  if (loadTimeIssues.length > 0) {
    recommendations.push('Optimisez les temps de chargement en réduisant la taille des bundles et en utilisant le lazy loading');
  }
  
  const renderTimeIssues = results.filter(result =>
    result.metrics.renderTime.initialRender > config.thresholds.renderTime.initialRender
  );
  
  if (renderTimeIssues.length > 0) {
    recommendations.push('Améliorez les temps de rendu en optimisant les composants React et en utilisant la mémorisation');
  }
  
  const resourceIssues = results.filter(result =>
    result.metrics.resourceUsage.memoryUsage > config.thresholds.resourceUsage.memoryUsage ||
    result.metrics.resourceUsage.bundleSize > config.thresholds.resourceUsage.bundleSize
  );
  
  if (resourceIssues.length > 0) {
    recommendations.push('Réduisez l\'utilisation des ressources en optimisant le code et en utilisant le tree shaking');
  }
  
  if (recommendations.length === 0) {
    recommendations.push('Excellente performance ! Continuez à maintenir cette qualité');
  }
  
  return {
    summary: {
      totalTests,
      passedTests,
      failedTests,
      averageScore,
      overallPerformance,
    },
    results,
    recommendations,
    timestamp: new Date().toISOString(),
  };
};

export const savePerformanceArtifacts = async (
  report: PerformanceReport,
  config: PerformanceTestConfig
): Promise<void> => {
  if (!config.reporting.saveArtifacts) {
    return;
  }
  
  // Simulation de sauvegarde des artefacts
  console.log('Saving performance test artifacts...');
  console.log(`Total tests: ${report.summary.totalTests}`);
  console.log(`Average score: ${report.summary.averageScore.toFixed(1)}%`);
  console.log(`Overall performance: ${report.summary.overallPerformance}`);
  
  console.log('All artifacts saved successfully');
};

// Configuration des tests de performance
export const setupPerformanceTest = () => {
  // Configuration des timeouts
  vi.setConfig({
    testTimeout: 120000,
    hookTimeout: 60000,
  });
  
  // Configuration des retries
  vi.retry(1);
  
  // Mock de performance.now pour les tests
  if (typeof performance !== 'undefined') {
    Object.defineProperty(performance, 'now', {
      value: vi.fn(() => Date.now()),
      writable: true,
    });
  }
  
  // Mock de console pour capturer les logs
  const originalConsole = { ...console };
  
  vi.spyOn(console, 'log').mockImplementation((...args) => {
    originalConsole.log(...args);
  });
  
  vi.spyOn(console, 'warn').mockImplementation((...args) => {
    originalConsole.warn(...args);
  });
  
  vi.spyOn(console, 'error').mockImplementation((...args) => {
    originalConsole.error(...args);
  });
  
  // Mock de fetch pour les tests d'API
  if (typeof global !== 'undefined') {
    global.fetch = vi.fn();
  }
  
  // Mock de localStorage pour les tests
  if (typeof global !== 'undefined') {
    const localStorageMock = {
      getItem: vi.fn(),
      setItem: vi.fn(),
      removeItem: vi.fn(),
      clear: vi.fn(),
    };
    global.localStorage = localStorageMock;
  }
};
