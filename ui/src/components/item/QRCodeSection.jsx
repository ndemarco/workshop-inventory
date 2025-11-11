import React from 'react'
import { QRCodeSVG } from 'qrcode.react'
import { Card, Button } from '../UI'
import APIService from '../../services/api'

export default function QRCodeSection({
  item,
  mode = 'view', // 'view' or 'edit'
  regeneratingQR = false,
  onDownloadQR,
  onRegenerateQR
}) {
  if (!item?.qr_code) return null

  if (mode === 'view') {
    return (
      <Card>
        <h3 className="font-semibold mb-4">QR Code</h3>
        <div className="flex flex-col items-center">
          <div className="bg-white p-4 rounded-lg border-2 border-gray-200 mb-4">
            <QRCodeSVG value={`/item/${item.id}`} size={256} level="H" includeMargin={true}/>
          </div>
          <p className="text-xs text-gray-600 mb-4 text-center">
            <span className="font-mono bg-gray-100 px-2 py-1 rounded block mb-2">{item.qr_code}</span>
            Scan to view this item
          </p>
        </div>
        <Button variant="success" size="sm" onClick={onDownloadQR} className="w-full">
          ⬇️ Download QR Code
        </Button>
      </Card>
    )
  }

  // Edit mode
  return (
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 sm:p-6">
      <h3 className="text-sm sm:text-base font-bold text-gray-900 mb-3">QR Code Management</h3>
      <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 sm:gap-4 mb-4">
        <div className="text-xs sm:text-sm text-gray-700">
          QR Code: <span className="font-mono font-bold text-blue-600">{item.qr_code}</span>
        </div>
      </div>
      <div className="flex flex-col sm:flex-row gap-2">
        <Button
          type="button"
          variant="success"
          size="sm"
          onClick={onDownloadQR}
          className="flex-1"
        >
          ⬇️ Download QR Code
        </Button>
        <Button
          type="button"
          variant="warning"
          size="sm"
          onClick={onRegenerateQR}
          disabled={regeneratingQR}
          className="flex-1"
        >
          {regeneratingQR ? '⏳ Regenerating...' : '🔄 Regenerate QR Code'}
        </Button>
      </div>
    </div>
  )
}