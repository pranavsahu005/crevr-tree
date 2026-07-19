import { Github, Linkedin, Mail } from 'lucide-react';

interface FooterProps {
  onNavigate: (page: string) => void;
  onOpenCategory: (cat: string) => void;
}

export default function Footer({ onNavigate, onOpenCategory }: FooterProps) {
  return (
    <footer className="relative bg-gradient-to-b from-warm-white to-[#F5F2ED] border-t border-border-soft py-16 mt-16 overflow-hidden" id="platform-footer">
      {/* Decorative leaf backgrounds from design system assets */}
      <div className="absolute right-12 bottom-6 w-20 h-20 bg-[#43C97E]/5 rounded-tl-full rounded-br-full pointer-events-none transform rotate-45 border border-[#43C97E]/10" />
      <div className="absolute left-8 top-6 w-10 h-10 bg-[#43C97E]/8 rounded-tl-full rounded-br-full pointer-events-none transform -rotate-12 border border-[#43C97E]/10" />

      {/* Decorative tech graphic from user assets folder */}
      <img 
        src="/project_imgs_to_we_use/tech/tech-footer.webp" 
        alt="Ecosystem Art" 
        className="absolute right-0 bottom-0 h-48 w-auto object-contain opacity-[0.06] pointer-events-none mix-blend-multiply"
      />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 grid grid-cols-1 md:grid-cols-4 gap-8 relative z-10">
        {/* Brand Info */}
        <div className="space-y-4">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-honey-amber rounded-full flex items-center justify-center shadow-[1.5px_1.5px_0px_0px_#2D2D2D] border-2 border-[#2D2D2D]">
              <svg className="w-4 h-4 text-earth-brown" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 3v18M12 9c2-2 4-2 6 0M12 14c-2-2-4-2-6 0M12 9c-2-1-4-1-6 0M12 14c2-1 4-1 6 0"></path>
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
                className="text-soft-brown hover:text-honey-amber-dark cursor-pointer text-left transition-colors"
              >
                Platform Home
              </button>
            </li>
            <li>
              <button 
                onClick={() => onOpenCategory('career')} 
                className="text-soft-brown hover:text-honey-amber-dark cursor-pointer text-left transition-colors"
              >
                Career Paths
              </button>
            </li>
            <li>
              <button 
                onClick={() => onOpenCategory('government')} 
                className="text-soft-brown hover:text-honey-amber-dark cursor-pointer text-left transition-colors"
              >
                Government Directory
              </button>
            </li>
            <li>
              <button 
                onClick={() => onOpenCategory('business')} 
                className="text-soft-brown hover:text-honey-amber-dark cursor-pointer text-left transition-colors"
              >
                Startup & MSME
              </button>
            </li>
          </ul>
        </div>

        {/* Links 2 */}
        <div className="space-y-3">
          <h5 className="text-xs font-bold text-earth-brown uppercase tracking-widest font-display">Ecosystem Tools</h5>
          <ul className="space-y-2 text-xs font-semibold text-soft-brown">
            <li>
              <a 
                href="https://nearbyhiring.com/ai-mock-interview"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-honey-amber-dark transition-colors"
              >
                AI Mock Interview
              </a>
            </li>
            <li>
              <a 
                href="https://nearbyhiring.com/ai-resume-builder"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-honey-amber-dark transition-colors"
              >
                AI Resume Builder
              </a>
            </li>
            <li>
              <a 
                href="https://nearbyhiring.com/career-flow"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-honey-amber-dark transition-colors"
              >
                Career Flow
              </a>
            </li>
          </ul>
        </div>

        {/* Legal Details */}
        <div className="space-y-3 text-xs font-sans">
          <h5 className="text-xs font-bold text-earth-brown uppercase tracking-widest font-display">Transparency</h5>
          <p className="text-[11px] text-soft-brown leading-relaxed">
            CrevrTree is a self-funded open educational repository. No cookie tracking, no profiling. Made with ❤️ in Madhya Pradesh, India.
          </p>
          <div className="flex space-x-3 text-soft-brown pt-1">
            <a href="https://github.com" target="_blank" rel="noreferrer" className="hover:text-honey-amber-dark transition-colors">
              <Github className="w-4 h-4" />
            </a>
            <a href="https://linkedin.com" target="_blank" rel="noreferrer" className="hover:text-honey-amber-dark transition-colors">
              <Linkedin className="w-4 h-4" />
            </a>
            <a href="mailto:support@crevrtree.com" className="hover:text-honey-amber-dark transition-colors">
              <Mail className="w-4 h-4" />
            </a>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 border-t border-border-soft/60 mt-8 pt-8 text-center text-[10px] text-soft-brown uppercase tracking-wider font-sans">
        © 2026 CrevrTree Ecosystem. All pathways are verified open-source schemas.
      </div>
    </footer>
  );
}
