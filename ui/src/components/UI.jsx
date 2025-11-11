import clsx from 'clsx'

export function Button({ children, variant = 'primary', size = 'md', disabled = false, className = '', ...props }) {
  const baseClasses = 'font-medium rounded-lg transition-all duration-200 inline-flex items-center gap-2 justify-center touch-manipulation'
  
  const variants = {
    primary: 'bg-primary-600 text-white hover:bg-primary-700 hover:shadow-md active:scale-95 disabled:bg-gray-400 disabled:cursor-not-allowed disabled:scale-100',
    secondary: 'bg-gray-600 text-white hover:bg-gray-700 hover:shadow-md active:scale-95 disabled:bg-gray-400 disabled:cursor-not-allowed disabled:scale-100',
    danger: 'bg-danger-600 text-white hover:bg-danger-700 hover:shadow-md active:scale-95 disabled:bg-gray-400 disabled:cursor-not-allowed disabled:scale-100',
    warning: 'bg-warning-600 text-white hover:bg-warning-700 hover:shadow-md active:scale-95 disabled:bg-gray-400 disabled:cursor-not-allowed disabled:scale-100',
    success: 'bg-success-600 text-white hover:bg-success-700 hover:shadow-md active:scale-95 disabled:bg-gray-400 disabled:cursor-not-allowed disabled:scale-100',
    outline: 'border-2 border-primary-600 text-primary-600 hover:bg-primary-100 hover:shadow-md active:scale-95 disabled:border-gray-400 disabled:text-gray-400 disabled:cursor-not-allowed disabled:scale-100',
    ghost: 'text-gray-700 hover:bg-gray-100 hover:shadow-md active:scale-95 disabled:text-gray-400 disabled:cursor-not-allowed disabled:scale-100',
  }

  const sizes = {
    sm: 'px-2 sm:px-3 py-1 sm:py-1.5 text-xs sm:text-sm min-h-[32px] sm:min-h-[36px]',
    md: 'px-4 py-2 text-base min-h-[44px]',
    lg: 'px-6 py-3 text-lg min-h-[48px]',
  }

  return (
    <button
      className={clsx(baseClasses, variants[variant], sizes[size], className)}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  )
}

export function Card({ children, className = '', ...props }) {
  return (
    <div className={clsx('bg-white border border-gray-200 rounded-lg p-4 sm:p-6 shadow-soft', className)} {...props}>
      {children}
    </div>
  )
}

export function Badge({ children, variant = 'gray', ...props }) {
  const variants = {
    gray: 'bg-gray-100 text-gray-800',
    success: 'bg-success-50 text-success-600',
    danger: 'bg-danger-50 text-danger-600',
    warning: 'bg-warning-50 text-warning-600',
    primary: 'bg-primary-50 text-primary-600',
  }

  return (
    <span className={clsx('inline-block px-3 py-1 rounded-full text-sm font-medium', variants[variant])} {...props}>
      {children}
    </span>
  )
}

export function Modal({ isOpen, onClose, title, children, size = 'md' }) {
  if (!isOpen) return null

  const sizes = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-2xl',
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className={clsx('bg-white rounded-lg shadow-lg w-full', sizes[size])}>
        <div className="flex items-center justify-between px-4 sm:px-6 py-3 sm:py-4 border-b">
          <h2 className="text-lg sm:text-xl font-bold break-words">{title}</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl font-light flex-shrink-0 ml-4"
          >
            ×
          </button>
        </div>
        <div className="px-4 sm:px-6 py-3 sm:py-4 max-h-[60vh] overflow-y-auto">
          {children}
        </div>
      </div>
    </div>
  )
}

export function FormGroup({ label, error, required, children }) {
  return (
    <div className="mb-4 sm:mb-6">
      {label && (
        <label className="block text-xs sm:text-sm font-medium text-gray-700 mb-2">
          {label}
          {required && <span className="text-danger-600">*</span>}
        </label>
      )}
      {children}
      {error && <p className="text-danger-600 text-xs sm:text-sm mt-1">{error}</p>}
    </div>
  )
}

export function Input({ label, error, required, ...props }) {
  return (
    <FormGroup label={label} error={error} required={required}>
      <input
        className={clsx(
          'w-full px-3 sm:px-4 py-2 sm:py-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent text-sm min-h-[44px]',
          error ? 'border-danger-600' : 'border-gray-300'
        )}
        {...props}
      />
    </FormGroup>
  )
}

export function Textarea({ label, error, required, ...props }) {
  return (
    <FormGroup label={label} error={error} required={required}>
      <textarea
        className={clsx(
          'w-full px-3 sm:px-4 py-2 sm:py-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent text-sm min-h-[120px]',
          error ? 'border-danger-600' : 'border-gray-300'
        )}
        {...props}
      />
    </FormGroup>
  )
}

export function Select({ label, error, required, options, ...props }) {
  return (
    <FormGroup label={label} error={error} required={required}>
      <select
        className={clsx(
          'w-full px-3 sm:px-4 py-2 sm:py-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent text-sm min-h-[44px]',
          error ? 'border-danger-600' : 'border-gray-300'
        )}
        {...props}
      >
        <option value="">Select {label?.toLowerCase() || 'an option'}...</option>
        {options?.map(opt => (
          <option key={opt.value} value={opt.value}>{opt.label}</option>
        ))}
      </select>
    </FormGroup>
  )
}

export function Table({ columns, data, loading = false, onRowClick }) {
  return (
    <div className="overflow-x-auto -mx-4 sm:mx-0 sm:rounded-lg">
      <table className="w-full">
        <thead className="bg-gray-50 border-b sticky top-0">
          <tr>
            {columns.map(col => (
              <th key={col.key} className="px-3 sm:px-6 py-2 sm:py-3 text-left text-xs sm:text-sm font-semibold text-gray-900 whitespace-nowrap">
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y">
          {loading ? (
            <tr>
              <td colSpan={columns.length} className="px-3 sm:px-6 py-3 sm:py-4 text-center text-gray-600 text-sm">
                Loading...
              </td>
            </tr>
          ) : data.length === 0 ? (
            <tr>
              <td colSpan={columns.length} className="px-3 sm:px-6 py-3 sm:py-4 text-center text-gray-600 text-sm">
                No data found
              </td>
            </tr>
          ) : (
            data.map((row, idx) => (
              <tr
                key={idx}
                onClick={() => onRowClick?.(row)}
                className={clsx('hover:bg-gray-50 transition-colors', onRowClick && 'cursor-pointer active:bg-gray-100')}
              >
                {columns.map(col => (
                  <td key={col.key} className="px-3 sm:px-6 py-3 sm:py-4 text-gray-600 text-xs sm:text-sm">
                    {col.render ? col.render(row) : row[col.key]}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  )
}

export function PageHeader({ title, subtitle, action }) {
  return (
    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6 sm:mb-8 gap-4">
      <div className="min-w-0">
        <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">{title}</h1>
        {subtitle && <p className="text-xs sm:text-sm text-gray-600 mt-1 truncate">{subtitle}</p>}
      </div>
      {action && <div className="sm:ml-auto">{action}</div>}
    </div>
  )
}

export function EmptyState({ icon = '📭', title, description, action }) {
  return (
    <Card className="text-center py-8 sm:py-12">
      <div className="text-4xl sm:text-5xl mb-3 sm:mb-4">{icon}</div>
      <h3 className="text-lg sm:text-xl font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-xs sm:text-sm text-gray-600 mb-4 sm:mb-6">{description}</p>
      {action && <div>{action}</div>}
    </Card>
  )
}

export function Alert({ variant = 'info', title, message, onClose }) {
  const variants = {
    success: 'bg-success-50 text-success-600 border-success-200',
    error: 'bg-danger-50 text-danger-600 border-danger-200',
    warning: 'bg-warning-50 text-warning-600 border-warning-200',
    info: 'bg-primary-50 text-primary-600 border-primary-200',
  }

  return (
    <div className={clsx('border rounded-lg p-3 sm:p-4 flex items-start justify-between gap-3', variants[variant])}>
      <div className="min-w-0">
        {title && <h4 className="font-semibold text-sm sm:text-base">{title}</h4>}
        {message && <p className="text-xs sm:text-sm mt-1">{message}</p>}
      </div>
      {onClose && (
        <button onClick={onClose} className="ml-2 font-bold text-lg flex-shrink-0 hover:opacity-70">
          ×
        </button>
      )}
    </div>
  )
}
