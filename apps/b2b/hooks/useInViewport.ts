import { useEffect, useState, useRef, RefObject } from 'react'

interface UseInViewportOptions {
  rootMargin?: string
  threshold?: number | number[]
  triggerOnce?: boolean
}

export function useInViewport<T extends HTMLElement = HTMLDivElement>(
  options: UseInViewportOptions = {}
): [RefObject<T>, boolean] {
  const {
    rootMargin = '50px',
    threshold = 0,
    triggerOnce = true
  } = options

  const ref = useRef<T>(null)
  const [isInViewport, setIsInViewport] = useState(false)
  const [hasBeenInViewport, setHasBeenInViewport] = useState(false)

  useEffect(() => {
    if (!ref.current || (triggerOnce && hasBeenInViewport)) return

    const observer = new IntersectionObserver(
      ([entry]) => {
        const inView = entry.isIntersecting
        setIsInViewport(inView)
        
        if (inView && !hasBeenInViewport) {
          setHasBeenInViewport(true)
        }
      },
      {
        rootMargin,
        threshold
      }
    )

    observer.observe(ref.current)

    return () => {
      if (ref.current) {
        observer.unobserve(ref.current)
      }
    }
  }, [rootMargin, threshold, triggerOnce, hasBeenInViewport])

  return [ref, triggerOnce ? hasBeenInViewport : isInViewport]
}