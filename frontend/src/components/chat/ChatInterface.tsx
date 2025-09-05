import React, { useState, useEffect, useRef } from 'react';
import { io, Socket } from 'socket.io-client';
import { toast } from 'react-hot-toast';
import { Send, Paperclip, Smile, MoreVertical, Phone, Video } from 'lucide-react';

interface ChatMessage {
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

interface ChatParticipant {
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

interface ChatInterfaceProps {
  chatId: string;
  currentUserId: string;
  onClose?: () => void;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({
  chatId,
  currentUserId,
  onClose
}) => {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [participants, setParticipants] = useState<ChatParticipant[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [typingUsers, setTypingUsers] = useState<string[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Scroll vers le bas des messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initialiser la connexion WebSocket
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      toast.error('Token d\'authentification manquant');
      return;
    }

    const newSocket = io('http://localhost:5000', {
      auth: {
        token: token
      },
      transports: ['websocket', 'polling']
    });

    newSocket.on('connect', () => {
      console.log('Connecté au serveur WebSocket');
      setIsConnected(true);
      
      // Rejoindre le chat
      newSocket.emit('join_chat', { chat_id: chatId });
    });

    newSocket.on('disconnect', () => {
      console.log('Déconnecté du serveur WebSocket');
      setIsConnected(false);
    });

    newSocket.on('new_message', (message: ChatMessage) => {
      setMessages(prev => [...prev, message]);
    });

    newSocket.on('user_typing', (data: { user_id: string; is_typing: boolean }) => {
      if (data.user_id !== currentUserId) {
        setTypingUsers(prev => {
          if (data.is_typing) {
            return prev.includes(data.user_id) ? prev : [...prev, data.user_id];
          } else {
            return prev.filter(id => id !== data.user_id);
          }
        });
      }
    });

    newSocket.on('user_joined', (data: { user_id: string; chat_id: string }) => {
      toast.success('Un utilisateur a rejoint le chat');
    });

    newSocket.on('user_left', (data: { user_id: string; chat_id: string }) => {
      toast.info('Un utilisateur a quitté le chat');
    });

    setSocket(newSocket);

    return () => {
      newSocket.close();
    };
  }, [chatId, currentUserId]);

  // Charger les messages et participants
  useEffect(() => {
    const loadChatData = async () => {
      try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`http://localhost:5000/api/chat/chats/${chatId}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (response.ok) {
          const chatData = await response.json();
          setParticipants(chatData.chat.participants || []);
        }

        // Charger les messages
        const messagesResponse = await fetch(`http://localhost:5000/api/chat/chats/${chatId}/messages`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (messagesResponse.ok) {
          const messagesData = await messagesResponse.json();
          setMessages(messagesData.messages || []);
        }

        setIsLoading(false);
      } catch (error) {
        console.error('Erreur lors du chargement des données du chat:', error);
        toast.error('Erreur lors du chargement du chat');
        setIsLoading(false);
      }
    };

    if (chatId) {
      loadChatData();
    }
  }, [chatId]);

  // Envoyer un message
  const sendMessage = async () => {
    if (!newMessage.trim() || !socket) return;

    try {
      const response = await fetch(`http://localhost:5000/api/chat/chats/${chatId}/messages`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: newMessage.trim(),
          message_type: 'text'
        })
      });

      if (response.ok) {
        setNewMessage('');
        // Arrêter l'indicateur de frappe
        socket.emit('typing_stop', { chat_id: chatId });
      } else {
        toast.error('Erreur lors de l\'envoi du message');
      }
    } catch (error) {
      console.error('Erreur lors de l\'envoi du message:', error);
      toast.error('Erreur lors de l\'envoi du message');
    }
  };

  // Gérer la frappe
  const handleTyping = () => {
    if (!socket) return;

    if (!isTyping) {
      setIsTyping(true);
      socket.emit('typing_start', { chat_id: chatId });
    }

    // Arrêter l'indicateur après 3 secondes d'inactivité
    clearTimeout(typingTimeout);
    const typingTimeout = setTimeout(() => {
      setIsTyping(false);
      socket.emit('typing_stop', { chat_id: chatId });
    }, 3000);
  };

  // Gérer l'upload de fichier
  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Ici, vous implémenteriez l'upload de fichier
    toast.info('Upload de fichier en cours de développement');
  };

  // Formater l'heure
  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('fr-FR', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  // Obtenir le nom d'utilisateur
  const getUserName = (userId: string) => {
    const participant = participants.find(p => p.id === userId);
    return participant ? `${participant.first_name} ${participant.last_name}` : 'Utilisateur';
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-lg">
      {/* Header du chat */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center">
            <span className="text-white font-semibold">
              {participants.length > 0 ? participants[0].first_name[0] : 'C'}
            </span>
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">
              Chat avec {participants.length} participant{participants.length > 1 ? 's' : ''}
            </h3>
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className="text-sm text-gray-500">
                {isConnected ? 'En ligne' : 'Hors ligne'}
              </span>
            </div>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <button className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-200 rounded-lg">
            <Phone className="w-5 h-5" />
          </button>
          <button className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-200 rounded-lg">
            <Video className="w-5 h-5" />
          </button>
          <button className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-200 rounded-lg">
            <MoreVertical className="w-5 h-5" />
          </button>
          {onClose && (
            <button 
              onClick={onClose}
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-200 rounded-lg"
            >
              ×
            </button>
          )}
        </div>
      </div>

      {/* Zone des messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.user.id === currentUserId ? 'justify-end' : 'justify-start'}`}
          >
            <div className={`flex max-w-xs lg:max-w-md ${message.user.id === currentUserId ? 'flex-row-reverse' : 'flex-row'} space-x-2`}>
              {/* Avatar */}
              <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center flex-shrink-0">
                <span className="text-sm font-medium text-gray-700">
                  {message.user.first_name[0]}
                </span>
              </div>
              
              {/* Message */}
              <div className={`px-4 py-2 rounded-lg ${
                message.user.id === currentUserId 
                  ? 'bg-blue-500 text-white' 
                  : 'bg-gray-200 text-gray-900'
              }`}>
                {message.user.id !== currentUserId && (
                  <div className="text-xs font-medium mb-1 opacity-75">
                    {getUserName(message.user.id)}
                  </div>
                )}
                
                <div className="text-sm">
                  {message.message}
                </div>
                
                {message.is_edited && (
                  <div className="text-xs opacity-75 mt-1">
                    (modifié)
                  </div>
                )}
                
                <div className={`text-xs mt-1 ${
                  message.user.id === currentUserId ? 'text-blue-100' : 'text-gray-500'
                }`}>
                  {formatTime(message.created_at)}
                </div>
              </div>
            </div>
          </div>
        ))}
        
        {/* Indicateur de frappe */}
        {typingUsers.length > 0 && (
          <div className="flex justify-start">
            <div className="flex items-center space-x-2 px-4 py-2 bg-gray-100 rounded-lg">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
              <span className="text-sm text-gray-500">
                {typingUsers.length === 1 ? 'Quelqu\'un tape...' : `${typingUsers.length} personnes tapent...`}
              </span>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Zone de saisie */}
      <div className="p-4 border-t border-gray-200 bg-gray-50">
        <div className="flex items-center space-x-2">
          <button
            onClick={() => fileInputRef.current?.click()}
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-200 rounded-lg"
          >
            <Paperclip className="w-5 h-5" />
          </button>
          
          <div className="flex-1 relative">
            <input
              type="text"
              value={newMessage}
              onChange={(e) => {
                setNewMessage(e.target.value);
                handleTyping();
              }}
              onKeyPress={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  sendMessage();
                }
              }}
              placeholder="Tapez votre message..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          
          <button
            onClick={sendMessage}
            disabled={!newMessage.trim()}
            className="p-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
        
        <input
          ref={fileInputRef}
          type="file"
          onChange={handleFileUpload}
          className="hidden"
          accept="image/*,video/*,audio/*,.pdf,.doc,.docx"
        />
      </div>
    </div>
  );
};

export default ChatInterface;