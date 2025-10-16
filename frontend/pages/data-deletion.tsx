import Head from 'next/head';

export default function DataDeletion() {
  return (
    <>
      <Head>
        <title>Data Deletion - SwellSense</title>
        <meta name="description" content="Request deletion of your SwellSense data" />
      </Head>

      <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-3xl mx-auto bg-white shadow-lg rounded-lg p-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-8">Data Deletion Request</h1>
          
          <div className="mb-8 bg-blue-50 border-l-4 border-blue-400 p-4">
            <p className="text-blue-700">
              This page is for users who have used Facebook Login to access SwellSense and wish to 
              delete their data.
            </p>
          </div>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">How to Request Data Deletion</h2>
            <p className="text-gray-700 leading-relaxed mb-4">
              If you would like to delete all your data from SwellSense, you have several options:
            </p>
          </section>

          <section className="mb-8">
            <h3 className="text-xl font-semibold text-gray-800 mb-3">Option 1: Delete Through Your Account</h3>
            <ol className="list-decimal list-inside text-gray-700 space-y-2 ml-4">
              <li>Log in to your SwellSense account</li>
              <li>Go to your <a href="/account" className="text-blue-600 hover:underline">Account Settings</a></li>
              <li>Scroll to the bottom and click "Delete Account"</li>
              <li>Confirm the deletion</li>
            </ol>
            <p className="text-gray-600 text-sm mt-2 italic">
              This will immediately delete your account and all associated data.
            </p>
          </section>

          <section className="mb-8">
            <h3 className="text-xl font-semibold text-gray-800 mb-3">Option 2: Remove Facebook App Access</h3>
            <ol className="list-decimal list-inside text-gray-700 space-y-2 ml-4">
              <li>Go to your Facebook Settings</li>
              <li>Click on "Apps and Websites"</li>
              <li>Find "SwellSense" in the list</li>
              <li>Click "Remove"</li>
            </ol>
            <p className="text-gray-600 text-sm mt-2 italic">
              This will automatically trigger a data deletion request. Your data will be deleted within 30 days.
            </p>
          </section>

          <section className="mb-8">
            <h3 className="text-xl font-semibold text-gray-800 mb-3">Option 3: Email Request</h3>
            <p className="text-gray-700 leading-relaxed mb-3">
              Send an email to <a href="mailto:privacy@swellsense.app" className="text-blue-600 hover:underline font-semibold">privacy@swellsense.app</a> with:
            </p>
            <ul className="list-disc list-inside text-gray-700 space-y-2 ml-4">
              <li>Subject: "Data Deletion Request"</li>
              <li>Your email address associated with SwellSense</li>
              <li>Your Facebook ID (if known) or name you used to log in</li>
            </ul>
            <p className="text-gray-600 text-sm mt-2 italic">
              We will respond within 48 hours and complete deletion within 30 days.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">What Data Will Be Deleted?</h2>
            <p className="text-gray-700 leading-relaxed mb-3">
              When you request data deletion, we will permanently remove:
            </p>
            <ul className="list-disc list-inside text-gray-700 space-y-2 ml-4">
              <li>Your account profile (name, email, profile picture)</li>
              <li>Your saved favorite locations</li>
              <li>Your forecast preferences and settings</li>
              <li>Any chat or AI conversation history</li>
              <li>Your Facebook login association</li>
              <li>Any other personal data we have stored</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">Data Deletion Timeline</h2>
            <div className="bg-gray-50 p-4 rounded-lg">
              <ul className="text-gray-700 space-y-2">
                <li>
                  <strong>Immediate:</strong> Account access revoked, profile hidden
                </li>
                <li>
                  <strong>Within 30 days:</strong> All personal data permanently deleted from our systems
                </li>
                <li>
                  <strong>Within 90 days:</strong> Data removed from backups and archives
                </li>
              </ul>
            </div>
            <p className="text-gray-600 text-sm mt-3">
              Note: We may retain anonymized, aggregated data for analytics purposes, but this data 
              cannot be linked back to you.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">Check Deletion Status</h2>
            <p className="text-gray-700 leading-relaxed mb-3">
              If you've submitted a deletion request and want to check its status:
            </p>
            <div className="bg-blue-50 p-4 rounded-lg">
              <p className="text-gray-700 mb-2">
                Email: <a href="mailto:privacy@swellsense.app" className="text-blue-600 hover:underline font-semibold">privacy@swellsense.app</a>
              </p>
              <p className="text-gray-700">
                Include your confirmation code (if you received one) or the email address you used.
              </p>
            </div>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">Questions?</h2>
            <p className="text-gray-700 leading-relaxed mb-3">
              If you have questions about data deletion or privacy:
            </p>
            <ul className="list-disc list-inside text-gray-700 space-y-2 ml-4">
              <li>Read our <a href="/privacy" className="text-blue-600 hover:underline">Privacy Policy</a></li>
              <li>Contact us at <a href="mailto:privacy@swellsense.app" className="text-blue-600 hover:underline">privacy@swellsense.app</a></li>
              <li>Review your <a href="/account" className="text-blue-600 hover:underline">Account Settings</a></li>
            </ul>
          </section>

          <div className="mt-12 pt-8 border-t border-gray-200">
            <p className="text-center text-gray-600">
              <a href="/privacy" className="text-blue-600 hover:underline mr-4">Privacy Policy</a>
              <a href="/terms" className="text-blue-600 hover:underline mr-4">Terms of Service</a>
              <a href="/" className="text-blue-600 hover:underline">Back to SwellSense</a>
            </p>
          </div>
        </div>
      </div>
    </>
  );
}
