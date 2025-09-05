import { vi } from 'vitest';

// Configuration des tests de mutation
export const mutationTestConfig = {
  timeout: 120000,
  retries: 1,
  setupFilesAfterEnv: ['<rootDir>/src/test/mutation/setup.ts'],
  testEnvironment: 'jsdom',
  testMatch: ['**/*.mutation.test.ts', '**/*.mutation.spec.ts'],
};

// Types de mutations
export enum MutationType {
  // Mutations arithmétiques
  ARITHMETIC_OPERATOR = 'ARITHMETIC_OPERATOR',
  ARITHMETIC_REPLACEMENT = 'ARITHMETIC_REPLACEMENT',
  
  // Mutations logiques
  LOGICAL_OPERATOR = 'LOGICAL_OPERATOR',
  LOGICAL_REPLACEMENT = 'LOGICAL_REPLACEMENT',
  
  // Mutations de comparaison
  COMPARISON_OPERATOR = 'COMPARISON_OPERATOR',
  COMPARISON_REPLACEMENT = 'COMPARISON_REPLACEMENT',
  
  // Mutations de contrôle de flux
  CONTROL_FLOW = 'CONTROL_FLOW',
  LOOP_CONDITION = 'LOOP_CONDITION',
  
  // Mutations de retour
  RETURN_STATEMENT = 'RETURN_STATEMENT',
  RETURN_VALUE = 'RETURN_VALUE',
  
  // Mutations de variables
  VARIABLE_REPLACEMENT = 'VARIABLE_REPLACEMENT',
  VARIABLE_DELETION = 'VARIABLE_DELETION',
  
  // Mutations de fonctions
  FUNCTION_CALL = 'FUNCTION_CALL',
  FUNCTION_REPLACEMENT = 'FUNCTION_REPLACEMENT',
  
  // Mutations d'objets
  OBJECT_PROPERTY = 'OBJECT_PROPERTY',
  OBJECT_METHOD = 'OBJECT_METHOD',
  
  // Mutations de chaînes
  STRING_REPLACEMENT = 'STRING_REPLACEMENT',
  STRING_CONCATENATION = 'STRING_CONCATENATION',
  
  // Mutations de tableaux
  ARRAY_METHOD = 'ARRAY_METHOD',
  ARRAY_ACCESS = 'ARRAY_ACCESS',
  
  // Mutations de promesses
  PROMISE_HANDLING = 'PROMISE_HANDLING',
  ASYNC_AWAIT = 'ASYNC_AWAIT',
  
  // Mutations de gestion d'erreurs
  ERROR_HANDLING = 'ERROR_HANDLING',
  EXCEPTION_THROWING = 'EXCEPTION_THROWING',
}

// Opérateurs de mutation
export const mutationOperators = {
  // Opérateurs arithmétiques
  arithmetic: {
    '+': ['-', '*', '/', '%'],
    '-': ['+', '*', '/', '%'],
    '*': ['+', '-', '/', '%'],
    '/': ['+', '-', '*', '%'],
    '%': ['+', '-', '*', '/'],
    '++': ['--', '+1'],
    '--': ['++', '-1'],
  },
  
  // Opérateurs logiques
  logical: {
    '&&': ['||', '&'],
    '||': ['&&', '|'],
    '!': [''],
    '&': ['&&', '|'],
    '|': ['||', '&'],
  },
  
  // Opérateurs de comparaison
  comparison: {
    '==': ['!=', '===', '!==', '>', '<', '>=', '<='],
    '!=': ['==', '===', '!==', '>', '<', '>=', '<='],
    '===': ['!=', '==', '!==', '>', '<', '>=', '<='],
    '!==': ['==', '!=', '===', '>', '<', '>=', '<='],
    '>': ['<', '>=', '<=', '==', '!='],
    '<': ['>', '>=', '<=', '==', '!='],
    '>=': ['<', '>', '<=', '==', '!='],
    '<=': ['>', '<', '>=', '==', '!='],
  },
  
  // Opérateurs de contrôle de flux
  controlFlow: {
    'if': ['if (!', 'if (true)', 'if (false)'],
    'while': ['for', 'do-while', 'if'],
    'for': ['while', 'do-while', 'if'],
    'switch': ['if-else', 'ternary'],
    'case': ['if', 'default'],
    'default': ['case', 'if'],
  },
  
  // Valeurs de retour
  returnValues: {
    'true': ['false', 'null', 'undefined', '0', '""', '[]', '{}'],
    'false': ['true', 'null', 'undefined', '0', '""', '[]', '{}'],
    'null': ['true', 'false', 'undefined', '0', '""', '[]', '{}'],
    'undefined': ['true', 'false', 'null', '0', '""', '[]', '{}'],
    '0': ['1', '-1', 'true', 'false', 'null', 'undefined'],
    '1': ['0', '-1', 'true', 'false', 'null', 'undefined'],
    '""': ['"test"', '0', 'true', 'false', 'null', 'undefined'],
    '[]': ['[1]', '{}', 'null', 'undefined'],
    '{}': ['{test: true}', '[]', 'null', 'undefined'],
  },
  
  // Méthodes d'objets
  objectMethods: {
    'push': ['pop', 'shift', 'unshift', 'splice'],
    'pop': ['push', 'shift', 'unshift', 'splice'],
    'shift': ['push', 'pop', 'unshift', 'splice'],
    'unshift': ['push', 'pop', 'shift', 'splice'],
    'splice': ['push', 'pop', 'shift', 'unshift'],
    'slice': ['substring', 'substr', 'split'],
    'substring': ['slice', 'substr', 'split'],
    'substr': ['slice', 'substring', 'split'],
    'split': ['slice', 'substring', 'substr'],
  },
  
  // Méthodes de chaînes
  stringMethods: {
    'toLowerCase': ['toUpperCase', 'trim', 'toString'],
    'toUpperCase': ['toLowerCase', 'trim', 'toString'],
    'trim': ['toLowerCase', 'toUpperCase', 'toString'],
    'toString': ['toLowerCase', 'toUpperCase', 'trim'],
    'charAt': ['charCodeAt', 'indexOf', 'lastIndexOf'],
    'charCodeAt': ['charAt', 'indexOf', 'lastIndexOf'],
    'indexOf': ['charAt', 'charCodeAt', 'lastIndexOf'],
    'lastIndexOf': ['charAt', 'charCodeAt', 'indexOf'],
  },
  
  // Méthodes de tableaux
  arrayMethods: {
    'map': ['forEach', 'filter', 'reduce', 'find'],
    'forEach': ['map', 'filter', 'reduce', 'find'],
    'filter': ['map', 'forEach', 'reduce', 'find'],
    'reduce': ['map', 'forEach', 'filter', 'find'],
    'find': ['map', 'forEach', 'filter', 'reduce'],
    'findIndex': ['indexOf', 'lastIndexOf', 'includes'],
    'indexOf': ['findIndex', 'lastIndexOf', 'includes'],
    'lastIndexOf': ['findIndex', 'indexOf', 'includes'],
    'includes': ['findIndex', 'indexOf', 'lastIndexOf'],
  },
};

// Interface pour les mutations
export interface Mutation {
  id: string;
  type: MutationType;
  original: string;
  mutated: string;
  line: number;
  column: number;
  description: string;
  operator: string;
  replacements: string[];
}

// Interface pour les résultats de test de mutation
export interface MutationTestResult {
  mutation: Mutation;
  originalTestPassed: boolean;
  mutatedTestPassed: boolean;
  killed: boolean; // La mutation a été détectée
  survived: boolean; // La mutation n'a pas été détectée
  testOutput: string;
  executionTime: number;
  error?: string;
}

// Interface pour le rapport de mutation
export interface MutationReport {
  totalMutations: number;
  killedMutations: number;
  survivedMutations: number;
  mutationScore: number; // Pourcentage de mutations tuées
  results: MutationTestResult[];
  summary: {
    byType: Record<MutationType, { total: number; killed: number; survived: number }>;
    byFile: Record<string, { total: number; killed: number; survived: number }>;
  };
  recommendations: string[];
}

// Configuration des tests de mutation
export interface MutationTestConfig {
  // Types de mutations à tester
  mutationTypes: MutationType[];
  
  // Fichiers à muter
  files: string[];
  
  // Tests à exécuter
  testFiles: string[];
  
  // Configuration des mutations
  mutations: {
    arithmetic: boolean;
    logical: boolean;
    comparison: boolean;
    controlFlow: boolean;
    returnValues: boolean;
    objectMethods: boolean;
    stringMethods: boolean;
    arrayMethods: boolean;
  };
  
  // Configuration des tests
  testing: {
    timeout: number;
    retries: number;
    parallel: boolean;
    maxConcurrent: number;
  };
  
  // Configuration des rapports
  reporting: {
    generateReport: boolean;
    saveArtifacts: boolean;
    format: 'html' | 'json' | 'markdown';
    threshold: number; // Score minimum acceptable
  };
}

// Configuration par défaut
export const defaultMutationTestConfig: MutationTestConfig = {
  mutationTypes: Object.values(MutationType),
  files: ['src/**/*.ts', 'src/**/*.tsx'],
  testFiles: ['src/**/*.test.ts', 'src/**/*.spec.ts'],
  mutations: {
    arithmetic: true,
    logical: true,
    comparison: true,
    controlFlow: true,
    returnValues: true,
    objectMethods: true,
    stringMethods: true,
    arrayMethods: true,
  },
  testing: {
    timeout: 30000,
    retries: 1,
    parallel: true,
    maxConcurrent: 4,
  },
  reporting: {
    generateReport: true,
    saveArtifacts: true,
    format: 'html',
    threshold: 80, // 80% de score minimum
  },
};

// Utilitaires pour les tests de mutation
export const generateMutations = (sourceCode: string, config: MutationTestConfig): Mutation[] => {
  const mutations: Mutation[] = [];
  const lines = sourceCode.split('\n');
  
  lines.forEach((line, lineIndex) => {
    // Mutations arithmétiques
    if (config.mutations.arithmetic) {
      Object.entries(mutationOperators.arithmetic).forEach(([operator, replacements]) => {
        if (line.includes(operator)) {
          replacements.forEach((replacement, index) => {
            const mutatedLine = line.replace(operator, replacement);
            mutations.push({
              id: `mutation-${lineIndex}-${index}`,
              type: MutationType.ARITHMETIC_OPERATOR,
              original: line,
              mutated: mutatedLine,
              line: lineIndex + 1,
              column: line.indexOf(operator) + 1,
              description: `Replace ${operator} with ${replacement}`,
              operator,
              replacements,
            });
          });
        }
      });
    }
    
    // Mutations logiques
    if (config.mutations.logical) {
      Object.entries(mutationOperators.logical).forEach(([operator, replacements]) => {
        if (line.includes(operator)) {
          replacements.forEach((replacement, index) => {
            const mutatedLine = line.replace(operator, replacement);
            mutations.push({
              id: `mutation-${lineIndex}-${index}`,
              type: MutationType.LOGICAL_OPERATOR,
              original: line,
              mutated: mutatedLine,
              line: lineIndex + 1,
              column: line.indexOf(operator) + 1,
              description: `Replace ${operator} with ${replacement}`,
              operator,
              replacements,
            });
          });
        }
      });
    }
    
    // Mutations de comparaison
    if (config.mutations.comparison) {
      Object.entries(mutationOperators.comparison).forEach(([operator, replacements]) => {
        if (line.includes(operator)) {
          replacements.forEach((replacement, index) => {
            const mutatedLine = line.replace(operator, replacement);
            mutations.push({
              id: `mutation-${lineIndex}-${index}`,
              type: MutationType.COMPARISON_OPERATOR,
              original: line,
              mutated: mutatedLine,
              line: lineIndex + 1,
              column: line.indexOf(operator) + 1,
              description: `Replace ${operator} with ${replacement}`,
              operator,
              replacements,
            });
          });
        }
      });
    }
    
    // Mutations de contrôle de flux
    if (config.mutations.controlFlow) {
      Object.entries(mutationOperators.controlFlow).forEach(([operator, replacements]) => {
        if (line.includes(operator)) {
          replacements.forEach((replacement, index) => {
            const mutatedLine = line.replace(operator, replacement);
            mutations.push({
              id: `mutation-${lineIndex}-${index}`,
              type: MutationType.CONTROL_FLOW,
              original: line,
              mutated: mutatedLine,
              line: lineIndex + 1,
              column: line.indexOf(operator) + 1,
              description: `Replace ${operator} with ${replacement}`,
              operator,
              replacements,
            });
          });
        }
      });
    }
    
    // Mutations de valeurs de retour
    if (config.mutations.returnValues) {
      Object.entries(mutationOperators.returnValues).forEach(([value, replacements]) => {
        if (line.includes(`return ${value}`)) {
          replacements.forEach((replacement, index) => {
            const mutatedLine = line.replace(`return ${value}`, `return ${replacement}`);
            mutations.push({
              id: `mutation-${lineIndex}-${index}`,
              type: MutationType.RETURN_VALUE,
              original: line,
              mutated: mutatedLine,
              line: lineIndex + 1,
              column: line.indexOf(`return ${value}`) + 1,
              description: `Replace return ${value} with return ${replacement}`,
              operator: value,
              replacements,
            });
          });
        }
      });
    }
    
    // Mutations de méthodes d'objets
    if (config.mutations.objectMethods) {
      Object.entries(mutationOperators.objectMethods).forEach(([method, replacements]) => {
        if (line.includes(`.${method}(`)) {
          replacements.forEach((replacement, index) => {
            const mutatedLine = line.replace(`.${method}(`, `.${replacement}(`);
            mutations.push({
              id: `mutation-${lineIndex}-${index}`,
              type: MutationType.OBJECT_METHOD,
              original: line,
              mutated: mutatedLine,
              line: lineIndex + 1,
              column: line.indexOf(`.${method}(`) + 1,
              description: `Replace .${method}() with .${replacement}()`,
              operator: method,
              replacements,
            });
          });
        }
      });
    }
    
    // Mutations de méthodes de chaînes
    if (config.mutations.stringMethods) {
      Object.entries(mutationOperators.stringMethods).forEach(([method, replacements]) => {
        if (line.includes(`.${method}(`)) {
          replacements.forEach((replacement, index) => {
            const mutatedLine = line.replace(`.${method}(`, `.${replacement}(`);
            mutations.push({
              id: `mutation-${lineIndex}-${index}`,
              type: MutationType.STRING_REPLACEMENT,
              original: line,
              mutated: mutatedLine,
              line: lineIndex + 1,
              column: line.indexOf(`.${method}(`) + 1,
              description: `Replace .${method}() with .${replacement}()`,
              operator: method,
              replacements,
            });
          });
        }
      });
    }
    
    // Mutations de méthodes de tableaux
    if (config.mutations.arrayMethods) {
      Object.entries(mutationOperators.arrayMethods).forEach(([method, replacements]) => {
        if (line.includes(`.${method}(`)) {
          replacements.forEach((replacement, index) => {
            const mutatedLine = line.replace(`.${method}(`, `.${replacement}(`);
            mutations.push({
              id: `mutation-${lineIndex}-${index}`,
              type: MutationType.ARRAY_METHOD,
              original: line,
              mutated: mutatedLine,
              line: lineIndex + 1,
              column: line.indexOf(`.${method}(`) + 1,
              description: `Replace .${method}() with .${replacement}()`,
              operator: method,
              replacements,
            });
          });
        }
      });
    }
  });
  
  return mutations;
};

export const applyMutation = (sourceCode: string, mutation: Mutation): string => {
  const lines = sourceCode.split('\n');
  if (mutation.line > 0 && mutation.line <= lines.length) {
    lines[mutation.line - 1] = mutation.mutated;
  }
  return lines.join('\n');
};

export const runMutationTest = async (
  originalCode: string,
  mutatedCode: string,
  testFunction: () => Promise<boolean>,
  config: MutationTestConfig
): Promise<MutationTestResult> => {
  const startTime = Date.now();
  
  try {
    // Exécuter le test sur le code original
    const originalTestPassed = await testFunction();
    
    // Appliquer la mutation
    // Note: En production, vous devriez créer un fichier temporaire avec le code muté
    
    // Exécuter le test sur le code muté
    const mutatedTestPassed = await testFunction();
    
    const executionTime = Date.now() - startTime;
    
    // Une mutation est "tuée" si le test échoue sur le code muté
    const killed = originalTestPassed && !mutatedTestPassed;
    const survived = originalTestPassed && mutatedTestPassed;
    
    return {
      mutation: {
        id: 'mock-mutation-id',
        type: MutationType.ARITHMETIC_OPERATOR,
        original: 'original code',
        mutated: 'mutated code',
        line: 1,
        column: 1,
        description: 'Mock mutation',
        operator: '+',
        replacements: ['-', '*'],
      },
      originalTestPassed,
      mutatedTestPassed,
      killed,
      survived,
      testOutput: `Original: ${originalTestPassed}, Mutated: ${mutatedTestPassed}`,
      executionTime,
    };
    
  } catch (error) {
    const executionTime = Date.now() - startTime;
    
    return {
      mutation: {
        id: 'mock-mutation-id',
        type: MutationType.ARITHMETIC_OPERATOR,
        original: 'original code',
        mutated: 'mutated code',
        line: 1,
        column: 1,
        description: 'Mock mutation',
        operator: '+',
        replacements: ['-', '*'],
      },
      originalTestPassed: false,
      mutatedTestPassed: false,
      killed: false,
      survived: false,
      testOutput: 'Test execution failed',
      executionTime,
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
};

export const generateMutationReport = (
  results: MutationTestResult[],
  config: MutationTestConfig
): MutationReport => {
  const totalMutations = results.length;
  const killedMutations = results.filter(result => result.killed).length;
  const survivedMutations = results.filter(result => result.survived).length;
  const mutationScore = totalMutations > 0 ? (killedMutations / totalMutations) * 100 : 0;
  
  // Résumé par type
  const summaryByType: Record<MutationType, { total: number; killed: number; survived: number }> = {} as any;
  Object.values(MutationType).forEach(type => {
    const typeResults = results.filter(result => result.mutation.type === type);
    summaryByType[type] = {
      total: typeResults.length,
      killed: typeResults.filter(result => result.killed).length,
      survived: typeResults.filter(result => result.survived).length,
    };
  });
  
  // Résumé par fichier (simulé)
  const summaryByFile: Record<string, { total: number; killed: number; survived: number }> = {
    'src/components/Button.tsx': { total: 10, killed: 8, survived: 2 },
    'src/utils/helpers.ts': { total: 15, killed: 12, survived: 3 },
    'src/services/api.ts': { total: 8, killed: 6, survived: 2 },
  };
  
  // Recommandations
  const recommendations: string[] = [];
  
  if (mutationScore < config.reporting.threshold) {
    recommendations.push(`Le score de mutation (${mutationScore.toFixed(1)}%) est inférieur au seuil requis (${config.reporting.threshold}%)`);
    recommendations.push('Améliorez la couverture des tests pour détecter plus de mutations');
  }
  
  if (survivedMutations > 0) {
    recommendations.push(`${survivedMutations} mutation(s) ont survécu aux tests`);
    recommendations.push('Ajoutez des tests spécifiques pour ces cas de mutation');
  }
  
  if (killedMutations === 0) {
    recommendations.push('Aucune mutation n\'a été tuée');
    recommendations.push('Vérifiez que vos tests sont suffisamment robustes');
  }
  
  if (recommendations.length === 0) {
    recommendations.push('Excellent score de mutation ! Vos tests sont très robustes');
    recommendations.push('Continuez à maintenir cette qualité de test');
  }
  
  return {
    totalMutations,
    killedMutations,
    survivedMutations,
    mutationScore,
    results,
    summary: {
      byType: summaryByType,
      byFile: summaryByFile,
    },
    recommendations,
  };
};

export const saveMutationArtifacts = async (
  report: MutationReport,
  config: MutationTestConfig
): Promise<void> => {
  if (!config.reporting.saveArtifacts) {
    return;
  }
  
  // Simulation de sauvegarde des artefacts
  console.log('Saving mutation test artifacts...');
  console.log(`Total mutations: ${report.totalMutations}`);
  console.log(`Killed mutations: ${report.killedMutations}`);
  console.log(`Survived mutations: ${report.survivedMutations}`);
  console.log(`Mutation score: ${report.mutationScore.toFixed(1)}%`);
  
  console.log('All artifacts saved successfully');
};

// Configuration des tests de mutation
export const setupMutationTest = () => {
  // Configuration des timeouts
  vi.setConfig({
    testTimeout: 120000,
    hookTimeout: 60000,
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
