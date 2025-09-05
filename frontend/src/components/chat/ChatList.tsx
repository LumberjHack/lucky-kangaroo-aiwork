import React, { useState, useEffect } from 'react';
import { MessageCircle, Users, Clock, Check, CheckCheck } from 'lucide-react';

interface Chat {
  id: string;
  type: string;
  name: string;
  description?: string;
  avatar_url?: string;
  status: string;
  participants_count: number;
  last_message?: {
    id: string;
    message: string;
    message_type: string;
    created_at: string;
    user: {
      id: string;
      username: string;
      first_name: string;
    };
  };
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

interface ChatListProps {
  onChatSelect: (chatId: string) => void;
  selectedChatId?: string;
}

const ChatList: React.FC<ChatListProps> = ({ onChatSelect, selectedChatId }) => {
  const [chats, setChats] = useState<Chat[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  // Charger la liste des chats
  useEffect(() => {
    const loadChats = async () => {
      try {
        const token = localStorage.getItem('access_token');
        const response = await fetch('http://localhost:5000/api/chat/chats', {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (response.ok) {
          const data = await response.json();
          setChats(data.chats || []);
        } else {
          console.error('Erreur lors du chargement des chats');
        }
      } catch (error) {
        console.error('Erreur lors du chargement des chats:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadChats();
  }, []);

  // Filtrer les chats selon la recherche
  const filteredChats = chats.filter(chat =>
    chat.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    chat.last_message?.message.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Formater l'heure du dernier message
  const formatLastMessageTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);

    if (diffInHours < 24) {
      return date.toLocaleTimeString('fr-FR', { 
        hour: '2-digit', 
        minute: '2-digit' 
      });
    } else if (diffInHours < 168) { // 7 jours
      return date.toLocaleDateString('fr-FR', { 
        weekday: 'short' 
      });
    } else {
      return date.toLocaleDateString('fr-FR', { 
        day: '2-digit', 
        month: '2-digit' 
      });
    }
  };

  // Tronquer le message
  const truncateMessage = (message: string, maxLength: number = 50) => {
    if (message.length <= maxLength) return message;
    return message.substring(0, maxLength) + '...';
  };

  // Obtenir l'icône du type de chat
  const getChatIcon = (type: string) => {
    switch (type) {
      case 'direct':
        return <MessageCircle className="w-5 h-5" />;
      case 'group':
        return <Users className="w-5 h-5" />;
      case 'listing':
        return <MessageCircle className="w-5 h-5" />;
      case 'exchange':
        return <MessageCircle className="w-5 h-5" />;
      default:
        return <MessageCircle className="w-5 h-5" />;
    }
  };

  // Obtenir le statut de lecture
  const getReadStatus = (chat: Chat) => {
    if (chat.unread_count > 0) {
      return <div className="w-2 h-2 bg-blue-500 rounded-full"></div>;
    }
    return <CheckCheck className="w-4 h-4 text-blue-500" />;
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Messages</h2>
        
        {/* Barre de recherche */}
        <div className="relative">
          <input
            type="text"
            placeholder="Rechercher dans les conversations..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-4 py-2 pl-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>
      </div>

      {/* Liste des chats */}
      <div className="flex-1 overflow-y-auto">
        {filteredChats.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-64 text-gray-500">
            <MessageCircle className="w-12 h-12 mb-4" />
            <p className="text-lg font-medium">Aucune conversation</p>
            <p className="text-sm">Commencez une nouvelle conversation</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {filteredChats.map((chat) => (
              <div
                key={chat.id}
                onClick={() => onChatSelect(chat.id)}
                className={`p-4 hover:bg-gray-50 cursor-pointer transition-colors ${
                  selectedChatId === chat.id ? 'bg-blue-50 border-r-2 border-blue-500' : ''
                }`}
              >
                <div className="flex items-start space-x-3">
                  {/* Avatar */}
                  <div className="flex-shrink-0">
                    {chat.avatar_url ? (
                      <img
                        src={chat.avatar_url}
                        alt={chat.name}
                        className="w-12 h-12 rounded-full object-cover"
                      />
                    ) : (
                      <div className="w-12 h-12 bg-gray-300 rounded-full flex items-center justify-center">
                        {getChatIcon(chat.type)}
                      </div>
                    )}
                  </div>

                  {/* Contenu du chat */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <h3 className="text-sm font-medium text-gray-900 truncate">
                        {chat.name}
                      </h3>
                      <div className="flex items-center space-x-2">
                        {chat.last_message && (
                          <span className="text-xs text-gray-500">
                            {formatLastMessageTime(chat.last_message.created_at)}
                          </span>
                        )}
                        {getReadStatus(chat)}
                      </div>
                    </div>

                    {/* Dernier message */}
                    {chat.last_message ? (
                      <div className="flex items-center justify-between mt-1">
                        <p className="text-sm text-gray-600 truncate">
                          <span className="font-medium">
                            {chat.last_message.user.first_name}:
                          </span>{' '}
                          {truncateMessage(chat.last_message.message)}
                        </p>
                        {chat.unread_count > 0 && (
                          <div className="flex-shrink-0">
                            <span className="inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white bg-blue-500 rounded-full">
                              {chat.unread_count > 99 ? '99+' : chat.unread_count}
                            </span>
                          </div>
                        )}
                      </div>
                    ) : (
                      <p className="text-sm text-gray-500 mt-1">
                        Aucun message
                      </p>
                    )}

                    {/* Informations contextuelles */}
                    <div className="flex items-center space-x-2 mt-1">
                      {chat.listing && (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          Annonce: {chat.listing.title}
                        </span>
                      )}
                      {chat.exchange && (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                          Échange: {chat.exchange.title}
                        </span>
                      )}
                      <span className="text-xs text-gray-500">
                        {chat.participants_count} participant{chat.participants_count > 1 ? 's' : ''}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Actions rapides */}
      <div className="p-4 border-t border-gray-200">
        <button className="w-full bg-blue-500 text-white py-2 px-4 rounded-lg hover:bg-blue-600 transition-colors">
          Nouvelle conversation
        </button>
      </div>
    </div>
  );
};

export default ChatList;