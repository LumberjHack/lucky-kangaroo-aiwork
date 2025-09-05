import { vi } from 'vitest';

// Configuration des tests de charge
export const loadTestConfig = {
  timeout: 120000,
  retries: 1,
  setupFilesAfterEnv: ['<rootDir>/src/test/load/setup.ts'],
  testEnvironment: 'node',
  testMatch: ['**/*.load.test.ts', '**/*.load.spec.ts'],
};

// Types de tests de charge
export enum LoadTestType {
  STRESS = 'STRESS',
  SPIKE = 'SPIKE',
  SOAK = 'SOAK',
  BREAKPOINT = 'BREAKPOINT',
  SCALABILITY = 'SCALABILITY',
}

// Métriques de performance
export interface LoadTestMetrics {
  // Métriques de temps
  responseTime: {
    min: number;
    max: number;
    mean: number;
    median: number;
    p95: number;
    p99: number;
  };
  
  // Métriques de débit
  throughput: {
    requestsPerSecond: number;
    bytesPerSecond: number;
    transactionsPerSecond: number;
  };
  
  // Métriques d'erreurs
  errors: {
    total: number;
    rate: number;
    byType: Record<string, number>;
  };
  
  // Métriques de ressources
  resources: {
    cpu: number;
    memory: number;
    network: number;
    disk: number;
  };
  
  // Métriques de concurrence
  concurrency: {
    activeUsers: number;
    peakUsers: number;
    averageUsers: number;
  };
}

// Configuration des scénarios de test
export interface LoadTestScenario {
  name: string;
  type: LoadTestType;
  duration: number; // en secondes
  rampUp: number; // en secondes
  rampDown: number; // en secondes
  targetUsers: number;
  maxUsers: number;
  thinkTime: number; // en millisecondes
  requests: LoadTestRequest[];
}

export interface LoadTestRequest {
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  url: string;
  headers?: Record<string, string>;
  body?: any;
  weight: number; // probabilité relative
  expectedStatus: number;
  timeout: number; // en millisecondes
}

// Scénarios de test prédéfinis
export const loadTestScenarios: LoadTestScenario[] = [
  // Test de stress - charge normale puis pic
  {
    name: 'Stress Test - Normal to Peak',
    type: LoadTestType.STRESS,
    duration: 300, // 5 minutes
    rampUp: 60, // 1 minute
    rampDown: 60, // 1 minute
    targetUsers: 100,
    maxUsers: 200,
    thinkTime: 1000,
    requests: [
      {
        method: 'GET',
        url: '/api/listings',
        weight: 40,
        expectedStatus: 200,
        timeout: 5000,
      },
      {
        method: 'GET',
        url: '/api/listings/search',
        weight: 30,
        expectedStatus: 200,
        timeout: 5000,
      },
      {
        method: 'POST',
        url: '/api/auth/login',
        weight: 20,
        expectedStatus: 200,
        timeout: 3000,
        body: { email: 'test@example.com', password: 'password' },
      },
      {
        method: 'GET',
        url: '/api/user/profile',
        weight: 10,
        expectedStatus: 200,
        timeout: 3000,
      },
    ],
  },
  
  // Test de pic - montée rapide
  {
    name: 'Spike Test - Rapid Increase',
    type: LoadTestType.SPIKE,
    duration: 120, // 2 minutes
    rampUp: 10, // 10 secondes
    rampDown: 30, // 30 secondes
    targetUsers: 50,
    maxUsers: 100,
    thinkTime: 500,
    requests: [
      {
        method: 'GET',
        url: '/api/listings',
        weight: 60,
        expectedStatus: 200,
        timeout: 3000,
      },
      {
        method: 'GET',
        url: '/api/listings/featured',
        weight: 40,
        expectedStatus: 200,
        timeout: 3000,
      },
    ],
  },
  
  // Test de trempage - charge soutenue
  {
    name: 'Soak Test - Sustained Load',
    type: LoadTestType.SOAK,
    duration: 1800, // 30 minutes
    rampUp: 300, // 5 minutes
    rampDown: 300, // 5 minutes
    targetUsers: 50,
    maxUsers: 75,
    thinkTime: 2000,
    requests: [
      {
        method: 'GET',
        url: '/api/listings',
        weight: 50,
        expectedStatus: 200,
        timeout: 5000,
      },
      {
        method: 'GET',
        url: '/api/listings/search',
        weight: 30,
        expectedStatus: 200,
        timeout: 5000,
      },
      {
        method: 'GET',
        url: '/api/categories',
        weight: 20,
        expectedStatus: 200,
        timeout: 3000,
      },
    ],
  },
  
  // Test de point de rupture
  {
    name: 'Breakpoint Test - Find Limits',
    type: LoadTestType.BREAKPOINT,
    duration: 600, // 10 minutes
    rampUp: 120, // 2 minutes
    rampDown: 120, // 2 minutes
    targetUsers: 200,
    maxUsers: 500,
    thinkTime: 1000,
    requests: [
      {
        method: 'GET',
        url: '/api/listings',
        weight: 70,
        expectedStatus: 200,
        timeout: 10000,
      },
      {
        method: 'POST',
        url: '/api/listings',
        weight: 30,
        expectedStatus: 201,
        timeout: 10000,
        body: {
          title: 'Test Listing',
          description: 'Test description',
          price: 100,
          category: 'Test',
        },
      },
    ],
  },
  
  // Test de scalabilité
  {
    name: 'Scalability Test - Linear Growth',
    type: LoadTestType.SCALABILITY,
    duration: 900, // 15 minutes
    rampUp: 300, // 5 minutes
    rampDown: 300, // 5 minutes
    targetUsers: 100,
    maxUsers: 300,
    thinkTime: 1500,
    requests: [
      {
        method: 'GET',
        url: '/api/listings',
        weight: 40,
        expectedStatus: 200,
        timeout: 5000,
      },
      {
        method: 'GET',
        url: '/api/listings/search',
        weight: 35,
        expectedStatus: 200,
        timeout: 5000,
      },
      {
        method: 'GET',
        url: '/api/user/profile',
        weight: 25,
        expectedStatus: 200,
        timeout: 3000,
      },
    ],
  },
];

// Utilitaires pour les tests de charge
export const simulateLoadTest = async (
  scenario: LoadTestScenario,
  requestCallback: (request: LoadTestRequest) => Promise<{
    success: boolean;
    responseTime: number;
    statusCode: number;
    error?: string;
  }>
): Promise<LoadTestMetrics> => {
  const startTime = Date.now();
  const results: Array<{
    success: boolean;
    responseTime: number;
    statusCode: number;
    error?: string;
    timestamp: number;
  }> = [];
  
  const errors: Record<string, number> = {};
  let activeUsers = 0;
  let peakUsers = 0;
  let totalRequests = 0;
  let successfulRequests = 0;
  
  // Fonction pour exécuter une requête
  const executeRequest = async (): Promise<void> => {
    const request = selectRandomRequest(scenario.requests);
    const requestStart = Date.now();
    
    try {
      const result = await requestCallback(request);
      const responseTime = Date.now() - requestStart;
      
      results.push({
        success: result.success,
        responseTime,
        statusCode: result.statusCode,
        timestamp: Date.now(),
      });
      
      if (result.success) {
        successfulRequests++;
      } else {
        const errorType = result.error || `HTTP_${result.statusCode}`;
        errors[errorType] = (errors[errorType] || 0) + 1;
      }
      
      totalRequests++;
    } catch (error) {
      const responseTime = Date.now() - requestStart;
      const errorType = error instanceof Error ? error.name : 'Unknown';
      
      results.push({
        success: false,
        responseTime,
        statusCode: 0,
        error: errorType,
        timestamp: Date.now(),
      });
      
      errors[errorType] = (errors[errorType] || 0) + 1;
      totalRequests++;
    }
  };
  
  // Simulation de la montée en charge
  const rampUpInterval = setInterval(() => {
    if (activeUsers < scenario.targetUsers) {
      activeUsers = Math.min(activeUsers + 1, scenario.targetUsers);
      peakUsers = Math.max(peakUsers, activeUsers);
      
      // Démarrer des utilisateurs virtuels
      for (let i = 0; i < activeUsers; i++) {
        const userInterval = setInterval(async () => {
          if (Date.now() - startTime >= scenario.duration * 1000) {
            clearInterval(userInterval);
            return;
          }
          
          await executeRequest();
          
          // Temps de réflexion
          await new Promise(resolve => setTimeout(resolve, scenario.thinkTime));
        }, scenario.thinkTime);
      }
    } else {
      clearInterval(rampUpInterval);
    }
  }, (scenario.rampUp * 1000) / scenario.targetUsers);
  
  // Attendre la fin du test
  await new Promise(resolve => setTimeout(resolve, scenario.duration * 1000));
  
  // Calcul des métriques
  const responseTimes = results.map(r => r.responseTime).sort((a, b) => a - b);
  const totalTime = Date.now() - startTime;
  
  const metrics: LoadTestMetrics = {
    responseTime: {
      min: responseTimes[0] || 0,
      max: responseTimes[responseTimes.length - 1] || 0,
      mean: responseTimes.reduce((sum, time) => sum + time, 0) / responseTimes.length,
      median: responseTimes[Math.floor(responseTimes.length / 2)] || 0,
      p95: responseTimes[Math.floor(responseTimes.length * 0.95)] || 0,
      p99: responseTimes[Math.floor(responseTimes.length * 0.99)] || 0,
    },
    throughput: {
      requestsPerSecond: (totalRequests / totalTime) * 1000,
      bytesPerSecond: 0, // À implémenter si nécessaire
      transactionsPerSecond: (successfulRequests / totalTime) * 1000,
    },
    errors: {
      total: totalRequests - successfulRequests,
      rate: ((totalRequests - successfulRequests) / totalRequests) * 100,
      byType: errors,
    },
    resources: {
      cpu: 0, // À implémenter avec monitoring système
      memory: 0, // À implémenter avec monitoring système
      network: 0, // À implémenter avec monitoring système
      disk: 0, // À implémenter avec monitoring système
    },
    concurrency: {
      activeUsers: activeUsers,
      peakUsers: peakUsers,
      averageUsers: activeUsers, // Simplifié pour l'instant
    },
  };
  
  return metrics;
};

// Sélection aléatoire d'une requête basée sur les poids
const selectRandomRequest = (requests: LoadTestRequest[]): LoadTestRequest => {
  const totalWeight = requests.reduce((sum, req) => sum + req.weight, 0);
  let random = Math.random() * totalWeight;
  
  for (const request of requests) {
    random -= request.weight;
    if (random <= 0) {
      return request;
    }
  }
  
  return requests[0];
};

// Test de charge simple
export const runSimpleLoadTest = async (
  url: string,
  method: 'GET' | 'POST' = 'GET',
  concurrentUsers: number = 10,
  duration: number = 60,
  requestCallback?: (request: LoadTestRequest) => Promise<{
    success: boolean;
    responseTime: number;
    statusCode: number;
    error?: string;
  }>
): Promise<LoadTestMetrics> => {
  const scenario: LoadTestScenario = {
    name: 'Simple Load Test',
    type: LoadTestType.STRESS,
    duration,
    rampUp: duration * 0.2,
    rampDown: duration * 0.2,
    targetUsers: concurrentUsers,
    maxUsers: concurrentUsers * 1.5,
    thinkTime: 1000,
    requests: [
      {
        method,
        url,
        weight: 100,
        expectedStatus: 200,
        timeout: 5000,
      },
    ],
  };
  
  const defaultCallback = async (request: LoadTestRequest) => {
    const start = Date.now();
    try {
      const response = await fetch(request.url, {
        method: request.method,
        headers: request.headers,
        body: request.body ? JSON.stringify(request.body) : undefined,
      });
      
      const responseTime = Date.now() - start;
      const success = response.status === request.expectedStatus;
      
      return {
        success,
        responseTime,
        statusCode: response.status,
        error: success ? undefined : `HTTP ${response.status}`,
      };
    } catch (error) {
      const responseTime = Date.now() - start;
      return {
        success: false,
        responseTime,
        statusCode: 0,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  };
  
  return simulateLoadTest(scenario, requestCallback || defaultCallback);
};

// Test de charge avec monitoring des ressources
export const runLoadTestWithMonitoring = async (
  scenario: LoadTestScenario,
  requestCallback: (request: LoadTestRequest) => Promise<{
    success: boolean;
    responseTime: number;
    statusCode: number;
    error?: string;
  }>,
  monitoringCallback?: (metrics: Partial<LoadTestMetrics>) => void
): Promise<LoadTestMetrics> => {
  const startTime = Date.now();
  const monitoringInterval = setInterval(() => {
    const elapsed = Date.now() - startTime;
    const progress = (elapsed / (scenario.duration * 1000)) * 100;
    
    if (monitoringCallback) {
      monitoringCallback({
        concurrency: {
          activeUsers: 0, // À implémenter
          peakUsers: 0, // À implémenter
          averageUsers: 0, // À implémenter
        },
      });
    }
    
    console.log(`Load test progress: ${progress.toFixed(1)}%`);
  }, 1000);
  
  try {
    const metrics = await simulateLoadTest(scenario, requestCallback);
    
    if (monitoringCallback) {
      monitoringCallback(metrics);
    }
    
    return metrics;
  } finally {
    clearInterval(monitoringInterval);
  }
};

// Validation des métriques de performance
export const validatePerformanceMetrics = (metrics: LoadTestMetrics): {
  passed: boolean;
  issues: string[];
  recommendations: string[];
} => {
  const issues: string[] = [];
  const recommendations: string[] = [];
  
  // Seuils de performance
  const thresholds = {
    responseTime: {
      p95: 2000, // 2s
      p99: 5000, // 5s
    },
    errorRate: 5, // 5%
    throughput: {
      min: 10, // 10 req/s minimum
    },
  };
  
  // Vérification du temps de réponse
  if (metrics.responseTime.p95 > thresholds.responseTime.p95) {
    issues.push(`P95 response time (${metrics.responseTime.p95}ms) exceeds threshold (${thresholds.responseTime.p95}ms)`);
    recommendations.push('Optimize database queries, implement caching, or scale horizontally');
  }
  
  if (metrics.responseTime.p99 > thresholds.responseTime.p99) {
    issues.push(`P99 response time (${metrics.responseTime.p99}ms) exceeds threshold (${thresholds.responseTime.p99}ms)`);
    recommendations.push('Investigate slow queries, optimize critical paths, or add more resources');
  }
  
  // Vérification du taux d'erreur
  if (metrics.errors.rate > thresholds.errorRate) {
    issues.push(`Error rate (${metrics.errors.rate.toFixed(2)}%) exceeds threshold (${thresholds.errorRate}%)`);
    recommendations.push('Investigate error causes, improve error handling, or fix bugs');
  }
  
  // Vérification du débit
  if (metrics.throughput.requestsPerSecond < thresholds.throughput.min) {
    issues.push(`Throughput (${metrics.throughput.requestsPerSecond.toFixed(2)} req/s) below threshold (${thresholds.throughput.min} req/s)`);
    recommendations.push('Optimize application performance, reduce response times, or scale up');
  }
  
  const passed = issues.length === 0;
  
  if (passed) {
    recommendations.push('Performance meets all thresholds. Consider running longer tests for stability validation.');
  }
  
  return {
    passed,
    issues,
    recommendations,
  };
};

// Configuration des tests de charge
export const setupLoadTest = () => {
  // Configuration des timeouts
  vi.setConfig({
    testTimeout: 120000,
    hookTimeout: 30000,
  });
  
  // Configuration des retries
  vi.retry(1);
  
  // Mock de fetch pour les tests
  if (typeof global !== 'undefined') {
    global.fetch = vi.fn();
  }
  
  // Mock de performance.now pour les tests
  if (typeof performance !== 'undefined') {
    Object.defineProperty(performance, 'now', {
      value: vi.fn(() => Date.now()),
      writable: true,
    });
  }
};
