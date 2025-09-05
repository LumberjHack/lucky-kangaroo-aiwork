import { User, Listing, Exchange, ChatMessage } from '../types';

// Types pour les tests
export interface TestUser extends Partial<User> {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
}

export interface TestListing extends Partial<Listing> {
  id: string;
  title: string;
  description: string;
  price: number;
  userId: string;
}

export interface TestExchange extends Partial<Exchange> {
  id: string;
  listingId: string;
  proposerId: string;
  status: string;
}

export interface TestChatMessage extends Partial<ChatMessage> {
  id: string;
  content: string;
  senderId: string;
  roomId: string;
}

// Données de test
export const mockUsers: TestUser[] = [
  {
    id: '1',
    email: 'test1@example.com',
    firstName: 'John',
    lastName: 'Doe',
    trustScore: 85,
    isEmailVerified: true,
    isPremium: false,
  },
  {
    id: '2',
    email: 'test2@example.com',
    firstName: 'Jane',
    lastName: 'Smith',
    trustScore: 92,
    isEmailVerified: true,
    isPremium: true,
  },
];

export const mockListings: TestListing[] = [
  {
    id: '1',
    title: 'iPhone 12 Pro',
    description: 'Excellent état, boîte d\'origine',
    price: 500,
    userId: '1',
    category: 'Électronique',
    condition: 'Excellent',
    location: 'Paris, France',
  },
  {
    id: '2',
    title: 'Vélo VTT',
    description: 'Vélo de montagne en bon état',
    price: 200,
    userId: '2',
    category: 'Sport',
    condition: 'Bon',
    location: 'Lyon, France',
  },
];

export const mockExchanges: TestExchange[] = [
  {
    id: '1',
    listingId: '1',
    proposerId: '2',
    status: 'pending',
    createdAt: new Date().toISOString(),
  },
  {
    id: '2',
    listingId: '2',
    proposerId: '1',
    status: 'accepted',
    createdAt: new Date().toISOString(),
  },
];

export const mockChatMessages: TestChatMessage[] = [
  {
    id: '1',
    content: 'Bonjour, votre iPhone est-il toujours disponible ?',
    senderId: '2',
    roomId: '1',
    timestamp: new Date().toISOString(),
  },
  {
    id: '2',
    content: 'Oui, il est toujours disponible !',
    senderId: '1',
    roomId: '1',
    timestamp: new Date().toISOString(),
  },
];

// Utilitaires pour les tests
export const createMockUser = (overrides: Partial<TestUser> = {}): TestUser => ({
  id: 'mock-user-id',
  email: 'mock@example.com',
  firstName: 'Mock',
  lastName: 'User',
  trustScore: 80,
  isEmailVerified: true,
  isPremium: false,
  ...overrides,
});

export const createMockListing = (overrides: Partial<TestListing> = {}): TestListing => ({
  id: 'mock-listing-id',
  title: 'Mock Listing',
  description: 'Mock description',
  price: 100,
  userId: 'mock-user-id',
  category: 'Mock Category',
  condition: 'Bon',
  location: 'Mock Location',
  ...overrides,
});

export const createMockExchange = (overrides: Partial<TestExchange> = {}): TestExchange => ({
  id: 'mock-exchange-id',
  listingId: 'mock-listing-id',
  proposerId: 'mock-proposer-id',
  status: 'pending',
  createdAt: new Date().toISOString(),
  ...overrides,
});

export const createMockChatMessage = (overrides: Partial<TestChatMessage> = {}): TestChatMessage => ({
  id: 'mock-message-id',
  content: 'Mock message content',
  senderId: 'mock-sender-id',
  roomId: 'mock-room-id',
  timestamp: new Date().toISOString(),
  ...overrides,
});
