import { vi } from 'vitest';

// Configuration des tests E2E
export const e2eTestConfig = {
  timeout: 30000,
  retries: 1,
  setupFilesAfterEnv: ['<rootDir>/src/test/e2e/setup.ts'],
  testEnvironment: 'node',
  testMatch: ['**/*.e2e.test.ts', '**/*.e2e.spec.ts'],
};

// Mocks pour les tests E2E
export const setupE2EMocks = () => {
  // Mock de l'environnement navigateur
  global.navigator = {
    ...global.navigator,
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    language: 'fr-FR',
    languages: ['fr-FR', 'fr', 'en'],
    cookieEnabled: true,
    onLine: true,
    platform: 'Win32',
  };

  // Mock de l'écran
  global.screen = {
    width: 1920,
    height: 1080,
    availWidth: 1920,
    availHeight: 1040,
    colorDepth: 24,
    pixelDepth: 24,
  };

  // Mock de la géolocalisation
  global.navigator.geolocation = {
    getCurrentPosition: vi.fn(),
    watchPosition: vi.fn(),
    clearWatch: vi.fn(),
  };

  // Mock des permissions
  global.navigator.permissions = {
    query: vi.fn().mockResolvedValue({ state: 'granted' }),
  };

  // Mock des notifications
  global.Notification = vi.fn().mockImplementation(() => ({
    requestPermission: vi.fn().mockResolvedValue('granted'),
    permission: 'granted',
  }));

  // Mock de l'indexedDB
  global.indexedDB = {
    open: vi.fn(),
    deleteDatabase: vi.fn(),
    cmp: vi.fn(),
  };

  // Mock de localStorage
  const localStorageMock = {
    getItem: vi.fn(),
    setItem: vi.fn(),
    removeItem: vi.fn(),
    clear: vi.fn(),
    key: vi.fn(),
    length: 0,
  };
  global.localStorage = localStorageMock;

  // Mock de sessionStorage
  const sessionStorageMock = {
    getItem: vi.fn(),
    setItem: vi.fn(),
    removeItem: vi.fn(),
    clear: vi.fn(),
    key: vi.fn(),
    length: 0,
  };
  global.sessionStorage = sessionStorageMock;

  // Mock de fetch
  global.fetch = vi.fn();

  // Mock de WebSocket
  global.WebSocket = vi.fn().mockImplementation(() => ({
    send: vi.fn(),
    close: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    readyState: 1,
    CONNECTING: 0,
    OPEN: 1,
    CLOSING: 2,
    CLOSED: 3,
  }));

  // Mock de XMLHttpRequest
  global.XMLHttpRequest = vi.fn().mockImplementation(() => ({
    open: vi.fn(),
    send: vi.fn(),
    setRequestHeader: vi.fn(),
    getResponseHeader: vi.fn(),
    getAllResponseHeaders: vi.fn(),
    readyState: 4,
    status: 200,
    statusText: 'OK',
    responseText: '',
    response: '',
    responseType: '',
    responseURL: '',
    timeout: 0,
    withCredentials: false,
    onreadystatechange: null,
    onload: null,
    onerror: null,
    ontimeout: null,
    upload: {},
    DONE: 4,
    HEADERS_RECEIVED: 2,
    LOADING: 3,
    OPENED: 1,
    UNSENT: 0,
  }));

  // Mock de FormData
  global.FormData = vi.fn().mockImplementation(() => ({
    append: vi.fn(),
    delete: vi.fn(),
    get: vi.fn(),
    getAll: vi.fn(),
    has: vi.fn(),
    set: vi.fn(),
    forEach: vi.fn(),
    entries: vi.fn(),
    keys: vi.fn(),
    values: vi.fn(),
  }));

  // Mock de FileReader
  global.FileReader = vi.fn().mockImplementation(() => ({
    readAsText: vi.fn(),
    readAsDataURL: vi.fn(),
    readAsArrayBuffer: vi.fn(),
    readAsBinaryString: vi.fn(),
    abort: vi.fn(),
    readyState: 0,
    result: null,
    error: null,
    onload: null,
    onerror: null,
    onabort: null,
    onloadstart: null,
    onloadend: null,
    onprogress: null,
    EMPTY: 0,
    LOADING: 1,
    DONE: 2,
  }));

  // Mock de File
  global.File = vi.fn().mockImplementation(() => ({
    name: 'mock-file.txt',
    size: 1024,
    type: 'text/plain',
    lastModified: Date.now(),
    slice: vi.fn(),
    stream: vi.fn(),
    text: vi.fn(),
    arrayBuffer: vi.fn(),
  }));

  // Mock de Blob
  global.Blob = vi.fn().mockImplementation(() => ({
    size: 1024,
    type: 'text/plain',
    slice: vi.fn(),
    stream: vi.fn(),
    text: vi.fn(),
    arrayBuffer: vi.fn(),
  }));

  // Mock de URL
  global.URL = vi.fn().mockImplementation(() => ({
    href: 'https://example.com',
    origin: 'https://example.com',
    protocol: 'https:',
    username: '',
    password: '',
    host: 'example.com',
    hostname: 'example.com',
    port: '',
    pathname: '/',
    search: '',
    searchParams: new URLSearchParams(),
    hash: '',
    toJSON: vi.fn(),
  }));

  // Mock de URLSearchParams
  global.URLSearchParams = vi.fn().mockImplementation(() => ({
    append: vi.fn(),
    delete: vi.fn(),
    get: vi.fn(),
    getAll: vi.fn(),
    has: vi.fn(),
    set: vi.fn(),
    sort: vi.fn(),
    toString: vi.fn(),
    forEach: vi.fn(),
    entries: vi.fn(),
    keys: vi.fn(),
    values: vi.fn(),
  }));

  // Mock de Headers
  global.Headers = vi.fn().mockImplementation(() => ({
    append: vi.fn(),
    delete: vi.fn(),
    get: vi.fn(),
    has: vi.fn(),
    set: vi.fn(),
    forEach: vi.fn(),
    entries: vi.fn(),
    keys: vi.fn(),
    values: vi.fn(),
  }));

  // Mock de Request
  global.Request = vi.fn().mockImplementation(() => ({
    method: 'GET',
    url: 'https://example.com',
    headers: new Headers(),
    body: null,
    bodyUsed: false,
    cache: 'default',
    credentials: 'same-origin',
    destination: '',
    integrity: '',
    keepalive: false,
    mode: 'cors',
    redirect: 'follow',
    referrer: 'about:client',
    referrerPolicy: '',
    signal: null,
    clone: vi.fn(),
    arrayBuffer: vi.fn(),
    blob: vi.fn(),
    formData: vi.fn(),
    json: vi.fn(),
    text: vi.fn(),
  }));

  // Mock de Response
  global.Response = vi.fn().mockImplementation(() => ({
    type: 'default',
    url: 'https://example.com',
    status: 200,
    ok: true,
    statusText: 'OK',
    headers: new Headers(),
    body: null,
    bodyUsed: false,
    clone: vi.fn(),
    arrayBuffer: vi.fn(),
    blob: vi.fn(),
    formData: vi.fn(),
    json: vi.fn(),
    text: vi.fn(),
  }));

  // Mock de AbortController
  global.AbortController = vi.fn().mockImplementation(() => ({
    signal: {
      aborted: false,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    },
    abort: vi.fn(),
  }));

  // Mock de AbortSignal
  global.AbortSignal = vi.fn().mockImplementation(() => ({
    aborted: false,
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  }));

  // Mock de TextEncoder
  global.TextEncoder = vi.fn().mockImplementation(() => ({
    encode: vi.fn(),
    encodeInto: vi.fn(),
  }));

  // Mock de TextDecoder
  global.TextDecoder = vi.fn().mockImplementation(() => ({
    decode: vi.fn(),
    encoding: 'utf-8',
    fatal: false,
    ignoreBOM: false,
  }));

  // Mock de crypto
  global.crypto = {
    getRandomValues: vi.fn(),
    randomUUID: vi.fn(),
    subtle: {
      generateKey: vi.fn(),
      importKey: vi.fn(),
      exportKey: vi.fn(),
      encrypt: vi.fn(),
      decrypt: vi.fn(),
      sign: vi.fn(),
      verify: vi.fn(),
      digest: vi.fn(),
      deriveKey: vi.fn(),
      deriveBits: vi.fn(),
      wrapKey: vi.fn(),
      unwrapKey: vi.fn(),
    },
  };

  // Mock de performance
  global.performance = {
    now: vi.fn(),
    timeOrigin: Date.now(),
    mark: vi.fn(),
    measure: vi.fn(),
    clearMarks: vi.fn(),
    clearMeasures: vi.fn(),
    getEntries: vi.fn(),
    getEntriesByName: vi.fn(),
    getEntriesByType: vi.fn(),
    toJSON: vi.fn(),
  };

  // Mock de requestAnimationFrame
  global.requestAnimationFrame = vi.fn((callback) => {
    setTimeout(callback, 16);
    return 1;
  });

  // Mock de cancelAnimationFrame
  global.cancelAnimationFrame = vi.fn();

  // Mock de requestIdleCallback
  global.requestIdleCallback = vi.fn((callback) => {
    setTimeout(callback, 1);
    return 1;
  });

  // Mock de cancelIdleCallback
  global.cancelIdleCallback = vi.fn();

  // Mock de IntersectionObserver
  global.IntersectionObserver = vi.fn().mockImplementation(() => ({
    observe: vi.fn(),
    unobserve: vi.fn(),
    disconnect: vi.fn(),
  }));

  // Mock de ResizeObserver
  global.ResizeObserver = vi.fn().mockImplementation(() => ({
    observe: vi.fn(),
    unobserve: vi.fn(),
    disconnect: vi.fn(),
  }));

  // Mock de MutationObserver
  global.MutationObserver = vi.fn().mockImplementation(() => ({
    observe: vi.fn(),
    disconnect: vi.fn(),
    takeRecords: vi.fn(),
  }));

  // Mock de matchMedia
  global.matchMedia = vi.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  }));

  // Mock de console
  global.console = {
    ...console,
    log: vi.fn(),
    debug: vi.fn(),
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
    assert: vi.fn(),
    clear: vi.fn(),
    count: vi.fn(),
    countReset: vi.fn(),
    dir: vi.fn(),
    dirxml: vi.fn(),
    group: vi.fn(),
    groupCollapsed: vi.fn(),
    groupEnd: vi.fn(),
    table: vi.fn(),
    time: vi.fn(),
    timeEnd: vi.fn(),
    timeLog: vi.fn(),
    trace: vi.fn(),
    profile: vi.fn(),
    profileEnd: vi.fn(),
  };
};

// Configuration des tests E2E
export const setupE2ETest = () => {
  setupE2EMocks();
  
  // Configuration des timeouts
  vi.setConfig({
    testTimeout: 30000,
    hookTimeout: 10000,
  });
  
  // Configuration des retries
  vi.retry(1);
};
