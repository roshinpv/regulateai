import React, { useState, useRef, useEffect } from 'react';
import { Send, FileText, Loader } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { assistantAPI } from '../../api';
import { ChatMessage } from '../../types';

const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { user } = useAuth();
  
  // Fetch chat history when component mounts
  useEffect(() => {
    const fetchChatHistory = async () => {
      if (!user) return;
      
      try {
        setIsLoadingHistory(true);
        const history = await assistantAPI.getHistory(user.id);
        setMessages(history);
      } catch (error) {
        console.error('Error fetching chat history:', error);
      } finally {
        setIsLoadingHistory(false);
      }
    };
    
    fetchChatHistory();
  }, [user]);
  
  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!input.trim() || !user) return;
    
    // Add user message
    const userMessage: ChatMessage = {
      id: `temp-${Date.now()}`,
      content: input,
      sender: 'user',
      timestamp: new Date().toISOString(),
      user_id: user.id
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    
    try {
      // Send query to API
      const response = await assistantAPI.query(input, user.id);
      
      // Add bot response
      const botMessage: ChatMessage = {
        id: `resp-${Date.now()}`,
        content: response.response,
        sender: 'bot',
        timestamp: new Date().toISOString(),
        user_id: user.id,
        citations: response.citations
      };
      
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error querying assistant:', error);
      
      // Add error message
      const errorMessage: ChatMessage = {
        id: `error-${Date.now()}`,
        content: "I'm sorry, I encountered an error processing your request. Please try again.",
        sender: 'bot',
        timestamp: new Date().toISOString(),
        user_id: user.id
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleClearChat = async () => {
    if (!user) return;
    
    try {
      await assistantAPI.clearHistory(user.id);
      setMessages([]);
    } catch (error) {
      console.error('Error clearing chat history:', error);
    }
  };
  
  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  return (
    <div className="card h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold">AI Compliance Assistant</h2>
        <button 
          className="btn btn-outline text-sm"
          onClick={handleClearChat}
          disabled={isLoadingHistory || messages.length === 0}
        >
          Clear Chat
        </button>
      </div>
      
      <div className="flex-1 overflow-y-auto mb-4 pr-2">
        {isLoadingHistory ? (
          <div className="h-full flex flex-col items-center justify-center text-neutral-light">
            <Loader className="animate-spin mb-2" />
            <p>Loading chat history...</p>
          </div>
        ) : messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-neutral-light">
            <p className="mb-2">No messages yet.</p>
            <p>Ask me anything about banking regulations and compliance!</p>
          </div>
        ) : (
          <div className="space-y-4">
            {messages.map((message) => (
              <div 
                key={message.id} 
                className={`chat-message ${
                  message.sender === 'user' ? 'chat-message-user' : 'chat-message-bot'
                }`}
              >
                <div className="text-sm">
                  {message.content}
                </div>
                
                {message.citations && message.citations.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-neutral-lighter/50">
                    <div className="flex items-center text-xs text-neutral-light">
                      <FileText size={12} className="mr-1" />
                      <span>Citations:</span>
                    </div>
                    <ul className="mt-1 space-y-1">
                      {message.citations.map((citation, index) => (
                        <li key={index} className="text-xs text-primary">
                          <button className="underline">
                            {citation.text}
                          </button>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                
                <div className="text-right mt-1">
                  <span className="text-xs text-neutral-light">
                    {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>
      
      <form onSubmit={handleSendMessage} className="mt-auto">
        <div className="flex items-center border border-neutral-lighter rounded-lg overflow-hidden">
          <input
            type="text"
            placeholder="Ask about regulations or compliance..."
            className="flex-1 px-4 py-3 focus:outline-none"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isLoading || isLoadingHistory}
          />
          <button 
            type="submit" 
            className="bg-primary text-white p-3 hover:bg-primary-dark disabled:bg-neutral-lighter disabled:cursor-not-allowed"
            disabled={!input.trim() || isLoading || isLoadingHistory}
          >
            {isLoading ? <Loader className="animate-spin" size={18} /> : <Send size={18} />}
          </button>
        </div>
        {isLoading && (
          <p className="text-xs text-neutral-light mt-2">
            Thinking...
          </p>
        )}
        {!isLoading && (
          <p className="text-xs text-neutral-light mt-2">
            Powered by Llama 3 with local document knowledge base
          </p>
        )}
      </form>
    </div>
  );
};

export default ChatInterface;