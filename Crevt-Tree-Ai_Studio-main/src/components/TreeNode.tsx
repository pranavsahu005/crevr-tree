import React from 'react';
import { Step } from '../types';
import { Play, Check, Shield } from 'lucide-react';

interface TreeNodeProps {
  key?: string;
  step: Step;
  index: number;
  isCompleted: boolean;
  isCurrent: boolean;
  isMobile: boolean;
  category: 'medical' | 'education' | 'government' | 'business' | 'finance' | 'tech';
  isSelected: boolean;
  onClick: () => void;
}

export default function TreeNode({
  step,
  index,
  isCompleted,
  isCurrent,
  isMobile,
  category,
  isSelected,
  onClick,
}: TreeNodeProps) {
  const indexLabel = index < 9 ? `0${index + 1}` : `${index + 1}`;

  // Select neubrutalist theme colors based on category
  const getCategoryStyle = () => {
    switch (category) {
      case 'medical':
        return {
          bgActive: 'bg-rose-100 text-rose-950',
          bgCompleted: 'bg-[#DCFCE7] text-emerald-950', // Completed stays consistently positive green
          textActive: 'text-rose-600 font-bold',
          borderActive: 'border-[#2D2D2D]',
          accent: '#E11D48',
          badgeColor: 'bg-emerald-500 text-white border-[#2D2D2D]'
        };
      case 'education':
        return {
          bgActive: 'bg-teal-100 text-teal-950',
          bgCompleted: 'bg-[#DCFCE7] text-emerald-950',
          textActive: 'text-teal-600 font-bold',
          borderActive: 'border-[#2D2D2D]',
          accent: '#0D9488',
          badgeColor: 'bg-emerald-500 text-white border-[#2D2D2D]'
        };
      case 'government':
        return {
          bgActive: 'bg-amber-100 text-amber-950',
          bgCompleted: 'bg-[#DCFCE7] text-emerald-950',
          textActive: 'text-amber-600 font-bold',
          borderActive: 'border-[#2D2D2D]',
          accent: '#D97706',
          badgeColor: 'bg-emerald-500 text-white border-[#2D2D2D]'
        };
      case 'business':
        return {
          bgActive: 'bg-emerald-100 text-emerald-950',
          bgCompleted: 'bg-[#DCFCE7] text-emerald-950',
          textActive: 'text-emerald-600 font-bold',
          borderActive: 'border-[#2D2D2D]',
          accent: '#16A34A',
          badgeColor: 'bg-emerald-500 text-white border-[#2D2D2D]'
        };
      case 'finance':
        return {
          bgActive: 'bg-indigo-100 text-indigo-950',
          bgCompleted: 'bg-[#DCFCE7] text-emerald-950',
          textActive: 'text-indigo-600 font-bold',
          borderActive: 'border-[#2D2D2D]',
          accent: '#4F46E5',
          badgeColor: 'bg-emerald-500 text-white border-[#2D2D2D]'
        };
      case 'tech':
      default:
        return {
          bgActive: 'bg-sky-100 text-sky-950',
          bgCompleted: 'bg-[#DCFCE7] text-emerald-950',
          textActive: 'text-sky-600 font-bold',
          borderActive: 'border-[#2D2D2D]',
          accent: '#0284C7',
          badgeColor: 'bg-emerald-500 text-white border-[#2D2D2D]'
        };
    }
  };

  const theme = getCategoryStyle();

  if (isMobile) {
    // Mobile Single Column stacked layout
    let stateIcon = <span className="text-xs font-bold text-[#6B665F] font-mono">{indexLabel}</span>;
    let containerBorder = 'border-[#EAE6E1]';
    let containerBg = 'bg-white';
    let pulseClass = '';
    let shadowClass = 'shadow-sm';

    if (isCompleted) {
      containerBorder = 'border-[#2D2D2D] border-2';
      containerBg = 'bg-[#DCFCE7]';
      stateIcon = <Check className="w-4 h-4 text-emerald-700 stroke-[3]" />;
      shadowClass = 'shadow-[3px_3px_0px_0px_#2D2D2D]';
    } else if (isCurrent) {
      containerBorder = 'border-[#2D2D2D] border-2';
      containerBg = theme.bgActive;
      pulseClass = 'pulse-halo-active';
      stateIcon = <Play className="w-3.5 h-3.5 fill-current text-earth-brown" />;
      shadowClass = 'shadow-[4px_4px_0px_0px_#2D2D2D]';
    }

    if (isSelected) {
      containerBorder = 'border-[#2D2D2D] border-2 ring-4 ring-offset-1 ring-sky-100';
    }

    return (
      <div
        id={`node-el-${step.id}`}
        onClick={onClick}
        className={`w-full max-w-sm border ${containerBorder} ${containerBg} ${pulseClass} ${shadowClass} p-4 rounded-xl hover:scale-[1.01] transition-all duration-200 flex items-start space-x-3 cursor-pointer`}
      >
        <div className={`w-8 h-8 rounded-lg border border-[#2D2D2D] flex items-center justify-center flex-shrink-0 bg-white shadow-[1px_1px_0px_0px_#2D2D2D]`}>
          {stateIcon}
        </div>
        <div className="space-y-1 flex-grow">
          <span className="text-[9px] uppercase font-bold tracking-widest text-[#6B665F] block">
            Milestone {indexLabel}
          </span>
          <h4 className="font-display font-bold text-[#2D2D2D] text-sm leading-snug">
            {step.name}
          </h4>
          <p className="text-[11px] text-[#6B665F] line-clamp-2 leading-relaxed">
            {step.desc}
          </p>
        </div>
      </div>
    );
  }

  // Desktop coordinate mapped layout
  let nodeStyleClass = '';
  let ringStyleClass = '';
  let pulseClass = '';
  let badgeEl = null;
  let textStyleClass = 'text-[#2D2D2D]';
  let categoryLabelClass = 'text-[#6B665F] font-mono';
  let shadowClass = 'shadow-[2px_2px_0px_0px_#EAE6E1]';

  if (isCompleted) {
    nodeStyleClass = 'border-2 border-[#2D2D2D] bg-[#DCFCE7]';
    shadowClass = 'shadow-[3px_3px_0px_0px_#2D2D2D]';
    badgeEl = (
      <div className="absolute -top-2.5 -right-2.5 w-6 h-6 rounded-lg bg-[#4ADE80] flex items-center justify-center text-white border-2 border-[#2D2D2D] shadow-[1px_1px_0px_0px_#2D2D2D]">
        <Check className="w-3.5 h-3.5 stroke-[3]" />
      </div>
    );
    categoryLabelClass = 'text-emerald-800 font-bold font-mono';
  } else if (isCurrent) {
    nodeStyleClass = `border-2 border-[#2D2D2D] ${theme.bgActive}`;
    shadowClass = 'shadow-[5px_5px_0px_0px_#2D2D2D]';
    pulseClass = 'pulse-halo-active';
    categoryLabelClass = `${theme.textActive} uppercase font-mono`;
    badgeEl = (
      <div className="absolute -top-2.5 -right-2.5 w-6 h-6 rounded-lg bg-[#FEF08A] flex items-center justify-center text-amber-950 border-2 border-[#2D2D2D] shadow-[1px_1px_0px_0px_#2D2D2D] animate-bounce">
        <Play className="w-3 h-3 fill-current" />
      </div>
    );
  } else {
    // Locked future states
    nodeStyleClass = 'border border-slate-300 bg-[#FAF9F5] opacity-75 hover:opacity-100';
  }

  if (isSelected) {
    nodeStyleClass += ' ring-4 ring-sky-500/30 scale-105';
  }

  return (
    <button
      id={`node-el-${step.id}`}
      onClick={onClick}
      style={{
        left: `calc(${step.coords.x}% - 110px)`,
        top: `calc(${step.coords.y}% - 42px)`,
      }}
      className={`absolute z-30 border p-4 rounded-xl transition-all duration-200 cursor-pointer flex flex-col items-center justify-center text-center w-[220px] h-[84px] hover:translate-x-[1px] hover:translate-y-[1px] hover:shadow-[3px_3px_0px_0px_#2D2D2D] ${nodeStyleClass} ${ringStyleClass} ${pulseClass} ${shadowClass}`}
    >
      {badgeEl}
      <span className={`text-[9px] uppercase tracking-wider block ${categoryLabelClass}`}>
        Milestone {indexLabel}
      </span>
      <h4 className={`font-display font-bold ${textStyleClass} text-xs sm:text-sm mt-1 leading-snug line-clamp-2`}>
        {step.name}
      </h4>
    </button>
  );
}

