import { io, Socket } from 'socket.io-client';
import api from './api';

export interface ChatMessage {
  id: string;
  message: string;
  message_type: string;
  attachment_url?: string;
  attachment_filename?: string;
  location?: {
    latitude: number;
    longitude: number;
    name: string;
  };
  reply_to_id?: string;
  is_edited: boolean;
  edited_at?: string;
  user: {
    id: string;
    username: string;
    first_name: string;
    last_name: string;
    profile_picture?: string;
  };
  created_at: string;
}

export interface ChatParticipant {
  id: string;
  username: string;
  first_name: string;
  last_name: string;
  profile_picture?: string;
  role: string;
  is_admin: boolean;
  joined_at: string;
  last_activity_at: string;
}

export interface Chat {
  id: string;
  type: string;
  name: string;
  description?: string;
  avatar_url?: string;
  status: string;
  participants_count: number;
  last_message?: ChatMessage;
  unread_count: number;
  created_at: string;
  updated_at: string;
  listing?: {
    id: string;
    title: string;
    images: string[];
  };
  exchange?: {
    id: string;
    title: string;
    status: string;
  };
}

export interface ChatDetails extends Chat {
  participants: ChatParticipant[];
}

class ChatService {
  private socket: Socket | null = null;
  private isConnected = false;
  private eventListeners: Map<string, Function[]> = new Map();

  // Initialiser la connexion WebSocket
  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      const token = localStorage.getItem('access_token');
      if (!token) {
        reject(new Error('Token d\'authentification manquant'));
        return;
      }

      this.socket = io('http://localhost:5000', {
        auth: {
          token: token
        },
        transports: ['websocket', 'polling']
      });

      this.socket.on('connect', () => {
        console.log('Connecté au serveur WebSocket');
        this.isConnected = true;
        this.emit('connected');
        resolve();
      });

      this.socket.on('disconnect', () => {
        console.log('Déconnecté du serveur WebSocket');
        this.isConnected = false;
        this.emit('disconnected');
      });

      this.socket.on('connect_error', (error) => {
        console.error('Erreur de connexion WebSocket:', error);
        this.isConnected = false;
        this.emit('connection_error', error);
        reject(error);
      });

      // Écouter les événements de chat
      this.socket.on('new_message', (message: ChatMessage) => {
        this.emit('new_message', message);
      });

      this.socket.on('user_typing', (data: { user_id: string; is_typing: boolean; chat_id: string }) => {
        this.emit('user_typing', data);
      });

      this.socket.on('user_joined', (data: { user_id: string; chat_id: string }) => {
        this.emit('user_joined', data);
      });

      this.socket.on('user_left', (data: { user_id: string; chat_id: string }) => {
        this.emit('user_left', data);
      });

      this.socket.on('message_read', (data: { message_id: string; user_id: string; chat_id: string }) => {
        this.emit('message_read', data);
      });
    });
  }

  // Déconnecter
  disconnect(): void {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
      this.isConnected = false;
    }
  }

  // Rejoindre un chat
  joinChat(chatId: string): void {
    if (this.socket && this.isConnected) {
      this.socket.emit('join_chat', { chat_id: chatId });
    }
  }

  // Quitter un chat
  leaveChat(chatId: string): void {
    if (this.socket && this.isConnected) {
      this.socket.emit('leave_chat', { chat_id: chatId });
    }
  }

  // Indiquer que l'utilisateur tape
  startTyping(chatId: string): void {
    if (this.socket && this.isConnected) {
      this.socket.emit('typing_start', { chat_id: chatId });
    }
  }

  // Arrêter l'indicateur de frappe
  stopTyping(chatId: string): void {
    if (this.socket && this.isConnected) {
      this.socket.emit('typing_stop', { chat_id: chatId });
    }
  }

  // Marquer un message comme lu
  markMessageAsRead(messageId: string, chatId: string): void {
    if (this.socket && this.isConnected) {
      this.socket.emit('message_read', { message_id: messageId, chat_id: chatId });
    }
  }

  // Gestion des événements
  on(event: string, callback: Function): void {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, []);
    }
    this.eventListeners.get(event)!.push(callback);
  }

  off(event: string, callback: Function): void {
    const listeners = this.eventListeners.get(event);
    if (listeners) {
      const index = listeners.indexOf(callback);
      if (index > -1) {
        listeners.splice(index, 1);
      }
    }
  }

  private emit(event: string, data?: any): void {
    const listeners = this.eventListeners.get(event);
    if (listeners) {
      listeners.forEach(callback => callback(data));
    }
  }

  // API REST pour les chats
  async getChats(): Promise<Chat[]> {
    try {
      const response = await api.get('/chat/chats');
      return response.data.chats || [];
    } catch (error) {
      console.error('Erreur lors de la récupération des chats:', error);
      throw error;
    }
  }

  async getChatDetails(chatId: string): Promise<ChatDetails> {
    try {
      const response = await api.get(`/chat/chats/${chatId}`);
      return response.data.chat;
    } catch (error) {
      console.error('Erreur lors de la récupération des détails du chat:', error);
      throw error;
    }
  }

  async getChatMessages(chatId: string, page: number = 1, perPage: number = 50): Promise<{
    messages: ChatMessage[];
    pagination: {
      page: number;
      per_page: number;
      total: number;
      pages: number;
      has_next: boolean;
      has_prev: boolean;
    };
  }> {
    try {
      const response = await api.get(`/chat/chats/${chatId}/messages`, {
        params: { page, per_page: perPage }
      });
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération des messages:', error);
      throw error;
    }
  }

  async sendMessage(chatId: string, message: string, messageType: string = 'text'): Promise<ChatMessage> {
    try {
      const response = await api.post(`/chat/chats/${chatId}/messages`, {
        message,
        message_type: messageType
      });
      return response.data.message;
    } catch (error) {
      console.error('Erreur lors de l\'envoi du message:', error);
      throw error;
    }
  }

  async markChatAsRead(chatId: string): Promise<void> {
    try {
      await api.post(`/chat/chats/${chatId}/read`);
    } catch (error) {
      console.error('Erreur lors du marquage du chat comme lu:', error);
      throw error;
    }
  }

  async createChat(participants: string[], chatType: string = 'direct', name?: string): Promise<Chat> {
    try {
      const response = await api.post('/chat/chats', {
        participants,
        chat_type: chatType,
        name
      });
      return response.data.chat;
    } catch (error) {
      console.error('Erreur lors de la création du chat:', error);
      throw error;
    }
  }

  async createListingChat(listingId: string, message?: string): Promise<Chat> {
    try {
      const response = await api.post('/chat/chats/listing', {
        listing_id: listingId,
        initial_message: message
      });
      return response.data.chat;
    } catch (error) {
      console.error('Erreur lors de la création du chat d\'annonce:', error);
      throw error;
    }
  }

  async createExchangeChat(exchangeId: string, message?: string): Promise<Chat> {
    try {
      const response = await api.post('/chat/chats/exchange', {
        exchange_id: exchangeId,
        initial_message: message
      });
      return response.data.chat;
    } catch (error) {
      console.error('Erreur lors de la création du chat d\'échange:', error);
      throw error;
    }
  }

  // Upload de fichier
  async uploadFile(chatId: string, file: File): Promise<{ url: string; filename: string }> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('chat_id', chatId);

      const response = await api.post('/chat/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      return response.data;
    } catch (error) {
      console.error('Erreur lors de l\'upload du fichier:', error);
      throw error;
    }
  }

  // Envoyer un message avec fichier
  async sendFileMessage(chatId: string, file: File, message?: string): Promise<ChatMessage> {
    try {
      const uploadResult = await this.uploadFile(chatId, file);
      
      return await this.sendMessage(chatId, message || '', 'file', {
        attachment_url: uploadResult.url,
        attachment_filename: uploadResult.filename
      });
    } catch (error) {
      console.error('Erreur lors de l\'envoi du message avec fichier:', error);
      throw error;
    }
  }

  // Envoyer un message avec pièce jointe
  async sendMessage(chatId: string, message: string, messageType: string = 'text', attachment?: {
    attachment_url?: string;
    attachment_filename?: string;
  }): Promise<ChatMessage> {
    try {
      const response = await api.post(`/chat/chats/${chatId}/messages`, {
        message,
        message_type: messageType,
        ...attachment
      });
      return response.data.message;
    } catch (error) {
      console.error('Erreur lors de l\'envoi du message:', error);
      throw error;
    }
  }

  // Obtenir le statut de connexion
  getConnectionStatus(): boolean {
    return this.isConnected;
  }

  // Obtenir l'instance socket
  getSocket(): Socket | null {
    return this.socket;
  }
}

// Instance singleton
const chatService = new ChatService();
export default chatService;
