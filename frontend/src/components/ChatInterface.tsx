import React, { useState, useRef, useEffect } from 'react';
import type { Message, DatasetInfo, ConfigResponse, ObservabilityData, ChatRequest } from '../types';
import { chat, submitEvaluation } from '../services/api';

interface ChatInterfaceProps {
  datasets: DatasetInfo[];
  config: ConfigResponse | null;
  onObservabilityUpdate: (data: ObservabilityData) => void;
}

const SAMPLE_QUESTIONS = [
  "What lesson does the tortoise teach us?",
  "Which fables involve foxes?",
  "Tell me about the boy who cried wolf",
  "What do the fables say about greed?",
];

const ChatInterface: React.FC<ChatInterfaceProps> = ({
  datasets,
  config,
  onObservabilityUpdate,
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const totalChunks = datasets.reduce((sum, d) => sum + d.num_chunks, 0);
  const activeDatasets = datasets.filter(d => d.enabled).length;

  const handleSend = async (question?: string) => {
    const query = question || input;
    if (!query.trim() || loading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: query,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const enabledDatasets = datasets.filter((d) => d.enabled).map((d) => d.id);

      const request: ChatRequest = {
        query,
        top_k: config?.default_top_k,
        enabled_datasets: enabledDatasets,
        model: config?.default_model,
        temperature: config?.default_temperature,
        max_tokens: config?.default_max_tokens,
        min_score: config?.default_min_score,
      };

      const response = await chat(request);

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.answer,
        observability: response.observability,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
      onObservabilityUpdate(response.observability);
    } catch (error) {
      console.error('Error sending message:', error);
      alert('Error: ' + (error as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const handleClearMessages = () => {
    setMessages([]);
    setInput('');
  };

  const handleEvaluate = async (message: Message, rating: number) => {
    if (!message.observability) return;

    try {
      const chunks = message.observability.steps.find(s => s.name === 'retrieval')?.details.chunks || [];
      await submitEvaluation({
        query: messages.find(m => m.role === 'user' && messages.indexOf(m) < messages.indexOf(message))?.content || '',
        response: message.content,
        retrieved_chunks: chunks,
        rating,
        observability_data: message.observability,
      });
      alert('Evaluation submitted!');
    } catch (error) {
      console.error('Error submitting evaluation:', error);
    }
  };

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Header */}
      <div className="flex items-center justify-between gap-4 px-4 py-3.5 bg-gray-50 border-b border-gray-200">
        <div className="flex items-center gap-2">
          <img src="/icons/message-icon.svg" alt="Chat" className="w-5 h-5" />
          <h2 className="text-base font-normal text-[#0A0A0A]">Chat Interface</h2>
        </div>
        <button
          onClick={handleClearMessages}
          className="flex items-center gap-2 px-3 py-1.5 text-[#0A0A0A] text-sm font-medium opacity-50 hover:opacity-100 rounded-lg transition-opacity"
          disabled={messages.length === 0}
        >
          <img src="/icons/x-icon.svg" alt="Clear" className="w-4 h-4" />
          Clear
        </button>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-y-auto px-4 py-4">
        {/* Sample Questions Section */}
        {messages.length === 0 && (
          <div className="mb-4">
            <div className="flex items-center gap-2 mb-2">
              <img src="/icons/lightbulb-icon.svg" alt="Ideas" className="w-4 h-4" />
              <span className="text-sm text-[#4A5565]">Try these sample questions:</span>
            </div>
            <div className="grid grid-cols-2 gap-2">
              {SAMPLE_QUESTIONS.map((q, i) => (
                <button
                  key={i}
                  onClick={() => handleSend(q)}
                  className="px-3 py-2 bg-white border border-[rgba(0,0,0,0.1)] rounded-lg text-xs text-[#0A0A0A] hover:bg-gray-50 transition-colors text-left"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Info Banner */}
        <div className="bg-[#FEF9C3] border border-[#FDE047] rounded-lg p-3 mb-4">
          <div className="flex items-start gap-2">
            <span className="text-sm">ℹ️</span>
            <span className="text-sm text-[#854D0E]">
              {activeDatasets} datasets active, {totalChunks.toLocaleString()} chunks available
            </span>
          </div>
        </div>

        {/* Messages */}
        <div className="space-y-4">
          {messages.length === 0 ? (
            <div className="flex justify-center items-center h-20">
              <span className="text-sm text-[#99A1AF]">Ask a question to begin...</span>
            </div>
          ) : (
            messages.map((message) => (
              <div key={message.id}>
                <div
                  className={`flex gap-3 ${message.role === 'user' ? 'flex-row-reverse' : ''}`}
                >
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-medium flex-shrink-0 ${
                    message.role === 'user'
                      ? 'bg-[#EFF6FF] text-[#155DFC]'
                      : 'bg-[#F3F4F6] text-[#4A5565]'
                  }`}>
                    {message.role === 'user' ? 'You' : '🤖'}
                  </div>
                  <div
                    className={`max-w-[70%] p-3 rounded-lg text-sm leading-relaxed ${
                      message.role === 'user'
                        ? 'bg-[#155DFC] text-white'
                        : 'bg-[#F9FAFB] text-[#0A0A0A]'
                    }`}
                  >
                    <div className="whitespace-pre-wrap">{message.content}</div>
                  </div>
                </div>
                {message.role === 'assistant' && (
                  <div className="flex gap-2 ml-11 mt-2">
                    <button
                      onClick={() => handleEvaluate(message, 5)}
                      className="px-2 py-1 border border-[rgba(0,0,0,0.1)] rounded text-xs text-[#4A5565] hover:bg-gray-50 transition-colors"
                    >
                      👍 Good
                    </button>
                    <button
                      onClick={() => handleEvaluate(message, 1)}
                      className="px-2 py-1 border border-[rgba(0,0,0,0.1)] rounded text-xs text-[#4A5565] hover:bg-gray-50 transition-colors"
                    >
                      👎 Poor
                    </button>
                  </div>
                )}
              </div>
            ))
          )}
          {loading && (
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-[#F3F4F6] text-[#4A5565] flex items-center justify-center text-xs font-medium flex-shrink-0">
                🤖
              </div>
              <div className="max-w-[70%] p-3 rounded-lg bg-[#F9FAFB] text-sm text-[#4A5565]">
                Thinking...
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="px-4 py-4 border-t border-gray-200 bg-gray-50">
        <div className="mb-2">
          <div className="flex gap-2">
            <button
              onClick={() => handleSend()}
              disabled={loading || !input.trim()}
              className="px-4 py-2 bg-[#030213] text-white rounded-lg text-sm font-medium hover:bg-[#1a1a2e] transition-colors disabled:bg-[#E5E7EB] disabled:cursor-not-allowed flex items-center gap-2"
            >
              <img src="/icons/send-icon.svg" alt="Send" className="w-4 h-4" />
              Send
            </button>
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              placeholder="Ask a question about Aesop's Fables..."
              className="flex-1 px-3 py-2 bg-white border border-[rgba(0,0,0,0.1)] rounded-lg text-sm text-[#0A0A0A] resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={3}
              disabled={loading}
            />
          </div>
        </div>
        <div className="text-xs text-[#6A7282]">
          Press Enter to send, Shift+Enter for new line
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
