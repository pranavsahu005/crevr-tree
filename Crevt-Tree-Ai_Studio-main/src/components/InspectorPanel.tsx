import { useState, useEffect } from 'react';
import { Step } from '../types';
import { 
  Compass, 
  Link2, 
  ExternalLink, 
  FileText, 
  PlayCircle, 
  GraduationCap, 
  Check, 
  DollarSign, 
  Building2, 
  School, 
  Award, 
  BookOpen,
  FileCode,
  ChevronRight,
  Clock,
  Star,
  Lock,
  Compass as CompassIcon
} from 'lucide-react';

interface InspectorPanelProps {
  step: Step | null;
  completedNodes: Record<string, boolean>;
  onToggleCompletion: (stepId: string) => void;
  onExplorePath?: (nodeId: string) => void;
}

type TabType = 'official' | 'resources' | 'checklist' | 'metadata';

export default function InspectorPanel({
  step,
  completedNodes,
  onToggleCompletion,
  onExplorePath,
}: InspectorPanelProps) {
  const [activeTab, setActiveTab] = useState<TabType>('official');

  // Reset tab when active step changes
  useEffect(() => {
    setActiveTab('official');
  }, [step]);

  if (!step) {
    return (
      <div 
        id="tree-inspector-empty" 
        className="bg-white border-2 border-[#2D2D2D] rounded-3xl p-6 shadow-[4px_4px_0px_0px_#2D2D2D] text-center py-16 space-y-4 font-sans"
      >
        <div className="w-16 h-16 rounded-full bg-sky-100 border-2 border-[#2D2D2D] mx-auto flex items-center justify-center text-sky-800 shadow-[2px_2px_0px_0px_#2D2D2D]">
          <Compass className="w-8 h-8 animate-spin-slow" />
        </div>
        <h4 className="font-display font-bold text-[#2D2D2D] text-lg">Interactive Inspector</h4>
        <p className="text-xs text-[#6B665F] leading-relaxed max-w-xs mx-auto">
          Click any milestone node or related concept card in the roadmap to load official websites, syllabus checklists, and learning material.
        </p>
      </div>
    );
  }

  const isCompleted = !!completedNodes[step.id];

  // Helper to render stars for difficulty
  const renderDifficultyStars = (difficulty: number) => {
    const stars = [];
    for (let i = 1; i <= 5; i++) {
      stars.push(
        <Star 
          key={i} 
          className={`w-3.5 h-3.5 ${i <= difficulty ? 'fill-amber-400 text-amber-500' : 'text-slate-300'}`} 
        />
      );
    }
    return <div className="flex space-x-1">{stars}</div>;
  };

  return (
    <div 
      id="tree-inspector-panel" 
      className="space-y-6 transition-all duration-300 font-sans"
    >
      {/* Header Info */}
      <div className="pb-4">
        <h3 className="text-xl sm:text-2xl font-extrabold text-[#2D2D2D] font-display leading-tight">
          {step.name}
        </h3>
        <p className="text-xs text-[#6B665F] mt-2 leading-relaxed font-sans font-medium">
          {step.desc}
        </p>
      </div>

      {/* iOS-Style Segmented Tab Selectors */}
      <div className="bg-[#FAF9F5] p-1 rounded-xl flex justify-between space-x-1 border-2 border-[#2D2D2D] shadow-[2px_2px_0px_0px_#2D2D2D]">
        <button 
          onClick={() => setActiveTab('official')} 
          className={`flex-1 text-center py-2 px-1 rounded-lg font-extrabold transition-all text-[11px] cursor-pointer border ${
            activeTab === 'official' 
              ? 'bg-[#FFC020] text-[#2D2D2D] border-[#2D2D2D]' 
              : 'text-slate-600 hover:text-slate-900 border-transparent hover:bg-slate-100'
          }`}
        >
          Official
        </button>
        <button 
          onClick={() => setActiveTab('resources')} 
          className={`flex-1 text-center py-2 px-1 rounded-lg font-extrabold transition-all text-[11px] cursor-pointer border ${
            activeTab === 'resources' 
              ? 'bg-[#FFC020] text-[#2D2D2D] border-[#2D2D2D]' 
              : 'text-slate-600 hover:text-slate-900 border-transparent hover:bg-slate-100'
          }`}
        >
          Resources
        </button>
        <button 
          onClick={() => setActiveTab('checklist')} 
          className={`flex-1 text-center py-2 px-1 rounded-lg font-extrabold transition-all text-[11px] cursor-pointer border ${
            activeTab === 'checklist' 
              ? 'bg-[#FFC020] text-[#2D2D2D] border-[#2D2D2D]' 
              : 'text-slate-600 hover:text-slate-900 border-transparent hover:bg-slate-100'
          }`}
        >
          Checklist
        </button>
        <button 
          onClick={() => setActiveTab('metadata')} 
          className={`flex-1 text-center py-2 px-1 rounded-lg font-extrabold transition-all text-[11px] cursor-pointer border ${
            activeTab === 'metadata' 
              ? 'bg-[#FFC020] text-[#2D2D2D] border-[#2D2D2D]' 
              : 'text-slate-600 hover:text-slate-900 border-transparent hover:bg-slate-100'
          }`}
        >
          Metrics
        </button>
      </div>

      {/* Tab Panels */}
      <div className="min-h-[160px] text-xs">
        {activeTab === 'official' && (
          <div className="space-y-3 animation-fade-in">
            <p className="text-[11px] text-[#6B665F] italic leading-normal">
              Verified statutory channels, registration hubs, and documentation portals:
            </p>
            <div className="space-y-2">
              {step.official && (
                <a 
                  href={step.official.url} 
                  target="_blank" 
                  rel="noreferrer"
                  className="flex items-center justify-between p-3 bg-slate-50 border-2 border-[#2D2D2D] hover:bg-[#E0F2FE] rounded-xl text-xs text-[#2D2D2D] transition-all shadow-[2px_2px_0px_0px_#2D2D2D] hover:shadow-[1px_1px_0px_0px_#2D2D2D]"
                >
                  <div className="flex items-center space-x-2">
                    <Link2 className="w-4 h-4 text-[#6B665F]" />
                    <span className="font-bold">{step.official.label}</span>
                  </div>
                  <ExternalLink className="w-3.5 h-3.5 text-[#6B665F]" />
                </a>
              )}

              {step.gov_website && (
                <a 
                  href={step.gov_website.url} 
                  target="_blank" 
                  rel="noreferrer"
                  className="flex items-center justify-between p-3 bg-slate-50 border-2 border-[#2D2D2D] hover:bg-[#E0F2FE] rounded-xl text-xs text-[#2D2D2D] transition-all shadow-[2px_2px_0px_0px_#2D2D2D] hover:shadow-[1px_1px_0px_0px_#2D2D2D]"
                >
                  <div className="flex items-center space-x-2">
                    <School className="w-4 h-4 text-[#6B665F]" />
                    <span className="font-bold">{step.gov_website.label}</span>
                  </div>
                  <ExternalLink className="w-3.5 h-3.5 text-[#6B665F]" />
                </a>
              )}

              {step.documentation && (
                <a 
                  href={step.documentation.url} 
                  target="_blank" 
                  rel="noreferrer"
                  className="flex items-center justify-between p-3 bg-slate-50 border-2 border-[#2D2D2D] hover:bg-[#E0F2FE] rounded-xl text-xs text-[#2D2D2D] transition-all shadow-[2px_2px_0px_0px_#2D2D2D] hover:shadow-[1px_1px_0px_0px_#2D2D2D]"
                >
                  <div className="flex items-center space-x-2">
                    <FileCode className="w-4 h-4 text-[#6B665F]" />
                    <span className="font-bold">{step.documentation.label}</span>
                  </div>
                  <ExternalLink className="w-3.5 h-3.5 text-[#6B665F]" />
                </a>
              )}

              {!step.official && !step.gov_website && !step.documentation && (
                <p className="text-xs text-[#6B665F] font-sans">No official websites recorded for this step.</p>
              )}
            </div>
          </div>
        )}

        {activeTab === 'resources' && (
          <div className="space-y-3 animation-fade-in">
            <p className="text-[11px] text-[#6B665F] italic leading-normal">
              Curated textbook PDFs, YouTube tutorials, and course lectures:
            </p>
            {step.resources && step.resources.length > 0 ? (
              <div className="space-y-2">
                {step.resources.map((res, i) => {
                  let Icon = FileText;
                  if (res.type === 'video') Icon = PlayCircle;
                  if (res.type === 'course') Icon = GraduationCap;
                  if (res.type === 'pdf') Icon = BookOpen;

                  return (
                    <a 
                      key={i}
                      href={res.url} 
                      target="_blank" 
                      rel="noreferrer"
                      className="flex items-center justify-between p-3 bg-slate-50 border-2 border-[#2D2D2D] hover:bg-[#E0F2FE] rounded-xl text-xs text-[#2D2D2D] transition-all shadow-[2px_2px_0px_0px_#2D2D2D] hover:shadow-[1px_1px_0px_0px_#2D2D2D] group"
                    >
                      <div className="flex items-center space-x-2">
                        <Icon className="w-4 h-4 text-[#6B665F]" />
                        <span className="font-bold">{res.label}</span>
                      </div>
                      <ExternalLink className="w-3.5 h-3.5 text-[#6B665F]" />
                    </a>
                  );
                })}
              </div>
            ) : (
              <p className="text-xs text-[#6B665F]">No learning reference materials listed yet.</p>
            )}
          </div>
        )}

        {activeTab === 'checklist' && (
          <div className="space-y-4 animation-fade-in">
            {/* Prerequisites */}
            {step.prerequisites && step.prerequisites.length > 0 && (
              <div className="space-y-1.5">
                <span className="text-[10px] font-black uppercase text-rose-700 block flex items-center space-x-1">
                  <Lock className="w-3 h-3" />
                  <span>Academic Prerequisites</span>
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {step.prerequisites.map((p, i) => (
                    <span key={i} className="px-2 py-0.5 border border-rose-300 text-rose-900 bg-rose-50 rounded font-bold text-[10px]">
                      {p}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Checklist */}
            <div className="space-y-1.5">
              <span className="text-[10px] font-black uppercase text-slate-700 block">Syllabus Checkpoint Checklist</span>
              {step.checklist && step.checklist.length > 0 ? (
                <div className="space-y-1.5 text-xs text-[#2D2D2D]">
                  {step.checklist.map((item, i) => (
                    <label 
                      key={i} 
                      className="flex items-start space-x-2 p-1.5 cursor-pointer select-none hover:bg-slate-50 rounded-lg border border-transparent hover:border-[#2D2D2D]"
                    >
                      <input 
                        type="checkbox" 
                        className="rounded border-[#2D2D2D] border-2 text-sky-600 focus:ring-sky-500 mt-0.5 cursor-pointer" 
                      />
                      <span className="text-xs font-semibold leading-normal text-slate-700">
                        {item}
                      </span>
                    </label>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-[#6B665F]">No checklist checkpoints recorded.</p>
              )}
            </div>

            {/* Gained Skills */}
            {step.skills_gained && step.skills_gained.length > 0 && (
              <div className="space-y-1.5 border-t border-slate-200 pt-3">
                <span className="text-[10px] font-black uppercase text-emerald-700 block">Gained Capabilities</span>
                <div className="flex flex-wrap gap-1.5">
                  {step.skills_gained.map((s, i) => (
                    <span key={i} className="px-2 py-0.5 border border-emerald-300 text-emerald-950 bg-emerald-50 rounded font-bold text-[10px]">
                      {s}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'metadata' && (
          <div className="space-y-4 animation-fade-in">
            {/* Core difficulty and duration tags */}
            <div className="grid grid-cols-2 gap-3 pb-3 border-b border-slate-200">
              <div className="p-3 bg-slate-50 border-2 border-[#2D2D2D] rounded-xl flex flex-col justify-center space-y-1 shadow-[2px_2px_0px_0px_#2D2D2D]">
                <span className="text-[9px] uppercase font-bold text-[#6B665F] tracking-wider block flex items-center space-x-1">
                  <Star className="w-3 h-3 text-[#6B665F]" />
                  <span>Difficulty Level</span>
                </span>
                {renderDifficultyStars(step.difficulty || 2)}
              </div>

              <div className="p-3 bg-slate-50 border-2 border-[#2D2D2D] rounded-xl flex flex-col justify-center space-y-1 shadow-[2px_2px_0px_0px_#2D2D2D]">
                <span className="text-[9px] uppercase font-bold text-[#6B665F] tracking-wider block flex items-center space-x-1">
                  <Clock className="w-3 h-3 text-[#6B665F]" />
                  <span>Estimated Duration</span>
                </span>
                <span className="text-xs font-black text-slate-800">{step.duration ? `${step.duration} Months` : 'Variable'}</span>
              </div>
            </div>
            
            <div className="space-y-2.5">
              {step.salary && (
                <div className="p-3 bg-slate-50 border-2 border-[#2D2D2D] rounded-xl text-xs flex items-start space-x-2 shadow-[2px_2px_0px_0px_#2D2D2D]">
                  <DollarSign className="w-4 h-4 text-[#6B665F] flex-shrink-0 mt-0.5" />
                  <div>
                    <span className="font-bold text-[#2D2D2D] block">Estimated Salary Band</span>
                    <span className="text-[#6B665F] text-[11px] font-semibold">{step.salary}</span>
                  </div>
                </div>
              )}

              {step.colleges && step.colleges.length > 0 && (
                <div className="p-3 bg-slate-50 border-2 border-[#2D2D2D] rounded-xl text-xs flex items-start space-x-2 shadow-[2px_2px_0px_0px_#2D2D2D]">
                  <School className="w-4 h-4 text-[#6B665F] flex-shrink-0 mt-0.5" />
                  <div>
                    <span className="font-bold text-[#2D2D2D] block">Top Hubs & Colleges</span>
                    <span className="text-[#6B665F] text-[11px] font-semibold">{step.colleges.join(', ')}</span>
                  </div>
                </div>
              )}

              {step.entranceExams && step.entranceExams.length > 0 && (
                <div className="p-3 bg-slate-50 border-2 border-[#2D2D2D] rounded-xl text-xs flex items-start space-x-2 shadow-[2px_2px_0px_0px_#2D2D2D]">
                  <Award className="w-4 h-4 text-[#6B665F] flex-shrink-0 mt-0.5" />
                  <div>
                    <span className="font-bold text-[#2D2D2D] block">Associated Entrance Exams</span>
                    <span className="text-[#6B665F] text-[11px] font-semibold">{step.entranceExams.join(', ')}</span>
                  </div>
                </div>
              )}

              {step.companies && step.companies.length > 0 && (
                <div className="p-3 bg-slate-50 border-2 border-[#2D2D2D] rounded-xl text-xs flex items-start space-x-2 shadow-[2px_2px_0px_0px_#2D2D2D]">
                  <Building2 className="w-4 h-4 text-[#6B665F] flex-shrink-0 mt-0.5" />
                  <div>
                    <span className="font-bold text-[#2D2D2D] block">Target Employers</span>
                    <span className="text-[#6B665F] text-[11px] font-semibold">{step.companies.join(', ')}</span>
                  </div>
                </div>
              )}

              {/* Related Careers */}
              {step.related_careers && step.related_careers.length > 0 && (
                <div className="p-3 bg-slate-50 border-2 border-[#2D2D2D] rounded-xl text-xs space-y-1.5 shadow-[2px_2px_0px_0px_#2D2D2D]">
                  <span className="font-bold text-[#2D2D2D] block">Alternative / Related Careers</span>
                  <div className="flex flex-wrap gap-1.5">
                    {step.related_careers.map((career) => (
                      <button 
                        key={career.id}
                        onClick={() => onExplorePath && onExplorePath(career.id)}
                        className="px-2 py-1 bg-white border border-[#2D2D2D] rounded hover:bg-amber-100 text-[10px] font-bold text-slate-800 cursor-pointer shadow-[1px_1px_0px_0px_#2D2D2D] transition-all"
                      >
                        {career.title}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Future Opportunities */}
              {step.future_opportunities && step.future_opportunities.length > 0 && (
                <div className="p-3 bg-slate-50 border-2 border-[#2D2D2D] rounded-xl text-xs space-y-1.5 shadow-[2px_2px_0px_0px_#2D2D2D]">
                  <span className="font-bold text-[#2D2D2D] block">Future Career Paths & Opportunities</span>
                  <div className="flex flex-wrap gap-1.5">
                    {step.future_opportunities.map((role) => (
                      <button 
                        key={role.id}
                        onClick={() => onExplorePath && onExplorePath(role.id)}
                        className="px-2 py-1 bg-[#E0F2FE] border border-[#2D2D2D] rounded hover:bg-sky-200 text-[10px] font-bold text-sky-950 cursor-pointer shadow-[1px_1px_0px_0px_#2D2D2D] transition-all"
                      >
                        {role.title}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Explore Branches Action Trigger */}
              {onExplorePath && (
                <button 
                  onClick={() => onExplorePath(step.id)}
                  className="w-full mt-4 py-2.5 bg-sky-600 hover:bg-sky-700 text-white font-extrabold text-xs rounded-xl border-2 border-[#2D2D2D] shadow-[3px_3px_0px_0px_#2D2D2D] hover:shadow-[1px_1px_0px_0px_#2D2D2D] hover:translate-x-[1px] hover:translate-y-[1px] transition-all cursor-pointer flex items-center justify-center space-x-1.5"
                >
                  <CompassIcon className="w-4 h-4 animate-spin-slow" />
                  <span>Explore Future Path from Here →</span>
                </button>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Toggle completion control */}
      <div className="pt-4 border-t-2 border-[#EAE6E1] flex items-center justify-between">
        <div>
          <span className="text-[9px] font-bold text-[#6B665F] block uppercase font-mono">
            Mark Milestone
          </span>
          <span className="text-xs font-semibold text-[#2D2D2D] block">
            Have you completed this?
          </span>
        </div>
        <button 
          onClick={() => onToggleCompletion(step.id)} 
          className={`px-4 py-2.5 font-bold text-xs rounded-xl transition-all flex items-center space-x-1 border-2 border-[#2D2D2D] cursor-pointer ${
            isCompleted 
              ? 'bg-[#4ADE80] hover:bg-[#22C55E] text-white shadow-[2px_2px_0px_0px_#2D2D2D] hover:shadow-[1px_1px_0px_0px_#2D2D2D]' 
              : 'bg-[#FEF08A] hover:bg-[#FACC15] text-[#2D2D2D] shadow-[3px_3px_0px_0px_#2D2D2D] hover:shadow-[1px_1px_0px_0px_#2D2D2D]'
          }`}
        >
          <Check className="w-3.5 h-3.5 stroke-[3]" />
          <span>{isCompleted ? 'Completed (Clear)' : 'Mark Completed'}</span>
        </button>
      </div>
    </div>
  );
}
