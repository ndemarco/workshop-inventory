import { useState, useEffect } from 'react'
import Navbar from './components/Navbar'
import Dashboard from './pages/Dashboard'
import Items from './pages/Items'
import ItemDetail from './pages/ItemDetail'
import ItemForm from './pages/ItemForm'
import Modules from './pages/Modules'
import Levels from './pages/Levels'
import Locations from './pages/Locations'
import Search from './pages/Search'
import QRScanner from './pages/QRScanner'
import Docs from './pages/Docs'
import './index.css'

export default function App() {
  const [currentPage, setCurrentPage] = useState('dashboard')
  const [selectedItemId, setSelectedItemId] = useState(null)
  const [selectedModuleId, setSelectedModuleId] = useState(null)

  const navigateTo = (page, data = null) => {
    setCurrentPage(page)
    if (data?.itemId) setSelectedItemId(data.itemId)
    if (data?.moduleId) setSelectedModuleId(data.moduleId)
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-24 sm:pb-32">
      <Navbar onNavigate={navigateTo} />
      
      <main className="container mx-auto px-3 sm:px-4 py-6 sm:py-8">
        {currentPage === 'dashboard' && <Dashboard onNavigate={navigateTo} />}
        {currentPage === 'items' && <Items onNavigate={navigateTo} />}
        {currentPage === 'item-detail' && <ItemDetail itemId={selectedItemId} onNavigate={navigateTo} />}
        {currentPage === 'item-form' && <ItemForm itemId={selectedItemId} onNavigate={navigateTo} />}
        {currentPage === 'modules' && <Modules onNavigate={navigateTo} />}
        {currentPage === 'levels' && <Levels moduleId={selectedModuleId} onNavigate={navigateTo} />}
        {currentPage === 'locations' && <Locations onNavigate={navigateTo} />}
        {currentPage === 'search' && <Search onNavigate={navigateTo} />}
        {currentPage === 'qr-scanner' && <QRScanner onNavigate={navigateTo} />}
        {currentPage === 'docs' && <Docs onNavigate={navigateTo} />}
      </main>

      <footer className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 py-3 sm:py-4 text-center text-xs sm:text-sm text-gray-500">
        <p>&copy; 2025 Inventory System | v3.0.0</p>
      </footer>
    </div>
  )
}
