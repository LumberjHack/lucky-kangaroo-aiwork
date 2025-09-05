module.exports = {
  root: true,
  env: { browser: true, es2020: true },
  extends: [
    'eslint:recommended',
    '@typescript-eslint/recommended',
    'plugin:react-hooks/recommended',
  ],
  ignorePatterns: ['dist', '.eslintrc.cjs'],
  parser: '@typescript-eslint/parser',
  plugins: ['react-refresh'],
  rules: {
    'react-refresh/only-export-components': [
      'warn',
      { allowConstantExport: true },
    ],
    // Règles TypeScript
    '@typescript-eslint/no-unused-vars': ['error', { 
      argsIgnorePattern: '^_',
      varsIgnorePattern: '^_',
      caughtErrorsIgnorePattern: '^_'
    }],
    '@typescript-eslint/no-explicit-any': 'warn',
    '@typescript-eslint/explicit-function-return-type': 'off',
    '@typescript-eslint/explicit-module-boundary-types': 'off',
    '@typescript-eslint/no-non-null-assertion': 'warn',
    
    // Règles React
    'react-hooks/rules-of-hooks': 'error',
    'react-hooks/exhaustive-deps': 'warn',
    
    // Règles générales
    'no-console': 'warn',
    'no-debugger': 'error',
    'prefer-const': 'error',
    'no-var': 'error',
    'object-shorthand': 'error',
    'prefer-template': 'error',
    
    // Règles d'import
    'import/order': 'off', // Désactivé car nécessite le plugin import
    
    // Règles de formatage
    'indent': ['error', 2],
    'quotes': ['error', 'single'],
    'semi': ['error', 'always'],
    'comma-dangle': ['error', 'always-multiline'],
    'trailing-comma': 'off',
    
    // Règles de complexité
    'complexity': ['warn', 10],
    'max-depth': ['warn', 4],
    'max-lines': ['warn', 300],
    'max-params': ['warn', 5],
    
    // Règles de sécurité
    'no-eval': 'error',
    'no-implied-eval': 'error',
    'no-new-func': 'error',
    'no-script-url': 'error',
    
    // Règles d'accessibilité
    'jsx-a11y/alt-text': 'off', // Géré par le plugin jsx-a11y si installé
    'jsx-a11y/anchor-is-valid': 'off', // Géré par le plugin jsx-a11y si installé
    
    // Règles spécifiques au projet
    'no-magic-numbers': ['warn', { 
      ignore: [-1, 0, 1, 2, 100, 1000],
      ignoreArrayIndexes: true,
      detectObjects: false
    }],
    
    // Règles de nommage
    'camelcase': ['error', { properties: 'never' }],
    'id-length': ['warn', { min: 2, exceptions: ['i', 'j', 'k', 'x', 'y', 'z'] }],
    
    // Règles de performance
    'no-loop-func': 'error',
    'no-new-object': 'error',
    'no-new-array': 'error',
    'no-new-wrappers': 'error',
    
    // Règles de style
    'array-bracket-spacing': ['error', 'never'],
    'object-curly-spacing': ['error', 'always'],
    'computed-property-spacing': ['error', 'never'],
    'key-spacing': ['error', { beforeColon: false, afterColon: true }],
    'keyword-spacing': ['error', { before: true, after: true }],
    'space-before-blocks': ['error', 'always'],
    'space-before-function-paren': ['error', {
      anonymous: 'always',
      named: 'never',
      asyncArrow: 'always'
    }],
    'space-in-parens': ['error', 'never'],
    'space-infix-ops': 'error',
    'space-unary-ops': ['error', { words: true, nonwords: false }],
    
    // Règles de commentaires
    'spaced-comment': ['error', 'always'],
    'multiline-comment-style': ['error', 'starred-block'],
    
    // Règles de variables
    'no-undef': 'error',
    'no-unused-vars': 'off', // Remplacé par la rèle TypeScript
    'no-use-before-define': ['error', { functions: false, classes: true }],
    
    // Règles de fonctions
    'func-style': ['error', 'expression'],
    'no-param-reassign': 'error',
    'prefer-arrow-callback': 'error',
    'arrow-spacing': 'error',
    'arrow-parens': ['error', 'always'],
    
    // Règles d'objets
    'object-curly-newline': ['error', { 
      multiline: true,
      consistent: true
    }],
    'object-property-newline': 'off',
    
    // Règles d'arrays
    'array-element-newline': 'off',
    'array-bracket-newline': ['error', 'consistent'],
    
    // Règles de chaînes
    'quotes': ['error', 'single', { avoidEscape: true }],
    'jsx-quotes': ['error', 'prefer-double'],
    'template-curly-spacing': 'error',
    
    // Règles de conditions
    'no-cond-assign': ['error', 'always'],
    'no-constant-condition': ['error', { checkLoops: false }],
    'no-dupe-keys': 'error',
    'no-dupe-args': 'error',
    'no-dupe-class-members': 'error',
    'no-dupe-else-if': 'error',
    
    // Règles de switch
    'no-fallthrough': 'error',
    'default-case': 'error',
    'default-case-last': 'error',
    
    // Règles de try-catch
    'no-unsafe-finally': 'error',
    'no-unsafe-negation': 'error',
    
    // Règles de regex
    'no-regex-spaces': 'error',
    'no-control-regex': 'error',
    
    // Règles de fichiers
    'eol-last': 'error',
    'no-trailing-spaces': 'error',
    'no-multiple-empty-lines': ['error', { max: 2, maxEOF: 1 }],
    'no-empty-lines': ['error', { max: 2, maxEOF: 1 }],
    
    // Règles de fin de ligne
    'linebreak-style': ['error', 'unix'],
    'max-len': ['warn', { 
      code: 100,
      ignoreUrls: true,
      ignoreStrings: true,
      ignoreTemplateLiterals: true,
      ignoreRegExpLiterals: true
    }],
    
    // Règles de promesses
    'no-async-promise-executor': 'error',
    'no-promise-executor-return': 'error',
    'prefer-promise-reject-errors': 'error',
    
    // Règles de classes
    'class-methods-use-this': 'warn',
    'no-useless-constructor': 'error',
    'prefer-class-properties': 'error',
    
    // Règles de modules
    'no-duplicate-imports': 'error',
    'no-useless-rename': 'error',
    'prefer-named-capture-group': 'error',
    
    // Règles de destructuring
    'prefer-destructuring': ['error', {
      array: false,
      object: true
    }],
    
    // Règles de spread/rest
    'prefer-spread': 'error',
    'prefer-rest-params': 'error',
    
    // Règles de template literals
    'prefer-template': 'error',
    'template-curly-spacing': 'error',
    
    // Règles de ternaires
    'no-unneeded-ternary': 'error',
    'operator-assignment': 'error',
    
    // Règles d'opérateurs
    'operator-linebreak': ['error', 'before'],
    'nonblock-statement-body-position': ['error', 'beside'],
    
    // Règles de blocs
    'brace-style': ['error', '1tbs', { allowSingleLine: true }],
    'block-spacing': 'error',
    'keyword-spacing': 'error',
    
    // Règles de fonctions fléchées
    'arrow-body-style': ['error', 'as-needed'],
    'arrow-parens': ['error', 'always'],
    'arrow-spacing': 'error',
    
    // Règles de générateurs
    'generator-star-spacing': ['error', { before: false, after: true }],
    'yield-star-spacing': ['error', { before: false, after: true }],
    
    // Règles de callbacks
    'callback-return': 'error',
    'handle-callback-err': 'error',
    'no-callback-literal': 'error',
    
    // Règles de gestion d'erreurs
    'no-throw-literal': 'error',
    'prefer-promise-reject-errors': 'error',
    
    // Règles de sécurité
    'no-implied-eval': 'error',
    'no-new-func': 'error',
    'no-script-url': 'error',
    'no-unsafe-optional-chaining': 'error',
    
    // Règles de compatibilité
    'no-var': 'error',
    'prefer-const': 'error',
    'object-shorthand': 'error',
    'prefer-arrow-callback': 'error',
    
    // Règles de performance
    'no-loop-func': 'error',
    'no-new-object': 'error',
    'no-new-array': 'error',
    'no-new-wrappers': 'error',
    'no-return-assign': 'error',
    'no-self-compare': 'error',
    'no-sequences': 'error',
    'no-throw-literal': 'error',
    'no-unmodified-loop-condition': 'error',
    'no-unused-expressions': 'error',
    'no-useless-call': 'error',
    'no-useless-concat': 'error',
    'no-useless-return': 'error',
    'no-void': 'error',
    'no-warning-comments': 'warn',
    'prefer-promise-reject-errors': 'error',
    'require-await': 'error',
    'yoda': 'error',
    
    // Règles de style avancées
    'array-bracket-newline': ['error', 'consistent'],
    'array-element-newline': 'off',
    'function-call-argument-newline': ['error', 'consistent'],
    'function-paren-newline': ['error', 'consistent'],
    'implicit-arrow-linebreak': ['error', 'beside'],
    'multiline-ternary': ['error', 'always-multiline'],
    'newline-per-chained-call': ['error', { ignoreChainWithDepth: 3 }],
    'object-curly-newline': ['error', { 
      multiline: true,
      consistent: true
    }],
    'object-property-newline': 'off',
    'operator-linebreak': ['error', 'before'],
    'padded-blocks': ['error', 'never'],
    'padding-line-between-statements': [
      'error',
      { blankLine: 'always', prev: '*', next: 'return' },
      { blankLine: 'always', prev: ['const', 'let', 'var'], next: '*' },
      { blankLine: 'any', prev: ['const', 'let', 'var'], next: ['const', 'let', 'var'] }
    ],
    'semi-spacing': 'error',
    'semi-style': ['error', 'last'],
    'space-before-blocks': 'error',
    'space-before-function-paren': ['error', {
      anonymous: 'always',
      named: 'never',
      asyncArrow: 'always'
    }],
    'space-in-parens': 'error',
    'space-infix-ops': 'error',
    'space-unary-ops': 'error',
    'switch-colon-spacing': 'error',
    'template-tag-spacing': 'error',
    'unicode-bom': 'error',
    'wrap-iife': ['error', 'any'],
    'wrap-regex': 'error',
    
    // Règles de variables avancées
    'init-declarations': 'off',
    'no-catch-shadow': 'error',
    'no-delete-var': 'error',
    'no-label-var': 'error',
    'no-restricted-globals': 'error',
    'no-shadow': 'error',
    'no-shadow-restricted-names': 'error',
    'no-undef': 'error',
    'no-undef-init': 'error',
    'no-undefined': 'off',
    'no-unused-vars': 'off', // Remplacé par TypeScript
    'no-use-before-define': ['error', { functions: false, classes: true }],
    
    // Règles de fonctions avancées
    'array-callback-return': 'error',
    'consistent-return': 'error',
    'default-case': 'error',
    'default-case-last': 'error',
    'default-param-last': 'error',
    'func-name-matching': 'error',
    'func-names': 'off',
    'func-style': ['error', 'expression'],
    'id-length': ['warn', { min: 2, exceptions: ['i', 'j', 'k', 'x', 'y', 'z'] }],
    'max-lines-per-function': ['warn', { max: 50, skipBlankLines: true, skipComments: true }],
    'max-params': ['warn', 5],
    'max-statements': ['warn', 20],
    'max-statements-per-line': ['error', { max: 1 }],
    'no-alert': 'warn',
    'no-caller': 'error',
    'no-case-declarations': 'error',
    'no-constructor-return': 'error',
    'no-div-regex': 'error',
    'no-else-return': 'error',
    'no-empty-function': 'error',
    'no-empty-pattern': 'error',
    'no-eq-null': 'error',
    'no-eval': 'error',
    'no-extend-native': 'error',
    'no-extra-bind': 'error',
    'no-extra-label': 'error',
    'no-fallthrough': 'error',
    'no-floating-decimal': 'error',
    'no-global-assign': 'error',
    'no-implicit-coercion': 'error',
    'no-implicit-globals': 'error',
    'no-implied-eval': 'error',
    'no-invalid-this': 'error',
    'no-iterator': 'error',
    'no-labels': 'error',
    'no-lone-blocks': 'error',
    'no-loop-func': 'error',
    'no-magic-numbers': ['warn', { 
      ignore: [-1, 0, 1, 2, 100, 1000],
      ignoreArrayIndexes: true,
      detectObjects: false
    }],
    'no-multi-spaces': 'error',
    'no-multi-str': 'error',
    'no-new': 'error',
    'no-new-func': 'error',
    'no-new-wrappers': 'error',
    'no-octal': 'error',
    'no-octal-escape': 'error',
    'no-param-reassign': 'error',
    'no-proto': 'error',
    'no-redeclare': 'error',
    'no-restricted-properties': 'error',
    'no-return-assign': 'error',
    'no-return-await': 'error',
    'no-script-url': 'error',
    'no-self-assign': 'error',
    'no-self-compare': 'error',
    'no-sequences': 'error',
    'no-throw-literal': 'error',
    'no-unmodified-loop-condition': 'error',
    'no-unused-expressions': 'error',
    'no-useless-call': 'error',
    'no-useless-catch': 'error',
    'no-useless-concat': 'error',
    'no-useless-escape': 'error',
    'no-useless-return': 'error',
    'no-void': 'error',
    'no-warning-comments': 'warn',
    'no-with': 'error',
    'prefer-named-capture-group': 'error',
    'prefer-promise-reject-errors': 'error',
    'radix': 'error',
    'require-await': 'error',
    'require-unicode-regexp': 'off',
    'vars-on-top': 'error',
    'wrap-iife': ['error', 'any'],
    'yoda': 'error'
  },
  settings: {
    react: {
      version: 'detect'
    }
  }
};
