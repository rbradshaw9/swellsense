import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { WavesIcon, BarChart3, MessageSquare, User, LogIn } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Navbar: React.FC = () => {
  const router = useRouter();
  const { user, loading } = useAuth();

  const isActive = (path: string) => router.pathname === path;

  return (
    <nav className="sticky top-0 z-50 bg-white/95 backdrop-blur-sm border-b border-gray-200 shadow-sm">
      <div className="mx-auto max-w-7xl px-6">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-2 hover:opacity-80 transition-opacity">
            <WavesIcon className="h-8 w-8 text-blue-600" />
            <span className="text-2xl font-bold text-gray-900">SwellSense</span>
          </Link>

          {/* Navigation Links */}
          <div className="flex items-center space-x-1">
            <Link
              href="/"
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                isActive('/')
                  ? 'bg-blue-50 text-blue-600'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              Home
            </Link>
            <Link
              href="/forecast"
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors inline-flex items-center ${
                isActive('/forecast')
                  ? 'bg-blue-50 text-blue-600'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              <BarChart3 className="w-4 h-4 mr-1.5" />
              Forecast
            </Link>
            <Link
              href="/ai"
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors inline-flex items-center ${
                isActive('/ai')
                  ? 'bg-blue-50 text-blue-600'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              <MessageSquare className="w-4 h-4 mr-1.5" />
              AI Chat
            </Link>
          </div>

          {/* Auth Section */}
          <div className="hidden md:block">
            {loading ? (
              <div className="w-24 h-10 bg-gray-100 rounded-lg animate-pulse" />
            ) : user ? (
              <Link
                href="/account"
                className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors inline-flex items-center ${
                  isActive('/account')
                    ? 'bg-blue-50 text-blue-600'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <User className="w-4 h-4 mr-1.5" />
                Account
              </Link>
            ) : (
              <Link
                href="/login"
                className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 transition-colors inline-flex items-center"
              >
                <LogIn className="w-4 h-4 mr-1.5" />
                Sign In
              </Link>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
