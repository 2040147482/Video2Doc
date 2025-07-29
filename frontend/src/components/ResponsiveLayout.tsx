'use client'

import React, { ReactNode } from 'react'
import { useMediaQuery } from '@/hooks/useMediaQuery'

interface ResponsiveLayoutProps {
    children: ReactNode
    className?: string
}

interface ResponsiveGridProps {
    children: ReactNode
    cols?: {
        default: number
        sm?: number
        md?: number
        lg?: number
        xl?: number
    }
    gap?: number
    className?: string
}

interface ResponsiveStackProps {
    children: ReactNode
    direction?: 'horizontal' | 'vertical'
    breakpoint?: 'sm' | 'md' | 'lg'
    spacing?: number
    className?: string
}

// 主响应式布局容器
export default function ResponsiveLayout({ children, className = '' }: ResponsiveLayoutProps) {
    return (
        <div className={`w-full ${className}`}>
            {children}
        </div>
    )
}

// 响应式网格组件
export function ResponsiveGrid({
    children,
    cols = { default: 1, md: 2, lg: 3 },
    gap = 4,
    className = ''
}: ResponsiveGridProps) {
    const getGridClasses = () => {
        const baseClass = 'grid'
        const gapClass = `gap-${gap}`

        let colClasses = `grid-cols-${cols.default}`

        if (cols.sm) colClasses += ` sm:grid-cols-${cols.sm}`
        if (cols.md) colClasses += ` md:grid-cols-${cols.md}`
        if (cols.lg) colClasses += ` lg:grid-cols-${cols.lg}`
        if (cols.xl) colClasses += ` xl:grid-cols-${cols.xl}`

        return `${baseClass} ${colClasses} ${gapClass} ${className}`
    }

    return (
        <div className={getGridClasses()}>
            {children}
        </div>
    )
}

// 响应式堆栈组件
export function ResponsiveStack({
    children,
    direction = 'vertical',
    breakpoint = 'md',
    spacing = 4,
    className = ''
}: ResponsiveStackProps) {
    const getStackClasses = () => {
        const baseClass = 'flex'
        const spaceClass = direction === 'horizontal' ? `space-x-${spacing}` : `space-y-${spacing}`

        if (direction === 'horizontal') {
            return `${baseClass} flex-col ${breakpoint}:flex-row ${breakpoint}:space-y-0 ${breakpoint}:${spaceClass} space-y-${spacing} ${className}`
        } else {
            return `${baseClass} flex-row ${breakpoint}:flex-col ${breakpoint}:space-x-0 ${breakpoint}:${spaceClass} space-x-${spacing} ${className}`
        }
    }

    return (
        <div className={getStackClasses()}>
            {children}
        </div>
    )
}

// 响应式容器组件
export function ResponsiveContainer({
    children,
    size = 'default',
    className = ''
}: {
    children: ReactNode
    size?: 'small' | 'default' | 'large' | 'full'
    className?: string
}) {
    const getSizeClasses = () => {
        switch (size) {
            case 'small':
                return 'max-w-2xl'
            case 'large':
                return 'max-w-6xl'
            case 'full':
                return 'max-w-full'
            default:
                return 'max-w-4xl'
        }
    }

    return (
        <div className={`w-full ${getSizeClasses()} mx-auto px-4 sm:px-6 lg:px-8 ${className}`}>
            {children}
        </div>
    )
}

// 响应式卡片组件
export function ResponsiveCard({
    children,
    padding = 'default',
    className = ''
}: {
    children: ReactNode
    padding?: 'small' | 'default' | 'large'
    className?: string
}) {
    const getPaddingClasses = () => {
        switch (padding) {
            case 'small':
                return 'p-3 sm:p-4'
            case 'large':
                return 'p-6 sm:p-8'
            default:
                return 'p-4 sm:p-6'
        }
    }

    return (
        <div className={`bg-white rounded-xl shadow-lg overflow-hidden ${getPaddingClasses()} ${className}`}>
            {children}
        </div>
    )
}

// 响应式文本组件
export function ResponsiveText({
    children,
    size = 'base',
    className = ''
}: {
    children: ReactNode
    size?: 'sm' | 'base' | 'lg' | 'xl' | '2xl'
    className?: string
}) {
    const getSizeClasses = () => {
        switch (size) {
            case 'sm':
                return 'text-sm sm:text-base'
            case 'lg':
                return 'text-base sm:text-lg'
            case 'xl':
                return 'text-lg sm:text-xl'
            case '2xl':
                return 'text-xl sm:text-2xl'
            default:
                return 'text-sm sm:text-base'
        }
    }

    return (
        <div className={`${getSizeClasses()} ${className}`}>
            {children}
        </div>
    )
}

// 响应式间距组件
export function ResponsiveSpacing({
    size = 'default',
    className = ''
}: {
    size?: 'small' | 'default' | 'large'
    className?: string
}) {
    const getSpacingClasses = () => {
        switch (size) {
            case 'small':
                return 'h-4 sm:h-6'
            case 'large':
                return 'h-8 sm:h-12'
            default:
                return 'h-6 sm:h-8'
        }
    }

    return <div className={`${getSpacingClasses()} ${className}`} />
}

// 移动端优化的按钮组件
export function ResponsiveButton({
    children,
    size = 'default',
    variant = 'primary',
    fullWidth = false,
    className = '',
    ...props
}: {
    children: ReactNode
    size?: 'small' | 'default' | 'large'
    variant?: 'primary' | 'secondary' | 'outline'
    fullWidth?: boolean
    className?: string
    [key: string]: any
}) {
    const getSizeClasses = () => {
        switch (size) {
            case 'small':
                return 'px-3 py-2 text-sm sm:px-4 sm:py-2'
            case 'large':
                return 'px-6 py-3 text-base sm:px-8 sm:py-4 sm:text-lg'
            default:
                return 'px-4 py-2 text-sm sm:px-6 sm:py-3 sm:text-base'
        }
    }

    const getVariantClasses = () => {
        switch (variant) {
            case 'secondary':
                return 'bg-gray-600 text-white hover:bg-gray-700'
            case 'outline':
                return 'border border-blue-600 text-blue-600 hover:bg-blue-50'
            default:
                return 'bg-blue-600 text-white hover:bg-blue-700'
        }
    }

    const widthClass = fullWidth ? 'w-full' : ''

    return (
        <button
            className={`
                ${getSizeClasses()} 
                ${getVariantClasses()} 
                ${widthClass}
                rounded-lg font-medium transition-all duration-200
                focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
                disabled:opacity-50 disabled:cursor-not-allowed
                ${className}
            `}
            {...props}
        >
            {children}
        </button>
    )
} 