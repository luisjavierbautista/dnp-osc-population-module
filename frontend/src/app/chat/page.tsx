'use client';

import React, { useState, useEffect } from 'react';
import { ChatInterface } from '@/components/ChatInterface';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Plus, MessageSquare } from 'lucide-react';
import { MainLayout } from '@/components/layout/MainLayout';
import { chatApi } from '@/services/api';

interface Chat {
  id: number;
  title: string;
  created_at: string;
}

interface Message {
  id: number;
  role: string;
  content: string;
  message_metadata?: any;
  chat_id: number;
  created_at: string;
}

export default function ChatPage() {
  const [chats, setChats] = useState<Chat[]>([]);
  const [currentChatId, setCurrentChatId] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showSidebar, setShowSidebar] = useState(true);
  const [availableProviders, setAvailableProviders] = useState<string[]>([]);
  const [defaultProvider, setDefaultProvider] = useState<string | null>(null);
  const [selectedProvider, setSelectedProvider] = useState<string | null>(null);

  // Load chats and providers on mount
  useEffect(() => {
    loadChats();
    loadProviders();
  }, []);

  // Load messages when chat changes
  useEffect(() => {
    if (currentChatId) {
      loadMessages(currentChatId);
    } else {
      setMessages([]);
    }
  }, [currentChatId]);

  const loadProviders = async () => {
    try {
      const data = await chatApi.getProviders();
      setAvailableProviders(data.available || []);
      setDefaultProvider(data.default);
      setSelectedProvider(data.default);
    } catch (error) {
      console.error('Error loading providers:', error);
    }
  };

  const loadChats = async () => {
    try {
      const data = await chatApi.getChats();
      setChats(data);

      // If no current chat and we have chats, select the first one
      if (!currentChatId && data.length > 0) {
        setCurrentChatId(data[0].id);
      }
    } catch (error) {
      console.error('Error loading chats:', error);
    }
  };

  const loadMessages = async (chatId: number) => {
    try {
      const data = await chatApi.getMessages(chatId);
      setMessages(data);
    } catch (error) {
      console.error('Error loading messages:', error);
    }
  };

  const createNewChat = async (): Promise<number | null> => {
    try {
      const newChat = await chatApi.createChat('Nueva conversación');
      setChats([newChat, ...chats]);
      setCurrentChatId(newChat.id);
      return newChat.id;
    } catch (error) {
      console.error('Error creating chat:', error);
      return null;
    }
  };

  const deleteChat = async (chatId: number) => {
    try {
      await chatApi.deleteChat(chatId);
      setChats(chats.filter(chat => chat.id !== chatId));
      if (currentChatId === chatId) {
        setCurrentChatId(null);
      }
    } catch (error) {
      console.error('Error deleting chat:', error);
    }
  };

  const sendMessage = async (message: string) => {
    let chatId = currentChatId;

    if (!chatId) {
      // Create new chat if none exists
      const newChatId = await createNewChat();
      if (!newChatId) return;
      chatId = newChatId;
    }

    // Optimistically add user message to UI
    const tempUserMessage: Message = {
      id: Date.now(),
      role: 'user',
      content: message,
      message_metadata: null,
      chat_id: chatId,
      created_at: new Date().toISOString()
    };
    setMessages([...messages, tempUserMessage]);
    setIsLoading(true);

    try {
      await chatApi.sendQuery({
        query: message,
        chat_id: chatId,
        provider: selectedProvider || undefined
      });

      // Reload messages to get the full conversation
      await loadMessages(chatId);

      // Reload chats to get updated title (first message)
      await loadChats();
    } catch (error) {
      console.error('Error sending message:', error);
      // Remove optimistic message on error
      setMessages(messages.filter(m => m.id !== tempUserMessage.id));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <MainLayout>
      <div className="flex h-[calc(100vh-8rem)] bg-background">
        {/* Sidebar */}
        {showSidebar && (
          <div className="w-64 border-r bg-muted/10 p-4 flex flex-col">
            <Button
              onClick={createNewChat}
              className="mb-4 w-full"
              size="sm"
            >
              <Plus className="mr-2 h-4 w-4" />
              Nueva conversación
            </Button>

            <div className="flex-1 overflow-y-auto space-y-2">
              {chats.map((chat) => (
                <Card
                  key={chat.id}
                  className={`p-3 cursor-pointer hover:bg-accent transition-colors ${
                    currentChatId === chat.id ? 'bg-accent' : ''
                  }`}
                  onClick={() => setCurrentChatId(chat.id)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <MessageSquare className="h-4 w-4 flex-shrink-0" />
                        <p className="text-sm font-medium truncate">
                          {chat.title}
                        </p>
                      </div>
                      <p className="text-xs text-muted-foreground mt-1">
                        {new Date(chat.created_at).toLocaleDateString('es-CO')}
                      </p>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-6 w-6 p-0 ml-2"
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteChat(chat.id);
                      }}
                    >
                      ×
                    </Button>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* Main chat area */}
        <div className="flex-1 flex flex-col">
          {currentChatId || chats.length === 0 ? (
            <ChatInterface
              messages={messages}
              isLoading={isLoading}
              onSendMessage={sendMessage}
              availableProviders={availableProviders}
              selectedProvider={selectedProvider}
              onProviderChange={setSelectedProvider}
            />
          ) : (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <MessageSquare className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                <h2 className="text-xl font-semibold mb-2">
                  Selecciona una conversación
                </h2>
                <p className="text-muted-foreground mb-4">
                  o crea una nueva para comenzar
                </p>
                <Button onClick={createNewChat}>
                  <Plus className="mr-2 h-4 w-4" />
                  Nueva conversación
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </MainLayout>
  );
}
