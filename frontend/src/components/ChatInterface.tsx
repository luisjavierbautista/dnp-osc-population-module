'use client';

import React, { useState, useRef } from 'react';
import {
  Branch,
  BranchMessages,
  BranchNext,
  BranchPage,
  BranchPrevious,
  BranchSelector,
} from '@/components/ai-elements/branch';
import {
  Conversation,
  ConversationContent,
  ConversationScrollButton,
} from '@/components/ai-elements/conversation';
import {
  PromptInput,
  PromptInputActionAddAttachments,
  PromptInputActionMenu,
  PromptInputActionMenuContent,
  PromptInputActionMenuTrigger,
  PromptInputAttachment,
  PromptInputAttachments,
  PromptInputBody,
  type PromptInputMessage,
  PromptInputSubmit,
  PromptInputTextarea,
  PromptInputFooter,
  PromptInputTools,
} from '@/components/ai-elements/prompt-input';
import {
  Message,
  MessageAvatar,
  MessageContent,
} from '@/components/ai-elements/message';
import { Response } from '@/components/ai-elements/response';
import {
  Suggestion,
  Suggestions,
} from '@/components/ai-elements/suggestion';
import { VisualizationRenderer } from './VisualizationRenderer';

interface ChatMessage {
  id: number;
  role: string;
  content: string;
  message_metadata?: any;
}

interface MessageTypeExtended {
  key: string;
  from: 'user' | 'assistant';
  versions: {
    id: string;
    content: string;
    metadata?: any;
  }[];
  avatar: string;
  name: string;
}

interface ChatInterfaceProps {
  messages: ChatMessage[];
  isLoading: boolean;
  onSendMessage: (message: string) => void;
  availableProviders?: string[];
  selectedProvider?: string | null;
  onProviderChange?: (provider: string) => void;
}

const suggestions = [
  '¿Cuál es la población total de Medellín en 2025?',
  'Muéstrame la pirámide poblacional de Bogotá',
  '¿Cómo ha evolucionado la población de Cali desde 2018?',
  'Compara la población de las principales ciudades',
  'Distribución urbano-rural en Antioquia',
  '¿Cuál es el ratio de dependencia demográfica en Colombia?',
];

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  messages: rawMessages,
  isLoading,
  onSendMessage,
  availableProviders = [],
  selectedProvider = null,
  onProviderChange,
}) => {
  const [text, setText] = useState<string>('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const getProviderDisplayName = (provider: string) => {
    switch (provider) {
      case 'claude':
        return 'Claude (Anthropic)';
      case 'azure_openai':
        return 'Azure OpenAI (DNP)';
      default:
        return provider;
    }
  };

  // Convert raw messages to the format expected by AI Elements
  const messages: MessageTypeExtended[] = rawMessages.map((msg) => ({
    key: `${msg.id}`,
    from: msg.role === 'user' ? 'user' : 'assistant',
    versions: [
      {
        id: `${msg.id}`,
        content: msg.content,
        metadata: msg.message_metadata,
      },
    ],
    avatar: msg.role === 'user'
      ? 'https://api.dicebear.com/7.x/avataaars/svg?seed=user'
      : 'https://api.dicebear.com/7.x/bottts/svg?seed=dnp-assistant',
    name: msg.role === 'user' ? 'Usuario' : 'Asistente DNP Población',
  }));

  const handleSubmit = (message: PromptInputMessage) => {
    const hasText = Boolean(message.text);

    if (!hasText || isLoading) {
      return;
    }

    onSendMessage(message.text || '');
    setText('');
  };

  const handleSuggestionClick = (suggestion: string) => {
    if (!isLoading) {
      onSendMessage(suggestion);
    }
  };

  return (
    <div className="relative flex size-full flex-col divide-y overflow-hidden bg-background">
      {/* Provider selector/indicator header */}
      {availableProviders.length > 0 && (
        <div className="flex items-center justify-between px-4 py-2 border-b bg-muted/20">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-muted-foreground">
              Modelo LLM:
            </span>
            {availableProviders.length > 1 && onProviderChange ? (
              <select
                value={selectedProvider || ''}
                onChange={(e) => onProviderChange(e.target.value)}
                className="text-sm border rounded px-3 py-1 bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                disabled={isLoading}
              >
                {availableProviders.map((provider) => (
                  <option key={provider} value={provider}>
                    {getProviderDisplayName(provider)}
                  </option>
                ))}
              </select>
            ) : (
              <span className="text-sm font-medium">
                {selectedProvider && getProviderDisplayName(selectedProvider)}
              </span>
            )}
          </div>
          <div className="text-xs text-muted-foreground">
            {selectedProvider === 'azure_openai' && '🇨🇴 DNP Official'}
            {selectedProvider === 'claude' && '🤖 Claude Sonnet 4.5'}
          </div>
        </div>
      )}

      <Conversation>
        <ConversationContent>
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center p-4 md:p-8">
              <h2 className="text-xl md:text-2xl font-bold mb-3 md:mb-4">
                ¡Bienvenido al Asistente de Población DNP!
              </h2>
              <p className="text-sm md:text-base text-muted-foreground mb-4 md:mb-6">
                Haz preguntas sobre demografía y población en Colombia. Puedo ayudarte con:
              </p>
              <div className="text-left w-full max-w-2xl">
                <h3 className="text-base md:text-lg font-semibold mb-2">Totales de Población:</h3>
                <ul className="list-disc list-inside mb-3 md:mb-4 space-y-1 text-xs md:text-sm text-muted-foreground">
                  <li>Población total por territorio y año</li>
                  <li>Distribución por género (hombres/mujeres)</li>
                  <li>Comparación entre municipios y departamentos</li>
                </ul>
                <h3 className="text-base md:text-lg font-semibold mb-2">Estructura por Edad:</h3>
                <ul className="list-disc list-inside mb-3 md:mb-4 space-y-1 text-xs md:text-sm text-muted-foreground">
                  <li>Pirámides poblacionales por territorio</li>
                  <li>Grupos etarios y distribución demográfica</li>
                  <li>Índices de envejecimiento y dependencia</li>
                </ul>
                <h3 className="text-base md:text-lg font-semibold mb-2">Análisis Temporal:</h3>
                <ul className="list-disc list-inside space-y-1 text-xs md:text-sm text-muted-foreground">
                  <li>Proyecciones demográficas (2018-2050)</li>
                  <li>Tasas de crecimiento poblacional</li>
                </ul>
              </div>
            </div>
          ) : (
            <>
              {messages.map(({ versions, ...message }) => (
                <Branch defaultBranch={0} key={message.key}>
                  <BranchMessages>
                    {versions.map((version) => (
                      <Message
                        from={message.from}
                        key={`${message.key}-${version.id}`}
                      >
                        <div>
                          <MessageContent>
                            <Response>{version.content}</Response>
                            {version.metadata?.visualizations && (
                              <VisualizationRenderer
                                visualizations={version.metadata.visualizations}
                              />
                            )}
                            {version.metadata && (
                              <div className="mt-4 text-sm text-muted-foreground">
                                {version.metadata.sql_query && (
                                  <details className="mt-2">
                                    <summary className="cursor-pointer font-medium">
                                      Ver consulta SQL
                                    </summary>
                                    <pre className="mt-2 p-2 bg-muted rounded text-xs overflow-auto">
                                      {version.metadata.sql_query}
                                    </pre>
                                  </details>
                                )}
                                {version.metadata.data_count !== undefined && (
                                  <p className="mt-2">
                                    Registros procesados: {version.metadata.data_count.toLocaleString('es-CO')}
                                  </p>
                                )}
                              </div>
                            )}
                          </MessageContent>
                        </div>
                        <MessageAvatar name={message.name} src={message.avatar} />
                      </Message>
                    ))}
                  </BranchMessages>
                  {versions.length > 1 && (
                    <BranchSelector from={message.from}>
                      <BranchPrevious />
                      <BranchPage />
                      <BranchNext />
                    </BranchSelector>
                  )}
                </Branch>
              ))}
              {isLoading && (
                <Message from="assistant">
                  <div>
                    <MessageContent>
                      <div className="flex items-center gap-2 text-muted-foreground">
                        <div className="flex gap-1">
                          <div className="w-2 h-2 bg-primary rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                          <div className="w-2 h-2 bg-primary rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                          <div className="w-2 h-2 bg-primary rounded-full animate-bounce"></div>
                        </div>
                        <span className="text-sm">Analizando datos de población...</span>
                      </div>
                    </MessageContent>
                  </div>
                  <MessageAvatar
                    name="Asistente DNP Población"
                    src="https://api.dicebear.com/7.x/bottts/svg?seed=dnp-assistant"
                  />
                </Message>
              )}
            </>
          )}
        </ConversationContent>
        <ConversationScrollButton />
      </Conversation>
      <div className="grid shrink-0 gap-2 md:gap-4 pt-2 md:pt-4 px-2 md:px-4">
        {messages.length === 0 && (
          <Suggestions>
            {suggestions.map((suggestion) => (
              <Suggestion
                key={suggestion}
                onClick={() => handleSuggestionClick(suggestion)}
                suggestion={suggestion}
              />
            ))}
          </Suggestions>
        )}
        <div className="w-full pb-2 md:pb-4">
          <PromptInput onSubmit={handleSubmit}>
            <PromptInputBody>
              <PromptInputAttachments>
                {(attachment) => <PromptInputAttachment data={attachment} />}
              </PromptInputAttachments>
              <PromptInputTextarea
                onChange={(event) => setText(event.target.value)}
                ref={textareaRef}
                value={text}
                placeholder="Pregunta sobre población en Colombia..."
                className="text-sm md:text-base"
              />
            </PromptInputBody>
            <PromptInputFooter>
              <PromptInputTools>
                <PromptInputActionMenu>
                  <PromptInputActionMenuTrigger />
                  <PromptInputActionMenuContent>
                    <PromptInputActionAddAttachments />
                  </PromptInputActionMenuContent>
                </PromptInputActionMenu>
              </PromptInputTools>
              <PromptInputSubmit
                disabled={!text.trim() || isLoading}
                status={isLoading ? 'streaming' : 'ready'}
              />
            </PromptInputFooter>
          </PromptInput>
        </div>
      </div>
    </div>
  );
};
