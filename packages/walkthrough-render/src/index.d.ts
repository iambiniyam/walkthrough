export interface Step {
  number: number;
  title?: string;
  body?: string;
  callout?: string;
  image?: string;
}

export interface Guide {
  title?: string;
  summary?: string;
  steps: Step[];
}

export interface RenderOptions {
  imageDir?: string;
}

export function renderMarkdown(guide: Guide, options?: RenderOptions): string;
export function renderHtml(guide: Guide, options?: RenderOptions): string;
