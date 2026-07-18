import { Link, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { Search, Heart, Layers, Image, Palette, Menu, X, LayoutDashboard } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

export default function Navbar() {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleSearch = (e) => {
    e.preventDefault();
    if (query.trim()) {
      navigate(`/?q=${encodeURIComponent(query.trim())}`);
      setMobileOpen(false);
    }
  };

  const links = [
    { to: '/', label: 'Browse', icon: Layers },
    { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/categories', label: 'Categories', icon: Palette },
    { to: '/extractor', label: 'Extractor', icon: Image },
    { to: '/favorites', label: 'Favorites', icon: Heart },
  ];

  return (
    <header className="sticky top-0 z-50 border-b border-border bg-background/80 backdrop-blur-md">
      <div className="mx-auto flex h-14 max-w-7xl items-center gap-4 px-4">
        <Link to="/" className="flex items-center gap-2 shrink-0">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-gradient-to-br from-violet-500 to-pink-500">
            <Palette className="h-4 w-4 text-white" />
          </div>
          <span className="font-heading text-lg font-bold">Hexatom</span>
        </Link>

        <form onSubmit={handleSearch} className="relative hidden flex-1 max-w-md sm:block">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search palettes, colors, moods..."
            className="pl-9"
          />
        </form>

        <nav className="hidden md:flex items-center gap-1 ml-auto">
          {links.map((link) => (
            <Link
              key={link.to}
              to={link.to}
              className="flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
            >
              <link.icon className="h-4 w-4" />
              {link.label}
            </Link>
          ))}
        </nav>

        <button
          onClick={() => setMobileOpen(!mobileOpen)}
          className="md:hidden ml-auto p-2"
        >
          {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </div>

      {mobileOpen && (
        <div className="md:hidden border-t border-border bg-background px-4 py-3 space-y-2">
          <form onSubmit={handleSearch} className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search palettes..."
              className="pl-9"
            />
          </form>
          {links.map((link) => (
            <Link
              key={link.to}
              to={link.to}
              onClick={() => setMobileOpen(false)}
              className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium hover:bg-accent"
            >
              <link.icon className="h-4 w-4" />
              {link.label}
            </Link>
          ))}
        </div>
      )}
    </header>
  );
}