import React, { useEffect, useRef, useState, useMemo, useCallback } from 'react';
import { Roadmap, Step } from '../types';
import { ChevronDown, ChevronRight, Check, Play, ZoomIn, ZoomOut, Maximize2 } from 'lucide-react';

interface TreeCanvasProps {
  roadmap: Roadmap;
  completedNodes: Record<string, boolean>;
  selectedNode: Step | null;
  onSelectNode: (step: Step) => void;
}

interface LayoutResult {
  positions: Record<string, { x: number; y: number }>;
  nodeDepths: Record<string, number>;
  visibleIds: string[];
  childMap: Record<string, string[]>;
  stepMap: Record<string, Step>;
  canvasHeight: number;
  canvasWidth: number;
  edges: Array<{ from: string; to: string }>;
}

const NODE_W = 220;
const NODE_H = 84;
const V_GAP = 56;
const H_GAP = 36;
const PADDING_X = 60;
const PADDING_TOP = 50;

function buildChildMap(steps: Step[]): { childMap: Record<string, string[]>; roots: string[]; stepMap: Record<string, Step> } {
  const childMap: Record<string, string[]> = {};
  const roots: string[] = [];
  const stepMap: Record<string, Step> = {};

  steps.forEach(s => {
    stepMap[s.id] = s;
    if (s.parent) {
      if (!childMap[s.parent]) childMap[s.parent] = [];
      childMap[s.parent].push(s.id);
    } else {
      roots.push(s.id);
    }
  });

  return { childMap, roots, stepMap };
}

function computeLayout(
  steps: Step[],
  collapsedIds: Set<string>,
  availableWidth: number
): LayoutResult {
  const { childMap, roots, stepMap } = buildChildMap(steps);

  const positions: Record<string, { x: number; y: number }> = {};
  const nodeDepths: Record<string, number> = {};
  const visibleIds: string[] = [];
  const edges: Array<{ from: string; to: string }> = [];

  let leafCursor = 0;

  function assign(id: string, depth: number) {
    nodeDepths[id] = depth;
    visibleIds.push(id);

    const isCollapsed = collapsedIds.has(id);
    const kids = isCollapsed ? [] : (childMap[id] || []);

    if (kids.length === 0) {
      positions[id] = {
        x: PADDING_X + leafCursor * (NODE_W + H_GAP) + NODE_W / 2,
        y: PADDING_TOP + depth * (NODE_H + V_GAP)
      };
      leafCursor++;
    } else {
      kids.forEach(kid => {
        edges.push({ from: id, to: kid });
        assign(kid, depth + 1);
      });
      const childXs = kids.map(k => positions[k].x);
      const minCx = Math.min(...childXs);
      const maxCx = Math.max(...childXs);
      positions[id] = {
        x: (minCx + maxCx) / 2,
        y: PADDING_TOP + depth * (NODE_H + V_GAP)
      };
    }
  }

  roots.forEach(r => assign(r, 0));

  const allXs = Object.values(positions).map(p => p.x);
  const treeMinX = Math.min(...allXs);
  const treeMaxX = Math.max(...allXs);
  const treeWidth = treeMaxX - treeMinX;

  const effectiveWidth = Math.max(availableWidth - 48, 400);
  const offsetX = treeWidth < effectiveWidth
    ? (effectiveWidth - treeWidth) / 2 - treeMinX + 24
    : -treeMinX + 24;

  Object.keys(positions).forEach(id => {
    positions[id].x += offsetX;
  });

  const allYs = Object.values(positions).map(p => p.y);
  const canvasHeight = Math.max(...allYs) + NODE_H + PADDING_TOP + 40;
  const canvasWidth = Math.max(
    effectiveWidth,
    treeWidth + PADDING_X * 2
  );

  return { positions, nodeDepths, visibleIds, childMap, stepMap, canvasHeight, canvasWidth, edges };
}

function getDescendantIds(id: string, childMap: Record<string, string[]>): string[] {
  const result: string[] = [];
  const stack = [...(childMap[id] || [])];
  while (stack.length) {
    const cur = stack.pop()!;
    result.push(cur);
    (childMap[cur] || []).forEach(c => stack.push(c));
  }
  return result;
}

function getPathToRoot(id: string, stepMap: Record<string, Step>): Set<string> {
  const path = new Set<string>();
  let cur: string | null = id;
  while (cur) {
    path.add(cur);
    cur = stepMap[cur]?.parent || null;
  }
  return path;
}

const categoryAccents: Record<string, string> = {
  medical: '#E11D48',
  education: '#0D9488',
  government: '#D97706',
  business: '#16A34A',
  finance: '#4F46E5',
  tech: '#0284C7'
};

const categoryBgs: Record<string, string> = {
  medical: 'bg-rose-100',
  education: 'bg-teal-100',
  government: 'bg-amber-100',
  business: 'bg-emerald-100',
  finance: 'bg-indigo-100',
  tech: 'bg-sky-100'
};

const categoryTexts: Record<string, string> = {
  medical: 'text-rose-600',
  education: 'text-teal-600',
  government: 'text-amber-600',
  business: 'text-emerald-600',
  finance: 'text-indigo-600',
  tech: 'text-sky-600'
};

function ConnectorPath({
  fromX, fromY, toX, toY, isCompleted, isCurrent, isOnActivePath
}: {
  fromX: number; fromY: number; toX: number; toY: number;
  isCompleted: boolean; isCurrent: boolean; isOnActivePath: boolean;
}) {
  const startY = fromY + NODE_H;
  const endY = toY;
  const midY = (startY + endY) / 2;

  const d = `M ${fromX} ${startY} C ${fromX} ${midY}, ${toX} ${midY}, ${toX} ${endY}`;

  let stroke = '#CBD5E1';
  let strokeWidth = 2.5;
  let dashArray: string | undefined;
  let opacity = 0.6;

  if (isOnActivePath) {
    stroke = '#0284C7';
    strokeWidth = 4;
    opacity = 1;
  } else if (isCompleted) {
    stroke = '#22C55E';
    strokeWidth = 3.5;
    opacity = 1;
  } else if (isCurrent) {
    stroke = '#F59E0B';
    strokeWidth = 3.5;
    opacity = 1;
  } else {
    dashArray = '6 4';
  }

  return (
    <path
      d={d}
      fill="none"
      stroke={stroke}
      strokeWidth={strokeWidth}
      strokeDasharray={dashArray}
      strokeOpacity={opacity}
      strokeLinecap="round"
      className="transition-all duration-500 ease-in-out"
    />
  );
}

function TreeCard({
  step, index, category, isCompleted, isCurrent, isSelected,
  hasChildren, isCollapsed, onToggleCollapse
}: {
  step: Step;
  index: number;
  category: string;
  isCompleted: boolean;
  isCurrent: boolean;
  isSelected: boolean;
  hasChildren: boolean;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}) {
  const indexLabel = index < 9 ? `0${index + 1}` : `${index + 1}`;
  const accent = categoryAccents[category] || '#0284C7';
  const bgClass = categoryBgs[category] || 'bg-sky-100';
  const textClass = categoryTexts[category] || 'text-sky-600';

  let containerClass = 'border border-slate-200 bg-[#FAF9F5] opacity-80 hover:opacity-100';
  let shadowClass = 'shadow-[2px_2px_0px_0px_#EAE6E1]';
  let badge = null;
  let labelClass = `text-[#6B665F] font-mono`;
  let textColor = 'text-[#2D2D2D]';
  let pulseClass = '';

  if (isCompleted) {
    containerClass = 'border-2 border-[#2D2D2D] bg-[#DCFCE7]';
    shadowClass = 'shadow-[3px_3px_0px_0px_#2D2D2D]';
    labelClass = 'text-emerald-800 font-bold font-mono';
    badge = (
      <div className="absolute -top-2.5 -right-2.5 w-6 h-6 rounded-lg bg-[#4ADE80] flex items-center justify-center text-white border-2 border-[#2D2D2D] shadow-[1px_1px_0px_0px_#2D2D2D] z-30">
        <Check className="w-3.5 h-3.5 stroke-[3]" />
      </div>
    );
  } else if (isCurrent) {
    containerClass = `border-2 border-[#2D2D2D] ${bgClass}`;
    shadowClass = 'shadow-[5px_5px_0px_0px_#2D2D2D]';
    labelClass = `${textClass} uppercase font-mono font-bold`;
    pulseClass = 'pulse-halo-active';
    badge = (
      <div className="absolute -top-2.5 -right-2.5 w-6 h-6 rounded-lg bg-[#FEF08A] flex items-center justify-center text-amber-950 border-2 border-[#2D2D2D] shadow-[1px_1px_0px_0px_#2D2D2D] animate-bounce z-30">
        <Play className="w-3 h-3 fill-current" />
      </div>
    );
  }

  if (isSelected) {
    containerClass += ' ring-4 ring-sky-400/30 scale-[1.04]';
  }

  return (
    <div
      className={`relative rounded-xl transition-all duration-300 cursor-pointer flex flex-col items-center justify-center text-center w-[${NODE_W}px] h-[${NODE_H}px] hover:translate-x-[1px] hover:translate-y-[1px] hover:shadow-[3px_3px_0px_0px_#2D2D2D] ${containerClass} ${shadowClass} ${pulseClass}`}
      style={{ width: NODE_W, height: NODE_H }}
    >
      {badge}

      {hasChildren && (
        <button
          onClick={(e) => { e.stopPropagation(); onToggleCollapse(); }}
          className="absolute -bottom-3 left-1/2 -translate-x-1/2 w-6 h-6 rounded-full bg-[#FAF9F5] border-2 border-[#2D2D2D] shadow-[1px_1px_0px_0px_#2D2D2D] flex items-center justify-center z-30 hover:bg-[#FEF08A] transition-all hover:scale-110"
          title={isCollapsed ? 'Expand children' : 'Collapse children'}
        >
          {isCollapsed
            ? <ChevronRight className="w-3 h-3 text-[#2D2D2D] stroke-[3]" />
            : <ChevronDown className="w-3 h-3 text-[#2D2D2D] stroke-[3]" />
          }
        </button>
      )}

      <span className={`text-[9px] uppercase tracking-wider block px-3 ${labelClass}`}>
        Milestone {indexLabel}
      </span>
      <h4 className={`font-display font-bold ${textColor} text-xs mt-0.5 leading-snug line-clamp-2 px-3`}>
        {step.name}
      </h4>

      {step.sub_topics && step.sub_topics.length > 0 && (
        <div className="absolute -right-2 top-1/2 -translate-y-1/2 translate-x-full ml-1 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
          <div className="bg-[#FAF9F5] border-2 border-[#2D2D2D] rounded-lg p-1.5 shadow-[2px_2px_0px_0px_#2D2D2D] min-w-[100px]">
            <span className="text-[8px] font-black uppercase text-[#6B665F] tracking-wider block mb-1">
              {step.sub_topics_title || 'Key Subjects'}
            </span>
            <div className="flex flex-wrap gap-0.5">
              {step.sub_topics.slice(0, 4).map((sub, i) => (
                <span key={i} className="bg-[#FEF08A] text-[#2D2D2D] border border-[#2D2D2D] px-1 py-px rounded text-[7px] font-bold shadow-[1px_1px_0px_0px_#2D2D2D]">
                  {sub.label}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function TreeCanvas({
  roadmap,
  completedNodes,
  selectedNode,
  onSelectNode,
}: TreeCanvasProps) {
  const [collapsedIds, setCollapsedIds] = useState<Set<string>>(() => new Set());
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const dragRef = useRef({ startX: 0, startY: 0, panX: 0, panY: 0 });
  const canvasRef = useRef<HTMLDivElement>(null);
  const [canvasWidth, setCanvasWidth] = useState(900);
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const check = () => {
      const w = window.innerWidth;
      setIsMobile(w < 1024);
      if (canvasRef.current) setCanvasWidth(canvasRef.current.clientWidth);
    };
    check();
    window.addEventListener('resize', check);
    return () => window.removeEventListener('resize', check);
  }, []);

  const layout = useMemo(
    () => computeLayout(roadmap.steps, collapsedIds, canvasWidth),
    [roadmap.steps, collapsedIds, canvasWidth]
  );

  useEffect(() => {
    if (selectedNode) {
      const pos = layout.positions[selectedNode.id];
      if (pos && canvasRef.current) {
        const rect = canvasRef.current.getBoundingClientRect();
        const targetX = -(pos.x - rect.width / 2) * zoom + 24;
        const targetY = -(pos.y - rect.height / 3) * zoom + 24;
        setPan({ x: targetX, y: targetY });
      }
    }
  }, [selectedNode, layout.positions, zoom]);

  const toggleCollapse = useCallback((nodeId: string) => {
    setCollapsedIds(prev => {
      const next = new Set(prev);
      if (next.has(nodeId)) next.delete(nodeId);
      else {
        next.add(nodeId);
        getDescendantIds(nodeId, layout.childMap).forEach(d => next.delete(d));
      }
      return next;
    });
  }, [layout.childMap]);

  const collapseAll = useCallback(() => {
    const newCollapsed = new Set<string>();
    layout.visibleIds.forEach(id => {
      if ((layout.childMap[id] || []).length > 0) newCollapsed.add(id);
    });
    setCollapsedIds(newCollapsed);
  }, [layout.visibleIds, layout.childMap]);

  const expandAll = useCallback(() => {
    setCollapsedIds(new Set());
  }, []);

  const handleZoomIn = () => setZoom(z => Math.min(z * 1.15, 2.5));
  const handleZoomOut = () => setZoom(z => Math.max(z / 1.15, 0.2));
  const handleResetView = () => { setZoom(1); setPan({ x: 0, y: 0 }); };

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    if ((e.target as HTMLElement).closest('button') || (e.target as HTMLElement).closest('[data-node]')) return;
    setIsDragging(true);
    dragRef.current = { startX: e.clientX, startY: e.clientY, panX: pan.x, panY: pan.y };
  }, [pan]);

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (!isDragging) return;
    const dx = e.clientX - dragRef.current.startX;
    const dy = e.clientY - dragRef.current.startY;
    setPan({ x: dragRef.current.panX + dx, y: dragRef.current.panY + dy });
  }, [isDragging]);

  const handleMouseUp = useCallback(() => setIsDragging(false), []);

  const handleWheel = useCallback((e: React.WheelEvent) => {
    e.preventDefault();
    const factor = e.deltaY > 0 ? 0.92 : 1.08;
    setZoom(z => Math.min(Math.max(z * factor, 0.2), 2.5));
  }, []);

  const activePathIds = selectedNode ? getPathToRoot(selectedNode.id, layout.stepMap) : new Set<string>();

  if (isMobile) {
    return (
      <div
        ref={canvasRef}
        className="bg-white border-2 border-[#2D2D2D] rounded-3xl p-6 relative overflow-hidden shadow-[4px_4px_0px_0px_#2D2D2D]"
        style={{
          background: 'radial-gradient(#EAE6E1 1.5px, transparent 1.5px)',
          backgroundSize: '24px 24px'
        }}
      >
        <div className="relative z-20 space-y-6 flex flex-col items-center w-full">
          {roadmap.steps.map((step, idx) => {
            const isCompleted = !!completedNodes[step.id];
            const isCurrent = !isCompleted && (
              idx === 0 || (step.parent && completedNodes[step.parent])
            );
            const isSel = selectedNode?.id === step.id;
            const hasKids = (layout.childMap[step.id] || []).length > 0;
            const isColl = collapsedIds.has(step.id);

            return (
              <React.Fragment key={step.id}>
                <div
                  data-node
                  onClick={() => onSelectNode(step)}
                  className={`w-full max-w-sm border p-4 rounded-xl transition-all duration-200 flex items-start space-x-3 cursor-pointer ${
                    isCompleted
                      ? 'border-[#2D2D2D] border-2 bg-[#DCFCE7] shadow-[3px_3px_0px_0px_#2D2D2D]'
                      : isCurrent
                      ? `border-2 border-[#2D2D2D] ${categoryBgs[roadmap.category]} shadow-[4px_4px_0px_0px_#2D2D2D] pulse-halo-active`
                      : 'border-[#EAE6E1] bg-white shadow-sm'
                  } ${isSel ? 'ring-4 ring-offset-1 ring-sky-100' : ''}`}
                >
                  <div className="w-8 h-8 rounded-lg border border-[#2D2D2D] flex items-center justify-center flex-shrink-0 bg-white shadow-[1px_1px_0px_0px_#2D2D2D]">
                    {isCompleted ? (
                      <Check className="w-4 h-4 text-emerald-700 stroke-[3]" />
                    ) : isCurrent ? (
                      <Play className="w-3.5 h-3.5 fill-current text-earth-brown" />
                    ) : (
                      <span className="text-xs font-bold text-[#6B665F] font-mono">
                        {idx < 9 ? `0${idx + 1}` : `${idx + 1}`}
                      </span>
                    )}
                  </div>
                  <div className="space-y-1 flex-grow">
                    <span className="text-[9px] uppercase font-bold tracking-widest text-[#6B665F] block">
                      Milestone {idx < 9 ? `0${idx + 1}` : `${idx + 1}`}
                    </span>
                    <h4 className="font-display font-bold text-[#2D2D2D] text-sm leading-snug">
                      {step.name}
                    </h4>
                    <p className="text-[11px] text-[#6B665F] line-clamp-2 leading-relaxed">
                      {step.desc}
                    </p>
                  </div>
                  {hasKids && (
                    <button
                      onClick={(e) => { e.stopPropagation(); toggleCollapse(step.id); }}
                      className="flex-shrink-0 w-7 h-7 rounded-full border-2 border-[#2D2D2D] bg-[#FAF9F5] flex items-center justify-center shadow-[1px_1px_0px_0px_#2D2D2D] hover:bg-[#FEF08A] transition-all"
                    >
                      {isColl
                        ? <ChevronRight className="w-3 h-3 stroke-[3]" />
                        : <ChevronDown className="w-3 h-3 stroke-[3]" />
                      }
                    </button>
                  )}
                </div>

                {idx < roadmap.steps.length - 1 && !isColl && (
                  <div className="w-1.5 h-8 bg-[#2D2D2D] my-1 rounded-full" />
                )}
              </React.Fragment>
            );
          })}
        </div>
      </div>
    );
  }

  return (
    <div
      ref={canvasRef}
      className="bg-white border-2 border-[#2D2D2D] rounded-3xl relative overflow-hidden shadow-[4px_4px_0px_0px_#2D2D2D]"
      style={{
        background: 'radial-gradient(#EAE6E1 1.5px, transparent 1.5px)',
        backgroundSize: '24px 24px',
        cursor: isDragging ? 'grabbing' : 'default',
        minHeight: 480
      }}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
      onWheel={handleWheel}
    >
      {/* Controls */}
      <div className="absolute top-4 right-4 z-50 flex flex-col gap-1.5">
        <button
          onClick={handleZoomIn}
          className="w-8 h-8 rounded-lg bg-[#FAF9F5] border-2 border-[#2D2D2D] shadow-[2px_2px_0px_0px_#2D2D2D] flex items-center justify-center hover:bg-[#FEF08A] transition-all hover:translate-x-[1px] hover:translate-y-[1px] hover:shadow-[1px_1px_0px_0px_#2D2D2D]"
          title="Zoom in"
        >
          <ZoomIn className="w-3.5 h-3.5 text-[#2D2D2D]" />
        </button>
        <button
          onClick={handleZoomOut}
          className="w-8 h-8 rounded-lg bg-[#FAF9F5] border-2 border-[#2D2D2D] shadow-[2px_2px_0px_0px_#2D2D2D] flex items-center justify-center hover:bg-[#FEF08A] transition-all hover:translate-x-[1px] hover:translate-y-[1px] hover:shadow-[1px_1px_0px_0px_#2D2D2D]"
          title="Zoom out"
        >
          <ZoomOut className="w-3.5 h-3.5 text-[#2D2D2D]" />
        </button>
        <button
          onClick={handleResetView}
          className="w-8 h-8 rounded-lg bg-[#FAF9F5] border-2 border-[#2D2D2D] shadow-[2px_2px_0px_0px_#2D2D2D] flex items-center justify-center hover:bg-[#FEF08A] transition-all hover:translate-x-[1px] hover:translate-y-[1px] hover:shadow-[1px_1px_0px_0px_#2D2D2D]"
          title="Reset view"
        >
          <Maximize2 className="w-3.5 h-3.5 text-[#2D2D2D]" />
        </button>
        <div className="w-8 h-px bg-[#2D2D2D] my-0.5" />
        <button
          onClick={expandAll}
          className="w-8 h-8 rounded-lg bg-[#FAF9F5] border-2 border-[#2D2D2D] shadow-[2px_2px_0px_0px_#2D2D2D] flex items-center justify-center hover:bg-[#DCFCE7] transition-all hover:translate-x-[1px] hover:translate-y-[1px] hover:shadow-[1px_1px_0px_0px_#2D2D2D]"
          title="Expand all"
        >
          <ChevronDown className="w-3.5 h-3.5 text-[#2D2D2D] stroke-[3]" />
        </button>
        <button
          onClick={collapseAll}
          className="w-8 h-8 rounded-lg bg-[#FAF9F5] border-2 border-[#2D2D2D] shadow-[2px_2px_0px_0px_#2D2D2D] flex items-center justify-center hover:bg-[#FEF08A] transition-all hover:translate-x-[1px] hover:translate-y-[1px] hover:shadow-[1px_1px_0px_0px_#2D2D2D]"
          title="Collapse all"
        >
          <ChevronRight className="w-3.5 h-3.5 text-[#2D2D2D] stroke-[3]" />
        </button>
      </div>

      {/* Zoom indicator */}
      <div className="absolute bottom-4 left-4 z-50 bg-[#FAF9F5] border-2 border-[#2D2D2D] rounded-lg px-2.5 py-1 shadow-[2px_2px_0px_0px_#2D2D2D] font-mono text-[10px] font-bold text-[#6B665F]">
        {Math.round(zoom * 100)}%
      </div>

      {/* Transform container */}
      <div
        className="relative"
        style={{
          width: layout.canvasWidth,
          height: layout.canvasHeight,
          transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
          transformOrigin: 'top left',
          transition: isDragging ? 'none' : 'transform 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94)',
          willChange: 'transform'
        }}
      >
        {/* SVG connectors layer */}
        <svg
          className="absolute inset-0 pointer-events-none z-10"
          style={{ width: layout.canvasWidth, height: layout.canvasHeight }}
        >
          <defs>
            <filter id="glow-active">
              <feGaussianBlur stdDeviation="3" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          {layout.edges.map(({ from, to }) => {
            const fromPos = layout.positions[from];
            const toPos = layout.positions[to];
            if (!fromPos || !toPos) return null;

            const fromStep = layout.stepMap[from];
            const toStep = layout.stepMap[to];
            const fromCompleted = !!completedNodes[from];
            const toCompleted = !!completedNodes[to];
            const bothCompleted = fromCompleted && toCompleted;
            const eitherCurrent = (!fromCompleted && fromStep?.parent && completedNodes[fromStep.parent]) ||
              (!toCompleted && toStep?.parent && completedNodes[toStep.parent]);
            const onActivePath = activePathIds.has(from) && activePathIds.has(to);

            return (
              <g key={`${from}-${to}`}>
                <ConnectorPath
                  fromX={fromPos.x}
                  fromY={fromPos.y}
                  toX={toPos.x}
                  toY={toPos.y}
                  isCompleted={bothCompleted}
                  isCurrent={!!eitherCurrent}
                  isOnActivePath={onActivePath}
                />
              </g>
            );
          })}
        </svg>

        {/* Nodes layer */}
        {layout.visibleIds.map((id, displayIdx) => {
          const step = layout.stepMap[id];
          const pos = layout.positions[id];
          if (!step || !pos) return null;

          const nodeIndex = roadmap.steps.findIndex(s => s.id === id);
          const isCompleted = !!completedNodes[id];
          const isCurrent = !isCompleted && (
            nodeIndex === 0 || (step.parent && completedNodes[step.parent])
          );
          const isSelected = selectedNode?.id === id;
          const hasKids = (layout.childMap[id] || []).length > 0;
          const isColl = collapsedIds.has(id);

          return (
            <div
              key={id}
              data-node
              className="absolute z-20 group"
              style={{
                left: pos.x - NODE_W / 2,
                top: pos.y,
                transition: 'left 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94), top 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94)',
                willChange: 'left, top'
              }}
              onClick={() => onSelectNode(step)}
            >
              <TreeCard
                step={step}
                index={nodeIndex >= 0 ? nodeIndex : displayIdx}
                category={roadmap.category}
                isCompleted={isCompleted}
                isCurrent={isCurrent}
                isSelected={isSelected}
                hasChildren={hasKids}
                isCollapsed={isColl}
                onToggleCollapse={() => toggleCollapse(id)}
              />
            </div>
          );
        })}
      </div>
    </div>
  );
}
