import React, { useState } from 'react';
import { MessageSquare, Send, Sparkles } from 'lucide-react';

const AIChat: React.FC = () => {
  const [message, setMessage] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Placeholder - not functional yet
    console.log('AI Chat coming soon! Message:', message);
    setMessage('');
  };

  return (
    <div className="card bg-gradient-to-br from-blue-50 to-cyan-50 border-2 border-blue-200">
      {/* Header */}
      <div className="flex items-center space-x-3 mb-4">
        <div className="p-2 bg-gradient-ocean rounded-lg">
          <Sparkles className="w-5 h-5 text-white" />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Ask SwellSense AI</h3>
          <p className="text-xs text-gray-600">Get intelligent surf recommendations</p>
        </div>
      </div>

      {/* Coming Soon Badge */}
      <div className="mb-4 inline-flex items-center px-3 py-1 bg-yellow-100 border border-yellow-300 rounded-full">
        <Sparkles className="w-3 h-3 mr-1.5 text-yellow-600" />
        <span className="text-xs font-medium text-yellow-800">Coming Soon</span>
      </div>

      {/* Example Questions */}
      <div className="mb-4 space-y-2">
        <p className="text-sm font-medium text-gray-700">Example questions:</p>
        <div className="space-y-1.5">
          {[
            'When is the best time to surf today?',
            'How are the conditions for beginner surfers?',
            'What breaks are firing right now?'
          ].map((question, idx) => (
            <div
              key={idx}
              className="text-sm text-gray-600 bg-white rounded-lg px-3 py-2 border border-gray-200 hover:border-blue-300 transition-colors cursor-not-allowed opacity-60"
            >
              <MessageSquare className="w-3 h-3 inline mr-2 text-gray-400" />
              {question}
            </div>
          ))}
        </div>
      </div>

      {/* Input Form (Disabled) */}
      <form onSubmit={handleSubmit} className="relative">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Ask about surf conditions, best times, breaks..."
          disabled
          className="w-full pl-4 pr-12 py-3 border-2 border-gray-300 rounded-lg bg-white text-gray-400 cursor-not-allowed focus:outline-none"
        />
        <button
          type="submit"
          disabled
          className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-gray-300 text-gray-500 rounded-lg cursor-not-allowed"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>

      {/* Feature Preview */}
      <div className="mt-4 pt-4 border-t border-blue-200">
        <p className="text-xs text-gray-600">
          <span className="font-semibold">Coming in v0.3:</span> Chat with AI to get personalized surf advice,
          break recommendations, and real-time condition analysis powered by OpenAI.
        </p>
      </div>
    </div>
  );
};

export default AIChat;
