/**
 * Smart scroll utility with container detection and post-layout adjustments
 */

// Detecta o container que realmente rola (window ou ancestor com overflow)
function getScrollRoot(node: Element | null): Element | Document {
  let el: Element | null = node as Element;
  while (el) {
    const style = getComputedStyle(el);
    const canScrollY =
      /(auto|scroll|overlay)/.test(style.overflowY) && el.scrollHeight > el.clientHeight;
    if (canScrollY) return el;
    el = el.parentElement;
  }
  return document.scrollingElement ?? document.documentElement;
}

function getHeaderOffset(headerSelector = '[data-fixed-header]', fallback = 80) {
  const header = document.querySelector(headerSelector) as HTMLElement | null;
  if (!header) return fallback;
  const rect = header.getBoundingClientRect();
  return Math.max(rect.height, fallback);
}

function getViewportHeight(scrollRoot: Element | Document) {
  if (scrollRoot === document.scrollingElement || scrollRoot === document.documentElement) {
    return window.visualViewport?.height ?? window.innerHeight;
  }
  return (scrollRoot as Element).clientHeight;
}

function getScrollTop(scrollRoot: Element | Document) {
  return scrollRoot === document.scrollingElement || scrollRoot === document.documentElement
    ? window.pageYOffset
    : (scrollRoot as Element).scrollTop;
}

function setScrollTop(scrollRoot: Element | Document, top: number, behavior: ScrollBehavior) {
  if (scrollRoot === document.scrollingElement || scrollRoot === document.documentElement) {
    window.scrollTo({ top, behavior });
  } else {
    (scrollRoot as Element).scrollTo({ top, behavior });
  }
}

export type ScrollSmartOpts = {
  headerSelector?: string;
  topGuard?: number;    // padding extra no topo
  bottomGuard?: number; // padding extra no bottom (ex.: botão flutuante)
  behavior?: ScrollBehavior;
  centerIfFits?: boolean;
  maxAdjusts?: number;  // quantas correções pós-layout
};

export function scrollIntoViewSmart(
  target: string | Element,
  opts: ScrollSmartOpts = {}
) {
  const el = typeof target === 'string' ? document.querySelector(target) as Element | null : target;
  if (!el) {
    console.warn('scrollIntoViewSmart: target not found', target);
    return;
  }

  const {
    headerSelector = '[data-fixed-header]',
    topGuard = 12,
    bottomGuard = 24,
    behavior = 'smooth',
    centerIfFits = true,
    maxAdjusts = 4
  } = opts;

  const scrollRoot = getScrollRoot(el);
  const headerOffset = getHeaderOffset(headerSelector, 80);
  const vh = getViewportHeight(scrollRoot);

  // Debug info
  console.log('scrollIntoViewSmart debug:', {
    scrollRoot: scrollRoot === document.documentElement ? 'window' : scrollRoot,
    headerOffset,
    vh,
    element: el
  });

  // Temporariamente desabilita scroll-snap do container, se existir
  let prevSnap = '';
  if (scrollRoot instanceof Element) {
    prevSnap = scrollRoot.style.scrollSnapType;
    scrollRoot.style.scrollSnapType = 'none';
  }

  const doScroll = () => {
    const rect = el.getBoundingClientRect();
    const rootTop =
      scrollRoot === document.scrollingElement || scrollRoot === document.documentElement
        ? 0
        : (scrollRoot as Element).getBoundingClientRect().top;

    const currentTop = getScrollTop(scrollRoot);
    const elTopAbs = rect.top + currentTop - rootTop;
    const elHeight = rect.height;

    const usableVh = vh - headerOffset - topGuard - bottomGuard;

    let targetTop: number;
    if (centerIfFits && elHeight <= usableVh) {
      // centraliza no espaço útil
      const centerOffset = (usableVh - elHeight) / 2;
      targetTop = elTopAbs - headerOffset - topGuard - centerOffset;
    } else {
      // alinha topo abaixo do header
      targetTop = elTopAbs - headerOffset - topGuard;
    }

    setScrollTop(scrollRoot, Math.max(0, targetTop), behavior);
  };

  doScroll();

  // Correções pós-layout: fonts/lazy/accordion
  let attempts = 0;
  const fixLoop = () => {
    attempts++;
    const rect = el.getBoundingClientRect();
    const topClip = rect.top < headerOffset + 4;
    const bottomClip = rect.bottom > (window.visualViewport?.height ?? window.innerHeight) - 4;

    if (topClip || bottomClip) {
      console.log(`Adjusting scroll (attempt ${attempts}):`, { topClip, bottomClip });
      doScroll();
      if (attempts < maxAdjusts) {
        requestAnimationFrame(fixLoop);
      }
    } else {
      // restaura scroll-snap
      if (scrollRoot instanceof Element && prevSnap) {
        scrollRoot.style.scrollSnapType = prevSnap;
      }
      
      // acessibilidade: foca no heading
      setTimeout(() => {
        const focusable = el.querySelector('h1, h2, h3, [data-heading], [tabindex]') as HTMLElement | null;
        if (focusable) {
          focusable.setAttribute('tabindex', '-1');
          focusable.focus();
          // Remove tabindex after focus
          setTimeout(() => focusable.removeAttribute('tabindex'), 100);
        }
      }, 300);
    }
  };
  
  requestAnimationFrame(fixLoop);
}