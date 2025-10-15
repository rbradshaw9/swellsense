import type { NextPage } from 'next'
import Head from 'next/head'
import { useState } from 'react'
import { ChevronRightIcon, WavesIcon } from 'lucide-react'

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
        {/* Navigation */}
        <nav className="relative px-6 py-4">
          <div className="mx-auto flex max-w-7xl items-center justify-between">
            <div className="flex items-center space-x-2">
              <WavesIcon className="h-8 w-8 text-blue-600" />
              <span className="text-2xl font-bold text-gray-900">SwellSense</span>
            </div>
            <div className="hidden md:flex items-center space-x-6">
              <a href="#features" className="text-gray-600 hover:text-gray-900">Features</a>
              <a href="#about" className="text-gray-600 hover:text-gray-900">About</a>
              <button className="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 transition-colors">
                Get Early Access
              </button>
            </div>
          </div>
        </nav>

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

            {/* Email Signup */}
            <div className="mt-12 max-w-md mx-auto">
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
                  className="inline-flex items-center rounded-lg bg-blue-600 px-6 py-3 text-white font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors disabled:bg-green-500"
                >
                  {isSubmitted ? (
                    'Thanks! 🤙'
                  ) : (
                    <>
                      Get Early Access
                      <ChevronRightIcon className="ml-2 h-4 w-4" />
                    </>
                  )}
                </button>
              </form>
              <p className="mt-3 text-sm text-gray-500">
                Join the waitlist for early access. No spam, just waves. 🏄‍♂️
              </p>
            </div>

            {/* Features Preview */}
            <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-12 h-12 rounded-lg bg-blue-100 text-blue-600 mb-4">
                  📊
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">Real-Time Data</h3>
                <p className="text-gray-600 text-sm">
                  Live buoy readings, wind data, and tide information
                </p>
              </div>
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-12 h-12 rounded-lg bg-blue-100 text-blue-600 mb-4">
                  🤖
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">AI Predictions</h3>
                <p className="text-gray-600 text-sm">
                  Machine learning models trained on surf conditions
                </p>
              </div>
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-12 h-12 rounded-lg bg-blue-100 text-blue-600 mb-4">
                  📍
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">Local Focus</h3>
                <p className="text-gray-600 text-sm">
                  Personalized forecasts for your favorite breaks
                </p>
              </div>
            </div>
          </div>
        </main>

        {/* Footer */}
        <footer className="border-t border-gray-200 bg-white">
          <div className="mx-auto max-w-7xl px-6 py-8">
            <div className="flex flex-col md:flex-row items-center justify-between">
              <div className="flex items-center space-x-2">
                <WavesIcon className="h-6 w-6 text-blue-600" />
                <span className="font-medium text-gray-900">SwellSense</span>
              </div>
              <p className="mt-4 md:mt-0 text-sm text-gray-500">
                Built for surfers, by surfers. Coming soon. 🌊
              </p>
            </div>
          </div>
        </footer>
      </div>
    </>
  )
}

export default Home