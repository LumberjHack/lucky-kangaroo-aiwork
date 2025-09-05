import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import api from '../../services/api';

// Types
export interface ChatMessage {
  id: string;
  chat_id: string;
  user_id: string;
  content: string;
  message_type: 'text' | 'image' | 'file' | 'system';
  metadata?: any;
  created_at: string;
  updated_at: string;
  user?: {
    id: string;
    first_name: string;
    last_name: string;
    avatar_url?: string;
  };
}

export interface Chat {
  id: string;
  type: 'direct' | 'group' | 'exchange';
  title?: string;
  description?: string;
  created_by: string;
  created_at: string;
  updated_at: string;
  last_message?: ChatMessage;
  participants: Array<{
    id: string;
    user_id: string;
    role: 'admin' | 'member';
    joined_at: string;
    user?: {
      id: string;
      first_name: string;
      last_name: string;
      avatar_url?: string;
    };
  }>;
  unread_count: number;
  is_archived: boolean;
  metadata?: any;
}

export interface ChatState {
  chats: Chat[];
  currentChat: Chat | null;
  messages: ChatMessage[];
  loading: boolean;
  error: string | null;
  typingUsers: Array<{
    chatId: string;
    userId: string;
    userName: string;
  }>;
  onlineUsers: string[];
  unreadCount: number;
}

const initialState: ChatState = {
  chats: [],
  currentChat: null,
  messages: [],
  loading: false,
  error: null,
  typingUsers: [],
  onlineUsers: [],
  unreadCount: 0
};

// Async thunks
export const fetchChats = createAsyncThunk(
  'chat/fetchChats',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/chat');
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Erreur lors du chargement des conversations');
    }
  }
);

export const fetchChatById = createAsyncThunk(
  'chat/fetchChatById',
  async (chatId: string, { rejectWithValue }) => {
    try {
      const response = await api.get(`/chat/${chatId}`);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Erreur lors du chargement de la conversation');
    }
  }
);

export const fetchChatMessages = createAsyncThunk(
  'chat/fetchChatMessages',
  async ({ chatId, page = 1, limit = 50 }: { chatId: string; page?: number; limit?: number }, { rejectWithValue }) => {
    try {
      const response = await api.get(`/chat/${chatId}/messages`, { 
        params: { page, limit } 
      });
      return { chatId, messages: response.data };
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Erreur lors du chargement des messages');
    }
  }
);

export const createChat = createAsyncThunk(
  'chat/createChat',
  async (chatData: Partial<Chat>, { rejectWithValue }) => {
    try {
      const response = await api.post('/chat', chatData);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Erreur lors de la création de la conversation');
    }
  }
);

export const sendMessage = createAsyncThunk(
  'chat/sendMessage',
  async ({ chatId, content, messageType = 'text' }: { 
    chatId: string; 
    content: string; 
    messageType?: 'text' | 'image' | 'file' | 'system' 
  }, { rejectWithValue }) => {
    try {
      const response = await api.post(`/chat/${chatId}/messages`, {
        content,
        message_type: messageType
      });
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Erreur lors de l\'envoi du message');
    }
  }
);

export const markMessagesAsRead = createAsyncThunk(
  'chat/markMessagesAsRead',
  async (chatId: string, { rejectWithValue }) => {
    try {
      await api.put(`/chat/${chatId}/read`);
      return chatId;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Erreur lors de la mise à jour des messages');
    }
  }
);

export const addChatParticipant = createAsyncThunk(
  'chat/addChatParticipant',
  async ({ chatId, userId }: { chatId: string; userId: string }, { rejectWithValue }) => {
    try {
      const response = await api.post(`/chat/${chatId}/participants`, { user_id: userId });
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Erreur lors de l\'ajout du participant');
    }
  }
);

export const removeChatParticipant = createAsyncThunk(
  'chat/removeChatParticipant',
  async ({ chatId, userId }: { chatId: string; userId: string }, { rejectWithValue }) => {
    try {
      await api.delete(`/chat/${chatId}/participants/${userId}`);
      return { chatId, userId };
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Erreur lors de la suppression du participant');
    }
  }
);

// Slice
const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    setCurrentChat: (state, action: PayloadAction<Chat | null>) => {
      state.currentChat = action.payload;
      if (action.payload) {
        state.messages = [];
      }
    },
    addMessage: (state, action: PayloadAction<ChatMessage>) => {
      const message = action.payload;
      
      // Ajouter le message à la liste
      state.messages.push(message);
      
      // Mettre à jour le dernier message du chat
      const chat = state.chats.find(c => c.id === message.chat_id);
      if (chat) {
        chat.last_message = message;
        chat.updated_at = message.created_at;
        
        // Incrémenter le compteur de messages non lus si ce n'est pas notre message
        if (message.user_id !== state.currentChat?.created_by) {
          chat.unread_count += 1;
          state.unreadCount += 1;
        }
      }
    },
    updateMessage: (state, action: PayloadAction<ChatMessage>) => {
      const updatedMessage = action.payload;
      const index = state.messages.findIndex(m => m.id === updatedMessage.id);
      if (index !== -1) {
        state.messages[index] = updatedMessage;
      }
    },
    deleteMessage: (state, action: PayloadAction<string>) => {
      state.messages = state.messages.filter(m => m.id !== action.payload);
    },
    setTypingUser: (state, action: PayloadAction<{ chatId: string; userId: string; userName: string }>) => {
      const { chatId, userId, userName } = action.payload;
      const existingIndex = state.typingUsers.findIndex(
        u => u.chatId === chatId && u.userId === userId
      );
      
      if (existingIndex !== -1) {
        state.typingUsers[existingIndex] = { chatId, userId, userName };
      } else {
        state.typingUsers.push({ chatId, userId, userName });
      }
    },
    removeTypingUser: (state, action: PayloadAction<{ chatId: string; userId: string }>) => {
      const { chatId, userId } = action.payload;
      state.typingUsers = state.typingUsers.filter(
        u => !(u.chatId === chatId && u.userId === userId)
      );
    },
    setOnlineUsers: (state, action: PayloadAction<string[]>) => {
      state.onlineUsers = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
    clearMessages: (state) => {
      state.messages = [];
    }
  },
  extraReducers: (builder) => {
    builder
      // Fetch chats
      .addCase(fetchChats.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchChats.fulfilled, (state, action) => {
        state.loading = false;
        state.chats = action.payload.chats || action.payload;
        state.unreadCount = action.payload.unread_count || 
          state.chats.reduce((total, chat) => total + chat.unread_count, 0);
      })
      .addCase(fetchChats.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Fetch chat by ID
      .addCase(fetchChatById.fulfilled, (state, action) => {
        state.currentChat = action.payload;
      })
      
      // Fetch chat messages
      .addCase(fetchChatMessages.fulfilled, (state, action) => {
        const { chatId, messages } = action.payload;
        if (state.currentChat?.id === chatId) {
          state.messages = messages;
        }
      })
      
      // Create chat
      .addCase(createChat.fulfilled, (state, action) => {
        state.chats.unshift(action.payload);
      })
      
      // Send message
      .addCase(sendMessage.fulfilled, (state, action) => {
        state.messages.push(action.payload);
        
        // Mettre à jour le dernier message du chat
        const chat = state.chats.find(c => c.id === action.payload.chat_id);
        if (chat) {
          chat.last_message = action.payload;
          chat.updated_at = action.payload.created_at;
        }
      })
      
      // Mark messages as read
      .addCase(markMessagesAsRead.fulfilled, (state, action) => {
        const chatId = action.payload;
        const chat = state.chats.find(c => c.id === chatId);
        if (chat) {
          state.unreadCount -= chat.unread_count;
          chat.unread_count = 0;
        }
      })
      
      // Add chat participant
      .addCase(addChatParticipant.fulfilled, (state, action) => {
        const chat = state.chats.find(c => c.id === action.payload.chat_id);
        if (chat) {
          chat.participants.push(action.payload);
        }
        if (state.currentChat?.id === action.payload.chat_id) {
          state.currentChat.participants.push(action.payload);
        }
      })
      
      // Remove chat participant
      .addCase(removeChatParticipant.fulfilled, (state, action) => {
        const { chatId, userId } = action.payload;
        const chat = state.chats.find(c => c.id === chatId);
        if (chat) {
          chat.participants = chat.participants.filter(p => p.user_id !== userId);
        }
        if (state.currentChat?.id === chatId) {
          state.currentChat.participants = state.currentChat.participants.filter(p => p.user_id !== userId);
        }
      });
  }
});

export const {
  setCurrentChat,
  addMessage,
  updateMessage,
  deleteMessage,
  setTypingUser,
  removeTypingUser,
  setOnlineUsers,
  clearError,
  clearMessages
} = chatSlice.actions;

export default chatSlice.reducer;
