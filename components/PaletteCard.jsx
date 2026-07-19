import { Link } from 'react-router-dom';
import { useState } from 'react';
import { Heart, Copy, Eye } from 'lucide-react';
import { getContrastColor, copyToClipboard } from '@/lib/colorUtils';
import { useToast } from '@/components/ui/use-toast';
import { base44 } from '@/api/base44Client';

export default function PaletteCard({ palette }) {
  const { toast } = useToast();
  const [favorited, setFavorited] = useState(false);
  const [favCount, setFavCount] = useState(palette.favorite_count || 0);

  const handleCopy = async (e, hex) => {
    e.preventDefault();
    e.stopPropagation();
    await copyToClipboard(hex);
    toast({ description: `Copied ${hex}` });
    try {
      await base44.entities.Palette.update(palette.id, { copy_count: (palette.copy_count || 0) + 1 });
    } catch { /* non-critical */ }
  };

  const handleFavorite = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (favorited) return;
    try {
      await base44.entities.Favorite.create({ palette_id: palette.id });
      await base44.entities.Palette.update(palette.id, { favorite_count: favCount + 1 });
      setFavorited(true);
      setFavCount(favCount + 1);
      toast({ description: 'Added to favorites' });
    } catch {
      toast({ variant: 'destructive', description: 'Sign in to save favorites' });
    }
  };

  return (
    <Link
      to={`/palette/${palette.id}`}
      className="group block overflow-hidden rounded-xl border border-border bg-card transition-all hover:shadow-lg hover:-translate-y-0.5"
    >
      <div className="flex h-28 sm:h-32">
        {palette.colors.slice(0, 5).map((color, i) => (
          <div
            key={i}
            className="relative flex-1 transition-all group-hover:flex-[1.2]"
            style={{ backgroundColor: color }}
            onClick={(e) => handleCopy(e, color)}
            role="button"
            tabIndex={0}
          >
            <span
              className="absolute bottom-1.5 left-1/2 -translate-x-1/2 opacity-0 transition-opacity group-hover:opacity-100 text-[10px] font-mono font-semibold"
              style={{ color: getContrastColor(color) }}
            >
              {color.toUpperCase()}
            </span>
          </div>
        ))}
      </div>
      <div className="flex items-center justify-between gap-2 p-3">
        <div className="min-w-0">
          <h3 className="truncate text-sm font-semibold">{palette.name}</h3>
          <div className="flex items-center gap-2 mt-0.5 text-xs text-muted-foreground">
            <span className="capitalize">{palette.color_family}</span>
            {palette.is_featured && <span className="text-amber-500">★</span>}
            {palette.is_editor_choice && <span className="text-blue-500">✦</span>}
          </div>
        </div>
        <div className="flex items-center gap-1 text-xs text-muted-foreground">
          <span className="flex items-center gap-0.5"><Eye className="h-3 w-3" />{palette.view_count || 0}</span>
          <button onClick={handleFavorite} className="flex items-center gap-0.5 hover:text-red-500 transition-colors">
            <Heart className={`h-3 w-3 ${favorited ? 'fill-red-500 text-red-500' : ''}`} />{favCount}
          </button>
        </div>
      </div>
    </Link>
  );
}