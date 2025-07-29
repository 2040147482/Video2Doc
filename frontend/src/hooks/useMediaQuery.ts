'use client'

import { useState, useEffect } from 'react'

export function useMediaQuery(query: string): boolean {
    const [matches, setMatches] = useState(false)

    useEffect(() => {
        if (typeof window !== 'undefined') {
            const media = window.matchMedia(query)
            setMatches(media.matches)

            const listener = (event: MediaQueryListEvent) => {
                setMatches(event.matches)
            }

            media.addEventListener('change', listener)
            return () => media.removeEventListener('change', listener)
        }
    }, [query])

    return matches
}

// 预定义的断点
export const breakpoints = {
    sm: '(min-width: 640px)',
    md: '(min-width: 768px)',
    lg: '(min-width: 1024px)',
    xl: '(min-width: 1280px)',
    '2xl': '(min-width: 1536px)',
    mobile: '(max-width: 767px)',
    tablet: '(min-width: 768px) and (max-width: 1023px)',
    desktop: '(min-width: 1024px)'
}

// 便捷的hook
export const useIsMobile = () => useMediaQuery(breakpoints.mobile)
export const useIsTablet = () => useMediaQuery(breakpoints.tablet)
export const useIsDesktop = () => useMediaQuery(breakpoints.desktop) 