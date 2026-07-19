import { Github, Linkedin, Mail } from 'lucide-react';

interface FooterProps {
  onNavigate: (page: string) => void;
  onOpenCategory: (cat: string) => void;
}

export default function Footer({ onNavigate, onOpenCategory }: FooterProps) {
  return (
    <footer className="bg-warm-white border-t border-border-soft py-12 mt-12" id="platform-footer">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 grid grid-cols-1 md:grid-cols-4 gap-8">
        {/* Brand Info */}
        <div className="space-y-4">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-honey-amber rounded-full flex items-center justify-center">
              <svg className="w-4 h-4 text-earth-brown" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 3v18M12 9c2-2 4-2 6 0M12 14c-2-2-4-2-6 0"></path>
              </svg>
            </div>
            <span className="text-xl font-bold text-earth-brown font-display">CrevrTree</span>
          </div>
          <p className="text-xs text-soft-brown leading-relaxed font-sans">
            Organizing educational and vocational streams as clear downward-growing tree roadmaps. Build standard, trusted milestones for India.
          </p>
        </div>

        {/* Links 1 */}
        <div className="space-y-3">
          <h5 className="text-xs font-bold text-earth-brown uppercase tracking-widest font-display">Platform Portals</h5>
          <ul className="space-y-1.5 text-xs font-semibold">
            <li>
              <button 
                onClick={() => onNavigate('home')} 
                className="text-soft-brown hover:text-honey-amber-dark cursor-pointer text-left"
              >
                Platform Home
              </button>
            </li>
            <li>
              <button 
                onClick={() => onOpenCategory('career')} 
                className="text-soft-brown hover:text-honey-amber-dark cursor-pointer text-left"
              >
                Career Paths
              </button>
            </li>
            <li>
              <button 
                onClick={() => onOpenCategory('government')} 
                className="text-soft-brown hover:text-honey-amber-dark cursor-pointer text-left"
              >
                Government Directory
              </button>
            </li>
            <li>
              <button 
                onClick={() => onOpenCategory('business')} 
                className="text-soft-brown hover:text-honey-amber-dark cursor-pointer text-left"
              >
                Startup & MSME
              </button>
            </li>
          </ul>
        </div>

        {/* Links 2 */}
        <div className="space-y-3">
          <h5 className="text-xs font-bold text-earth-brown uppercase tracking-widest font-display">Ecosystem Partners</h5>
          <ul className="space-y-1.5 text-xs font-sans text-soft-brown">
            <li><span className="hover:text-honey-amber-dark cursor-default">HexAtom Agency</span></li>
            <li><span className="hover:text-honey-amber-dark cursor-default">Aronar AI Systems</span></li>
            <li><span className="hover:text-honey-amber-dark cursor-default">Wear Tome Fashion</span></li>
            <li><span className="hover:text-honey-amber-dark cursor-default">Clever Tool SaaS</span></li>
          </ul>
        </div>

        {/* Legal Details */}
        <div className="space-y-3 text-xs font-sans">
          <h5 className="text-xs font-bold text-earth-brown uppercase tracking-widest font-display">Transparency</h5>
          <p className="text-[11px] text-soft-brown leading-relaxed">
            CrevrTree is a self-funded open educational repository. No cookie tracking, no profiling. Made with ❤️ in Madhya Pradesh, India.
          </p>
          <div className="flex space-x-3 text-soft-brown pt-1">
            <a href="https://github.com" target="_blank" rel="noreferrer" className="hover:text-honey-amber-dark">
              <Github className="w-4 h-4" />
            </a>
            <a href="https://linkedin.com" target="_blank" rel="noreferrer" className="hover:text-honey-amber-dark">
              <Linkedin className="w-4 h-4" />
            </a>
            <a href="mailto:support@crevrtree.com" className="hover:text-honey-amber-dark">
              <Mail className="w-4 h-4" />
            </a>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 border-t border-border-soft mt-8 pt-8 text-center text-[10px] text-soft-brown uppercase tracking-wider font-sans">
        © 2026 CrevrTree Ecosystem. All pathways are verified open-source schemas.
      </div>
    </footer>
  );
}
