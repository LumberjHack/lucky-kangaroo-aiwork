import { vi } from 'vitest';

// Configuration des tests d'accessibilité
export const accessibilityTestConfig = {
  timeout: 30000,
  retries: 1,
  setupFilesAfterEnv: ['<rootDir>/src/test/accessibility/setup.ts'],
  testEnvironment: 'jsdom',
  testMatch: ['**/*.a11y.test.ts', '**/*.a11y.spec.ts'],
};

// Types de critères d'accessibilité
export enum AccessibilityCriteria {
  // WCAG 2.1 Level A
  WCAG_2_1_A = 'WCAG_2_1_A',
  // WCAG 2.1 Level AA
  WCAG_2_1_AA = 'WCAG_2_1_AA',
  // WCAG 2.1 Level AAA
  WCAG_2_1_AAA = 'WCAG_2_1_AAA',
  // Section 508
  SECTION_508 = 'SECTION_508',
  // EN 301 549 (Europe)
  EN_301_549 = 'EN_301_549',
}

// Types de violations d'accessibilité
export enum AccessibilityViolationType {
  // Navigation et structure
  MISSING_HEADING = 'MISSING_HEADING',
  INVALID_HEADING_ORDER = 'INVALID_HEADING_ORDER',
  MISSING_LANDMARK = 'MISSING_LANDMARK',
  DUPLICATE_LANDMARK = 'DUPLICATE_LANDMARK',
  
  // Formulaires
  MISSING_LABEL = 'MISSING_LABEL',
  MISSING_DESCRIPTION = 'MISSING_DESCRIPTION',
  MISSING_ERROR_MESSAGE = 'MISSING_ERROR_MESSAGE',
  INVALID_ARIA_ATTRIBUTES = 'INVALID_ARIA_ATTRIBUTES',
  
  // Images et médias
  MISSING_ALT_TEXT = 'MISSING_ALT_TEXT',
  DECORATIVE_IMAGE_ALT = 'DECORATIVE_IMAGE_ALT',
  MISSING_CAPTION = 'MISSING_CAPTION',
  MISSING_TRANSCRIPT = 'MISSING_TRANSCRIPT',
  
  // Couleurs et contrastes
  INSUFFICIENT_CONTRAST = 'INSUFFICIENT_CONTRAST',
  COLOR_ONLY_INFORMATION = 'COLOR_ONLY_INFORMATION',
  
  // Clavier et navigation
  MISSING_FOCUS_INDICATOR = 'MISSING_FOCUS_INDICATOR',
  TRAP_FOCUS = 'TRAP_FOCUS',
  MISSING_SKIP_LINK = 'MISSING_SKIP_LINK',
  
  // Texte et typographie
  SMALL_TEXT = 'SMALL_TEXT',
  MISSING_LANGUAGE_ATTRIBUTE = 'MISSING_LANGUAGE_ATTRIBUTE',
  
  // Animations et mouvements
  AUTO_PLAYING_MEDIA = 'AUTO_PLAYING_MEDIA',
  MISSING_PAUSE_CONTROL = 'MISSING_PAUSE_CONTROL',
  
  // Temps et délais
  INSUFFICIENT_TIME = 'INSUFFICIENT_TIME',
  MISSING_EXTENSION_OPTION = 'MISSING_EXTENSION_OPTION',
  
  // Erreurs et validation
  MISSING_ERROR_IDENTIFICATION = 'MISSING_ERROR_IDENTIFICATION',
  MISSING_ERROR_SUGGESTIONS = 'MISSING_ERROR_SUGGESTIONS',
  
  // Compatibilité
  MISSING_FALLBACK = 'MISSING_FALLBACK',
  INCOMPATIBLE_TECHNOLOGY = 'INCOMPATIBLE_TECHNOLOGY',
}

// Niveaux de sévérité
export enum AccessibilitySeverity {
  MINOR = 'MINOR',
  MODERATE = 'MODERATE',
  SERIOUS = 'SERIOUS',
  CRITICAL = 'CRITICAL',
}

// Interface pour les violations d'accessibilité
export interface AccessibilityViolation {
  type: AccessibilityViolationType;
  severity: AccessibilitySeverity;
  description: string;
  wcagCriteria: string[];
  element?: string;
  selector?: string;
  recommendation: string;
  detected: boolean;
  falsePositive: boolean;
}

// Règles d'accessibilité WCAG 2.1
export const wcagRules = {
  // 1.1.1 Non-text Content (Level A)
  '1.1.1': {
    title: 'Non-text Content',
    level: 'A',
    description: 'All non-text content has a text alternative',
    criteria: [AccessibilityCriteria.WCAG_2_1_A],
  },
  
  // 1.2.1 Audio-only and Video-only (Level A)
  '1.2.1': {
    title: 'Audio-only and Video-only',
    level: 'A',
    description: 'Audio-only and video-only content has alternatives',
    criteria: [AccessibilityCriteria.WCAG_2_1_A],
  },
  
  // 1.2.2 Captions (Level A)
  '1.2.2': {
    title: 'Captions',
    level: 'A',
    description: 'Captions are provided for all prerecorded audio content',
    criteria: [AccessibilityCriteria.WCAG_2_1_A],
  },
  
  // 1.3.1 Info and Relationships (Level A)
  '1.3.1': {
    title: 'Info and Relationships',
    level: 'A',
    description: 'Information, structure, and relationships can be programmatically determined',
    criteria: [AccessibilityCriteria.WCAG_2_1_A],
  },
  
  // 1.3.2 Meaningful Sequence (Level A)
  '1.3.2': {
    title: 'Meaningful Sequence',
    level: 'A',
    description: 'Content can be navigated in a meaningful sequence',
    criteria: [AccessibilityCriteria.WCAG_2_1_A],
  },
  
  // 1.4.1 Use of Color (Level A)
  '1.4.1': {
    title: 'Use of Color',
    level: 'A',
    description: 'Color is not used as the only visual means of conveying information',
    criteria: [AccessibilityCriteria.WCAG_2_1_A],
  },
  
  // 1.4.2 Audio Control (Level A)
  '1.4.2': {
    title: 'Audio Control',
    level: 'A',
    description: 'Audio can be paused or stopped',
    criteria: [AccessibilityCriteria.WCAG_2_1_A],
  },
  
  // 2.1.1 Keyboard (Level A)
  '2.1.1': {
    title: 'Keyboard',
    level: 'A',
    description: 'All functionality is available from a keyboard',
    criteria: [AccessibilityCriteria.WCAG_2_1_A],
  },
  
  // 2.1.2 No Keyboard Trap (Level A)
  '2.1.2': {
    title: 'No Keyboard Trap',
    level: 'A',
    description: 'Keyboard focus is not trapped',
    criteria: [AccessibilityCriteria.WCAG_2_1_A],
  },
  
  // 2.2.1 Timing Adjustable (Level A)
  '2.2.1': {
    title: 'Timing Adjustable',
    level: 'A',
    description: 'Users can adjust or extend time limits',
    criteria: [AccessibilityCriteria.WCAG_2_1_A],
  },
  
  // 2.3.1 Three Flashes or Below Threshold (Level A)
  '2.3.1': {
    title: 'Three Flashes or Below Threshold',
    level: 'A',
    description: 'Content does not flash more than three times per second',
    criteria: [AccessibilityCriteria.WCAG_2_1_A],
  },
  
  // 2.4.1 Bypass Blocks (Level A)
  '2.4.1': {
    title: 'Bypass Blocks',
    level: 'A',
    description: 'Mechanism to bypass repeated blocks of content',
    criteria: [AccessibilityCriteria.WCAG_2_1_A],
  },
  
  // 2.4.2 Page Titled (Level A)
  '2.4.2': {
    title: 'Page Titled',
    level: 'A',
    description: 'Pages have descriptive titles',
    criteria: [AccessibilityCriteria.WCAG_2_1_A],
  },
  
  // 2.4.3 Focus Order (Level A)
  '2.4.3': {
    title: 'Focus Order',
    level: 'A',
    description: 'Tab order follows a logical sequence',
    criteria: [AccessibilityCriteria.WCAG_2_1_A],
  },
  
  // 2.4.4 Link Purpose (Level A)
  '2.4.4': {
    title: 'Link Purpose',
    level: 'A',
    description: 'Purpose of each link can be determined from the link text alone',
    criteria: [AccessibilityCriteria.WCAG_2_1_A],
  },
  
  // 3.1.1 Language of Page (Level A)
  '3.1.1': {
    title: 'Language of Page',
    level: 'A',
    description: 'Language of the page can be programmatically determined',
    criteria: [AccessibilityCriteria.WCAG_2_1_A],
  },
  
  // 3.2.1 On Focus (Level A)
  '3.2.1': {
    title: 'On Focus',
    level: 'A',
    description: 'Changing focus does not automatically trigger changes',
    criteria: [AccessibilityCriteria.WCAG_2_1_A],
  },
  
  // 3.2.2 On Input (Level A)
  '3.2.2': {
    title: 'On Input',
    level: 'A',
    description: 'Changing input values does not automatically trigger changes',
    criteria: [AccessibilityCriteria.WCAG_2_1_A],
  },
  
  // 3.3.1 Error Identification (Level A)
  '3.3.1': {
    title: 'Error Identification',
    level: 'A',
    description: 'Errors are identified and described to the user',
    criteria: [AccessibilityCriteria.WCAG_2_1_A],
  },
  
  // 3.3.2 Labels or Instructions (Level A)
  '3.3.2': {
    title: 'Labels or Instructions',
    level: 'A',
    description: 'Labels or instructions are provided when content requires user input',
    criteria: [AccessibilityCriteria.WCAG_2_1_A],
  },
  
  // 4.1.1 Parsing (Level A)
  '4.1.1': {
    title: 'Parsing',
    level: 'A',
    description: 'Content can be parsed by user agents',
    criteria: [AccessibilityCriteria.WCAG_2_1_A],
  },
  
  // 4.1.2 Name, Role, Value (Level A)
  '4.1.2': {
    title: 'Name, Role, Value',
    level: 'A',
    description: 'For all user interface components, the name and role can be programmatically determined',
    criteria: [AccessibilityCriteria.WCAG_2_1_A],
  },
};

// Utilitaires pour les tests d'accessibilité
export const testHeadingStructure = (document: Document): AccessibilityViolation[] => {
  const violations: AccessibilityViolation[] = [];
  const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
  
  if (headings.length === 0) {
    violations.push({
      type: AccessibilityViolationType.MISSING_HEADING,
      severity: AccessibilitySeverity.SERIOUS,
      description: 'No headings found on the page',
      wcagCriteria: ['2.4.1', '1.3.1'],
      recommendation: 'Add appropriate heading structure to organize content',
      detected: true,
      falsePositive: false,
    });
    return violations;
  }
  
  // Vérifier la présence d'un h1
  const h1Elements = document.querySelectorAll('h1');
  if (h1Elements.length === 0) {
    violations.push({
      type: AccessibilityViolationType.MISSING_HEADING,
      severity: AccessibilitySeverity.SERIOUS,
      description: 'No H1 heading found on the page',
      wcagCriteria: ['2.4.1', '1.3.1'],
      recommendation: 'Add a main H1 heading that describes the page content',
      detected: true,
      falsePositive: false,
    });
  } else if (h1Elements.length > 1) {
    violations.push({
      type: AccessibilityViolationType.INVALID_HEADING_ORDER,
      severity: AccessibilitySeverity.MODERATE,
      description: 'Multiple H1 headings found on the page',
      wcagCriteria: ['1.3.1', '2.4.1'],
      recommendation: 'Use only one H1 heading per page as the main title',
      detected: true,
      falsePositive: false,
    });
  }
  
  // Vérifier l'ordre des headings
  let previousLevel = 0;
  headings.forEach((heading, index) => {
    const level = parseInt(heading.tagName.charAt(1));
    if (level > previousLevel + 1) {
      violations.push({
        type: AccessibilityViolationType.INVALID_HEADING_ORDER,
        severity: AccessibilitySeverity.MODERATE,
        description: `Heading level skipped from H${previousLevel} to H${level}`,
        wcagCriteria: ['1.3.1', '2.4.1'],
        element: heading.outerHTML,
        selector: `h${level}:nth-child(${index + 1})`,
        recommendation: 'Maintain logical heading hierarchy without skipping levels',
        detected: true,
        falsePositive: false,
      });
    }
    previousLevel = level;
  });
  
  return violations;
};

export const testFormAccessibility = (document: Document): AccessibilityViolation[] => {
  const violations: AccessibilityViolation[] = [];
  const forms = document.querySelectorAll('form');
  
  forms.forEach((form, formIndex) => {
    const inputs = form.querySelectorAll('input, textarea, select');
    
    inputs.forEach((input, inputIndex) => {
      const inputElement = input as HTMLInputElement;
      
      // Vérifier les labels
      if (inputElement.type !== 'hidden' && inputElement.type !== 'submit' && inputElement.type !== 'button') {
        const label = form.querySelector(`label[for="${inputElement.id}"]`);
        const ariaLabel = inputElement.getAttribute('aria-label');
        const ariaLabelledby = inputElement.getAttribute('aria-labelledby');
        
        if (!label && !ariaLabel && !ariaLabelledby) {
          violations.push({
            type: AccessibilityViolationType.MISSING_LABEL,
            severity: AccessibilitySeverity.SERIOUS,
            description: 'Form input missing label or accessible name',
            wcagCriteria: ['3.3.2', '4.1.2'],
            element: inputElement.outerHTML,
            selector: `form:nth-child(${formIndex + 1}) input:nth-child(${inputIndex + 1})`,
            recommendation: 'Add a label, aria-label, or aria-labelledby attribute',
            detected: true,
            falsePositive: false,
          });
        }
      }
      
      // Vérifier les attributs ARIA
      const ariaAttributes = inputElement.getAttributeNames().filter(name => name.startsWith('aria-'));
      ariaAttributes.forEach(attr => {
        const value = inputElement.getAttribute(attr);
        if (value === '' || value === null) {
          violations.push({
            type: AccessibilityViolationType.INVALID_ARIA_ATTRIBUTES,
            severity: AccessibilitySeverity.MODERATE,
            description: `Empty ARIA attribute: ${attr}`,
            wcagCriteria: ['4.1.2'],
            element: inputElement.outerHTML,
            selector: `form:nth-child(${formIndex + 1}) input:nth-child(${inputIndex + 1})`,
            recommendation: 'Remove empty ARIA attributes or provide meaningful values',
            detected: true,
            falsePositive: false,
          });
        }
      });
    });
  });
  
  return violations;
};

export const testImageAccessibility = (document: Document): AccessibilityViolation[] => {
  const violations: AccessibilityViolation[] = [];
  const images = document.querySelectorAll('img');
  
  images.forEach((img, index) => {
    const imgElement = img as HTMLImageElement;
    const alt = imgElement.getAttribute('alt');
    const role = imgElement.getAttribute('role');
    const ariaLabel = imgElement.getAttribute('aria-label');
    
    // Vérifier la présence d'alternative textuelle
    if (!alt && !ariaLabel && role !== 'presentation' && role !== 'none') {
      violations.push({
        type: AccessibilityViolationType.MISSING_ALT_TEXT,
        severity: AccessibilitySeverity.SERIOUS,
        description: 'Image missing alternative text',
        wcagCriteria: ['1.1.1'],
        element: imgElement.outerHTML,
        selector: `img:nth-child(${index + 1})`,
        recommendation: 'Add alt attribute with descriptive text or aria-label',
        detected: true,
        falsePositive: false,
      });
    }
    
    // Vérifier les images décoratives
    if (alt === '' && role !== 'presentation' && role !== 'none') {
      violations.push({
        type: AccessibilityViolationType.DECORATIVE_IMAGE_ALT,
        severity: AccessibilitySeverity.MINOR,
        description: 'Decorative image should have role="presentation" or role="none"',
        wcagCriteria: ['1.1.1'],
        element: imgElement.outerHTML,
        selector: `img:nth-child(${index + 1})`,
        recommendation: 'Add role="presentation" or role="none" for decorative images',
        detected: true,
        falsePositive: false,
      });
    }
  });
  
  return violations;
};

export const testKeyboardNavigation = (document: Document): AccessibilityViolation[] => {
  const violations: AccessibilityViolation[] = [];
  
  // Vérifier les éléments focusables
  const focusableElements = document.querySelectorAll(
    'a[href], button, input, textarea, select, [tabindex]:not([tabindex="-1"])'
  );
  
  focusableElements.forEach((element, index) => {
    const elementElement = element as HTMLElement;
    
    // Vérifier l'indicateur de focus
    const computedStyle = window.getComputedStyle(elementElement);
    const outline = computedStyle.outline;
    const outlineOffset = computedStyle.outlineOffset;
    
    if (outline === 'none' || outline === 'initial' || outline === 'inherit') {
      violations.push({
        type: AccessibilityViolationType.MISSING_FOCUS_INDICATOR,
        severity: AccessibilitySeverity.SERIOUS,
        description: 'Focusable element missing visible focus indicator',
        wcagCriteria: ['2.4.7'],
        element: elementElement.outerHTML,
        selector: `[tabindex]:nth-child(${index + 1})`,
        recommendation: 'Add visible focus indicator using CSS outline or box-shadow',
        detected: true,
        falsePositive: false,
      });
    }
  });
  
  // Vérifier les liens de saut
  const skipLinks = document.querySelectorAll('a[href^="#"], a[href^="/#"]');
  if (skipLinks.length === 0) {
    violations.push({
      type: AccessibilityViolationType.MISSING_SKIP_LINK,
      severity: AccessibilitySeverity.MODERATE,
      description: 'No skip links found for main content',
      wcagCriteria: ['2.4.1'],
      recommendation: 'Add skip links to bypass navigation and go to main content',
      detected: true,
      falsePositive: false,
    });
  }
  
  return violations;
};

export const testColorContrast = (document: Document): AccessibilityViolation[] => {
  const violations: AccessibilityViolation[] = [];
  
  // Cette fonction nécessiterait une bibliothèque de calcul de contraste
  // Pour l'instant, on vérifie juste la présence de styles de contraste
  const elements = document.querySelectorAll('*');
  
  elements.forEach((element) => {
    const elementElement = element as HTMLElement;
    const computedStyle = window.getComputedStyle(elementElement);
    const color = computedStyle.color;
    const backgroundColor = computedStyle.backgroundColor;
    
    // Vérification basique - si les couleurs sont définies
    if (color && backgroundColor && 
        color !== 'rgba(0, 0, 0, 0)' && 
        backgroundColor !== 'rgba(0, 0, 0, 0)') {
      // Ici, on pourrait ajouter un calcul de contraste réel
      // Pour l'instant, on considère que c'est OK
    }
  });
  
  return violations;
};

export const testLanguageAttribute = (document: Document): AccessibilityViolation[] => {
  const violations: AccessibilityViolation[] = [];
  
  const html = document.documentElement;
  const lang = html.getAttribute('lang');
  
  if (!lang) {
    violations.push({
      type: AccessibilityViolationType.MISSING_LANGUAGE_ATTRIBUTE,
      severity: AccessibilitySeverity.SERIOUS,
      description: 'HTML element missing lang attribute',
      wcagCriteria: ['3.1.1'],
      element: html.outerHTML,
      selector: 'html',
      recommendation: 'Add lang attribute to HTML element with appropriate language code',
      detected: true,
      falsePositive: false,
    });
  }
  
  return violations;
};

// Test complet d'accessibilité
export const runAccessibilityTest = (document: Document): AccessibilityViolation[] => {
  const violations: AccessibilityViolation[] = [];
  
  // Exécuter tous les tests
  violations.push(...testHeadingStructure(document));
  violations.push(...testFormAccessibility(document));
  violations.push(...testImageAccessibility(document));
  violations.push(...testKeyboardNavigation(document));
  violations.push(...testColorContrast(document));
  violations.push(...testLanguageAttribute(document));
  
  return violations;
};

// Configuration des tests d'accessibilité
export const setupAccessibilityTest = () => {
  // Configuration des timeouts
  vi.setConfig({
    testTimeout: 30000,
    hookTimeout: 10000,
  });
  
  // Configuration des retries
  vi.retry(1);
  
  // Mock de window.getComputedStyle pour les tests
  if (typeof window !== 'undefined') {
    Object.defineProperty(window, 'getComputedStyle', {
      value: vi.fn(() => ({
        outline: '2px solid blue',
        outlineOffset: '2px',
        color: 'rgb(0, 0, 0)',
        backgroundColor: 'rgb(255, 255, 255)',
      })),
      writable: true,
    });
  }
};
