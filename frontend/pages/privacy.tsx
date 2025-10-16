import Head from 'next/head';

export default function Privacy() {
  return (
    <>
      <Head>
        <title>Privacy Policy - SwellSense</title>
        <meta name="description" content="SwellSense Privacy Policy" />
      </Head>

      <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto bg-white shadow-lg rounded-lg p-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-8">Privacy Policy</h1>
          
          <p className="text-sm text-gray-600 mb-8">
            <strong>Last Updated:</strong> October 16, 2025
          </p>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">1. Introduction</h2>
            <p className="text-gray-700 leading-relaxed mb-4">
              Welcome to SwellSense ("we," "our," or "us"). We are committed to protecting your privacy 
              and ensuring the security of your personal information. This Privacy Policy explains how we 
              collect, use, disclose, and safeguard your information when you use our AI-powered surf 
              forecast application and website.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">2. Information We Collect</h2>
            
            <h3 className="text-xl font-semibold text-gray-800 mb-3">2.1 Personal Information</h3>
            <ul className="list-disc list-inside text-gray-700 mb-4 space-y-2">
              <li>Email address (for account creation and authentication)</li>
              <li>Name (optional, for personalization)</li>
              <li>Profile information you choose to provide</li>
              <li>Location data (only when you search for surf forecasts)</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">2.2 Automatically Collected Information</h3>
            <ul className="list-disc list-inside text-gray-700 mb-4 space-y-2">
              <li>Device information (browser type, operating system)</li>
              <li>IP address and general location</li>
              <li>Usage data (pages visited, features used, time spent)</li>
              <li>Log data (API requests, errors, performance metrics)</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">2.3 Third-Party Authentication</h3>
            <p className="text-gray-700 leading-relaxed mb-4">
              If you choose to authenticate via Facebook or other third-party services, we receive 
              basic profile information as permitted by your privacy settings on those platforms.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">3. How We Use Your Information</h2>
            <ul className="list-disc list-inside text-gray-700 space-y-2">
              <li>To provide and maintain our surf forecast services</li>
              <li>To personalize your experience and deliver relevant forecasts</li>
              <li>To improve our AI models and forecast accuracy</li>
              <li>To communicate with you about service updates and features</li>
              <li>To analyze usage patterns and optimize performance</li>
              <li>To detect, prevent, and address technical issues or security threats</li>
              <li>To comply with legal obligations</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">4. Data Sources and Processing</h2>
            <p className="text-gray-700 leading-relaxed mb-4">
              SwellSense aggregates data from multiple third-party weather and oceanographic services 
              including StormGlass, OpenWeather, NOAA, Open-Meteo, Copernicus Marine, and others. We 
              process this data using artificial intelligence to provide you with accurate surf forecasts. 
              Your location searches are used solely to fetch relevant forecast data and are not stored 
              permanently unless you save them as favorites.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">5. Data Sharing and Disclosure</h2>
            
            <h3 className="text-xl font-semibold text-gray-800 mb-3">We do NOT sell your personal information.</h3>
            
            <p className="text-gray-700 leading-relaxed mb-4">We may share information only in these circumstances:</p>
            <ul className="list-disc list-inside text-gray-700 space-y-2">
              <li><strong>Service Providers:</strong> With trusted partners who help operate our service (hosting, analytics, authentication)</li>
              <li><strong>Legal Requirements:</strong> When required by law or to protect our rights</li>
              <li><strong>Business Transfers:</strong> In connection with a merger, acquisition, or sale of assets</li>
              <li><strong>With Your Consent:</strong> When you explicitly authorize sharing</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">6. Data Security</h2>
            <p className="text-gray-700 leading-relaxed mb-4">
              We implement industry-standard security measures to protect your information, including:
            </p>
            <ul className="list-disc list-inside text-gray-700 space-y-2">
              <li>Encrypted data transmission (HTTPS/TLS)</li>
              <li>Secure authentication via Supabase</li>
              <li>Regular security audits and updates</li>
              <li>Access controls and monitoring</li>
            </ul>
            <p className="text-gray-700 leading-relaxed mt-4">
              However, no method of transmission over the Internet is 100% secure. We cannot guarantee 
              absolute security of your data.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">7. Your Rights and Choices</h2>
            <p className="text-gray-700 leading-relaxed mb-4">You have the right to:</p>
            <ul className="list-disc list-inside text-gray-700 space-y-2">
              <li><strong>Access:</strong> Request a copy of your personal data</li>
              <li><strong>Correction:</strong> Update or correct inaccurate information</li>
              <li><strong>Deletion:</strong> Request deletion of your account and data</li>
              <li><strong>Opt-Out:</strong> Unsubscribe from marketing communications</li>
              <li><strong>Data Portability:</strong> Receive your data in a portable format</li>
            </ul>
            <p className="text-gray-700 leading-relaxed mt-4">
              To exercise these rights, contact us at <a href="mailto:privacy@swellsense.app" className="text-blue-600 hover:underline">privacy@swellsense.app</a>
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">8. Cookies and Tracking</h2>
            <p className="text-gray-700 leading-relaxed mb-4">
              We use cookies and similar technologies to maintain your session, remember preferences, 
              and analyze usage. You can control cookies through your browser settings, but this may 
              limit some functionality.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">9. Children's Privacy</h2>
            <p className="text-gray-700 leading-relaxed mb-4">
              SwellSense is not intended for children under 13. We do not knowingly collect information 
              from children. If you believe we have collected data from a child, please contact us 
              immediately.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">10. International Data Transfers</h2>
            <p className="text-gray-700 leading-relaxed mb-4">
              Your information may be transferred to and processed in countries other than your own. 
              We ensure appropriate safeguards are in place to protect your data in compliance with 
              applicable laws.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">11. Changes to This Policy</h2>
            <p className="text-gray-700 leading-relaxed mb-4">
              We may update this Privacy Policy from time to time. We will notify you of significant 
              changes by posting the new policy on this page and updating the "Last Updated" date. 
              Your continued use of SwellSense after changes constitutes acceptance of the updated policy.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">12. Contact Us</h2>
            <p className="text-gray-700 leading-relaxed mb-4">
              If you have questions or concerns about this Privacy Policy or our data practices:
            </p>
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="text-gray-700"><strong>Email:</strong> <a href="mailto:privacy@swellsense.app" className="text-blue-600 hover:underline">privacy@swellsense.app</a></p>
              <p className="text-gray-700"><strong>Website:</strong> <a href="https://swellsense.app" className="text-blue-600 hover:underline">https://swellsense.app</a></p>
            </div>
          </section>

          <div className="mt-12 pt-8 border-t border-gray-200">
            <p className="text-center text-gray-600">
              <a href="/terms" className="text-blue-600 hover:underline mr-4">Terms of Service</a>
              <a href="/" className="text-blue-600 hover:underline">Back to SwellSense</a>
            </p>
          </div>
        </div>
      </div>
    </>
  );
}
