import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { WavesIcon, BarChart3, MessageSquare, User, LogIn, Menu, X } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Navbar: React.FC = () => {
  const router = useRouter();
  const { user, loading } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const isActive = (path: string) => router.pathname === path;

  const closeMobileMenu = () => setMobileMenuOpen(false);

  return (
    <nav className="sticky top-0 z-50 bg-white/95 backdrop-blur-sm border-b border-gray-200 shadow-sm">
      <div className="mx-auto max-w-7xl px-4 sm:px-6">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link 
            href="/" 
            className="flex items-center space-x-2 hover:opacity-80 transition-opacity"
            onClick={closeMobileMenu}
          >
            <WavesIcon className="h-7 w-7 sm:h-8 sm:w-8 text-blue-600" />
            <span className="text-xl sm:text-2xl font-bold text-gray-900">SwellSense</span>
          </Link>

          {/* Desktop Navigation Links */}
          <div className="hidden md:flex items-center space-x-1">
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

          {/* Desktop Auth Section */}
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

          {/* Mobile Menu Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2 rounded-lg text-gray-600 hover:bg-gray-100 transition-colors"
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden py-4 space-y-2 border-t border-gray-200">
            <Link
              href="/"
              onClick={closeMobileMenu}
              className={`block px-4 py-3 rounded-lg text-base font-medium transition-colors ${
                isActive('/')
                  ? 'bg-blue-50 text-blue-600'
                  : 'text-gray-600 hover:bg-gray-50'
              }`}
            >
              Home
            </Link>
            <Link
              href="/forecast"
              onClick={closeMobileMenu}
              className={`block px-4 py-3 rounded-lg text-base font-medium transition-colors ${
                isActive('/forecast')
                  ? 'bg-blue-50 text-blue-600'
                  : 'text-gray-600 hover:bg-gray-50'
              }`}
            >
              <BarChart3 className="w-5 h-5 inline mr-2" />
              Forecast
            </Link>
            <Link
              href="/ai"
              onClick={closeMobileMenu}
              className={`block px-4 py-3 rounded-lg text-base font-medium transition-colors ${
                isActive('/ai')
                  ? 'bg-blue-50 text-blue-600'
                  : 'text-gray-600 hover:bg-gray-50'
              }`}
            >
              <MessageSquare className="w-5 h-5 inline mr-2" />
              AI Chat
            </Link>
            {loading ? (
              <div className="px-4 py-3">
                <div className="w-full h-12 bg-gray-100 rounded-lg animate-pulse" />
              </div>
            ) : user ? (
              <Link
                href="/account"
                onClick={closeMobileMenu}
                className={`block px-4 py-3 rounded-lg text-base font-medium transition-colors ${
                  isActive('/account')
                    ? 'bg-blue-50 text-blue-600'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <User className="w-5 h-5 inline mr-2" />
                Account
              </Link>
            ) : (
              <Link
                href="/login"
                onClick={closeMobileMenu}
                className="block mx-4 rounded-lg bg-blue-600 px-4 py-3 text-base font-medium text-white hover:bg-blue-700 transition-colors text-center"
              >
                <LogIn className="w-5 h-5 inline mr-2" />
                Sign In
              </Link>
            )}
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
