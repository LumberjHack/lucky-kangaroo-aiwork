import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { MessageCircle, ArrowLeft } from 'lucide-react';
import ChatList from '../components/chat/ChatList';
import ChatInterface from '../components/chat/ChatInterface';

const ChatPage: React.FC = () => {
  const [selectedChatId, setSelectedChatId] = useState<string | null>(null);
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);

  // Détecter la taille de l'écran
  React.useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 768);
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const handleChatSelect = (chatId: string) => {
    setSelectedChatId(chatId);
  };

  const handleCloseChat = () => {
    setSelectedChatId(null);
  };

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Liste des chats */}
      <div className={`${isMobile && selectedChatId ? 'hidden' : 'flex'} flex-col w-full md:w-1/3 lg:w-1/4 bg-white border-r border-gray-200`}>
        <ChatList 
          onChatSelect={handleChatSelect}
          selectedChatId={selectedChatId || undefined}
        />
      </div>

      {/* Interface de chat */}
      <div className={`${isMobile && !selectedChatId ? 'hidden' : 'flex'} flex-col flex-1`}>
        {selectedChatId ? (
          <div className="flex flex-col h-full">
            {/* Bouton retour sur mobile */}
            {isMobile && (
              <div className="flex items-center p-4 border-b border-gray-200 bg-white">
                <button
                  onClick={handleCloseChat}
                  className="p-2 hover:bg-gray-100 rounded-full transition-colors mr-3"
                >
                  <ArrowLeft size={20} />
                </button>
                <h1 className="text-lg font-semibold text-gray-900">Messages</h1>
              </div>
            )}
            
            <ChatInterface 
              chatId={selectedChatId}
              onClose={isMobile ? handleCloseChat : undefined}
            />
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-full bg-gray-50">
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              className="text-center"
            >
              <div className="w-24 h-24 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <MessageCircle size={48} className="text-blue-600" />
              </div>
              
              <h2 className="text-2xl font-semibold text-gray-900 mb-2">
                Bienvenue dans vos messages
              </h2>
              
              <p className="text-gray-600 mb-8 max-w-md">
                Sélectionnez une conversation pour commencer à discuter avec d'autres utilisateurs de Lucky Kangaroo.
              </p>
              
              <div className="space-y-4 text-sm text-gray-500">
                <div className="flex items-center justify-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span>Chat en temps réel</span>
                </div>
                <div className="flex items-center justify-center space-x-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <span>Partage de fichiers et images</span>
                </div>
                <div className="flex items-center justify-center space-x-2">
                  <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                  <span>Notifications instantanées</span>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatPage;
