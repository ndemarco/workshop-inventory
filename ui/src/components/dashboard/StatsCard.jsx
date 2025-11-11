import { Card } from '../UI'

export default function StatsCard({ title, value, loading, colorClass, onClick, linkText }) {
  return (
    <Card className="bg-white">
      <div className="text-gray-600 text-sm font-medium mb-2">{title}</div>
      <div className={`text-3xl font-bold ${colorClass}`}>
        {loading ? '...' : value}
      </div>
      {onClick && linkText && (
        <button
          onClick={onClick}
          className={`${colorClass} text-sm font-medium mt-4 hover:underline`}
        >
          {linkText}
        </button>
      )}
    </Card>
  )
}