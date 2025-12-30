import { useState } from "react";

export default function App() {
  const [files, setFiles] = useState([]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);

  const API_URL = import.meta.env.VITE_API_URL

  function handleFileChange(event) {
    setFiles(event.target.files);
  }

  async function handleSubmit() {
    if (files.length === 0) return;

    const formData = new FormData();
    for (let file of files) {
      formData.append("file", file);
    }

    setLoading(true);
    setResult(null);

    try {
      const response = await fetch(`${API_URL}/api/upload`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      setResult(data);

      if (data.ok && data.session_id) {
        setSessionId(data.session_id)
      }

    } catch (err) {
      console.error(err);
      setResult({ ok: false, error: "Something went wrong" });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 py-12">
        <header className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            SEC EDGAR System Earnings Per Share File Analyzer
          </h1>
          <p className="text-gray-600">
            Upload HTML files of 8-K filese to extract and analyze earnings per share "EPS" data
          </p>
        </header>

        <div className="bg-white rounded-lg shadow-md p-8 mb-8">
          <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
            <input
              type="file"
              accept=".html"
              multiple
              onChange={handleFileChange}
              className="flex-1 text-sm text-gray-600 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100 cursor-pointer"
            />
            <button
              onClick={handleSubmit}
              disabled={loading || files.length === 0}
              className="px-6 py-2 bg-indigo-600 text-white font-medium rounded-md hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? "Uploading..." : "Upload"}
            </button>
          </div>
          {files.length > 0 && (
            <p className="mt-4 text-sm text-gray-600">
              {files.length} file{files.length > 1 ? "s" : ""} selected
            </p>
          )}
        </div>

        {result && result.ok && (
          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            <div className="px-6 py-4 bg-indigo-600 text-white">
              <h2 className="text-xl font-semibold">Results</h2>
              {sessionId && ( <a
                href={`${API_URL}/api/download/${sessionId}`}
                download
                className="px-4 py-2 bg-white text-indigo-600 font-medium rounded-md hover:bg-gray-100 transition-colors text-sm"
              >
                Download CSV
              </a>
              )}
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="bg-gray-100 border-b border-gray-200">
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                      Filename
                    </th>
                    <th className="px-6 py-3 text-right text-sm font-semibold text-gray-700">
                      EPS
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {result.result.map((item, index) => (
                    <tr
                      key={index}
                      className="border-b border-gray-100 hover:bg-indigo-50 transition-colors"
                    >
                      <td className="px-6 py-4 text-sm text-gray-900">
                        {item.filename}
                      </td>
                      <td
                        className={`px-6 py-4 text-sm font-semibold text-right ${
                          item.eps >= 0 ? "text-green-600" : "text-red-600"
                        }`}
                      >
                        {item.eps.toFixed(2)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {result && !result.ok && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Error</h3>
                <p className="mt-1 text-sm text-red-700">{result.error}</p>
              </div>
            </div>
          </div>
        )}

        <div className="mt-12 bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-3">
            Need 8-K Filings?
          </h2>
          <p className="text-gray-600 mb-4">
            You can download 8-K filings from the SEC EDGAR database to use with this analyzer.
          </p>
          <a
            href="https://www.sec.gov/search-filings"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center px-4 py-2 bg-gray-100 text-gray-700 font-medium rounded-md hover:bg-gray-200 transition-colors"
          >
            Visit SEC EDGAR Database
            <svg className="ml-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
          </a>
        </div>
      </div>
    </div>
  );
}