import { useEffect, useRef, useState } from 'react'

export default function Docs() {
  const containerRef = useRef(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
  setLoading(true)
  setError(null)

  const container = containerRef.current
  if (!container) return

  const renderRedoc = () => {
    if (!window.Redoc) {
      setError('ReDoc failed to load')
      setLoading(false)
      return
    }
    window.Redoc.init('/api/openapi.json', {}, container)
    setLoading(false)
  }

  if (window.Redoc) {
    renderRedoc()
    return
  }

  const script = document.createElement('script')
  script.src = 'https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js'
  script.async = true
  script.onload = renderRedoc
  script.onerror = () => {
    setError('Failed to load ReDoc script')
    setLoading(false)
  }
  document.head.appendChild(script)
}, [])


  return (
    <div>
      <h1 className="text-2xl font-semibold mb-4">API Documentation</h1>
      <p className="text-sm text-gray-600 mb-6">Rendered from the server-generated OpenAPI spec at <code>/api/openapi.json</code>.</p>

      {loading && !error && (
        <div className="p-6 bg-white rounded shadow text-sm text-gray-600">Loading API docs…</div>
      )}
      {error && (
        <div className="p-6 bg-red-50 border border-red-200 rounded text-red-700">{error}</div>
      )}

      <div ref={containerRef} className="bg-white rounded shadow overflow-hidden">
        {/* ReDoc will render inside here via the <redoc> custom element. */}
      </div>
    </div>
  )
}
