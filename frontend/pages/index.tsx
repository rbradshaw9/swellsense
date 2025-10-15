import type { NextPage } from 'next'
import Head from 'next/head'
import Link from 'next/link'
import { useState } from 'react'
import { ChevronRightIcon, WavesIcon, BarChart3, Sparkles, MapPin } from 'lucide-react'

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
            <div className="inline-flex items-center rounded-full bg-blue-100 px-4 py-2 text-sm font-medium text-blue-800 mb-8">
              <span className="mr-2">🌊</span>
              AI-Powered Surf Forecasting
            </div>

            {/* Main Heading */}
            <h1 className="text-5xl font-bold tracking-tight text-gray-900 sm:text-7xl">
              Smarter Surf Forecasts,{' '}
              <span className="text-blue-600">Tuned to Your Break</span>
            </h1>

            {/* Subheading */}
            <p className="mt-6 text-xl leading-8 text-gray-600 max-w-2xl mx-auto">
              Get AI-powered surf predictions that analyze real-time buoy data, wind patterns, 
              and tide information to tell you exactly when and where to surf.
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
            <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
              Why SwellSense?
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {/* Real-Time Data */}
              <div className="bg-white rounded-xl p-8 shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
                <div className="inline-flex items-center justify-center w-14 h-14 rounded-lg bg-blue-100 text-blue-600 mb-6">
                  <BarChart3 className="w-7 h-7" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">Real-Time Data</h3>
                <p className="text-gray-600">
                  Live buoy readings, wind data, and tide information updated every 3 hours from NOAA stations.
                </p>
              </div>

              {/* AI Predictions */}
              <div className="bg-white rounded-xl p-8 shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
                <div className="inline-flex items-center justify-center w-14 h-14 rounded-lg bg-blue-100 text-blue-600 mb-6">
                  <Sparkles className="w-7 h-7" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">AI-Powered Insights</h3>
                <p className="text-gray-600">
                  Get intelligent surf recommendations and natural language explanations of conditions.
                </p>
              </div>

              {/* Local Focus */}
              <div className="bg-white rounded-xl p-8 shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
                <div className="inline-flex items-center justify-center w-14 h-14 rounded-lg bg-blue-100 text-blue-600 mb-6">
                  <MapPin className="w-7 h-7" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">Your Favorite Breaks</h3>
                <p className="text-gray-600">
                  Personalized forecasts tuned to your local surf spots and skill level.
                </p>
              </div>
            </div>
          </div>

          {/* Social Proof / Stats */}
          <div className="mx-auto max-w-4xl mt-32 text-center">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-8">
              <div>
                <div className="text-4xl font-bold text-blue-600">10+</div>
                <div className="mt-2 text-sm text-gray-600">Buoy Stations</div>
              </div>
              <div>
                <div className="text-4xl font-bold text-blue-600">24/7</div>
                <div className="mt-2 text-sm text-gray-600">Real-Time Updates</div>
              </div>
              <div>
                <div className="text-4xl font-bold text-blue-600">AI</div>
                <div className="mt-2 text-sm text-gray-600">Powered Insights</div>
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
