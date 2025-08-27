/**
 * Smooth scroll to section with header offset and centering
 */
export function scrollToSection(
  selector: string,
  opts?: { headerOffset?: number }
) {
  const el = document.querySelector(selector) as HTMLElement | null;
  if (!el) {
    console.warn(`Element not found: ${selector}`);
    return;
  }

  // Try to find header element or use default offset
  const header = document.querySelector('[data-fixed-header], nav, header') as HTMLElement | null;
  const headerOffset = opts?.headerOffset ?? header?.offsetHeight ?? 80;

  try {
    // Try native scrollIntoView with center alignment
    el.scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'nearest' });

    // Post-frame check to ensure visibility
    requestAnimationFrame(() => ensureVisible(el, headerOffset));
  } catch (e) {
    // Fallback for browsers without scrollIntoView options
    manualScroll(el, headerOffset);
  }
}

/**
 * Ensure element is visible and not cut off by header
 */
function ensureVisible(el: HTMLElement, headerOffset: number) {
  const rect = el.getBoundingClientRect();
  const vh = window.innerHeight;

  // If top is above header or bottom is below viewport, adjust
  if (rect.top < headerOffset || rect.bottom > vh) {
    // Only adjust if significantly cut off
    if (rect.top < headerOffset - 20) {
      manualScroll(el, headerOffset);
    }
  }
}

/**
 * Manual scroll fallback with centering logic
 */
function manualScroll(el: HTMLElement, headerOffset: number) {
  const rect = el.getBoundingClientRect();
  const pageY = window.pageYOffset || document.documentElement.scrollTop;
  const elHeight = rect.height;
  const vh = window.innerHeight;
  const availableHeight = vh - headerOffset;

  let targetY: number;

  if (elHeight <= availableHeight) {
    // Element fits in viewport - center it
    const centerOffset = Math.max(0, (availableHeight - elHeight) / 2);
    targetY = rect.top + pageY - headerOffset - centerOffset;
  } else {
    // Element doesn't fit - align to top with header offset
    targetY = rect.top + pageY - headerOffset - 20; // 20px padding
  }

  window.scrollTo({ 
    top: Math.max(0, targetY), 
    behavior: 'smooth' 
  });
}

/**
 * Scroll to section and focus on heading for accessibility
 */
export function scrollToSectionWithFocus(
  selector: string,
  opts?: { headerOffset?: number }
) {
  scrollToSection(selector, opts);
  
  // After scroll, focus on section heading for accessibility
  setTimeout(() => {
    const section = document.querySelector(selector) as HTMLElement | null;
    if (!section) return;
    
    const heading = section.querySelector('h1, h2, h3, [data-heading]') as HTMLElement | null;
    if (heading) {
      heading.setAttribute('tabindex', '-1');
      heading.focus();
      // Remove tabindex after focus to keep it clean
      setTimeout(() => heading.removeAttribute('tabindex'), 100);
    }
  }, 500); // Wait for scroll animation
}