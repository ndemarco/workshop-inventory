import { useState } from 'react'

export default function Navbar({ onNavigate }) {
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  const handleNavClick = (page) => {
    onNavigate(page)
    setIsMenuOpen(false)
  }

  const navItems = [
    { label: 'Dashboard', page: 'dashboard' },
    { label: 'Items', page: 'items' },
    { label: 'Modules', page: 'modules' },
    { label: 'Locations', page: 'locations' },
    { label: 'Search', page: 'search' },
    { label: 'API Docs', page: 'docs' },
    { label: '📷 QR Scanner', page: 'qr-scanner' },
  ]

  return (
    <nav className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-40">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <button
            onClick={() => handleNavClick('dashboard')}
            className="text-lg sm:text-2xl font-bold text-primary-600 hover:text-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 rounded whitespace-nowrap"
          >
            🏠 <span className="hidden sm:inline">Inventory System</span>
          </button>

          {/* Desktop Navigation */}
          <div className="hidden md:flex gap-6 flex-1 justify-end">
            {navItems.map(item => (
              <button
                key={item.page}
                onClick={() => handleNavClick(item.page)}
                className="text-gray-600 hover:text-primary-600 focus:outline-none focus:text-primary-700 font-medium text-sm lg:text-base whitespace-nowrap transition-colors"
              >
                {item.label}
              </button>
            ))}
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            className="md:hidden flex flex-col gap-1.5 p-2 hover:bg-gray-100 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500"
            title={isMenuOpen ? 'Close menu' : 'Open menu'}
          >
            <span className={`block w-6 h-0.5 bg-gray-600 transition-all ${isMenuOpen ? 'rotate-45 translate-y-2' : ''}`}></span>
            <span className={`block w-6 h-0.5 bg-gray-600 transition-all ${isMenuOpen ? 'opacity-0' : ''}`}></span>
            <span className={`block w-6 h-0.5 bg-gray-600 transition-all ${isMenuOpen ? '-rotate-45 -translate-y-2' : ''}`}></span>
          </button>
        </div>

        {/* Mobile Navigation Menu with smooth transition */}
        <div
          className={`md:hidden overflow-hidden transition-[max-height] duration-300 ease-in-out mt-4 border-t border-gray-200`}
          style={{ maxHeight: isMenuOpen ? '500px' : '0px' }}
        >
          <div className="pt-4 pb-2 space-y-2">
            {navItems.map(item => (
              <button
                key={item.page}
                onClick={() => handleNavClick(item.page)}
                className="block w-full text-left px-4 py-2 text-gray-600 hover:text-primary-600 hover:bg-primary-50 font-medium rounded-lg transition-colors focus:outline-none focus:bg-primary-100"
              >
                {item.label}
              </button>
            ))}
          </div>
        </div>
      </div>
    </nav>
  )
}
