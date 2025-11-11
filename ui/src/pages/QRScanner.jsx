import { useEffect, useRef, useState } from 'react'
import jsQR from 'jsqr'
import APIService from '../services/api'
import { Button, Card, PageHeader, Alert } from '../components/UI'

export default function QRScanner({ onNavigate }) {
  const videoRef = useRef(null)
  const canvasRef = useRef(null)
  const [scanning, setScanning] = useState(true)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    let stream = null
    let requestId = null

    const startScanning = async () => {
      try {
        stream = await navigator.mediaDevices.getUserMedia({
          video: {
            facingMode: 'environment',
            width: { ideal: 1280 },
            height: { ideal: 720 }
          }
        })

        if (videoRef.current) {
          videoRef.current.srcObject = stream
          videoRef.current.onloadedmetadata = () => {
            videoRef.current.play()
            scanQRCode()
          }
        }
      } catch (error) {
        console.error('Failed to access camera:', error)
        setError(`Camera access denied: ${error.message}`)
        setScanning(false)
      }
    }

    const scanQRCode = () => {
      if (!videoRef.current || !canvasRef.current) {
        requestId = requestAnimationFrame(scanQRCode)
        return
      }

      const video = videoRef.current
      const canvas = canvasRef.current
      const ctx = canvas.getContext('2d')

      if (video.videoWidth && video.videoHeight) {
        canvas.width = video.videoWidth
        canvas.height = video.videoHeight

        ctx.drawImage(video, 0, 0, canvas.width, canvas.height)

        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)
        const qrCode = jsQR(imageData.data, imageData.width, imageData.height, {
          inversionAttempts: 'dontInvert'
        })

        if (qrCode) {
          setResult(qrCode.data)
          setScanning(false)
        }
      }

      if (scanning) {
        requestId = requestAnimationFrame(scanQRCode)
      }
    }

    if (scanning) {
      startScanning()
    }

    return () => {
      if (requestId) cancelAnimationFrame(requestId)
      if (stream) stream.getTracks().forEach(track => track.stop())
    }
  }, [scanning])

  const handleRescan = () => {
    setResult(null)
    setError(null)
    setScanning(true)
  }

  const handleQRLookup = async (qrCode) => {
    setLoading(true)
    setError(null)

    try {
      const response = await APIService.scanQRCode(qrCode)

      if (response.success && response.data?.item) {
        const itemId = response.data.item.id
        onNavigate('item-detail', { itemId })
      } else {
        setError(response.data?.error || 'No item found for this QR code.')
        setResult(null)
        setScanning(true)
      }
    } catch (err) {
      setError(`Error fetching item: ${err.message}`)
      setResult(null)
      setScanning(true)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <PageHeader
        title="📷 QR Code Scanner"
        subtitle="Scan item QR codes to view details"
      />

      <canvas ref={canvasRef} style={{ display: 'none' }} />

      {error && (
        <Alert type="error" title="Error" message={error} />
      )}

      <div className="max-w-2xl mx-auto">
        {scanning && (
          <Card className="p-0 overflow-hidden">
            <div className="relative bg-black aspect-video sm:aspect-auto sm:h-96 lg:h-[500px]">
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className="w-full h-full object-cover"
              />
              <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                <div className="w-56 h-56 sm:w-64 sm:h-64 border-2 border-primary-400 rounded-lg opacity-70">
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="text-center">
                      <div className="text-white text-lg sm:text-xl font-bold mb-2">Scanning...</div>
                      <div className="text-white text-xs sm:text-sm opacity-80">Point at QR code</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div className="p-4 sm:p-6 bg-white border-t text-center">
              <p className="text-gray-600 text-xs sm:text-sm mb-4">
                Position QR code within the frame
              </p>
              <Button variant="secondary" onClick={() => setScanning(false)}>
                Cancel
              </Button>
            </div>
          </Card>
        )}

        {result && !scanning && (
          <Card className="space-y-6">
            <div className="text-center">
              <div className="text-5xl mb-4">📱</div>
              <h3 className="text-xl sm:text-2xl font-bold text-gray-900 mb-2">QR Code Detected!</h3>
              <div className="bg-gray-100 p-4 rounded-lg break-all">
                <p className="text-gray-700 font-mono text-xs sm:text-sm">{result}</p>
              </div>
            </div>

            <div className="space-y-3">
              <Button
                variant="primary"
                onClick={() => handleQRLookup(result)}
                disabled={loading}
                className="w-full"
              >
                {loading ? '⏳ Loading...' : '🔍 Fetch Item'}
              </Button>

              <Button
                variant="secondary"
                onClick={handleRescan}
                className="w-full"
              >
                ↻ Scan Another
              </Button>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 sm:p-4">
              <p className="text-xs sm:text-sm text-blue-900">
                <strong>Tip:</strong> Make sure QR codes are generated from the Items page for best results.
              </p>
            </div>
          </Card>
        )}

        {!scanning && !result && !error && (
          <Card className="text-center py-12">
            <div className="text-5xl mb-4">🚫</div>
            <h3 className="text-lg font-bold text-gray-900 mb-2">Camera Access Denied</h3>
            <p className="text-gray-600 mb-6">
              Enable camera permissions in your browser settings to use the QR scanner
            </p>
            <Button variant="primary" onClick={handleRescan}>
              Try Again
            </Button>
          </Card>
        )}
      </div>
    </div>
  )
}
