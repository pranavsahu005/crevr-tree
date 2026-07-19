import React, { useState, useEffect, useRef, useMemo } from 'react';
import { Roadmap, Step } from '../types';
import { Check, Play } from 'lucide-react';

interface TreeCanvasProps {
  roadmap: Roadmap;
  completedNodes: Record<string, boolean>;
  selectedNode: Step | null;
  onSelectNode: (step: Step) => void;
}

const categoryAccents: Record<string, string> = {
  medical: '#FF6B81',
  education: '#4ECDC4',
  government: '#FF9F43',
  business: '#43C97E',
  finance: '#6C5CE7',
  tech: '#2EAFFF',
  default: '#6B665F'
};

const categoryBgs: Record<string, string> = {
  medical: 'bg-rose-50 border-rose-200',
  education: 'bg-teal-50 border-teal-200',
  government: 'bg-amber-50 border-amber-200',
  business: 'bg-emerald-50 border-emerald-200',
  finance: 'bg-indigo-50 border-indigo-200',
  tech: 'bg-sky-50 border-sky-200',
  default: 'bg-slate-50 border-slate-200'
};

const categoryTexts: Record<string, string> = {
  medical: 'text-rose-600',
  education: 'text-teal-600',
  government: 'text-amber-600',
  business: 'text-emerald-600',
  finance: 'text-indigo-600',
  tech: 'text-sky-600',
  default: 'text-slate-600'
};

// Custom dynamic parents resolver for merge-diamond connections
function getParentsForStep(step: Step): string[] {
  const parents: string[] = [];
  if (step.parent) {
    parents.push(step.parent);
  }
  const parts = step.id.split('-');
  const level = parseInt(parts[parts.length - 1], 10);
  const prefix = parts.slice(0, -1).join('-');
  if (level === 5) {
    parents.push(`${prefix}-4`);
  } else if (level === 8) {
    parents.push(`${prefix}-7`);
  }
  return parents;
}

export default function TreeCanvas({
  roadmap,
  completedNodes,
  selectedNode,
  onSelectNode,
}: TreeCanvasProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 750 });

  // Find max coordinate Y to scale the steps perfectly inside the canvas
  const { maxCoordY, stepMap } = useMemo(() => {
    const map: Record<string, Step> = {};
    let maxY = 100;
    if (roadmap.steps) {
      roadmap.steps.forEach(s => {
        map[s.id] = s;
        if (s.coords && s.coords.y > maxY) {
          maxY = s.coords.y;
        }
      });
    }
    return { maxCoordY: maxY, stepMap: map };
  }, [roadmap.steps]);

  // Dynamically calculate desktop canvas height based on the maximum Y coordinate
  const desktopCanvasHeight = useMemo(() => {
    return Math.max(600, maxCoordY * 7.0 + 80);
  }, [maxCoordY]);

  // ResizeObserver to dynamically fetch parent width for pixel coordinate scaling
  useEffect(() => {
    if (!containerRef.current) return;
    const observer = new ResizeObserver(entries => {
      for (const entry of entries) {
        setDimensions({
          width: entry.contentRect.width || 800,
          height: desktopCanvasHeight
        });
      }
    });
    observer.observe(containerRef.current);
    return () => observer.disconnect();
  }, [desktopCanvasHeight]);

  // Calculate pixel coordinates for desktop absolute placement
  const getCoordsPx = (step: Step) => {
    const xRaw = step.coords?.x ?? 50;
    const yRaw = step.coords?.y ?? 10;
    const xPx = (xRaw / 100) * dimensions.width;
    // Map Y coordinate directly using a fixed scale factor of 7.0
    const yPx = yRaw * 7.0;
    return { x: xPx, y: yPx };
  };

  return (
    <div className="w-full font-sans">
      {/* Inline styles for the organic hand-drawn line drawing animation */}
      <style>{`
        @keyframes drawLine {
          to {
            stroke-dashoffset: 0;
          }
        }
        .tree-connector-path {
          stroke-dasharray: 1000;
          stroke-dashoffset: 1000;
          animation: drawLine 1.5s ease-out forwards;
        }
        @keyframes pulse-halo {
          0%, 100% { box-shadow: 0 0 0 4px rgba(171, 255, 46, 0.4); }
          50% { box-shadow: 0 0 0 10px rgba(171, 255, 46, 0.8); }
        }
        .pulse-halo-active {
          animation: pulse-halo 2.5s infinite ease-in-out;
        }
      `}</style>

      {/* 1. DESKTOP CANVAS VIEW (lg breakpoint) */}
      <div 
        ref={containerRef}
        className="hidden lg:block relative w-full bg-[#FFFDF8] border-2 border-[#2D2D2D] rounded-3xl overflow-hidden shadow-[4px_4px_0px_0px_#2D2D2D]"
        style={{
          height: desktopCanvasHeight,
          background: 'radial-gradient(#EAE6E1 1.5px, transparent 1.5px)',
          backgroundSize: '24px 24px'
        }}
      >
        {/* SVG Connectors Canvas */}
        <svg className="absolute inset-0 w-full h-full pointer-events-none z-10">
          {roadmap.steps?.map((step) => {
            const parents = getParentsForStep(step);
            return parents.map((parentId) => {
              const parentStep = stepMap[parentId];
              if (!parentStep) return null;

              const start = getCoordsPx(parentStep);
              const end = getCoordsPx(step);

              const controlOffset = (end.y - start.y) / 2.2;
              const pathD = `M ${start.x} ${start.y + 42} C ${start.x} ${start.y + 42 + controlOffset}, ${end.x} ${end.y - 42 - controlOffset}, ${end.x} ${end.y - 42}`;

              return (
                <path
                  key={`${parentId}-${step.id}`}
                  d={pathD}
                  fill="none"
                  stroke="#476E0C" // --leaf-dark
                  strokeWidth="3.5"
                  strokeOpacity="0.7"
                  className="tree-connector-path"
                />
              );
            });
          })}
        </svg>

        {/* Milestone Node Cards */}
        {roadmap.steps?.map((step, idx) => {
          const coords = getCoordsPx(step);
          const isCompleted = !!completedNodes[step.id];
          const isCurrent = !isCompleted && (
            idx === 0 || (step.parent && completedNodes[step.parent])
          );
          const isSelected = selectedNode?.id === step.id;

          const accent = categoryAccents[roadmap.category] || '#2EAFFF';
          const bgClass = categoryBgs[roadmap.category] || 'bg-sky-50';
          const textClass = categoryTexts[roadmap.category] || 'text-sky-600';

          let cardClass = 'border border-slate-200 bg-[#FAF9F5] opacity-85 hover:opacity-100';
          let shadowClass = 'shadow-[2px_2px_0px_0px_#EAE6E1]';
          let pulseClass = '';
          let badge = null;

          if (isCompleted) {
            cardClass = 'border-2 border-[#2D2D2D] bg-[#DCFCE7] opacity-100';
            shadowClass = 'shadow-[3px_3px_0px_0px_#2D2D2D]';
            badge = (
              <div className="absolute -top-2.5 -right-2.5 w-6 h-6 rounded-tl-xl rounded-br-xl rounded-tr-none rounded-bl-none bg-[#4ADE80] flex items-center justify-center text-[#2D2D2D] border-2 border-[#2D2D2D] shadow-[1.5px_1.5px_0px_0px_#2D2D2D] z-30 transform rotate-12">
                <Check className="w-3.5 h-3.5 text-white stroke-[3.5] transform -rotate-12" />
              </div>
            );
          } else if (isCurrent) {
            cardClass = `border-2 border-[#2D2D2D] ${bgClass} opacity-100`;
            shadowClass = 'shadow-[4px_4px_0px_0px_#2D2D2D]';
            pulseClass = 'pulse-halo-active';
            badge = (
              <div className="absolute -top-2 -right-2 w-5 h-5 rounded-lg bg-[#FEF08A] flex items-center justify-center text-[#2D2D2D] border-2 border-[#2D2D2D] shadow-[1px_1px_0px_0px_#2D2D2D] z-30">
                <Play className="w-2.5 h-2.5 fill-current" />
              </div>
            );
          }

          if (isSelected) {
            cardClass += ' ring-4 ring-sky-400/30 scale-[1.03]';
          }

          const leftPx = coords.x - 110;
          const topPx = coords.y - 42;

          return (
            <button
              key={step.id}
              onClick={() => onSelectNode(step)}
              className={`absolute z-20 rounded-2xl flex flex-col items-center justify-center text-center w-[220px] h-[84px] transition-all duration-200 cursor-pointer ${cardClass} ${shadowClass} ${pulseClass}`}
              style={{
                left: leftPx,
                top: topPx
              }}
            >
              {badge}
              <span className={`text-[9px] uppercase tracking-wider block font-mono font-bold ${isCompleted ? 'text-emerald-800' : isCurrent ? textClass : 'text-[#6B665F]'}`}>
                Milestone 0{idx + 1}
              </span>
              <h4 className="font-display font-bold text-[#2D2D2D] text-xs sm:text-[13px] mt-0.5 leading-snug line-clamp-2 px-3">
                {step.name}
              </h4>
            </button>
          );
        })}
      </div>

      {/* 2. MOBILE TIMELINE VIEW (stacked single column) */}
      <div className="lg:hidden flex flex-col items-center space-y-4 w-full px-2">
        {roadmap.steps?.map((step, idx) => {
          const isCompleted = !!completedNodes[step.id];
          const isCurrent = !isCompleted && (
            idx === 0 || (step.parent && completedNodes[step.parent])
          );
          const isSelected = selectedNode?.id === step.id;

          const bgClass = categoryBgs[roadmap.category] || 'bg-sky-50';
          const textClass = categoryTexts[roadmap.category] || 'text-sky-600';

          let cardClass = 'border-2 border-[#EAE6E1] bg-[#FAF9F5] opacity-90';
          let borderIndicatorClass = 'border-[#EAE6E1]';
          let marker = (
            <span className="text-[10px] font-bold text-[#6B665F] font-mono">0{idx + 1}</span>
          );

          if (isCompleted) {
            cardClass = 'border-2 border-[#2D2D2D] bg-[#DCFCE7]';
            borderIndicatorClass = 'border-[#2D2D2D] bg-[#4ADE80] rounded-tl-xl rounded-br-xl rounded-tr-none rounded-bl-none shadow-[1.5px_1.5px_0px_0px_#2D2D2D] transform rotate-12';
            marker = <Check className="w-3.5 h-3.5 text-white stroke-[3.5] transform -rotate-12" />;
          } else if (isCurrent) {
            cardClass = `border-2 border-[#2D2D2D] ${bgClass}`;
            borderIndicatorClass = `border-[#2D2D2D] bg-[#FEF08A] rounded-tl-xl rounded-br-xl rounded-tr-none rounded-bl-none shadow-[1.5px_1.5px_0px_0px_#2D2D2D] pulse-halo-active transform rotate-12`;
            marker = <Play className="w-2.5 h-2.5 text-[#2D2D2D] fill-current transform -rotate-12" />;
          }

          if (isSelected) {
            cardClass += ' ring-2 ring-sky-400/50';
          }

          return (
            <div
              key={step.id}
              onClick={() => onSelectNode(step)}
              className={`w-full max-w-sm rounded-2xl p-4 shadow-card transition-all flex items-start space-x-3 cursor-pointer ${cardClass}`}
            >
              <div className={`w-8 h-8 rounded-full border-2 flex items-center justify-center flex-shrink-0 ${borderIndicatorClass}`}>
                {marker}
              </div>
              <div className="space-y-1 flex-1">
                <h4 className="font-display font-bold text-[#2D2D2D] text-sm leading-snug">
                  {step.name}
                </h4>
                <p className="text-[11px] text-slate-500 line-clamp-2 leading-relaxed">
                  {step.desc}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
