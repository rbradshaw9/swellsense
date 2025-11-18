import type { NextPage } from 'next'
import Head from 'next/head'
import Link from 'next/link'
import { useState } from 'react'
import { ChevronRightIcon, WavesIcon, BarChart3, Sparkles, MapPin, Smartphone, Zap, Heart, TrendingUp } from 'lucide-react'

const Home: NextPage = () => {
  const [email, setEmail] = useState('')
  const [isSubmitted, setIsSubmitted] = useState(false)

  const handleEmailSignup = (e: React.FormEvent) => {
    e.preventDefault()
    // TODO: Implement email signup logic
    console.log('Email signup:', email)
    setIsSubmitted(true)
    // Reset after 3 seconds
    setTimeout(() => {
      setIsSubmitted(false)
      setEmail('')
    }, 3000)
  }

  return (
    <>
      <Head>
        <title>SwellSense - Smarter Surf Forecasts</title>
        <meta 
          name="description" 
          content="AI-powered surf forecasting that analyzes buoy, wind, and tide data to predict the best surf conditions for your break." 
        />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-cyan-50">
        {/* Hero Section */}
        <main className="relative px-6 pt-16 pb-20 sm:pt-24 sm:pb-32">
          <div className="mx-auto max-w-4xl text-center">
            {/* Badge */}
            <div className="inline-flex items-center rounded-full bg-gradient-to-r from-blue-100 to-cyan-100 px-4 py-2 text-sm font-medium text-blue-800 mb-8 animate-pulse">
              <span className="mr-2">🌊</span>
              iPhone App Coming Soon
            </div>

            {/* Main Heading */}
            <h1 className="text-5xl font-bold tracking-tight text-gray-900 sm:text-7xl leading-tight">
              Your Personal{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-cyan-600">
                Surf Coach
              </span>
              {' '}in Your Pocket
            </h1>

            {/* Subheading */}
            <p className="mt-6 text-xl leading-8 text-gray-600 max-w-2xl mx-auto">
              SwellSense learns from every session you log. Get personalized surf recommendations 
              that actually understand what you like—before you even check the forecast.
            </p>

            {/* CTA Buttons */}
            <div className="mt-12 flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/forecast"
                className="inline-flex items-center justify-center rounded-lg bg-blue-600 px-8 py-4 text-lg font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors shadow-lg hover:shadow-xl"
              >
                View Live Forecast
                <ChevronRightIcon className="ml-2 h-5 w-5" />
              </Link>
              <Link
                href="/ai"
                className="inline-flex items-center justify-center rounded-lg border-2 border-blue-600 bg-white px-8 py-4 text-lg font-medium text-blue-600 hover:bg-blue-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
              >
                Try AI Assistant
                <Sparkles className="ml-2 h-5 w-5" />
              </Link>
            </div>

            {/* iPhone Mockup Section */}
            <div className="mt-24 relative">
              <div className="mx-auto max-w-5xl">
                {/* Background gradient blur effect */}
                <div className="absolute inset-0 -z-10">
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-400 to-cyan-400 blur-3xl opacity-20"></div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-start">
                  {/* Phone 1 - Home Screen */}
                  <div className="transform hover:scale-105 transition-transform duration-300">
                    <div className="relative mx-auto w-[280px]">
                      {/* iPhone Frame */}
                      <div className="relative bg-gray-900 rounded-[3rem] p-3 shadow-2xl border-8 border-gray-800">
                        {/* Notch */}
                        <div className="absolute top-0 left-1/2 transform -translate-x-1/2 w-32 h-6 bg-gray-900 rounded-b-2xl z-10"></div>
                        
                        {/* Screen Content */}
                        <div className="bg-gradient-to-br from-blue-500 to-cyan-400 rounded-[2.5rem] overflow-hidden aspect-[9/19.5]">
                          <div className="p-6 pt-12">
                            {/* Status Bar */}
                            <div className="flex justify-between text-white text-xs mb-8">
                              <span>9:41</span>
                              <div className="flex gap-1">
                                <div className="w-4 h-4 bg-white/30 rounded"></div>
                                <div className="w-4 h-4 bg-white/30 rounded"></div>
                              </div>
                            </div>
                            
                            {/* App Content - Today's Forecast */}
                            <div className="text-white space-y-4">
                              <h3 className="text-2xl font-bold">Today's Forecast</h3>
                              <div className="bg-white/20 backdrop-blur-lg rounded-2xl p-4 space-y-2">
                                <div className="flex justify-between items-center">
                                  <span className="text-sm">Ocean Beach</span>
                                  <span className="text-2xl">⭐️ 8/10</span>
                                </div>
                                <div className="text-xs opacity-90">
                                  <div>4-6ft • 12s period</div>
                                  <div>Light offshore winds</div>
                                </div>
                              </div>
                              
                              <div className="bg-white/20 backdrop-blur-lg rounded-2xl p-4">
                                <div className="text-xs opacity-90 mb-2">💡 AI Recommendation</div>
                                <p className="text-sm">"Dawn patrol recommended. Conditions perfect for your style."</p>
                              </div>

                              <div className="grid grid-cols-3 gap-2 mt-6">
                                <div className="bg-white/10 rounded-xl p-3 text-center">
                                  <div className="text-2xl">🌊</div>
                                  <div className="text-xs mt-1">Sessions</div>
                                </div>
                                <div className="bg-white/10 rounded-xl p-3 text-center">
                                  <div className="text-2xl">📊</div>
                                  <div className="text-xs mt-1">Stats</div>
                                </div>
                                <div className="bg-white/10 rounded-xl p-3 text-center">
                                  <div className="text-2xl">🔔</div>
                                  <div className="text-xs mt-1">Alerts</div>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                    <p className="text-center mt-4 text-sm font-medium text-gray-700">Personalized Dashboard</p>
                  </div>

                  {/* Phone 2 - Log Session */}
                  <div className="transform hover:scale-105 transition-transform duration-300 md:mt-12">
                    <div className="relative mx-auto w-[280px]">
                      <div className="relative bg-gray-900 rounded-[3rem] p-3 shadow-2xl border-8 border-gray-800">
                        <div className="absolute top-0 left-1/2 transform -translate-x-1/2 w-32 h-6 bg-gray-900 rounded-b-2xl z-10"></div>
                        
                        <div className="bg-white rounded-[2.5rem] overflow-hidden aspect-[9/19.5]">
                          <div className="p-6 pt-12">
                            <h3 className="text-2xl font-bold text-gray-900 mb-6">Log Session</h3>
                            
                            {/* Form Preview */}
                            <div className="space-y-4">
                              <div>
                                <label className="text-xs text-gray-500 mb-1 block">Surf Spot</label>
                                <div className="bg-gray-100 rounded-lg p-3 text-sm">Ocean Beach</div>
                              </div>
                              
                              <div>
                                <label className="text-xs text-gray-500 mb-1 block">How was it?</label>
                                <div className="flex gap-1">
                                  {[1,2,3,4,5].map((i) => (
                                    <div key={i} className={`w-8 h-8 rounded-full flex items-center justify-center text-sm ${i <= 4 ? 'bg-yellow-400 text-white' : 'bg-gray-100'}`}>
                                      {i <= 4 ? '⭐️' : '☆'}
                                    </div>
                                  ))}
                                </div>
                              </div>

                              <div className="grid grid-cols-2 gap-3">
                                <div>
                                  <label className="text-xs text-gray-500 mb-1 block">Waves Caught</label>
                                  <div className="bg-gray-100 rounded-lg p-3 text-sm">12</div>
                                </div>
                                <div>
                                  <label className="text-xs text-gray-500 mb-1 block">Duration</label>
                                  <div className="bg-gray-100 rounded-lg p-3 text-sm">2h 30m</div>
                                </div>
                              </div>

                              <div>
                                <label className="text-xs text-gray-500 mb-1 block">Notes</label>
                                <div className="bg-gray-100 rounded-lg p-3 text-xs text-gray-600">
                                  Perfect dawn patrol! Glassy conditions...
                                </div>
                              </div>

                              <button className="w-full bg-blue-600 text-white rounded-lg py-3 font-medium">
                                Save Session
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                    <p className="text-center mt-4 text-sm font-medium text-gray-700">Track Every Session</p>
                  </div>

                  {/* Phone 3 - AI Chat */}
                  <div className="transform hover:scale-105 transition-transform duration-300">
                    <div className="relative mx-auto w-[280px]">
                      <div className="relative bg-gray-900 rounded-[3rem] p-3 shadow-2xl border-8 border-gray-800">
                        <div className="absolute top-0 left-1/2 transform -translate-x-1/2 w-32 h-6 bg-gray-900 rounded-b-2xl z-10"></div>
                        
                        <div className="bg-gray-50 rounded-[2.5rem] overflow-hidden aspect-[9/19.5]">
                          <div className="p-6 pt-12">
                            <h3 className="text-2xl font-bold text-gray-900 mb-6">AI Coach</h3>
                            
                            {/* Chat Messages */}
                            <div className="space-y-4">
                              <div className="flex justify-start">
                                <div className="bg-white rounded-2xl rounded-tl-sm p-3 shadow-sm max-w-[200px]">
                                  <p className="text-sm text-gray-700">When should I surf this week?</p>
                                </div>
                              </div>

                              <div className="flex justify-end">
                                <div className="bg-blue-600 rounded-2xl rounded-tr-sm p-3 shadow-sm max-w-[200px]">
                                  <p className="text-sm text-white">Based on your past sessions, Thursday morning looks perfect! 5-7ft swell, light winds, and high tide at 8am. 🏄‍♂️</p>
                                </div>
                              </div>

                              <div className="flex justify-start">
                                <div className="bg-white rounded-2xl rounded-tl-sm p-3 shadow-sm max-w-[200px]">
                                  <p className="text-sm text-gray-700">What about Saturday?</p>
                                </div>
                              </div>

                              <div className="flex justify-end">
                                <div className="bg-blue-600 rounded-2xl rounded-tr-sm p-3 shadow-sm max-w-[200px]">
                                  <p className="text-sm text-white">Saturday looks choppy with strong onshore winds. I'd skip it. Thursday is your best bet! 👍</p>
                                </div>
                              </div>
                            </div>

                            {/* Input Bar */}
                            <div className="absolute bottom-8 left-6 right-6">
                              <div className="bg-white rounded-full shadow-lg border border-gray-200 px-4 py-2 flex items-center">
                                <input 
                                  className="flex-1 text-sm outline-none"
                                  placeholder="Ask anything..."
                                  disabled
                                />
                                <div className="w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center">
                                  <Sparkles className="w-3 h-3 text-white" />
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                    <p className="text-center mt-4 text-sm font-medium text-gray-700">AI-Powered Insights</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Email Signup */}
            <div className="mt-16 max-w-md mx-auto">
              <p className="text-sm font-medium text-gray-700 mb-4">
                Join the waitlist for early access
              </p>
              <form onSubmit={handleEmailSignup} className="flex flex-col sm:flex-row gap-3">
                <div className="flex-1">
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="Enter your email"
                    required
                    className="w-full rounded-lg border border-gray-300 px-4 py-3 text-gray-900 placeholder-gray-500 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <button
                  type="submit"
                  disabled={isSubmitted}
                  className="inline-flex items-center justify-center rounded-lg bg-blue-600 px-6 py-3 text-white font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors disabled:bg-green-500"
                >
                  {isSubmitted ? 'Thanks! 🤙' : 'Get Early Access'}
                </button>
              </form>
              <p className="mt-3 text-sm text-gray-500">
                Join the waitlist for early access. No spam, just waves. 🏄‍♂️
              </p>
            </div>
          </div>

          {/* Value Props */}
          <div className="mx-auto max-w-6xl mt-32">
            <h2 className="text-3xl font-bold text-center text-gray-900 mb-4">
              Built for Surfers Who Actually Surf
            </h2>
            <p className="text-center text-gray-600 mb-12 max-w-2xl mx-auto">
              Not another generic surf forecast. SwellSense learns what you like and tells you when to paddle out.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {/* Session Tracking */}
              <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 hover:shadow-md transition-all hover:-translate-y-1">
                <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 text-white mb-4">
                  <Smartphone className="w-6 h-6" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Quick Session Logging</h3>
                <p className="text-sm text-gray-600">
                  Log every surf in 30 seconds. Rate conditions, track waves caught, add notes.
                </p>
              </div>

              {/* AI Learning */}
              <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 hover:shadow-md transition-all hover:-translate-y-1">
                <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-purple-600 text-white mb-4">
                  <Sparkles className="w-6 h-6" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Learns Your Style</h3>
                <p className="text-sm text-gray-600">
                  The more you log, the smarter it gets. AI understands what conditions you actually enjoy.
                </p>
              </div>

              {/* Push Alerts */}
              <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 hover:shadow-md transition-all hover:-translate-y-1">
                <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-500 to-cyan-600 text-white mb-4">
                  <Zap className="w-6 h-6" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Smart Alerts</h3>
                <p className="text-sm text-gray-600">
                  Get notified when YOUR favorite spots are firing. No more checking forecasts all day.
                </p>
              </div>

              {/* Real-Time Data */}
              <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 hover:shadow-md transition-all hover:-translate-y-1">
                <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-gradient-to-br from-green-500 to-green-600 text-white mb-4">
                  <TrendingUp className="w-6 h-6" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Live Buoy Data</h3>
                <p className="text-sm text-gray-600">
                  Real-time NOAA buoy readings, wind data, and tide charts updated every 3 hours.
                </p>
              </div>
            </div>

            {/* Additional Feature Highlight */}
            <div className="mt-12 bg-gradient-to-r from-blue-50 to-cyan-50 rounded-2xl p-8 border border-blue-100">
              <div className="flex flex-col md:flex-row items-center gap-6">
                <div className="flex-shrink-0">
                  <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
                    <Heart className="w-8 h-8 text-white" />
                  </div>
                </div>
                <div className="flex-1 text-center md:text-left">
                  <h3 className="text-xl font-bold text-gray-900 mb-2">
                    The More You Surf, The Smarter It Gets
                  </h3>
                  <p className="text-gray-600">
                    SwellSense analyzes your session history to predict exactly when you'll score. 
                    Think of it as Surfline meets Strava meets your best surf buddy who always knows when it's firing.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* How It Works */}
          <div className="mx-auto max-w-4xl mt-32">
            <h2 className="text-3xl font-bold text-center text-gray-900 mb-4">
              Three Steps to Better Surf Sessions
            </h2>
            <p className="text-center text-gray-600 mb-12">
              It's that simple. Start logging, start scoring.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-blue-100 text-blue-600 font-bold text-2xl mb-4">
                  1
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Log Your Sessions</h3>
                <p className="text-sm text-gray-600">
                  Quick tap after every surf. Rate it, add notes, done in 30 seconds.
                </p>
              </div>
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-purple-100 text-purple-600 font-bold text-2xl mb-4">
                  2
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">AI Learns Your Preferences</h3>
                <p className="text-sm text-gray-600">
                  SwellSense analyzes what conditions you actually enjoyed—not what the forecast says.
                </p>
              </div>
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-cyan-100 text-cyan-600 font-bold text-2xl mb-4">
                  3
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Get Personalized Alerts</h3>
                <p className="text-sm text-gray-600">
                  Notifications when your spots are firing. No more guessing, just surfing.
                </p>
              </div>
            </div>
          </div>

          {/* Social Proof / Stats */}
          <div className="mx-auto max-w-4xl mt-24 text-center">
            <div className="bg-gradient-to-r from-blue-600 to-cyan-600 rounded-2xl p-12 text-white">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-8">
                <div>
                  <div className="text-5xl font-bold mb-2">10+</div>
                  <div className="text-sm opacity-90">NOAA Buoy Stations</div>
                </div>
                <div>
                  <div className="text-5xl font-bold mb-2">24/7</div>
                  <div className="text-sm opacity-90">Real-Time Updates</div>
                </div>
                <div>
                  <div className="text-5xl font-bold mb-2">GPT-4</div>
                  <div className="text-sm opacity-90">AI-Powered Analysis</div>
                </div>
              </div>
            </div>
          </div>
        </main>

        {/* Footer */}
        <footer className="border-t border-gray-200 bg-white mt-20">
          <div className="mx-auto max-w-7xl px-6 py-12">
            <div className="flex flex-col md:flex-row items-center justify-between">
              <div className="flex items-center space-x-2 mb-4 md:mb-0">
                <WavesIcon className="h-6 w-6 text-blue-600" />
                <span className="font-medium text-gray-900">SwellSense</span>
              </div>
              <div className="flex items-center space-x-6 text-sm text-gray-600">
                <Link href="/forecast" className="hover:text-gray-900">Forecast</Link>
                <Link href="/ai" className="hover:text-gray-900">AI Chat</Link>
                <a href="https://github.com/rbradshaw9/swellsense" className="hover:text-gray-900" target="_blank" rel="noopener noreferrer">
                  GitHub
                </a>
              </div>
              <p className="mt-4 md:mt-0 text-sm text-gray-500">
                Built for surfers, by surfers. 🌊
              </p>
            </div>
          </div>
        </footer>
      </div>
    </>
  )
}

export default Home
