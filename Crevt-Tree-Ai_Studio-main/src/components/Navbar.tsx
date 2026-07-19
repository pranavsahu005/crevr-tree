import React, { useState } from 'react';
import { Search, Menu, X, BookOpen } from 'lucide-react';

interface NavbarProps {
  onNavigate: (page: string) => void;
  onSearch: (query: string) => void;
  onOpenCategory: (cat: string) => void;
}

export default function Navbar({ onNavigate, onSearch, onOpenCategory }: NavbarProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [searchVal, setSearchVal] = useState('');

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      onSearch(searchVal.trim());
      setMobileMenuOpen(false);
    }
  };

  return (
    <nav className="sticky top-0 z-40 bg-warm-white/95 backdrop-blur-md border-b border-border-soft px-4 sm:px-6 lg:px-8 py-4">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Brand Logo */}
        <div 
          onClick={() => onNavigate('home')} 
          className="flex items-center space-x-3 cursor-pointer"
          id="nav-logo"
        >
          <img 
            src="/main_logo_no_bg.webp" 
            alt="CrevrTree Logo" 
            className="w-10 h-10 object-contain hover:scale-105 transition-transform"
          />
          <div>
            <span className="text-2xl font-extrabold tracking-tight text-earth-brown font-display leading-none block">
              Crevr<span className="text-honey-amber-dark">Tree</span>
            </span>
            <span className="text-[9px] font-bold text-soft-brown uppercase tracking-widest block -mt-1">
              India Career Intelligence
            </span>
          </div>
        </div>

        {/* Central Nav Links (Desktop) */}
        <div className="hidden md:flex items-center space-x-1 font-semibold text-sm">
          <button 
            onClick={() => onNavigate('home')} 
            className="px-4 py-2 rounded-full text-earth-brown hover:bg-cream/50 transition-all cursor-pointer"
            id="nav-btn-home"
          >
            Home
          </button>
          <button 
            onClick={() => onOpenCategory('career')} 
            className="px-4 py-2 rounded-full text-earth-brown hover:bg-cream/50 transition-all cursor-pointer"
            id="nav-btn-career"
          >
            Career Paths
          </button>
          <button 
            onClick={() => onOpenCategory('government')} 
            className="px-4 py-2 rounded-full text-earth-brown hover:bg-cream/50 transition-all cursor-pointer"
            id="nav-btn-govt"
          >
            Government Exams
          </button>
          <button 
            onClick={() => onOpenCategory('business')} 
            className="px-4 py-2 rounded-full text-earth-brown hover:bg-cream/50 transition-all cursor-pointer"
            id="nav-btn-business"
          >
            Business & Startup
          </button>
          <button 
            onClick={() => onNavigate('about')} 
            className="px-4 py-2 rounded-full text-earth-brown hover:bg-cream/50 transition-all cursor-pointer"
            id="nav-btn-about"
          >
            Platform Vision
          </button>
        </div>

        {/* Right side interactive search utility */}
        <div className="flex items-center space-x-3">
          <div className="relative hidden sm:block">
            <input 
              id="nav-search-input"
              type="text" 
              placeholder="Search career or exam..." 
              value={searchVal}
              onChange={(e) => setSearchVal(e.target.value)}
              onKeyDown={handleKeyDown}
              className="w-48 md:w-56 px-4 py-2 pl-9 bg-cream/60 border border-border-soft rounded-full text-xs text-earth-brown placeholder-soft-brown focus:ring-2 focus:ring-honey-amber focus:outline-none transition-all"
            />
            <Search className="w-3.5 h-3.5 text-soft-brown absolute left-3 top-2.5" />
          </div>
          <button 
            onClick={() => onNavigate('about')} 
            className="px-4 py-2 rounded-full border-2 border-honey-amber hover:bg-honey-amber/10 text-earth-brown text-xs font-bold transition-all shadow-sm cursor-pointer"
            id="nav-btn-why"
          >
            Why CrevrTree?
          </button>
          <button 
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)} 
            className="md:hidden p-2 text-earth-brown hover:bg-cream/50 rounded-full transition-all cursor-pointer"
            id="mobile-menu-toggle"
          >
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Nav Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden mt-4 border-t border-border-soft pt-4 space-y-2" id="mobile-nav-drawer">
          <button 
            onClick={() => { onNavigate('home'); setMobileMenuOpen(false); }} 
            className="block w-full text-left px-4 py-2.5 rounded-xl text-earth-brown font-bold hover:bg-cream/50 cursor-pointer"
            id="mobile-nav-home"
          >
            Home
          </button>
          <button 
            onClick={() => { onOpenCategory('career'); setMobileMenuOpen(false); }} 
            className="block w-full text-left px-4 py-2.5 rounded-xl text-earth-brown font-bold hover:bg-cream/50 cursor-pointer"
            id="mobile-nav-career"
          >
            Career Paths
          </button>
          <button 
            onClick={() => { onOpenCategory('government'); setMobileMenuOpen(false); }} 
            className="block w-full text-left px-4 py-2.5 rounded-xl text-earth-brown font-bold hover:bg-cream/50 cursor-pointer"
            id="mobile-nav-govt"
          >
            Government Exams
          </button>
          <button 
            onClick={() => { onOpenCategory('business'); setMobileMenuOpen(false); }} 
            className="block w-full text-left px-4 py-2.5 rounded-xl text-earth-brown font-bold hover:bg-cream/50 cursor-pointer"
            id="mobile-nav-business"
          >
            Business & Startup
          </button>
          <button 
            onClick={() => { onNavigate('about'); setMobileMenuOpen(false); }} 
            className="block w-full text-left px-4 py-2.5 rounded-xl text-earth-brown font-bold hover:bg-cream/50 cursor-pointer"
            id="mobile-nav-about"
          >
            Platform Vision
          </button>
          <div className="px-4 py-2">
            <div className="relative">
              <input 
                id="mobile-search-input"
                type="text" 
                placeholder="Search career or exam..." 
                value={searchVal}
                onChange={(e) => setSearchVal(e.target.value)}
                onKeyDown={handleKeyDown}
                className="w-full px-4 py-3 pl-9 bg-cream border border-border-soft rounded-full text-xs text-earth-brown focus:ring-2 focus:ring-honey-amber focus:outline-none"
              />
              <Search className="w-4 h-4 text-soft-brown absolute left-3 top-3.5" />
            </div>
          </div>
        </div>
      )}
    </nav>
  );
}
