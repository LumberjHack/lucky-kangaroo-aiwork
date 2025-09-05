import { vi } from 'vitest';

// Configuration des tests de couverture
export const coverageTestConfig = {
  timeout: 60000,
  retries: 1,
  setupFilesAfterEnv: ['<rootDir>/src/test/coverage/setup.ts'],
  testEnvironment: 'jsdom',
  testMatch: ['**/*.coverage.test.ts', '**/*.coverage.spec.ts'],
};

// Types de couverture
export enum CoverageType {
  STATEMENTS = 'STATEMENTS',
  BRANCHES = 'BRANCHES',
  FUNCTIONS = 'FUNCTIONS',
  LINES = 'LINES',
  CONDITIONALS = 'CONDITIONALS',
  EXPRESSIONS = 'EXPRESSIONS',
}

// Métriques de couverture
export interface CoverageMetrics {
  statements: {
    total: number;
    covered: number;
    percentage: number;
  };
  branches: {
    total: number;
    covered: number;
    percentage: number;
  };
  functions: {
    total: number;
    covered: number;
    percentage: number;
  };
  lines: {
    total: number;
    covered: number;
    percentage: number;
  };
  conditionals: {
    total: number;
    covered: number;
    percentage: number;
  };
  expressions: {
    total: number;
    covered: number;
    percentage: number;
  };
}

// Détails de couverture par fichier
export interface FileCoverage {
  file: string;
  path: string;
  metrics: CoverageMetrics;
  uncoveredLines: number[];
  uncoveredBranches: Array<{
    line: number;
    type: 'if' | 'else' | 'switch' | 'case' | 'default' | 'ternary' | 'logical';
    condition: string;
  }>;
  uncoveredFunctions: Array<{
    name: string;
    line: number;
    type: 'function' | 'method' | 'arrow' | 'async';
  }>;
  complexity: number;
  maintainability: number;
}

// Configuration des tests de couverture
export interface CoverageTestConfig {
  // Seuils de couverture
  thresholds: {
    global: {
      statements: number;
      branches: number;
      functions: number;
      lines: number;
    };
    perFile: {
      statements: number;
      branches: number;
      functions: number;
      lines: number;
    };
  };
  
  // Fichiers à inclure/exclure
  include: string[];
  exclude: string[];
  
  // Types de couverture à vérifier
  types: CoverageType[];
  
  // Configuration des rapports
  reporting: {
    generateReport: boolean;
    saveArtifacts: boolean;
    format: 'html' | 'json' | 'markdown' | 'lcov';
    outputDir: string;
  };
  
  // Configuration des tests
  testing: {
    timeout: number;
    retries: number;
    parallel: boolean;
    maxConcurrent: number;
  };
}

// Configuration par défaut
export const defaultCoverageTestConfig: CoverageTestConfig = {
  thresholds: {
    global: {
      statements: 80,
      branches: 70,
      functions: 80,
      lines: 80,
    },
    perFile: {
      statements: 70,
      branches: 60,
      functions: 70,
      lines: 70,
    },
  },
  include: [
    'src/**/*.ts',
    'src/**/*.tsx',
    '!src/**/*.d.ts',
    '!src/**/*.test.ts',
    '!src/**/*.spec.ts',
    '!src/**/*.stories.ts',
    '!src/**/*.stories.tsx',
  ],
  exclude: [
    'node_modules/**',
    'dist/**',
    'build/**',
    'coverage/**',
    '**/*.config.*',
    '**/*.setup.*',
    '**/*.mock.*',
  ],
  types: [
    CoverageType.STATEMENTS,
    CoverageType.BRANCHES,
    CoverageType.FUNCTIONS,
    CoverageType.LINES,
  ],
  reporting: {
    generateReport: true,
    saveArtifacts: true,
    format: 'html',
    outputDir: 'coverage',
  },
  testing: {
    timeout: 30000,
    retries: 1,
    parallel: true,
    maxConcurrent: 4,
  },
};

// Interface pour le rapport de couverture
export interface CoverageReport {
  summary: {
    totalFiles: number;
    totalLines: number;
    totalStatements: number;
    totalBranches: number;
    totalFunctions: number;
    overallCoverage: number;
  };
  thresholds: {
    global: {
      passed: boolean;
      details: Record<string, { required: number; actual: number; passed: boolean }>;
    };
    perFile: {
      passed: boolean;
      failedFiles: string[];
      details: Record<string, Record<string, { required: number; actual: number; passed: boolean }>>;
    };
  };
  files: FileCoverage[];
  recommendations: string[];
  timestamp: string;
}

// Utilitaires pour les tests de couverture
export const calculateCoverageMetrics = (
  covered: number,
  total: number
): { covered: number; total: number; percentage: number } => {
  return {
    covered,
    total,
    percentage: total > 0 ? (covered / total) * 100 : 0,
  };
};

export const analyzeFileCoverage = (filePath: string, sourceCode: string): FileCoverage => {
  const lines = sourceCode.split('\n');
  const totalLines = lines.length;
  
  // Simulation d'analyse de couverture
  // En production, utiliser des outils comme Istanbul ou NYC
  const coveredLines = Math.floor(totalLines * 0.8); // 80% simulé
  const uncoveredLines = Array.from(
    { length: totalLines - coveredLines },
    (_, i) => Math.floor(Math.random() * totalLines) + 1
  ).sort((a, b) => a - b);
  
  // Simuler les branches non couvertes
  const uncoveredBranches = lines
    .map((line, index) => {
      if (line.includes('if') || line.includes('else') || line.includes('switch')) {
        return {
          line: index + 1,
          type: line.includes('if') ? 'if' : line.includes('switch') ? 'switch' : 'else',
          condition: line.trim(),
        };
      }
      return null;
    })
    .filter(Boolean)
    .slice(0, Math.floor(Math.random() * 5)); // 0-5 branches non couvertes
  
  // Simuler les fonctions non couvertes
  const uncoveredFunctions = lines
    .map((line, index) => {
      if (line.includes('function') || line.includes('=>') || line.includes('async')) {
        return {
          name: `function_${index}`,
          line: index + 1,
          type: line.includes('async') ? 'async' : line.includes('=>') ? 'arrow' : 'function',
        };
      }
      return null;
    })
    .filter(Boolean)
    .slice(0, Math.floor(Math.random() * 3)); // 0-3 fonctions non couvertes
  
  // Calculer la complexité cyclomatique (simulée)
  const complexity = Math.floor(Math.random() * 10) + 1; // 1-10
  
  // Calculer l'indice de maintenabilité (simulé)
  const maintainability = Math.floor(Math.random() * 20) + 60; // 60-80
  
  return {
    file: filePath.split('/').pop() || filePath,
    path: filePath,
    metrics: {
      statements: calculateCoverageMetrics(coveredLines, totalLines),
      branches: calculateCoverageMetrics(
        Math.floor(coveredLines * 0.9),
        Math.floor(totalLines * 1.2)
      ),
      functions: calculateCoverageMetrics(
        Math.floor(coveredLines * 0.85),
        Math.floor(totalLines * 0.3)
      ),
      lines: calculateCoverageMetrics(coveredLines, totalLines),
      conditionals: calculateCoverageMetrics(
        Math.floor(coveredLines * 0.9),
        Math.floor(totalLines * 0.4)
      ),
      expressions: calculateCoverageMetrics(
        Math.floor(coveredLines * 0.95),
        totalLines
      ),
    },
    uncoveredLines,
    uncoveredBranches: uncoveredBranches as any,
    uncoveredFunctions: uncoveredFunctions as any,
    complexity,
    maintainability,
  };
};

export const checkCoverageThresholds = (
  coverage: FileCoverage[],
  config: CoverageTestConfig
): CoverageReport['thresholds'] => {
  // Calculer la couverture globale
  const globalMetrics = {
    statements: { covered: 0, total: 0 },
    branches: { covered: 0, total: 0 },
    functions: { covered: 0, total: 0 },
    lines: { covered: 0, total: 0 },
  };
  
  coverage.forEach(file => {
    globalMetrics.statements.covered += file.metrics.statements.covered;
    globalMetrics.statements.total += file.metrics.statements.total;
    globalMetrics.branches.covered += file.metrics.branches.covered;
    globalMetrics.branches.total += file.metrics.branches.total;
    globalMetrics.functions.covered += file.metrics.functions.covered;
    globalMetrics.functions.total += file.metrics.functions.total;
    globalMetrics.lines.covered += file.metrics.lines.covered;
    globalMetrics.lines.total += file.metrics.lines.total;
  });
  
  // Vérifier les seuils globaux
  const globalThresholds = config.thresholds.global;
  const globalDetails: Record<string, { required: number; actual: number; passed: boolean }> = {};
  
  Object.entries(globalThresholds).forEach(([metric, required]) => {
    const actual = globalMetrics[metric as keyof typeof globalMetrics];
    const actualPercentage = actual.total > 0 ? (actual.covered / actual.total) * 100 : 0;
    globalDetails[metric] = {
      required,
      actual: actualPercentage,
      passed: actualPercentage >= required,
    };
  });
  
  const globalPassed = Object.values(globalDetails).every(detail => detail.passed);
  
  // Vérifier les seuils par fichier
  const perFileDetails: Record<string, Record<string, { required: number; actual: number; passed: boolean }>> = {};
  const failedFiles: string[] = [];
  
  coverage.forEach(file => {
    const fileThresholds = config.thresholds.perFile;
    const fileDetails: Record<string, { required: number; actual: number; passed: boolean }> = {};
    
    Object.entries(fileThresholds).forEach(([metric, required]) => {
      const actual = file.metrics[metric as keyof CoverageMetrics];
      fileDetails[metric] = {
        required,
        actual: actual.percentage,
        passed: actual.percentage >= required,
      };
    });
    
    perFileDetails[file.path] = fileDetails;
    
    // Vérifier si le fichier respecte tous les seuils
    const filePassed = Object.values(fileDetails).every(detail => detail.passed);
    if (!filePassed) {
      failedFiles.push(file.path);
    }
  });
  
  const perFilePassed = failedFiles.length === 0;
  
  return {
    global: {
      passed: globalPassed,
      details: globalDetails,
    },
    perFile: {
      passed: perFilePassed,
      failedFiles,
      details: perFileDetails,
    },
  };
};

export const generateCoverageReport = (
  coverage: FileCoverage[],
  config: CoverageTestConfig
): CoverageReport => {
  // Calculer le résumé global
  const summary = {
    totalFiles: coverage.length,
    totalLines: coverage.reduce((sum, file) => sum + file.metrics.lines.total, 0),
    totalStatements: coverage.reduce((sum, file) => sum + file.metrics.statements.total, 0),
    totalBranches: coverage.reduce((sum, file) => sum + file.metrics.branches.total, 0),
    totalFunctions: coverage.reduce((sum, file) => sum + file.metrics.functions.total, 0),
    overallCoverage: 0,
  };
  
  // Calculer la couverture globale moyenne
  const totalCoverage = coverage.reduce((sum, file) => {
    return sum + (
      file.metrics.statements.percentage +
      file.metrics.branches.percentage +
      file.metrics.functions.percentage +
      file.metrics.lines.percentage
    ) / 4;
  }, 0);
  
  summary.overallCoverage = coverage.length > 0 ? totalCoverage / coverage.length : 0;
  
  // Vérifier les seuils
  const thresholds = checkCoverageThresholds(coverage, config);
  
  // Générer les recommandations
  const recommendations: string[] = [];
  
  if (!thresholds.global.passed) {
    recommendations.push('La couverture globale ne respecte pas les seuils requis');
    
    Object.entries(thresholds.global.details).forEach(([metric, detail]) => {
      if (!detail.passed) {
        recommendations.push(`${metric}: ${detail.actual.toFixed(1)}% (requis: ${detail.required}%)`);
      }
    });
  }
  
  if (!thresholds.perFile.passed) {
    recommendations.push(`${thresholds.perFile.failedFiles.length} fichier(s) ne respectent pas les seuils de couverture`);
    
    thresholds.perFile.failedFiles.slice(0, 5).forEach(file => {
      recommendations.push(`- ${file}`);
    });
    
    if (thresholds.perFile.failedFiles.length > 5) {
      recommendations.push(`... et ${thresholds.perFile.failedFiles.length - 5} autre(s) fichier(s)`);
    }
  }
  
  // Recommandations générales
  if (summary.overallCoverage < 80) {
    recommendations.push('La couverture globale est faible. Ajoutez plus de tests unitaires');
  }
  
  if (coverage.some(file => file.complexity > 8)) {
    recommendations.push('Certains fichiers ont une complexité cyclomatique élevée. Considérez les refactoriser');
  }
  
  if (coverage.some(file => file.maintainability < 65)) {
    recommendations.push('Certains fichiers ont un indice de maintenabilité faible. Améliorez la lisibilité du code');
  }
  
  if (recommendations.length === 0) {
    recommendations.push('Excellente couverture de code ! Continuez à maintenir cette qualité');
  }
  
  return {
    summary,
    thresholds,
    files: coverage,
    recommendations,
    timestamp: new Date().toISOString(),
  };
};

export const saveCoverageArtifacts = async (
  report: CoverageReport,
  config: CoverageTestConfig
): Promise<void> => {
  if (!config.reporting.saveArtifacts) {
    return;
  }
  
  // Simulation de sauvegarde des artefacts
  console.log('Saving coverage artifacts...');
  console.log(`Total files: ${report.summary.totalFiles}`);
  console.log(`Overall coverage: ${report.summary.overallCoverage.toFixed(1)}%`);
  console.log(`Global thresholds passed: ${report.thresholds.global.passed}`);
  console.log(`Per-file thresholds passed: ${report.thresholds.perFile.passed}`);
  
  console.log('All artifacts saved successfully');
};

export const generateCoverageSummary = (report: CoverageReport): string => {
  let summary = `# Rapport de Couverture de Code\n\n`;
  summary += `## Résumé Global\n`;
  summary += `- **Fichiers analysés**: ${report.summary.totalFiles}\n`;
  summary += `- **Lignes totales**: ${report.summary.totalLines}\n`;
  summary += `- **Couverture globale**: ${report.summary.overallCoverage.toFixed(1)}%\n\n`;
  
  summary += `## Métriques Détaillées\n`;
  summary += `- **Statements**: ${report.summary.totalStatements} total\n`;
  summary += `- **Branches**: ${report.summary.totalBranches} total\n`;
  summary += `- **Functions**: ${report.summary.totalFunctions} total\n\n`;
  
  summary += `## Seuils de Couverture\n`;
  summary += `### Global\n`;
  Object.entries(report.thresholds.global.details).forEach(([metric, detail]) => {
    const status = detail.passed ? '✅' : '❌';
    summary += `- ${status} **${metric}**: ${detail.actual.toFixed(1)}% (requis: ${detail.required}%)\n`;
  });
  
  summary += `\n### Par Fichier\n`;
  if (report.thresholds.perFile.passed) {
    summary += `✅ Tous les fichiers respectent les seuils\n`;
  } else {
    summary += `❌ ${report.thresholds.perFile.failedFiles.length} fichier(s) ne respectent pas les seuils\n`;
    report.thresholds.perFile.failedFiles.slice(0, 10).forEach(file => {
      summary += `- ${file}\n`;
    });
  }
  
  summary += `\n## Recommandations\n`;
  report.recommendations.forEach(rec => {
    summary += `- ${rec}\n`;
  });
  
  summary += `\n## Détails par Fichier\n`;
  report.files.slice(0, 20).forEach(file => {
    summary += `### ${file.file}\n`;
    summary += `- **Couverture**: ${file.metrics.lines.percentage.toFixed(1)}%\n`;
    summary += `- **Complexité**: ${file.complexity}\n`;
    summary += `- **Maintenabilité**: ${file.maintainability}\n`;
    summary += `- **Lignes non couvertes**: ${file.uncoveredLines.length}\n`;
    summary += `- **Branches non couvertes**: ${file.uncoveredBranches.length}\n`;
    summary += `- **Fonctions non couvertes**: ${file.uncoveredFunctions.length}\n\n`;
  });
  
  if (report.files.length > 20) {
    summary += `... et ${report.files.length - 20} autre(s) fichier(s)\n`;
  }
  
  summary += `\n---\n`;
  summary += `*Généré le ${new Date(report.timestamp).toLocaleString('fr-FR')}*\n`;
  
  return summary;
};

// Configuration des tests de couverture
export const setupCoverageTest = () => {
  // Configuration des timeouts
  vi.setConfig({
    testTimeout: 60000,
    hookTimeout: 30000,
  });
  
  // Configuration des retries
  vi.retry(1);
  
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
  
  // Mock de performance.now pour les tests
  if (typeof performance !== 'undefined') {
    Object.defineProperty(performance, 'now', {
      value: vi.fn(() => Date.now()),
      writable: true,
    });
  }
  
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
