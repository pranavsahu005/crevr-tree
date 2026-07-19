import { useState, useEffect } from 'react';
import {
  Search,
  ArrowLeft,
  RotateCcw,
  ChevronDown,
  Info,
  GraduationCap,
  ShieldCheck,
  Store,
  Coins,
  HeartHandshake,
  Compass,
  Cpu,
  BookmarkCheck,
  Heart,
  X
} from 'lucide-react';

import { ROADMAPS_DATABASE } from './data';
import { Step, Roadmap } from './types';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import TreeCanvas from './components/TreeCanvas';
import InspectorPanel from './components/InspectorPanel';

export default function App() {
  const [currentPage, setCurrentPage] = useState<string>('home');
  const [selectedCategory, setSelectedCategory] = useState<string>('career');
  const [activeRoadmap, setActiveRoadmap] = useState<Roadmap | null>(null);
  const [selectedNode, setSelectedNode] = useState<Step | null>(null);
  const [roadmapsDatabase, setRoadmapsDatabase] = useState<Roadmap[]>(ROADMAPS_DATABASE);
  const [searchResults, setSearchResults] = useState<Roadmap[]>([]);

  // Load completed nodes from localStorage on startup
  const [completedNodes, setCompletedNodes] = useState<Record<string, boolean>>(() => {
    try {
      const stored = localStorage.getItem('crevrtree_completed_nodes');
      return stored ? JSON.parse(stored) : {};
    } catch {
      return {};
    }
  });

  // Fetch roadmaps list on mount
  useEffect(() => {
    const fetchRoadmaps = async () => {
      try {
        const res = await fetch('/api/roadmaps');
        if (res.ok) {
          const data = await res.json();
          if (data && data.length > 0) {
            const formatted = data.map((item: any) => ({
              id: item.id,
              name: item.name,
              category: item.category,
              tagline: item.tagline,
              steps: []
            }));
            setRoadmapsDatabase(formatted);
          }
        }
      } catch (err) {
        console.warn('[CrevrTree] Failed to fetch roadmaps index, using local static fallback.', err);
      }
    };
    fetchRoadmaps();
  }, []);

  // Global search values
  const [searchQuery, setSearchQuery] = useState('');

  // Custom toast notification states
  const [toast, setToast] = useState<{ title: string; body: string; show: boolean }>({
    title: '',
    body: '',
    show: false,
  });

  // FAQ open indexes
  const [openFaqs, setOpenFaqs] = useState<Record<number, boolean>>({
    0: false,
    1: false,
    2: false,
  });

  const [explainOpen, setExplainOpen] = useState(false);

  // Save progress changes to localStorage
  useEffect(() => {
    localStorage.setItem('crevrtree_completed_nodes', JSON.stringify(completedNodes));
  }, [completedNodes]);

  // Toast auto-hide trigger
  useEffect(() => {
    if (toast.show) {
      const timer = setTimeout(() => {
        setToast((prev) => ({ ...prev, show: false }));
      }, 4000);
      return () => clearTimeout(timer);
    }
  }, [toast.show]);

  // Utility toast dispatcher
  const triggerToast = (title: string, body: string) => {
    setToast({ title, body, show: true });
  };

  // SPA navigation routing handler
  const handleNavigate = (pageId: string) => {
    setCurrentPage(pageId);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // Dynamic category portal loader
  const handleOpenCategory = (categoryId: string) => {
    setSelectedCategory(categoryId);
    setCurrentPage('category');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // Node details inspector loader
  // Helper to map category from node properties
  const getCategoryFromNode = (node: any): 'medical' | 'education' | 'government' | 'business' | 'finance' | 'tech' => {
    const c = (node.category || '').toLowerCase();
    const t = (node.title || '').toLowerCase();
    const combined = `${c} ${t}`;
    if (combined.includes('med') || combined.includes('nurse') || combined.includes('doctor') || combined.includes('bams') || combined.includes('bds') || combined.includes('mbbs') || combined.includes('pharm')) return 'medical';
    if (combined.includes('govt') || combined.includes('police') || combined.includes('upsc') || combined.includes('civil') || combined.includes('ssc') || combined.includes('ias') || combined.includes('ips') || combined.includes('ifs') || combined.includes('psu') || combined.includes('rail')) return 'government';
    if (combined.includes('bus') || combined.includes('start') || combined.includes('entre') || combined.includes('farm') || combined.includes('shop') || combined.includes('store') || combined.includes('retail')) return 'business';
    if (combined.includes('fin') || combined.includes('audit') || combined.includes('bank') || combined.includes('tax') || combined.includes('ca ') || combined.includes('account')) return 'finance';
    if (combined.includes('tech') || combined.includes('soft') || combined.includes('ai') || combined.includes('code') || combined.includes('computer') || combined.includes('programming') || combined.includes('devops')) return 'tech';
    return 'education';
  };

  const handleLoadRoadmap = async (roadmapId: string) => {
    try {
      const cleanId = roadmapId.replace('dynamic-', '');

      // If it's a cp- ID, find it in searchResults and load its subtree by keyword
      if (cleanId.startsWith('cp-')) {
        const match = searchResults.find(r => r.id === cleanId || r.id === `dynamic-${cleanId}`);
        if (match) {
          await handleLoadCareerPathByKeyword(match.name);
          return;
        }
      }

      // 1. Try to fetch from curated roadmaps API
      let res = await fetch(`/api/roadmaps/${cleanId}`);
      if (res.ok) {
        const data = await res.json();
        if (data.steps && data.steps.length > 0) {
          setActiveRoadmap(data);
          setSelectedNode(null);
          setCurrentPage('tree');
          window.scrollTo({ top: 0, behavior: 'smooth' });
          return;
        }
      }

      // 2. Try career paths tree API (the full generated dataset)
      res = await fetch(`/api/career-paths/tree`);
      if (res.ok) {
        const data = await res.json();
        setActiveRoadmap(data);
        setSelectedNode(null);
        setCurrentPage('tree');
        window.scrollTo({ top: 0, behavior: 'smooth' });
        return;
      }

      // 3. Try dynamic graph generator API
      res = await fetch(`/api/nodes/${cleanId}/tree`);
      if (res.ok) {
        const data = await res.json();
        setActiveRoadmap(data);
        setSelectedNode(null);
        setCurrentPage('tree');
        window.scrollTo({ top: 0, behavior: 'smooth' });
        return;
      }
    } catch (err) {
      console.warn(`[CrevrTree] Failed to fetch roadmap details from API for ${roadmapId}.`, err);
    }

    // Fallback locally
    let rm = roadmapsDatabase.find((item) => item.id === roadmapId);
    if (rm && (!rm.steps || rm.steps.length === 0)) {
      const staticRm = ROADMAPS_DATABASE.find((item) => item.id === roadmapId);
      if (staticRm) {
        rm = staticRm;
      }
    }
    if (!rm || !rm.steps || rm.steps.length === 0) {
      triggerToast("Path Offline", "Could not load this career track.");
      return;
    }
    setActiveRoadmap(rm);
    setSelectedNode(null);
    setCurrentPage('tree');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // Load the full career paths tree (400K paths from career_paths.txt)
  const handleLoadFullCareerTree = async () => {
    try {
      triggerToast("Loading...", "Parsing 200,000 career paths from the knowledge graph...");
      const res = await fetch('/api/career-paths/tree?depth=5&children=5');
      if (res.ok) {
        const data = await res.json();
        setActiveRoadmap(data);
        setSelectedNode(null);
        setCurrentPage('tree');
        window.scrollTo({ top: 0, behavior: 'smooth' });
        triggerToast("Career Directory Loaded", `Showing the complete career pathway tree with ${data.steps?.length || 0} milestones.`);
        return;
      }
    } catch (err) {
      console.warn('[CrevrTree] Failed to fetch full career tree.', err);
    }
    triggerToast("Loading Failed", "Could not load the full career directory. Try again.");
  };

  // Load career path by keyword
  const handleLoadCareerPathByKeyword = async (keyword: string) => {
    try {
      const res = await fetch(`/api/career-paths/${encodeURIComponent(keyword)}/tree`);
      if (res.ok) {
        const data = await res.json();
        setActiveRoadmap(data);
        setSelectedNode(null);
        setCurrentPage('tree');
        window.scrollTo({ top: 0, behavior: 'smooth' });
        return;
      }
    } catch (err) {
      console.warn(`[CrevrTree] Failed to fetch career path for "${keyword}".`, err);
    }
    // Fallback to loading the full tree
    handleLoadFullCareerTree();
  };

  // Keyword text searches
  const handleSearch = async (query: string) => {
    if (!query) {
      triggerToast("Empty Search", "Please enter a career, business role, or exam keyword to search.");
      return;
    }

    const lowerQuery = query.toLowerCase().trim();

    try {
      // 1. Search career paths from the generated dataset (400K paths)
      const cpRes = await fetch(`/api/career-paths/search?q=${encodeURIComponent(lowerQuery)}`);
      let cpMatches: Roadmap[] = [];
      if (cpRes.ok) {
        const cpResults = await cpRes.json();
        cpMatches = cpResults.map((r: any) => ({
          id: r.id,
          name: r.name,
          category: getCategoryFromNode({ title: r.name, category: r.path?.[r.path.length - 2] || '' }) as any,
          tagline: `Path: ${r.path?.join(' → ') || r.name}`,
          steps: Array(r.path ? r.path.length : 0).fill(null).map((_, i) => ({ id: `dummy-${i}`, name: '', desc: '', parent: null, coords: { x: 0, y: 0 } }))
        }));
      }

      // 2. Search DB nodes via API
      const res = await fetch(`/api/nodes?search=${encodeURIComponent(lowerQuery)}`);
      let dbMatches: Roadmap[] = [];
      if (res.ok) {
        const nodes = await res.json();
        dbMatches = nodes.map((node: any) => ({
          id: node.node_id,
          name: node.title,
          category: getCategoryFromNode(node),
          tagline: node.description || `${node.title} pathway inside the knowledge graph.`,
          steps: Array(1).fill(null).map((_, i) => ({ id: node.node_id, name: node.title, desc: node.description || '', coords: { x: 50, y: 12 } }))
        }));
      }

      // 3. Search local curated roadmaps list
      const localMatches = roadmapsDatabase.filter((item) =>
        item.name.toLowerCase().includes(lowerQuery) ||
        item.category.toLowerCase().includes(lowerQuery) ||
        item.tagline.toLowerCase().includes(lowerQuery)
      );

      // Merge and deduplicate - prioritize career paths matches
      const allMatches = [...cpMatches, ...localMatches];
      dbMatches.forEach((dbM) => {
        if (!allMatches.some(m => m.id === dbM.id || m.name.toLowerCase() === dbM.name.toLowerCase())) {
          allMatches.push(dbM);
        }
      });

      if (allMatches.length > 0) {
        setSearchResults(allMatches);
        if (allMatches.length === 1) {
          handleLoadRoadmap(allMatches[0].id);
          triggerToast("Path Found", `Loading tree structure for: ${allMatches[0].name}`);
        } else {
          setSelectedCategory('search_results');
          setCurrentPage('category');
          triggerToast("Results Found", `Found ${allMatches.length} matching career trees.`);
        }
      } else {
        triggerToast("No Match Found", `No open career trees match: "${query}". Try 'Doctor', 'IAS', or 'AI'.`);
      }
    } catch (err) {
      console.error("Search failed:", err);
      // Fallback local search
      const localMatches = roadmapsDatabase.filter((item) =>
        item.name.toLowerCase().includes(lowerQuery) ||
        item.category.toLowerCase().includes(lowerQuery) ||
        item.tagline.toLowerCase().includes(lowerQuery)
      );
      if (localMatches.length > 0) {
        setSearchResults(localMatches);
        if (localMatches.length === 1) {
          handleLoadRoadmap(localMatches[0].id);
        } else {
          setSelectedCategory('search_results');
          setCurrentPage('category');
        }
      } else {
        triggerToast("No Match Found", `No career trees match: "${query}".`);
      }
    }
  };

  // Completion toggle updates
  const handleToggleNodeCompletion = (stepId: string) => {
    setCompletedNodes((prev) => {
      const updated = { ...prev };
      const isCurrentlyCompleted = !!updated[stepId];

      if (isCurrentlyCompleted) {
        delete updated[stepId];
        triggerToast("Milestone Reset", "Marked this step as incomplete.");
      } else {
        updated[stepId] = true;
        triggerToast("Milestone Complete!", "Excellent! Your knowledge tree continues to grow.");
      }

      return updated;
    });
  };

  // Roadmap specific progress resetter
  const handleResetRoadmapProgress = () => {
    if (!activeRoadmap) return;

    setCompletedNodes((prev) => {
      const updated = { ...prev };
      activeRoadmap.steps.forEach((step) => {
        delete updated[step.id];
      });
      return updated;
    });

    setSelectedNode(null);
    triggerToast("Progress Cleared", "Cleared all completed milestones for this specific path.");
  };

  // FAQ Accordion toggler
  const handleToggleFaq = (index: number) => {
    setOpenFaqs((prev) => ({
      ...prev,
      [index]: !prev[index],
    }));
  };

  // Filter roadmaps by selected category or search matches
  const getFilteredRoadmaps = () => {
    if (selectedCategory === 'search_results') {
      return searchResults;
    }
    if (selectedCategory === 'career') {
      return roadmapsDatabase.filter((item) => item.category === 'tech' || item.category === 'medical' || item.category === 'career');
    }
    return roadmapsDatabase.filter((item) => item.category === selectedCategory);
  };

  const getBorderColorClass = (cat: string) => {
    switch (cat) {
      case 'medical': return 'border-t-medical-primary';
      case 'education': return 'border-t-education-primary';
      case 'government': return 'border-t-govt-primary';
      case 'business': return 'border-t-business-primary';
      case 'finance': return 'border-t-finance-primary';
      case 'tech':
      default:
        return 'border-t-tech-primary';
    }
  };

  return (
    <div className="min-h-screen flex flex-col selection:bg-honey-amber selection:text-earth-brown bg-cream text-earth-brown">
      {/* Dynamic Nav Header */}
      <Navbar
        onNavigate={handleNavigate}
        onSearch={handleSearch}
        onOpenCategory={handleOpenCategory}
      />

      {/* Floating Animated Custom Toast */}
      <div
        id="toast-notification"
        className={`fixed bottom-6 right-6 z-50 transform transition-all duration-300 pointer-events-none max-w-sm ${toast.show ? 'translate-y-0 opacity-100' : 'translate-y-20 opacity-0'
          }`}
      >
        <div className="bg-warm-white border border-border-soft rounded-2xl shadow-hover p-4 flex items-start space-x-3 pointer-events-auto">
          <div className="w-10 h-10 rounded-full bg-honey-amber/20 flex items-center justify-center text-honey-amber-dark flex-shrink-0">
            <Info className="w-5 h-5 animate-bounce" />
          </div>
          <div>
            <h4 className="font-display font-bold text-earth-brown text-base">{toast.title || "Notice"}</h4>
            <p className="text-xs text-soft-brown mt-1 leading-normal">{toast.body || "Notification Details"}</p>
          </div>
        </div>
      </div>

      {/* ======================================================= */}
      {/* VIEWPORT AREA */}
      {/* ======================================================= */}

      {/* 1. HOME VIEW */}
      {currentPage === 'home' && (
        <main id="view-home" className="flex-grow">
          {/* HERO LAYOUT */}
          <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-20 lg:py-24 grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
            {/* Left Column Information */}
            <div className="lg:col-span-7 space-y-6 text-center lg:text-left">
              <div className="inline-flex items-center space-x-2 bg-honey-amber/15 px-4 py-1.5 rounded-full border border-border-soft">
                <span className="w-2 h-2 bg-honey-amber rounded-full animate-ping"></span>
                <span className="text-[10px] sm:text-xs font-bold text-soft-brown uppercase tracking-widest font-sans">
                  100% Free Interactive Directory
                </span>
              </div>

              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-earth-brown leading-tight tracking-tight">
                India's Career, Business & Government Path —{' '}
                <span className="text-honey-amber-dark relative">
                  In One Tree.
                  <span className="absolute bottom-2 left-0 w-full h-3 bg-honey-amber/30 -z-10 rounded-full"></span>
                </span>
              </h1>

              <p className="text-base sm:text-lg text-soft-brown leading-relaxed max-w-2xl mx-auto lg:mx-0 font-sans">
                Search anything — becoming a doctor, opening a shop, applying for a passport — and see the exact path, step by step. Zero corporate jargon, completely tailored guides for Indian youth.
              </p>

              {/* Central Large Pill Search Bar */}
              <div className="bg-warm-white p-2 rounded-full border-2 border-border-soft shadow-card max-w-xl mx-auto lg:mx-0 flex items-center transition-all hover:border-honey-amber focus-within:border-honey-amber">
                <div className="flex items-center pl-3 flex-grow">
                  <Search className="text-soft-brown w-5 h-5 flex-shrink-0" />
                  <input
                    id="hero-search-input"
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSearch(searchQuery)}
                    placeholder="Search a career, business, or service (e.g. Doctor, IAS)..."
                    className="w-full text-earth-brown placeholder-soft-brown bg-transparent outline-none text-xs sm:text-sm px-3 py-2 font-medium"
                  />
                </div>
                <button
                  onClick={() => handleSearch(searchQuery)}
                  className="px-6 py-3 bg-honey-amber hover:bg-honey-amber-dark text-earth-brown font-bold rounded-full text-xs sm:text-sm transition-all shadow-md hover:scale-[1.03] cursor-pointer"
                >
                  Search Paths
                </button>
              </div>

              {/* Instant Quick Access Tags */}
              <div className="flex flex-wrap items-center justify-center lg:justify-start gap-2 pt-2">
                <span className="text-xs font-bold text-soft-brown mr-1">Popular searches:</span>
                <button
                  onClick={() => handleLoadCareerPathByKeyword('Doctor')}
                  className="px-3 py-1 bg-warm-white border border-border-soft text-xs rounded-full hover:bg-honey-amber/15 hover:border-honey-amber transition-all text-earth-brown cursor-pointer font-semibold"
                >
                  Doctor
                </button>
                <button
                  onClick={() => handleLoadCareerPathByKeyword('AI Engineer')}
                  className="px-3 py-1 bg-warm-white border border-border-soft text-xs rounded-full hover:bg-honey-amber/15 hover:border-honey-amber transition-all text-earth-brown cursor-pointer font-semibold"
                >
                  AI Engineer
                </button>
                <button
                  onClick={() => handleLoadCareerPathByKeyword('IAS Officer')}
                  className="px-3 py-1 bg-warm-white border border-border-soft text-xs rounded-full hover:bg-honey-amber/15 hover:border-honey-amber transition-all text-earth-brown cursor-pointer font-semibold"
                >
                  IAS Officer
                </button>
                <button
                  onClick={() => handleLoadCareerPathByKeyword('Startup')}
                  className="px-3 py-1 bg-warm-white border border-border-soft text-xs rounded-full hover:bg-honey-amber/15 hover:border-honey-amber transition-all text-earth-brown cursor-pointer font-semibold"
                >
                  Startup
                </button>
                <button
                  onClick={handleLoadFullCareerTree}
                  className="px-3 py-1 bg-honey-amber/20 border border-honey-amber text-xs rounded-full hover:bg-honey-amber/40 transition-all text-earth-brown cursor-pointer font-bold"
                >
                  Explore All Paths
                </button>
              </div>
            </div>

            {/* Right Column Swaying Tree SVG Illustration */}
            <div className="lg:col-span-5 flex justify-center relative">

              {/* Leaf Mandala Animation from Resources/ui/leaf */}
              <div className="absolute w-[240px] h-[240px] flex items-center justify-center -z-10 pointer-events-none transform translate-y-16">
                {Array.from({ length: 33 }).map((_, i) => {
                  const delay = i * 0.15;
                  const rotation = (i + 2) * 10.5;
                  return (
                    <div
                      key={i}
                      className="absolute w-[100px] h-[100px] rounded-tl-[100px] rounded-br-[100px] rounded-tr-none rounded-bl-none origin-[100%_0] border border-[#2D2D2D]/5 transition-all"
                      style={{
                        transform: `rotate(${rotation}deg)`,
                        animation: `leaf-mandala-anim 13s infinite alternate ease-in-out`,
                        animationDelay: `${delay}s`,
                        opacity: 0.15,
                        backgroundColor: '#F95A8D',
                        // Inject variables for CSS keyframes
                        // @ts-ignore
                        '--final-rot': `${rotation}deg`,
                        '--final-color': '#704FFE',
                        '--mid-color': '#13E2BE'
                      } as any}
                    />
                  );
                })}
              </div>

              {/* Signature swaying tree illustration */}
              <svg className="w-72 h-72 sm:w-80 sm:h-80 lg:w-96 lg:h-96 animate-sway text-earth-brown" viewBox="0 0 200 200" fill="none">
                {/* Ground roots */}
                <path d="M40 180 C 70 178, 130 178, 160 180" stroke="#6B4A2E" strokeWidth="5" strokeLinecap="round" />
                <path d="M100 130 L100 180" stroke="#6B4A2E" strokeWidth="8" strokeLinecap="round" />
                <path d="M100 150 C 85 160, 70 165, 55 175" stroke="#6B4A2E" strokeWidth="4" strokeLinecap="round" />
                <path d="M100 145 C 115 155, 130 162, 145 172" stroke="#6B4A2E" strokeWidth="4" strokeLinecap="round" />

                {/* Branches themed after the Category Identity Colors (Lush 10-Branch structure) */}
                 <path d="M100 120 C 70 110, 50 110, 35 120" stroke="#FF6B81" strokeWidth="5.5" strokeLinecap="round" /> {/* Rose Branch 1 - Medical Lower Left */}
                 <path d="M100 110 C 80 90, 60 80, 45 90" stroke="#FF6B81" strokeWidth="5" strokeLinecap="round" /> {/* Rose Branch 2 - Medical Mid Left */}
                 <path d="M100 115 C 130 105, 150 105, 165 115" stroke="#4ECDC4" strokeWidth="5.5" strokeLinecap="round" /> {/* Teal Branch 1 - Education Lower Right */}
                 <path d="M100 100 C 120 75, 140 60, 155 75" stroke="#4ECDC4" strokeWidth="5" strokeLinecap="round" /> {/* Teal Branch 2 - Education Mid Right */}
                 <path d="M100 80 L100 40" stroke="#FF9F43" strokeWidth="5.5" strokeLinecap="round" /> {/* Orange Trunk - Govt Central */}
                 <path d="M100 65 C 85 50, 85 30, 75 22" stroke="#FF9F43" strokeWidth="4" strokeLinecap="round" /> {/* Orange Branch 2 - Govt Left Top */}
                 <path d="M100 65 C 115 50, 115 30, 125 22" stroke="#FFC020" strokeWidth="4" strokeLinecap="round" /> {/* Yellow Branch 3 - Govt Right Top */}
                 
                 <path d="M100 90 C 75 70, 55 55, 38 60" stroke="#43C97E" strokeWidth="4.5" strokeLinecap="round" /> {/* Green Branch 1 - Business Lower Left */}
                 <path d="M100 70 C 80 50, 70 30, 50 25" stroke="#43C97E" strokeWidth="4" strokeLinecap="round" /> {/* Green Branch 2 - Business Upper Left */}
                 
                 <path d="M100 85 C 125 65, 145 50, 162 55" stroke="#6C5CE7" strokeWidth="4.5" strokeLinecap="round" /> {/* Violet Branch 1 - Finance Lower Right */}
                 <path d="M100 55 C 120 40, 135 25, 150 20" stroke="#6C5CE7" strokeWidth="4" strokeLinecap="round" /> {/* Violet Branch 2 - Finance Upper Right */}

                 {/* Lush Organic Leaves markers (31 leaves total) */}
                 {/* Rose Branch (Medical) Leaves */}
                 <g transform="translate(75, 115) rotate(-60) scale(0.7)">
                   <path d="M 0,0 C -6,-5 -8,-12 -4,-16 C 0,-20 0,-20 4,-16 C 8,-12 6,-5 0,0 Z" fill="#FF6B81" stroke="#2D2D2D" strokeWidth="2.5" />
                 </g>
                 <g transform="translate(55, 112) rotate(-63) scale(0.85)">
                   <path d="M 0,0 C -6,-5 -8,-12 -4,-16 C 0,-20 0,-20 4,-16 C 8,-12 6,-5 0,0 Z" fill="#FF6B81" stroke="#2D2D2D" strokeWidth="2.5" />
                 </g>
                 <g transform="translate(35, 120) rotate(-65)">
                   <path d="M 0,0 C -6,-5 -8,-12 -4,-16 C 0,-20 0,-20 4,-16 C 8,-12 6,-5 0,0 Z" fill="#FF6B81" stroke="#2D2D2D" strokeWidth="2.5" />
                 </g>
                 <g transform="translate(75, 92) rotate(-50) scale(0.7)">
                   <path d="M 0,0 C -6,-5 -8,-12 -4,-16 C 0,-20 0,-20 4,-16 C 8,-12 6,-5 0,0 Z" fill="#FF6B81" stroke="#2D2D2D" strokeWidth="2.5" />
                 </g>
                 <g transform="translate(60, 87) rotate(-55) scale(0.85)">
                   <path d="M 0,0 C -6,-5 -8,-12 -4,-16 C 0,-20 0,-20 4,-16 C 8,-12 6,-5 0,0 Z" fill="#FF6B81" stroke="#2D2D2D" strokeWidth="2.5" />
                 </g>
                 <g transform="translate(45, 90) rotate(-60)">
                   <path d="M 0,0 C -6,-5 -8,-12 -4,-16 C 0,-20 0,-20 4,-16 C 8,-12 6,-5 0,0 Z" fill="#FF6B81" stroke="#2D2D2D" strokeWidth="2.5" />
                 </g>

                 {/* Teal Branch (Education) Leaves */}
                 <g transform="translate(125, 111) rotate(60) scale(0.7)">
                   <path d="M 0,0 C -6,-5 -8,-12 -4,-16 C 0,-20 0,-20 4,-16 C 8,-12 6,-5 0,0 Z" fill="#4ECDC4" stroke="#2D2D2D" strokeWidth="2.5" />
                 </g>
                 <g transform="translate(145, 110) rotate(63) scale(0.85)">
                   <path d="M 0,0 C -6,-5 -8,-12 -4,-16 C 0,-20 0,-20 4,-16 C 8,-12 6,-5 0,0 Z" fill="#4ECDC4" stroke="#2D2D2D" strokeWidth="2.5" />
                 </g>
                 <g transform="translate(165, 115) rotate(65)">
                   <path d="M 0,0 C -6,-5 -8,-12 -4,-16 C 0,-20 0,-20 4,-16 C 8,-12 6,-5 0,0 Z" fill="#4ECDC4" stroke="#2D2D2D" strokeWidth="2.5" />
                 </g>
                 <g transform="translate(120, 83) rotate(45) scale(0.7)">
                   <path d="M 0,0 C -6,-5 -8,-12 -4,-16 C 0,-20 0,-20 4,-16 C 8,-12 6,-5 0,0 Z" fill="#4ECDC4" stroke="#2D2D2D" strokeWidth="2.5" />
                 </g>
                 <g transform="translate(140, 71) rotate(55) scale(0.85)">
                   <path d="M 0,0 C -6,-5 -8,-12 -4,-16 C 0,-20 0,-20 4,-16 C 8,-12 6,-5 0,0 Z" fill="#4ECDC4" stroke="#2D2D2D" strokeWidth="2.5" />
                 </g>
                 <g transform="translate(155, 75) rotate(60)">
                   <path d="M 0,0 C -6,-5 -8,-12 -4,-16 C 0,-20 0,-20 4,-16 C 8,-12 6,-5 0,0 Z" fill="#4ECDC4" stroke="#2D2D2D" strokeWidth="2.5" />
                 </g>

                 {/* Orange Trunk (Govt) Leaves */}
                 <g transform="translate(100, 68) rotate(-15) scale(0.75)">
                   <path d="M 0,0 C -5,-4 -6.5,-9 -3.5,-12 C 0,-15 0,-15 3.5,-12 C 6.5,-9 5,-4 0,0 Z" fill="#FF9F43" stroke="#2D2D2D" strokeWidth="2.5" />
                 </g>
                 <g transform="translate(100, 52) rotate(15) scale(0.85)">
                   <path d="M 0,0 C -5,-4 -6.5,-9 -3.5,-12 C 0,-15 0,-15 3.5,-12 C 6.5,-9 5,-4 0,0 Z" fill="#FF9F43" stroke="#2D2D2D" strokeWidth="2.5" />
                 </g>
                 <g transform="translate(100, 40) rotate(0)">
                   <path d="M 0,0 C -5,-4 -6.5,-9 -3.5,-12 C 0,-15 0,-15 3.5,-12 C 6.5,-9 5,-4 0,0 Z" fill="#FF9F43" stroke="#2D2D2D" strokeWidth="2.5" />
                 </g>
                 <g transform="translate(88, 38) rotate(-20) scale(0.75)">
                   <path d="M 0,0 C -5,-4 -6.5,-9 -3.5,-12 C 0,-15 0,-15 3.5,-12 C 6.5,-9 5,-4 0,0 Z" fill="#FF9F43" stroke="#2D2D2D" strokeWidth="2.5" />
                 </g>
                 <g transform="translate(82, 28) rotate(-22) scale(0.85)">
                   <path d="M 0,0 C -5,-4 -6.5,-9 -3.5,-12 C 0,-15 0,-15 3.5,-12 C 6.5,-9 5,-4 0,0 Z" fill="#FF9F43" stroke="#2D2D2D" strokeWidth="2.5" />
                 </g>
                 <g transform="translate(75, 22) rotate(-25)">
                   <path d="M 0,0 C -5,-4 -6.5,-9 -3.5,-12 C 0,-15 0,-15 3.5,-12 C 6.5,-9 5,-4 0,0 Z" fill="#FF9F43" stroke="#2D2D2D" strokeWidth="2.5" />
                 </g>
                 <g transform="translate(112, 38) rotate(20) scale(0.75)">
                   <path d="M 0,0 C -5,-4 -6.5,-9 -3.5,-12 C 0,-15 0,-15 3.5,-12 C 6.5,-9 5,-4 0,0 Z" fill="#FFC020" stroke="#2D2D2D" strokeWidth="2.5" />
                 </g>
                 <g transform="translate(118, 28) rotate(22) scale(0.85)">
                   <path d="M 0,0 C -5,-4 -6.5,-9 -3.5,-12 C 0,-15 0,-15 3.5,-12 C 6.5,-9 5,-4 0,0 Z" fill="#FFC020" stroke="#2D2D2D" strokeWidth="2.5" />
                 </g>
                 <g transform="translate(125, 22) rotate(25)">
                   <path d="M 0,0 C -5,-4 -6.5,-9 -3.5,-12 C 0,-15 0,-15 3.5,-12 C 6.5,-9 5,-4 0,0 Z" fill="#FFC020" stroke="#2D2D2D" strokeWidth="2.5" />
                 </g>

                 {/* Green Branch (Business) Leaves */}
                 <g transform="translate(75, 72) rotate(-45) scale(0.7)">
                   <path d="M 0,0 C -6,-5 -8,-12 -4,-16 C 0,-20 0,-20 4,-16 C 8,-12 6,-5 0,0 Z" fill="#43C97E" stroke="#2D2D2D" strokeWidth="2.5" />
                 </g>
                 <g transform="translate(55, 63) rotate(-48) scale(0.85)">
                   <path d="M 0,0 C -6,-5 -8,-12 -4,-16 C 0,-20 0,-20 4,-16 C 8,-12 6,-5 0,0 Z" fill="#43C97E" stroke="#2D2D2D" strokeWidth="2.5" />
                 </g>
                 <g transform="translate(38, 60) rotate(-50)">
                   <path d="M 0,0 C -6,-5 -8,-12 -4,-16 C 0,-20 0,-20 4,-16 C 8,-12 6,-5 0,0 Z" fill="#43C97E" stroke="#2D2D2D" strokeWidth="2.5" />
                 </g>
                 <g transform="translate(80, 55) rotate(-35) scale(0.7)">
                   <path d="M 0,0 C -6,-5 -8,-12 -4,-16 C 0,-20 0,-20 4,-16 C 8,-12 6,-5 0,0 Z" fill="#43C97E" stroke="#2D2D2D" strokeWidth="2.5" />
                 </g>
                 <g transform="translate(65, 38) rotate(-40) scale(0.85)">
                   <path d="M 0,0 C -6,-5 -8,-12 -4,-16 C 0,-20 0,-20 4,-16 C 8,-12 6,-5 0,0 Z" fill="#43C97E" stroke="#2D2D2D" strokeWidth="2.5" />
                 </g>
                 <g transform="translate(50, 25) rotate(-45)">
                   <path d="M 0,0 C -6,-5 -8,-12 -4,-16 C 0,-20 0,-20 4,-16 C 8,-12 6,-5 0,0 Z" fill="#43C97E" stroke="#2D2D2D" strokeWidth="2.5" />
                 </g>

                 {/* Violet Branch (Finance) Leaves */}
                 <g transform="translate(125, 70) rotate(45) scale(0.7)">
                   <path d="M 0,0 C -6,-5 -8,-12 -4,-16 C 0,-20 0,-20 4,-16 C 8,-12 6,-5 0,0 Z" fill="#6C5CE7" stroke="#2D2D2D" strokeWidth="2.5" />
                 </g>
                 <g transform="translate(145, 61) rotate(48) scale(0.85)">
                   <path d="M 0,0 C -6,-5 -8,-12 -4,-16 C 0,-20 0,-20 4,-16 C 8,-12 6,-5 0,0 Z" fill="#6C5CE7" stroke="#2D2D2D" strokeWidth="2.5" />
                 </g>
                 <g transform="translate(162, 55) rotate(50)">
                   <path d="M 0,0 C -6,-5 -8,-12 -4,-16 C 0,-20 0,-20 4,-16 C 8,-12 6,-5 0,0 Z" fill="#6C5CE7" stroke="#2D2D2D" strokeWidth="2.5" />
                 </g>
                 <g transform="translate(120, 43) rotate(35) scale(0.7)">
                   <path d="M 0,0 C -6,-5 -8,-12 -4,-16 C 0,-20 0,-20 4,-16 C 8,-12 6,-5 0,0 Z" fill="#6C5CE7" stroke="#2D2D2D" strokeWidth="2.5" />
                 </g>
                 <g transform="translate(138, 30) rotate(40) scale(0.85)">
                   <path d="M 0,0 C -6,-5 -8,-12 -4,-16 C 0,-20 0,-20 4,-16 C 8,-12 6,-5 0,0 Z" fill="#6C5CE7" stroke="#2D2D2D" strokeWidth="2.5" />
                 </g>
                 <g transform="translate(150, 20) rotate(45)">
                   <path d="M 0,0 C -6,-5 -8,-12 -4,-16 C 0,-20 0,-20 4,-16 C 8,-12 6,-5 0,0 Z" fill="#6C5CE7" stroke="#2D2D2D" strokeWidth="2.5" />
                 </g>
                 
                 <path d="M100 120 C 90 100, 110 80, 100 60" stroke="#FFC020" strokeWidth="7" strokeLinecap="round" /> {/* Main Center */}
                 <g transform="translate(100, 60) rotate(15)">
                   <path d="M 0,0 C -4,-3 -5,-8 -2.5,-11 C 0,-13 0,-13 2.5,-11 C 5,-8 4,-3 0,0 Z" fill="#E9FFC7" stroke="#2D2D2D" strokeWidth="2.5" />
                 </g>    
              </svg>
            </div>
          </section>

          {/* FOUR DOORS (CATEGORIES) SECTION */}
          <section className="bg-warm-white/60 border-t border-b border-border-soft py-16 sm:py-24">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="text-center max-w-3xl mx-auto mb-12 space-y-3">
                <h2 className="text-3xl sm:text-4xl font-extrabold text-earth-brown">Discover Your Chosen Door</h2>
                <p className="text-base text-soft-brown">Select from four massive segments of Indian pathways to reveal curated roadmap trees.</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {/* Door 1: Professional Careers */}
                <div
                  onClick={() => handleOpenCategory('career')}
                  className="group cursor-pointer bg-warm-white border border-border-soft rounded-2xl p-6 shadow-card hover:shadow-hover transition-all duration-300 border-l-4 border-l-tech-primary"
                >
                  <div className="w-12 h-12 rounded-full bg-tech/20 flex items-center justify-center text-tech-primary mb-4">
                    <GraduationCap className="w-6 h-6" />
                  </div>
                  <h3 className="text-xl font-bold font-display text-earth-brown group-hover:text-honey-amber-dark transition-colors">
                    Professional Careers
                  </h3>
                  <p className="text-xs text-soft-brown mt-2 leading-relaxed font-sans">
                    Technical, medical, creative, and professional courses built step-by-step.
                  </p>
                  <div className="flex flex-wrap gap-1.5 mt-4">
                    <span className="text-[10px] font-bold bg-tech/20 text-blue-600 px-2 py-0.5 rounded-full">Doctor</span>
                    <span className="text-[10px] font-bold bg-tech/20 text-blue-600 px-2 py-0.5 rounded-full">AI Engineer</span>
                  </div>
                </div>

                {/* Door 2: Government & UPSC */}
                <div
                  onClick={() => handleOpenCategory('government')}
                  className="group cursor-pointer bg-warm-white border border-border-soft rounded-2xl p-6 shadow-card hover:shadow-hover transition-all duration-300 border-l-4 border-l-govt-primary"
                >
                  <div className="w-12 h-12 rounded-full bg-govt/20 flex items-center justify-center text-govt-primary mb-4">
                    <ShieldCheck className="w-6 h-6" />
                  </div>
                  <h3 className="text-xl font-bold font-display text-earth-brown group-hover:text-honey-amber-dark transition-colors">
                    Government & UPSC
                  </h3>
                  <p className="text-xs text-soft-brown mt-2 leading-relaxed font-sans">
                    Civil services, defense forces, banking PO, railways, and state level guidelines.
                  </p>
                  <div className="flex flex-wrap gap-1.5 mt-4">
                    <span className="text-[10px] font-bold bg-govt/20 text-amber-700 px-2 py-0.5 rounded-full">IAS Officer</span>
                    <span className="text-[10px] font-bold bg-govt/20 text-amber-700 px-2 py-0.5 rounded-full">Police SI</span>
                  </div>
                </div>

                {/* Door 3: Business & MSME */}
                <div
                  onClick={() => handleOpenCategory('business')}
                  className="group cursor-pointer bg-warm-white border border-border-soft rounded-2xl p-6 shadow-card hover:shadow-hover transition-all duration-300 border-l-4 border-l-business-primary"
                >
                  <div className="w-12 h-12 rounded-full bg-business/20 flex items-center justify-center text-business-primary mb-4">
                    <Store className="w-6 h-6" />
                  </div>
                  <h3 className="text-xl font-bold font-display text-earth-brown group-hover:text-honey-amber-dark transition-colors">
                    Business & MSME
                  </h3>
                  <p className="text-xs text-soft-brown mt-2 leading-relaxed font-sans">
                    How to start a cafe, register a shop, scaling startup ideas, and Mudra loans.
                  </p>
                  <div className="flex flex-wrap gap-1.5 mt-4">
                    <span className="text-[10px] font-bold bg-business/20 text-emerald-700 px-2 py-0.5 rounded-full">Organic Farm</span>
                    <span className="text-[10px] font-bold bg-business/20 text-emerald-700 px-2 py-0.5 rounded-full">Startup</span>
                  </div>
                </div>

                {/* Door 4: Finance & Chartered Accountant */}
                <div
                  onClick={() => handleOpenCategory('finance')}
                  className="group cursor-pointer bg-warm-white border border-border-soft rounded-2xl p-6 shadow-card hover:shadow-hover transition-all duration-300 border-l-4 border-l-finance-primary"
                >
                  <div className="w-12 h-12 rounded-full bg-finance/20 flex items-center justify-center text-finance-primary mb-4">
                    <Coins className="w-6 h-6" />
                  </div>
                  <h3 className="text-xl font-bold font-display text-earth-brown group-hover:text-honey-amber-dark transition-colors">
                    Finance & CA
                  </h3>
                  <p className="text-xs text-soft-brown mt-2 leading-relaxed font-sans">
                    Chartered accountancy exams, statutory audits, tax registrations, and bank jobs.
                  </p>
                  <div className="flex flex-wrap gap-1.5 mt-4">
                    <span className="text-[10px] font-bold bg-finance/20 text-indigo-700 px-2 py-0.5 rounded-full">CA Exam</span>
                    <span className="text-[10px] font-bold bg-finance/20 text-indigo-700 px-2 py-0.5 rounded-full">Bank PO</span>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* HOW IT WORKS SECTION */}
          <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-24">
            <div className="text-center max-w-2xl mx-auto mb-16 space-y-3">
              <h2 className="text-3xl font-extrabold text-earth-brown">How It Works</h2>
              <p className="text-base text-soft-brown">200,000 career paths. 146,000 milestones. All organized into one logical tree — so you never feel lost.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-12 relative">
              {/* Step 1 */}
              <div className="flex flex-col items-center text-center space-y-4">
                <div className="w-16 h-16 rounded-full bg-honey-amber flex items-center justify-center font-display font-bold text-2xl text-earth-brown shadow-md">
                  1
                </div>
                <h3 className="text-xl font-bold text-earth-brown font-display">Pick a Direction</h3>
                <p className="text-sm text-soft-brown max-w-xs leading-relaxed font-sans">
                  Search any career, exam, or business role. Our database covers Doctor, IAS, AI Engineer, Startup, and 200,000+ more paths.
                </p>
              </div>

              {/* Step 2 */}
              <div className="flex flex-col items-center text-center space-y-4">
                <div className="w-16 h-16 rounded-full bg-honey-amber flex items-center justify-center font-display font-bold text-2xl text-earth-brown shadow-md">
                  2
                </div>
                <h3 className="text-xl font-bold text-earth-brown font-display">Inspect the Tree</h3>
                <p className="text-sm text-soft-brown max-w-xs leading-relaxed font-sans">
                  See every step from school to career — with branching paths, connections, and milestones mapped with colored branches.
                </p>
              </div>

              {/* Step 3 */}
              <div className="flex flex-col items-center text-center space-y-4">
                <div className="w-16 h-16 rounded-full bg-honey-amber flex items-center justify-center font-display font-bold text-2xl text-earth-brown shadow-md">
                  3
                </div>
                <h3 className="text-xl font-bold text-earth-brown font-display">Access Real Assets</h3>
                <p className="text-sm text-soft-brown max-w-xs leading-relaxed font-sans">
                  Click any node to get official portal links, NCERT PDFs, exam guidelines, free YouTube playlists, and step-by-step checklists.
                </p>
              </div>
            </div>
          </section>

          {/* WHY THIS EXISTS SECTION */}
          <section className="bg-honey-amber/10 border-t border-b border-border-soft py-16">
            <div className="max-w-4xl mx-auto px-4 text-center space-y-6">
              <span className="text-xs font-extrabold text-honey-amber-dark uppercase tracking-widest font-sans">An Honest Mission</span>
              <h2 className="text-3xl font-extrabold text-[#2D2D2D]">India's Career Data Was Scattered. Now It's One Tree.</h2>
              <p className="text-base sm:text-lg text-soft-brown leading-relaxed font-sans">
                We mapped 200,000 career pathways from 10th grade to final career destinations — Doctor, IAS, AI Engineer, Startup Founder, and everything in between. Every node links to official portals, free resources, and real checklists. No paywalls. No corporate jargon. Just clarity.
              </p>
              <div className="pt-4">
                <button
                  onClick={handleLoadFullCareerTree}
                  className="px-6 py-3 bg-earth-brown hover:bg-earth-brown/90 text-white font-bold rounded-full text-sm transition-all shadow-md cursor-pointer"
                >
                  Explore All 200K Paths
                </button>
              </div>
            </div>
          </section>

          {/* FAQ SECTION */}
          <section className="max-w-4xl mx-auto px-4 py-16 sm:py-24 space-y-12">
            <div className="text-center space-y-3">
              <h2 className="text-3xl font-extrabold text-earth-brown">Frequently Asked Questions</h2>
              <p className="text-base text-soft-brown">Simple, plain-language answers about our platform.</p>
            </div>

            <div className="space-y-4">
              {/* Q1 */}
              <div className="bg-warm-white border border-border-soft rounded-2xl overflow-hidden shadow-card">
                <button
                  onClick={() => handleToggleFaq(0)}
                  className="w-full flex items-center justify-between p-5 text-left font-bold font-display text-earth-brown text-base hover:bg-cream/40 cursor-pointer"
                >
                  <span>Is this platform completely free to use?</span>
                  <ChevronDown className={`w-5 h-5 text-soft-brown transition-transform duration-300 ${openFaqs[0] ? 'rotate-180' : ''}`} />
                </button>
                {openFaqs[0] && (
                  <div className="p-5 border-t border-border-soft text-sm text-soft-brown bg-warm-white/40 leading-relaxed font-sans">
                    Yes! CrevrTree is fully open and completely free. We do not require any login, payment details, or lock any premium modules. Our goal is wide democratic accessibility for every school/college student across India.
                  </div>
                )}
              </div>

              {/* Q2 */}
              <div className="bg-warm-white border border-border-soft rounded-2xl overflow-hidden shadow-card">
                <button
                  onClick={() => handleToggleFaq(1)}
                  className="w-full flex items-center justify-between p-5 text-left font-bold font-display text-earth-brown text-base hover:bg-cream/40 cursor-pointer"
                >
                  <span>How are the resources verified?</span>
                  <ChevronDown className={`w-5 h-5 text-soft-brown transition-transform duration-300 ${openFaqs[1] ? 'rotate-180' : ''}`} />
                </button>
                {openFaqs[1] && (
                  <div className="p-5 border-t border-border-soft text-sm text-soft-brown bg-warm-white/40 leading-relaxed font-sans">
                    All links inside node details point strictly to official portals (e.g. NTA for NEET exam, ICAI for Chartered Accountants, or NPTEL for CSE lectures). Free reference resources include top-rated public NCERT textbooks and verified free educational creators with zero hidden paywalls.
                  </div>
                )}
              </div>

              {/* Q3 */}
              <div className="bg-warm-white border border-border-soft rounded-2xl overflow-hidden shadow-card">
                <button
                  onClick={() => handleToggleFaq(2)}
                  className="w-full flex items-center justify-between p-5 text-left font-bold font-display text-earth-brown text-base hover:bg-cream/40 cursor-pointer"
                >
                  <span>Do I need to sign in to save my roadmap progress?</span>
                  <ChevronDown className={`w-5 h-5 text-soft-brown transition-transform duration-300 ${openFaqs[2] ? 'rotate-180' : ''}`} />
                </button>
                {openFaqs[2] && (
                  <div className="p-5 border-t border-border-soft text-sm text-soft-brown bg-warm-white/40 leading-relaxed font-sans">
                    No login is required! We store your completed roadmap states and checkboxes directly inside your local browser storage (localStorage). As long as you don't clear your browser data, your progress remains beautifully tracked.
                  </div>
                )}
              </div>
            </div>
          </section>
        </main>
      )}

      {/* 2. CATEGORY FILTER VIEW */}
      {currentPage === 'category' && (
        <main id="view-category" className="flex-grow py-12">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
            {/* Back Navigation Action */}
            <div>
              <button
                onClick={() => handleNavigate('home')}
                className="inline-flex items-center space-x-2 text-sm font-semibold text-earth-brown hover:text-honey-amber-dark bg-warm-white px-4 py-2 rounded-full border border-border-soft transition-all cursor-pointer"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>Back to Home</span>
              </button>
            </div>

            {/* Page Title Block */}
            <div className="space-y-3">
              <span id="category-badge-pill" className="text-xs font-extrabold uppercase px-3 py-1 rounded-full bg-honey-amber/20 text-earth-brown border border-border-soft">
                {selectedCategory === 'search_results' ? 'Custom Filter' : `${selectedCategory} Directory`}
              </span>
              <h1 id="category-page-title" className="text-4xl font-extrabold text-earth-brown font-display">
                {selectedCategory === 'career' && "Professional Career Paths"}
                {selectedCategory === 'government' && "Government & Administrative Exams"}
                {selectedCategory === 'business' && "Business, MSME & Startups"}
                {selectedCategory === 'finance' && "Finance & Chartered Accountancy"}
                {selectedCategory === 'education' && "Academic Education Pathways"}
                {selectedCategory === 'medical' && "Healthcare & Medical Streams"}
                {selectedCategory === 'tech' && "Technology & Coding Milestones"}
                {selectedCategory === 'search_results' && "Interactive Search Matches"}
              </h1>
              <p id="category-page-desc" className="text-base text-soft-brown max-w-3xl">
                {selectedCategory === 'career' && "Step-by-step lifelines for medical degrees, high-value tech certifications, and technical engineering profiles."}
                {selectedCategory === 'government' && "Comprehensive structural timelines for UPSC Civil Services, police examinations, state PSCs, and railway jobs."}
                {selectedCategory === 'business' && "Tactical action roadmaps for incorporating businesses, obtaining Mudra loans, and scaling startup products."}
                {selectedCategory === 'finance' && "Complete timelines mapping Chartered Accountancy stages, direct/indirect taxes, and audit licensing."}
                {selectedCategory === 'search_results' && "Select one of our matches below to load the live node connection viewport."}
                {!['career', 'government', 'business', 'finance', 'search_results'].includes(selectedCategory || '') && "Select a path card below to open its custom node-by-node structured branching canvas."}
              </p>
            </div>

            {/* Roadmaps Grid */}
            <div id="category-roadmaps-grid" className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {getFilteredRoadmaps().map((roadmap) => (
                <div
                  key={roadmap.id}
                  onClick={() => handleLoadRoadmap(roadmap.id)}
                  className={`group bg-warm-white border border-border-soft rounded-2xl p-6 shadow-card hover:shadow-hover transition-all duration-300 cursor-pointer border-t-4 ${getBorderColorClass(roadmap.category)}`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-extrabold text-soft-brown uppercase tracking-widest">{roadmap.category} path</span>
                    <span className="text-[10px] bg-honey-amber/25 text-earth-brown font-bold px-2 py-0.5 rounded">{roadmap.steps.length} Milestones</span>
                  </div>
                  <h3 className="text-xl font-bold font-display text-earth-brown mt-3 group-hover:text-honey-amber-dark transition-colors">{roadmap.name}</h3>
                  <p className="text-xs text-soft-brown mt-2 leading-relaxed font-sans">{roadmap.tagline}</p>
                  <div className="flex items-center space-x-1.5 text-xs font-bold text-honey-amber-dark mt-4 group-hover:underline">
                    <span>Open Interactive Tree</span>
                    <Compass className="w-4 h-4 animate-spin-slow" />
                  </div>
                </div>
              ))}

              {getFilteredRoadmaps().length === 0 && (
                <div className="col-span-full py-16 text-center space-y-4 bg-warm-white border border-border-soft rounded-2xl">
                  <p className="text-sm text-soft-brown">No roadmaps are available inside this selected category right now.</p>
                  <button onClick={() => handleNavigate('home')} className="px-4 py-2 bg-honey-amber text-earth-brown text-xs font-bold rounded-full cursor-pointer">
                    Return Home
                  </button>
                </div>
              )}
            </div>
          </div>
        </main>
      )}

      {/* 3. TREE VIEW (THE MAIN INTERACTIVE PRODUCT) */}
      {currentPage === 'tree' && activeRoadmap && (
        <main id="view-tree" className="flex-grow py-8">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">

            {/* Top controls and metadata headers */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border-soft pb-6">
              <div className="space-y-1">
                <div className="flex items-center space-x-2 font-sans">
                  <button onClick={() => handleNavigate('home')} className="text-xs font-bold text-soft-brown hover:text-earth-brown cursor-pointer">Home</button>
                  <span className="text-xs text-soft-brown">/</span>
                  <button onClick={() => handleOpenCategory(activeRoadmap.category)} className="text-xs font-bold text-soft-brown hover:text-earth-brown capitalize cursor-pointer">
                    {activeRoadmap.category}
                  </button>
                  <span className="text-xs text-soft-brown">/</span>
                  <span className="text-xs font-bold text-earth-brown">{activeRoadmap.name}</span>
                </div>
                <h1 className="text-3xl sm:text-4xl font-extrabold text-earth-brown font-display leading-tight">
                  {activeRoadmap.name}
                </h1>
                <p className="text-sm text-soft-brown leading-relaxed max-w-3xl font-sans">
                  {activeRoadmap.tagline}
                </p>
              </div>

              {/* Progress and Search controls */}
              <div className="flex flex-col sm:flex-row items-center gap-3">
                {/* Inline Node Search Input */}
                <div className="relative">
                  <input
                    type="text"
                    placeholder="Locate step in this tree..."
                    className="px-4 py-2 pl-9 bg-warm-white border-2 border-[#2D2D2D] rounded-full text-xs font-sans text-earth-brown placeholder-soft-brown focus:outline-none shadow-[2px_2px_0px_0px_#2D2D2D] focus:shadow-[1px_1px_0px_0px_#2D2D2D] focus:translate-x-[1px] focus:translate-y-[1px] transition-all w-52"
                    onChange={(e) => {
                      const val = e.target.value.toLowerCase().trim();
                      if (!val) return;
                      const matched = activeRoadmap.steps.find(s =>
                        s.name.toLowerCase().includes(val) ||
                        s.desc.toLowerCase().includes(val)
                      );
                      if (matched) {
                        setSelectedNode(matched);
                      }
                    }}
                  />
                  <Search className="w-3.5 h-3.5 text-soft-brown absolute left-3 top-2.5" />
                </div>

                {/* Progress Reset button */}
                <button
                  onClick={handleResetRoadmapProgress}
                  className="inline-flex items-center space-x-1.5 px-4 py-2 bg-warm-white border-2 border-[#2D2D2D] hover:bg-cream/50 text-xs font-bold text-earth-brown rounded-full transition-all flex-shrink-0 cursor-pointer shadow-[2px_2px_0px_0px_#2D2D2D] hover:translate-x-[1px] hover:translate-y-[1px] hover:shadow-[1px_1px_0px_0px_#2D2D2D]"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  <span>Reset Progress</span>
                </button>
              </div>
            </div>

            {/* Collapsible "What is this?" explainer bar */}
            <div className="border border-border-soft bg-warm-white rounded-2xl overflow-hidden shadow-sm">
              <button
                onClick={() => setExplainOpen(!explainOpen)}
                className="w-full flex items-center justify-between p-4 font-display font-bold text-earth-brown text-left cursor-pointer hover:bg-cream/20 transition-colors"
              >
                <div className="flex items-center space-x-2.5">
                  <span className="text-honey-amber text-lg">💡</span>
                  <span>What is {activeRoadmap.name}?</span>
                </div>
                <ChevronDown className={`w-5 h-5 transition-transform duration-300 ${explainOpen ? 'rotate-180' : ''}`} />
              </button>
              {explainOpen && (
                <div className="p-5 border-t border-border-soft text-sm text-soft-brown bg-warm-white/40 leading-relaxed font-sans space-y-3">
                  <p>
                    This is an interactive step-by-step career mapping directory showing the typical pathways, milestones, required qualifications, and learning resources to become a <strong>{activeRoadmap.name}</strong> in India.
                  </p>
                  <p>
                    Click on any milestone node in the central spine to view salary bands, top hiring companies, entrance exams, recommended reference books, and free learning links in the Inspector Panel. Toggle completed nodes to track your milestones as you grow!
                  </p>
                </div>
              )}
            </div>

            {/* Main layout container: full-width Tree Canvas */}
            <div className="w-full relative min-h-[500px] space-y-6">

              {/* Tree canvas full width */}
              <div className="w-full space-y-6">
                <TreeCanvas
                  roadmap={activeRoadmap}
                  completedNodes={completedNodes}
                  selectedNode={selectedNode}
                  onSelectNode={setSelectedNode}
                />

                {/* Real Stats Strip */}
                {(() => {
                  const completedInRm = activeRoadmap.steps.filter(s => completedNodes[s.id]).length;
                  const percent = Math.round((completedInRm / activeRoadmap.steps.length) * 100);
                  return (
                    <div className="bg-[#FAF9F5] border-2 border-[#2D2D2D] rounded-3xl p-6 flex flex-wrap items-center justify-around gap-6 shadow-[3px_3px_0px_0px_#2D2D2D] font-sans text-center">
                      <div>
                        <span className="text-[10px] uppercase font-bold text-[#6B665F] tracking-widest block">Total Milestones</span>
                        <span className="text-xl font-black text-earth-brown mt-1 block">{activeRoadmap.steps.length}</span>
                      </div>
                      <div className="w-px h-8 bg-border-soft hidden md:block"></div>
                      <div>
                        <span className="text-[10px] uppercase font-bold text-[#6B665F] tracking-widest block">Completed Milestones</span>
                        <span className="text-xl font-black text-emerald-600 mt-1 block">{completedInRm} / {activeRoadmap.steps.length}</span>
                      </div>
                      <div className="w-px h-8 bg-border-soft hidden md:block"></div>
                      <div>
                        <span className="text-[10px] uppercase font-bold text-[#6B665F] tracking-widest block">Your Progress</span>
                        <span className="text-xl font-black text-honey-amber-dark mt-1 block">{percent}% Completed</span>
                      </div>
                    </div>
                  );
                })()}
              </div>

              {/* Dynamic Slide-out Inspector Drawer */}
              {selectedNode && (
                <div className="fixed inset-0 z-50 overflow-hidden font-sans pointer-events-none">
                  {/* Backdrop overlay (Mobile only) */}
                  <div
                    onClick={() => setSelectedNode(null)}
                    className="lg:hidden absolute inset-0 bg-slate-900/40 backdrop-blur-sm transition-opacity duration-300 cursor-pointer pointer-events-auto"
                  />

                  {/* Sliding panel container */}
                  <div className="absolute inset-y-0 right-0 pl-10 max-w-full flex">
                    <div
                      className="w-screen max-w-md bg-white shadow-2xl border-l-2 border-[#2D2D2D] flex flex-col transform transition-transform duration-300 ease-out translate-x-0 pointer-events-auto"
                      onClick={(e) => e.stopPropagation()}
                    >
                      {/* Drawer header / close button */}
                      <div className="p-4 bg-slate-50 border-b-2 border-[#2D2D2D] flex items-center justify-between">
                        <span className="text-xs font-black uppercase text-slate-700 bg-amber-100 px-2.5 py-1 rounded border border-[#2D2D2D] font-mono">
                          Milestone Inspector
                        </span>
                        <button
                          onClick={() => setSelectedNode(null)}
                          className="p-1 rounded-full hover:bg-slate-200 border-2 border-[#2D2D2D] bg-white cursor-pointer shadow-[1.5px_1.5px_0px_0px_#2D2D2D]"
                        >
                          <X className="w-4 h-4 text-[#2D2D2D]" />
                        </button>
                      </div>

                      {/* Scrollable Content Container */}
                      <div className="flex-1 overflow-y-auto p-5">
                        <InspectorPanel
                          step={selectedNode}
                          completedNodes={completedNodes}
                          onToggleCompletion={handleToggleNodeCompletion}
                          onExplorePath={handleLoadRoadmap}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Floating Menu/Toggle button to reopen details if closed */}
              {!selectedNode && activeRoadmap && activeRoadmap.steps && activeRoadmap.steps.length > 0 && (
                <button
                  onClick={() => setSelectedNode(activeRoadmap.steps[0])}
                  className="fixed bottom-6 right-6 z-40 bg-[#FFC020] hover:bg-[#E0A000] border-2 border-[#2D2D2D] text-[#2D2D2D] font-extrabold text-xs px-4 py-3 rounded-full shadow-[3px_3px_0px_0px_#2D2D2D] hover:shadow-[1px_1px_0px_0px_#2D2D2D] hover:translate-x-[1.5px] hover:translate-y-[1.5px] transition-all cursor-pointer flex items-center space-x-1.5"
                >
                  <Compass className="w-4 h-4 animate-spin-slow" />
                  <span>Open Inspector</span>
                </button>
              )}

            </div>

            {/* Roadmap FAQ Accordion */}
            <section className="border-t border-border-soft pt-12 mt-12 space-y-6">
              <h2 className="text-2xl font-extrabold text-earth-brown font-display text-center">
                Frequently Asked Questions — {activeRoadmap.name}
              </h2>
              <div className="max-w-4xl mx-auto space-y-4 font-sans">
                {/* FAQ Item 1 */}
                <div className="bg-warm-white border border-border-soft rounded-2xl overflow-hidden shadow-sm">
                  <button
                    onClick={() => handleToggleFaq(10)}
                    className="w-full flex items-center justify-between p-5 font-display font-bold text-earth-brown text-left cursor-pointer hover:bg-cream/10 transition-colors"
                  >
                    <span>How long does it typically take to complete this pathway?</span>
                    <ChevronDown className={`w-4 h-4 transition-transform duration-200 ${openFaqs[10] ? 'rotate-180' : ''}`} />
                  </button>
                  {openFaqs[10] && (
                    <div className="p-5 border-t border-border-soft text-sm text-soft-brown bg-warm-white/30 leading-relaxed">
                      The duration varies depending on your starting background, but typical academic and skill transitions take between 2 to 4 years to complete all milestones comprehensively.
                    </div>
                  )}
                </div>

                {/* FAQ Item 2 */}
                <div className="bg-warm-white border border-border-soft rounded-2xl overflow-hidden shadow-sm">
                  <button
                    onClick={() => handleToggleFaq(11)}
                    className="w-full flex items-center justify-between p-5 font-display font-bold text-earth-brown text-left cursor-pointer hover:bg-cream/10 transition-colors"
                  >
                    <span>Are the learning resources and reference links completely free?</span>
                    <ChevronDown className={`w-4 h-4 transition-transform duration-200 ${openFaqs[11] ? 'rotate-180' : ''}`} />
                  </button>
                  {openFaqs[11] && (
                    <div className="p-5 border-t border-border-soft text-sm text-soft-brown bg-warm-white/30 leading-relaxed">
                      Yes! All references, NCERT portals, textbooks, and tutorial checklists linked in the milestones are curated from open-access, publicly available free educational hubs.
                    </div>
                  )}
                </div>
              </div>
            </section>
          </div>
        </main>
      )}

      {/* 4. PLATFORM VISION VIEW */}
      {currentPage === 'about' && (
        <main id="view-about" className="flex-grow py-12 md:py-20 bg-warm-white/40">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 space-y-16">

            {/* Vision Header */}
            <div className="text-center space-y-4">
              <span className="text-xs font-extrabold uppercase px-3 py-1 rounded-full bg-honey-amber/20 text-earth-brown border border-border-soft block w-max mx-auto">
                About CrevrTree
              </span>
              <h1 className="text-4xl sm:text-5xl font-extrabold text-earth-brown font-display leading-tight">
                The Vision Behind CrevrTree
              </h1>
              <p className="text-base sm:text-lg text-soft-brown leading-relaxed max-w-2xl mx-auto font-sans font-medium">
                A visual directory that maps school-to-career lifelines for Indian youth. Free from advertisements, paywalls, and corporate jargon.
              </p>
            </div>

            {/* Challenge and Solution boxes */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 pt-6">
              <div className="bg-warm-white border border-border-soft p-8 rounded-2xl space-y-4 shadow-card">
                <div className="w-10 h-10 rounded-full bg-red-100 flex items-center justify-center text-red-500 font-display font-bold text-lg">
                  ⚠️
                </div>
                <h3 className="text-xl font-bold text-earth-brown font-display">The Problem We Solve</h3>
                <p className="text-xs sm:text-sm text-soft-brown leading-relaxed font-sans">
                  Indian high school and college students navigate career choices blind. They are targeted by massive commercial portals that lock standard checklists behind heavy paywalls. Jargon like "SaaS", "LPA", and "CTAs" confuse kids from smaller towns.
                </p>
              </div>

              <div className="bg-warm-white border border-border-soft p-8 rounded-2xl space-y-4 shadow-card">
                <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center text-green-500 font-display font-bold text-lg">
                  ✓
                </div>
                <h3 className="text-xl font-bold text-earth-brown font-display">Our Solution</h3>
                <p className="text-xs sm:text-sm text-soft-brown leading-relaxed font-sans">
                  We model educational and vocational tracks as <strong className="text-honey-amber-dark">living trees</strong>. Each node is fully transparent. A student in a village can immediately know what exams to take, what textbook to read, and verify the direct application URL without paywalls.
                </p>
              </div>
            </div>

            {/* Value/Tech Stack Highlight Cards */}
            <div className="bg-warm-white border border-border-soft rounded-2xl p-8 space-y-6 shadow-card">
              <h3 className="text-xl font-bold text-earth-brown text-center font-display">Values and Technical Stack</h3>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-center font-sans">
                <div className="p-4 bg-cream/30 rounded-xl border border-border-soft">
                  <span className="text-[10px] font-bold text-soft-brown block uppercase">Open Source</span>
                  <span className="text-sm font-extrabold text-earth-brown font-display">100% Democratic</span>
                </div>
                <div className="p-4 bg-cream/30 rounded-xl border border-border-soft">
                  <span className="text-[10px] font-bold text-soft-brown block uppercase">Core Engine</span>
                  <span className="text-sm font-extrabold text-earth-brown font-display">HTML5 / React JS</span>
                </div>
                <div className="p-4 bg-cream/30 rounded-xl border border-border-soft">
                  <span className="text-[10px] font-bold text-soft-brown block uppercase">Interface CSS</span>
                  <span className="text-sm font-extrabold text-earth-brown font-display">Tailwind v4</span>
                </div>
                <div className="p-4 bg-cream/30 rounded-xl border border-border-soft">
                  <span className="text-[10px] font-bold text-soft-brown block uppercase">Design Theme</span>
                  <span className="text-sm font-extrabold text-earth-brown font-display">Apple Education</span>
                </div>
              </div>
            </div>

            {/* Ecosystem connected brands */}
            <div className="border border-border-soft rounded-2xl p-8 bg-honey-amber/10 space-y-6">
              <div className="text-center space-y-1">
                <span className="text-xs font-bold text-honey-amber-dark uppercase tracking-wider block font-sans">
                  Crevr Brand Capital Unity
                </span>
                <h4 className="text-xl font-bold text-earth-brown font-display">Our Connected Tech Family</h4>
                <p className="text-xs text-soft-brown leading-relaxed max-w-xl mx-auto font-sans">
                  CrevrTree operates side-by-side with our premium tools and technology entities:
                </p>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 font-sans">
                <div className="bg-warm-white p-4 rounded-xl text-center border border-border-soft shadow-sm">
                  <span className="font-extrabold font-display text-sm text-earth-brown block">HexAtom</span>
                  <span className="text-[9px] text-soft-brown block uppercase mt-1">Core Tech & Software</span>
                </div>
                <div className="bg-warm-white p-4 rounded-xl text-center border border-border-soft shadow-sm">
                  <span className="font-extrabold font-display text-sm text-earth-brown block">Aronar AI</span>
                  <span className="text-[9px] text-soft-brown block uppercase mt-1">Future Agent Models</span>
                </div>
                <div className="bg-warm-white p-4 rounded-xl text-center border border-border-soft shadow-sm">
                  <span className="font-extrabold font-display text-sm text-earth-brown block">Wear Tome</span>
                  <span className="text-[9px] text-soft-brown block uppercase mt-1">D2C Fashion Brand</span>
                </div>
                <div className="bg-warm-white p-4 rounded-xl text-center border border-border-soft shadow-sm">
                  <span className="font-extrabold font-display text-sm text-earth-brown block">Clever Tool</span>
                  <span className="text-[9px] text-soft-brown block uppercase mt-1">Web Helper Utilities</span>
                </div>
              </div>
            </div>

          </div>
        </main>
      )}

      {/* Dynamic footer element */}
      <Footer onNavigate={handleNavigate} onOpenCategory={handleOpenCategory} />
    </div>
  );
}
