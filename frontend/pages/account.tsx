import type { NextPage } from 'next'
import Head from 'next/head'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/router'
import { useAuth } from '../context/AuthContext'
import { User, Mail, LogOut, Loader2, Edit, Save, X, Check } from 'lucide-react'
import toast from 'react-hot-toast'
import { api, ExtendedUserProfile, UserPreferences } from '../utils/api'
import { supabase } from '../lib/supabaseClient'

const Account: NextPage = () => {
  const { user, loading: authLoading, signOut } = useAuth()
  const router = useRouter()
  
  const [profile, setProfile] = useState<ExtendedUserProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [editing, setEditing] = useState(false)
  const [saving, setSaving] = useState(false)
  
  // Editable fields
  const [username, setUsername] = useState('')
  const [name, setName] = useState('')
  const [homeSpot, setHomeSpot] = useState('')
  const [units, setUnits] = useState<'imperial' | 'metric'>('imperial')
  const [skillLevel, setSkillLevel] = useState<'beginner' | 'intermediate' | 'advanced' | 'expert'>('intermediate')
  const [boardType, setBoardType] = useState<'shortboard' | 'longboard' | 'funboard' | 'fish' | 'gun'>('shortboard')
  const [notifications, setNotifications] = useState(true)
  const [aiPersona, setAiPersona] = useState<'beginner' | 'experienced' | 'expert' | 'local'>('experienced')
  
  const [usernameAvailable, setUsernameAvailable] = useState<boolean | null>(null)
  const [checkingUsername, setCheckingUsername] = useState(false)

  useEffect(() => {
    if (!authLoading && !user) {
      toast.error('Please sign in to view your account')
      router.push('/login')
    }
  }, [user, authLoading, router])

  useEffect(() => {
    if (user) {
      loadProfile()
    }
  }, [user])

  const loadProfile = async () => {
    try {
      const session = await supabase.auth.getSession()
      const token = session.data.session?.access_token
      
      if (!token) {
        throw new Error('No auth token')
      }

      const profileData = await api.getProfile(token)
      setProfile(profileData)
      
      // Initialize form fields
      setUsername(profileData.username || '')
      setName(profileData.name || '')
      setHomeSpot(profileData.home_spot || '')
      setUnits(profileData.preferences.units)
      setSkillLevel(profileData.preferences.skill_level)
      setBoardType(profileData.preferences.board_type)
      setNotifications(profileData.preferences.notifications)
      setAiPersona(profileData.preferences.ai_persona)
    } catch (error) {
      console.error('Failed to load profile:', error)
      toast.error('Failed to load profile')
    } finally {
      setLoading(false)
    }
  }

  const checkUsername = async (value: string) => {
    if (!value || value === profile?.username) {
      setUsernameAvailable(null)
      return
    }

    if (value.length < 3 || value.length > 30) {
      setUsernameAvailable(false)
      return
    }

    setCheckingUsername(true)
    try {
      const result = await api.checkUsernameAvailability(value)
      setUsernameAvailable(result.available)
    } catch (error) {
      console.error('Username check failed:', error)
    } finally {
      setCheckingUsername(false)
    }
  }

  const handleSave = async () => {
    if (username && !usernameAvailable && username !== profile?.username) {
      toast.error('Username is not available')
      return
    }

    setSaving(true)
    try {
      const session = await supabase.auth.getSession()
      const token = session.data.session?.access_token
      
      if (!token) {
        throw new Error('No auth token')
      }

      await api.updateProfile(token, {
        username: username || undefined,
        name: name || undefined,
        home_spot: homeSpot || undefined,
        preferences: {
          units,
          skill_level: skillLevel,
          board_type: boardType,
          notifications,
          ai_persona: aiPersona,
        },
      })

      toast.success('Profile updated successfully!')
      setEditing(false)
      await loadProfile()
    } catch (error: any) {
      console.error('Failed to update profile:', error)
      toast.error(error.message || 'Failed to update profile')
    } finally {
      setSaving(false)
    }
  }

  const handleCancel = () => {
    // Reset form fields
    setUsername(profile?.username || '')
    setName(profile?.name || '')
    setHomeSpot(profile?.home_spot || '')
    setUnits(profile?.preferences.units || 'imperial')
    setSkillLevel(profile?.preferences.skill_level || 'intermediate')
    setBoardType(profile?.preferences.board_type || 'shortboard')
    setNotifications(profile?.preferences.notifications ?? true)
    setAiPersona(profile?.preferences.ai_persona || 'experienced')
    setUsernameAvailable(null)
    setEditing(false)
  }

  const handleSignOut = async () => {
    try {
      await signOut()
      toast.success('Signed out successfully')
    } catch (error) {
      toast.error('Failed to sign out')
    }
  }

  if (authLoading || loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-cyan-500 via-blue-600 to-blue-700 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-white animate-spin mx-auto mb-4" />
          <p className="text-white text-lg">Loading...</p>
        </div>
      </div>
    )
  }

  if (!user || !profile) {
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
            <p className="text-blue-100">Manage your SwellSense profile and preferences</p>
          </div>

          {/* Profile Card */}
          <div className="bg-white/10 backdrop-blur-md rounded-2xl shadow-2xl border border-white/20 p-8 mb-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-semibold text-white">Profile Information</h2>
              {!editing ? (
                <button
                  onClick={() => setEditing(true)}
                  className="flex items-center space-x-2 px-4 py-2 bg-white/20 hover:bg-white/30 text-white rounded-lg transition-colors"
                >
                  <Edit className="w-4 h-4" />
                  <span>Edit</span>
                </button>
              ) : (
                <div className="flex space-x-2">
                  <button
                    onClick={handleCancel}
                    disabled={saving}
                    className="flex items-center space-x-2 px-4 py-2 bg-red-500/80 hover:bg-red-500 text-white rounded-lg transition-colors disabled:opacity-50"
                  >
                    <X className="w-4 h-4" />
                    <span>Cancel</span>
                  </button>
                  <button
                    onClick={handleSave}
                    disabled={saving || (username !== profile.username && !usernameAvailable)}
                    className="flex items-center space-x-2 px-4 py-2 bg-green-500/80 hover:bg-green-500 text-white rounded-lg transition-colors disabled:opacity-50"
                  >
                    {saving ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Save className="w-4 h-4" />
                    )}
                    <span>{saving ? 'Saving...' : 'Save'}</span>
                  </button>
                </div>
              )}
            </div>
            
            <div className="space-y-4">
              {/* Email (Read-only) */}
              <div className="flex items-center space-x-3 p-4 bg-white/10 rounded-xl">
                <Mail className="w-5 h-5 text-blue-200" />
                <div className="flex-1">
                  <p className="text-sm text-blue-100">Email</p>
                  <p className="text-white font-medium">{user.email}</p>
                </div>
              </div>

              {/* Username */}
              <div className="p-4 bg-white/10 rounded-xl">
                <label className="text-sm text-blue-100 block mb-2">Username</label>
                {editing ? (
                  <div className="relative">
                    <input
                      type="text"
                      value={username}
                      onChange={(e) => {
                        const value = e.target.value
                        setUsername(value)
                        checkUsername(value)
                      }}
                      placeholder="surferbro"
                      className="w-full px-3 py-2 bg-white/20 text-white placeholder-blue-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-300"
                      pattern="[a-zA-Z0-9_-]+"
                      minLength={3}
                      maxLength={30}
                    />
                    {checkingUsername && (
                      <Loader2 className="absolute right-3 top-2.5 w-5 h-5 text-blue-200 animate-spin" />
                    )}
                    {!checkingUsername && username && username !== profile.username && (
                      <div className="absolute right-3 top-2.5">
                        {usernameAvailable ? (
                          <Check className="w-5 h-5 text-green-400" />
                        ) : (
                          <X className="w-5 h-5 text-red-400" />
                        )}
                      </div>
                    )}
                  </div>
                ) : (
                  <p className="text-white font-medium">{profile.username || 'Not set'}</p>
                )}
                {editing && username && username.length < 3 && (
                  <p className="text-xs text-red-300 mt-1">Username must be at least 3 characters</p>
                )}
              </div>

              {/* Name */}
              <div className="p-4 bg-white/10 rounded-xl">
                <label className="text-sm text-blue-100 block mb-2">Name</label>
                {editing ? (
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="John Doe"
                    className="w-full px-3 py-2 bg-white/20 text-white placeholder-blue-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-300"
                    maxLength={100}
                  />
                ) : (
                  <p className="text-white font-medium">{profile.name || 'Not set'}</p>
                )}
              </div>

              {/* Home Spot */}
              <div className="p-4 bg-white/10 rounded-xl">
                <label className="text-sm text-blue-100 block mb-2">Home Spot</label>
                {editing ? (
                  <input
                    type="text"
                    value={homeSpot}
                    onChange={(e) => setHomeSpot(e.target.value)}
                    placeholder="Rincon, Puerto Rico"
                    className="w-full px-3 py-2 bg-white/20 text-white placeholder-blue-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-300"
                    maxLength={100}
                  />
                ) : (
                  <p className="text-white font-medium">{profile.home_spot || 'Not set'}</p>
                )}
              </div>
            </div>
          </div>

          {/* Preferences Card */}
          <div className="bg-white/10 backdrop-blur-md rounded-2xl shadow-2xl border border-white/20 p-8 mb-6">
            <h2 className="text-2xl font-semibold text-white mb-6">Preferences</h2>
            
            <div className="space-y-4">
              {/* Units */}
              <div className="p-4 bg-white/10 rounded-xl">
                <label className="text-sm text-blue-100 block mb-2">Units</label>
                {editing ? (
                  <select
                    value={units}
                    onChange={(e) => setUnits(e.target.value as 'imperial' | 'metric')}
                    className="w-full px-3 py-2 bg-white/20 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-300"
                  >
                    <option value="imperial">Imperial (ft, mph)</option>
                    <option value="metric">Metric (m, km/h)</option>
                  </select>
                ) : (
                  <p className="text-white font-medium capitalize">{profile.preferences.units}</p>
                )}
              </div>

              {/* Skill Level */}
              <div className="p-4 bg-white/10 rounded-xl">
                <label className="text-sm text-blue-100 block mb-2">Skill Level</label>
                {editing ? (
                  <select
                    value={skillLevel}
                    onChange={(e) => setSkillLevel(e.target.value as any)}
                    className="w-full px-3 py-2 bg-white/20 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-300"
                  >
                    <option value="beginner">Beginner</option>
                    <option value="intermediate">Intermediate</option>
                    <option value="advanced">Advanced</option>
                    <option value="expert">Expert</option>
                  </select>
                ) : (
                  <p className="text-white font-medium capitalize">{profile.preferences.skill_level}</p>
                )}
              </div>

              {/* Board Type */}
              <div className="p-4 bg-white/10 rounded-xl">
                <label className="text-sm text-blue-100 block mb-2">Board Type</label>
                {editing ? (
                  <select
                    value={boardType}
                    onChange={(e) => setBoardType(e.target.value as any)}
                    className="w-full px-3 py-2 bg-white/20 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-300"
                  >
                    <option value="shortboard">Shortboard</option>
                    <option value="longboard">Longboard</option>
                    <option value="funboard">Funboard</option>
                    <option value="fish">Fish</option>
                    <option value="gun">Gun</option>
                  </select>
                ) : (
                  <p className="text-white font-medium capitalize">{profile.preferences.board_type}</p>
                )}
              </div>

              {/* AI Persona */}
              <div className="p-4 bg-white/10 rounded-xl">
                <label className="text-sm text-blue-100 block mb-2">AI Assistant Style</label>
                {editing ? (
                  <select
                    value={aiPersona}
                    onChange={(e) => setAiPersona(e.target.value as any)}
                    className="w-full px-3 py-2 bg-white/20 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-300"
                  >
                    <option value="beginner">Beginner-friendly</option>
                    <option value="experienced">Experienced surfer</option>
                    <option value="expert">Expert analysis</option>
                    <option value="local">Local knowledge</option>
                  </select>
                ) : (
                  <p className="text-white font-medium capitalize">{profile.preferences.ai_persona}</p>
                )}
              </div>

              {/* Notifications */}
              <div className="p-4 bg-white/10 rounded-xl">
                <label className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-blue-100">Email Notifications</p>
                    <p className="text-xs text-blue-200 mt-1">Get alerts for optimal conditions</p>
                  </div>
                  {editing ? (
                    <input
                      type="checkbox"
                      checked={notifications}
                      onChange={(e) => setNotifications(e.target.checked)}
                      className="w-5 h-5 rounded bg-white/20 border-white/30 text-blue-500 focus:ring-2 focus:ring-blue-300"
                    />
                  ) : (
                    <span className="text-white font-medium">{profile.preferences.notifications ? 'On' : 'Off'}</span>
                  )}
                </label>
              </div>
            </div>
          </div>

          {/* Account Actions */}
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
