export interface Resource {
  type: 'pdf' | 'video' | 'course' | 'doc';
  label: string;
  url: string;
}

export interface OfficialLink {
  label: string;
  url: string;
}

export interface Step {
  id: string;
  name: string;
  desc: string;
  short_desc?: string;
  official?: OfficialLink;
  gov_website?: OfficialLink;
  documentation?: OfficialLink;
  resources?: Resource[];
  checklist?: string[];
  parent: string | null;
  coords: { x: number; y: number }; // Percentage coords (0-100) for SVG bezier drawing
  salary?: string;
  companies?: string[];
  colleges?: string[];
  scholarships?: string[];
  entranceExams?: string[];
  sub_topics?: Array<{ label: string }>;
  sub_topics_title?: string;
  difficulty?: number;
  duration?: number;
  prerequisites?: string[];
  skills_required?: string[];
  skills_gained?: string[];
  recommended_certifications?: string[];
  future_opportunities?: Array<{ id: string; title: string; type: string }>;
  related_careers?: Array<{ id: string; title: string }>;
}

export interface Roadmap {
  id: string;
  name: string;
  category: 'medical' | 'education' | 'government' | 'business' | 'finance' | 'tech';
  tagline: string;
  steps: Step[];
}
