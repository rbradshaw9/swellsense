import type { NextPage } from 'next'
import Head from 'next/head'
import { Sparkles, MessageSquare, Zap } from 'lucide-react'
import ChatBox from '../components/ui/ChatBox'

const AI: NextPage = () => {
  return (
    <>
      <Head>
        <title>AI Surf Advisor - SwellSense</title>
        <meta 
          name="description" 
          content="Chat with SwellSense AI to get personalized surf recommendations and intelligent condition analysis." 
        />
      </Head>

      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-cyan-50">
        <div className="mx-auto max-w-7xl px-6 py-12">
          {/* Header */}
          <div className="mb-12 text-center">
            <div className="inline-flex items-center justify-center p-3 bg-gradient-ocean rounded-xl shadow-lg mb-6">
              <Sparkles className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-4xl font-bold text-gray-900 mb-4">SwellSense AI Advisor</h1>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Get intelligent surf recommendations and real-time condition analysis powered by AI
            </p>
          </div>

          {/* Main Content */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12">
            {/* Chat Interface - Takes 2 columns */}
            <div className="lg:col-span-2">
              <ChatBox />
            </div>

            {/* Sidebar Info */}
            <div className="space-y-6">
              {/* Capabilities */}
              <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
                <div className="flex items-center space-x-2 mb-4">
                  <Zap className="w-5 h-5 text-blue-600" />
                  <h3 className="font-semibold text-gray-900">AI Capabilities</h3>
                </div>
                <ul className="space-y-3 text-sm text-gray-700">
                  <li className="flex items-start">
                    <span className="text-blue-600 mr-2">✓</span>
                    <span>Analyze current surf conditions</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-blue-600 mr-2">✓</span>
                    <span>Recommend best times to surf</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-blue-600 mr-2">✓</span>
                    <span>Explain wave patterns</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-blue-600 mr-2">✓</span>
                    <span>Skill-based personalization</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-blue-600 mr-2">✓</span>
                    <span>Safety alerts & warnings</span>
                  </li>
                </ul>
              </div>

              {/* Example Queries */}
              <div className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-xl p-6 border border-blue-200">
                <div className="flex items-center space-x-2 mb-4">
                  <MessageSquare className="w-5 h-5 text-blue-600" />
                  <h3 className="font-semibold text-gray-900">Try Asking</h3>
                </div>
                <div className="space-y-2 text-sm">
                  <div className="bg-white rounded-lg p-3 border border-blue-200">
                    "What are the best surf spots today?"
                  </div>
                  <div className="bg-white rounded-lg p-3 border border-blue-200">
                    "Is it safe for beginner surfers right now?"
                  </div>
                  <div className="bg-white rounded-lg p-3 border border-blue-200">
                    "When will the waves be biggest this week?"
                  </div>
                </div>
              </div>

              {/* Coming Soon Badge */}
              <div className="bg-yellow-50 rounded-xl p-6 border border-yellow-200">
                <div className="flex items-center space-x-2 mb-2">
                  <Sparkles className="w-5 h-5 text-yellow-600" />
                  <h3 className="font-semibold text-gray-900">Coming in v0.3</h3>
                </div>
                <p className="text-sm text-gray-700">
                  Full AI integration with OpenAI GPT-4 for natural language surf analysis and personalized recommendations.
                </p>
              </div>
            </div>
          </div>

          {/* How It Works */}
          <div className="bg-white rounded-xl p-8 shadow-sm border border-gray-200">
            <h2 className="text-2xl font-semibold text-gray-900 mb-6 text-center">How SwellSense AI Works</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-blue-100 text-blue-600 mb-4">
                  <span className="text-2xl font-bold">1</span>
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">Ask Your Question</h3>
                <p className="text-sm text-gray-600">
                  Type naturally - ask about conditions, best times, or get surf advice
                </p>
              </div>
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-blue-100 text-blue-600 mb-4">
                  <span className="text-2xl font-bold">2</span>
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">AI Analyzes Data</h3>
                <p className="text-sm text-gray-600">
                  Combines NOAA buoy data, weather, tides, and your preferences
                </p>
              </div>
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-blue-100 text-blue-600 mb-4">
                  <span className="text-2xl font-bold">3</span>
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">Get Smart Advice</h3>
                <p className="text-sm text-gray-600">
                  Receive personalized recommendations in plain English
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}

export default AI
