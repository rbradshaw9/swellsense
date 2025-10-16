import type { NextPage } from 'next'
import Head from 'next/head'
import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/router'
import { Sparkles, Send, Loader2, Trash2, Download } from 'lucide-react'
import toast from 'react-hot-toast'
import { useAuth } from '../context/AuthContext'

interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp: string
}

const AI: NextPage = () => {
  const { user, loading: authLoading } = useAuth()
  const router = useRouter()
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  // Protect route - redirect to login if not authenticated
  useEffect(() => {
    if (!authLoading && !user) {
      toast.error('Please sign in to use AI Chat')
      router.push('/login?redirect=/ai')
    }
  }, [user, authLoading, router])

  // Load chat history from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem('swellsense-chat-history')
    if (saved) {
      try {
        const parsed = JSON.parse(saved)
        setMessages(parsed)
      } catch (e) {
        console.error('Failed to load chat history:', e)
      }
    }
  }, [])

  // Save chat history to localStorage whenever messages change
  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem('swellsense-chat-history', JSON.stringify(messages))
    }
  }, [messages])

  // Auto-scroll to bottom on new message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const sendMessage = async (messageText?: string) => {
    const text = messageText || input.trim()
    if (!text || loading) return

    // Add user message
    const userMessage: Message = {
      role: 'user',
      content: text,
      timestamp: new Date().toISOString()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      // Call chat API
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/ai/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: [...messages, userMessage].map(m => ({
            role: m.role,
            content: m.content
          }))
        }),
      })

      if (!response.ok) {
        throw new Error(`Chat failed: ${response.statusText}`)
      }

      const data = await response.json()

      // Add assistant message
      const assistantMessage: Message = {
        role: 'assistant',
        content: data.reply,
        timestamp: data.timestamp
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Chat error:', error)
      toast.error('Failed to get AI response. Please try again.')
      
      // Remove the user message on error
      setMessages(prev => prev.slice(0, -1))
    } finally {
      setLoading(false)
      inputRef.current?.focus()
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const clearChat = () => {
    if (confirm('Clear all messages?')) {
      setMessages([])
      localStorage.removeItem('swellsense-chat-history')
      toast.success('Chat cleared')
    }
  }

  const exportChat = () => {
    const chatText = messages
      .map(m => `${m.role.toUpperCase()}: ${m.content}`)
      .join('\n\n')
    
    const blob = new Blob([chatText], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `swellsense-chat-${new Date().toISOString().split('T')[0]}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    toast.success('Chat exported')
  }

  const presetQuestions = [
    "What's the best time to surf Domes tomorrow?",
    "Compare Jobos vs Crash Boat this weekend",
    "Explain what offshore wind means",
    "What board should I ride for 3 ft glassy waves?"
  ]

  // Show loading state while checking authentication
  if (authLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-cyan-500 via-blue-600 to-blue-700 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-white animate-spin mx-auto mb-4" />
          <p className="text-white text-lg">Checking authentication...</p>
        </div>
      </div>
    )
  }

  // Don't render if not authenticated (will redirect)
  if (!user) {
    return null
  }

  return (
    <>
      <Head>
        <title>AI Surf Chat - SwellSense</title>
        <meta 
          name="description" 
          content="Chat with SwellSense AI to get personalized surf recommendations and intelligent condition analysis." 
        />
      </Head>

      <div className="min-h-screen bg-gradient-to-br from-cyan-500 via-blue-600 to-blue-700">
        <div className="mx-auto max-w-5xl px-3 sm:px-4 py-4 sm:py-8 min-h-screen flex flex-col">
          {/* Header */}
          <div className="mb-4 sm:mb-6 text-center">
            <div className="inline-flex items-center justify-center p-2 sm:p-3 bg-white/20 backdrop-blur-sm rounded-xl shadow-lg mb-3 sm:mb-4">
              <Sparkles className="w-6 h-6 sm:w-8 sm:h-8 text-white" />
            </div>
            <h1 className="text-3xl sm:text-4xl font-bold text-white mb-1 sm:mb-2">SwellSense AI</h1>
            <p className="text-blue-100 text-base sm:text-lg">
              Your personal surf forecasting assistant
            </p>
          </div>

          {/* Chat Container */}
          <div className="flex-1 bg-white/10 backdrop-blur-md rounded-xl sm:rounded-2xl shadow-2xl border border-white/20 flex flex-col overflow-hidden">
            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-3 sm:p-6 space-y-3 sm:space-y-4">
              {messages.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-center space-y-4 sm:space-y-6 py-8 sm:py-12">
                  <div className="text-white/80 space-y-3 sm:space-y-4 px-4">
                    <p className="text-lg sm:text-xl font-medium">👋 Stoked to help you score waves!</p>
                    <p className="text-base sm:text-lg">Ask me anything about surf conditions, spots, or gear.</p>
                  </div>
                  
                  {/* Preset Questions */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 sm:gap-3 max-w-2xl mt-6 sm:mt-8 w-full px-4">
                    {presetQuestions.map((question, index) => (
                      <button
                        key={index}
                        onClick={() => sendMessage(question)}
                        className="px-3 sm:px-4 py-2.5 sm:py-3 bg-white/20 hover:bg-white/30 text-white text-xs sm:text-sm rounded-lg transition-colors text-left border border-white/20"
                      >
                        💬 {question}
                      </button>
                    ))}
                  </div>
                </div>
              ) : (
                <>
                  {messages.map((message, index) => (
                    <div
                      key={index}
                      className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-[85%] sm:max-w-[80%] rounded-2xl px-4 sm:px-5 py-2.5 sm:py-3 ${
                          message.role === 'user'
                            ? 'bg-gradient-to-br from-blue-500 to-blue-600 text-white ml-auto'
                            : 'bg-white/90 backdrop-blur-sm text-gray-800 border border-gray-200'
                        }`}
                      >
                        <p className="text-xs sm:text-sm leading-relaxed whitespace-pre-wrap">
                          {message.content}
                        </p>
                        <p className={`text-[10px] sm:text-xs mt-1.5 sm:mt-2 ${
                          message.role === 'user' ? 'text-blue-100' : 'text-gray-500'
                        }`}>
                          {new Date(message.timestamp).toLocaleTimeString('en-US', {
                            hour: 'numeric',
                            minute: '2-digit',
                            hour12: true
                          })}
                        </p>
                      </div>
                    </div>
                  ))}
                  
                  {/* Typing indicator */}
                  {loading && (
                    <div className="flex justify-start">
                      <div className="bg-white/90 backdrop-blur-sm rounded-2xl px-5 py-3 border border-gray-200">
                        <div className="flex items-center space-x-2">
                          <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                          <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                          <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                        </div>
                      </div>
                    </div>
                  )}
                </>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-4 bg-white/10 border-t border-white/20">
              <div className="flex items-center space-x-3">
                <input
                  ref={inputRef}
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask about surf conditions, spots, or gear..."
                  disabled={loading}
                  className="flex-1 px-4 py-3 rounded-xl bg-white/90 backdrop-blur-sm border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-400 disabled:opacity-50 disabled:cursor-not-allowed text-gray-900 placeholder-gray-500"
                />
                <button
                  onClick={() => sendMessage()}
                  disabled={loading || !input.trim()}
                  className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 font-medium shadow-lg"
                >
                  {loading ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <>
                      <span>Send</span>
                      <Send className="w-5 h-5" />
                    </>
                  )}
                </button>
              </div>
              
              {/* Action Buttons */}
              {messages.length > 0 && (
                <div className="flex items-center justify-end space-x-3 mt-3">
                  <button
                    onClick={exportChat}
                    className="text-xs text-white/80 hover:text-white flex items-center space-x-1 transition-colors"
                  >
                    <Download className="w-4 h-4" />
                    <span>Export</span>
                  </button>
                  <button
                    onClick={clearChat}
                    className="text-xs text-white/80 hover:text-white flex items-center space-x-1 transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                    <span>Clear</span>
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Footer Info */}
          <div className="mt-6 text-center">
            <p className="text-xs text-white/60">
              🤖 Powered by OpenAI GPT-4 • SwellSense uses live forecast data for accurate surf insights
            </p>
          </div>
        </div>
      </div>
    </>
  )
}

export default AI
