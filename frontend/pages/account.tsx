import type { NextPage } from 'next'
import Head from 'next/head'
import { useEffect } from 'react'
import { useRouter } from 'next/router'
import { useAuth } from '../context/AuthContext'
import { User, Mail, LogOut, Loader2 } from 'lucide-react'
import toast from 'react-hot-toast'

const Account: NextPage = () => {
  const { user, loading, signOut } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!loading && !user) {
      toast.error('Please sign in to view your account')
      router.push('/login')
    }
  }, [user, loading, router])

  const handleSignOut = async () => {
    try {
      await signOut()
      toast.success('Signed out successfully')
    } catch (error) {
      toast.error('Failed to sign out')
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-cyan-500 via-blue-600 to-blue-700 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-white animate-spin mx-auto mb-4" />
          <p className="text-white text-lg">Loading...</p>
        </div>
      </div>
    )
  }

  if (!user) {
    return null
  }

  return (
    <>
      <Head>
        <title>Account - SwellSense</title>
        <meta name="description" content="Manage your SwellSense account" />
      </Head>

      <div className="min-h-screen bg-gradient-to-br from-cyan-500 via-blue-600 to-blue-700 px-4 py-12">
        <div className="max-w-2xl mx-auto">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center p-3 bg-white/20 backdrop-blur-sm rounded-xl shadow-lg mb-4">
              <User className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-4xl font-bold text-white mb-2">Your Account</h1>
            <p className="text-blue-100">Manage your SwellSense profile</p>
          </div>

          {/* Account Info Card */}
          <div className="bg-white/10 backdrop-blur-md rounded-2xl shadow-2xl border border-white/20 p-8 mb-6">
            <h2 className="text-2xl font-semibold text-white mb-6">Profile Information</h2>
            
            <div className="space-y-4">
              {/* Email */}
              <div className="flex items-center space-x-3 p-4 bg-white/10 rounded-xl">
                <Mail className="w-5 h-5 text-blue-200" />
                <div className="flex-1">
                  <p className="text-sm text-blue-100">Email</p>
                  <p className="text-white font-medium">{user.email}</p>
                </div>
              </div>

              {/* User ID */}
              <div className="flex items-center space-x-3 p-4 bg-white/10 rounded-xl">
                <User className="w-5 h-5 text-blue-200" />
                <div className="flex-1">
                  <p className="text-sm text-blue-100">User ID</p>
                  <p className="text-white font-mono text-sm">{user.id}</p>
                </div>
              </div>

              {/* Account Created */}
              <div className="flex items-center space-x-3 p-4 bg-white/10 rounded-xl">
                <User className="w-5 h-5 text-blue-200" />
                <div className="flex-1">
                  <p className="text-sm text-blue-100">Member Since</p>
                  <p className="text-white font-medium">
                    {user.created_at ? new Date(user.created_at).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric'
                    }) : 'Unknown'}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Coming Soon Features */}
          <div className="bg-white/10 backdrop-blur-md rounded-2xl shadow-2xl border border-white/20 p-8 mb-6">
            <h2 className="text-2xl font-semibold text-white mb-4">Coming Soon</h2>
            <div className="space-y-3 text-blue-100">
              <p className="flex items-start">
                <span className="text-blue-300 mr-2">🌟</span>
                <span>Save favorite surf spots</span>
              </p>
              <p className="flex items-start">
                <span className="text-blue-300 mr-2">🏄</span>
                <span>Set your skill level for personalized recommendations</span>
              </p>
              <p className="flex items-start">
                <span className="text-blue-300 mr-2">📊</span>
                <span>Track your surf sessions</span>
              </p>
              <p className="flex items-start">
                <span className="text-blue-300 mr-2">🔔</span>
                <span>Get alerts for optimal conditions</span>
              </p>
            </div>
          </div>

          {/* Actions */}
          <div className="space-y-3">
            <button
              onClick={handleSignOut}
              className="w-full py-3 bg-red-500 hover:bg-red-600 text-white rounded-xl transition-colors flex items-center justify-center space-x-2 font-medium shadow-lg"
            >
              <LogOut className="w-5 h-5" />
              <span>Sign Out</span>
            </button>
          </div>
        </div>
      </div>
    </>
  )
}

export default Account
