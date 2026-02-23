'use client'

import { useTheme } from 'next-themes'
import { useEffect, useState } from 'react'
import { Sun, Moon } from 'lucide-react'
import { cn } from '@/lib/utils'

interface ThemeToggleProps {
  className?: string
  /** 'icon' = just the icon button, 'pill' = icon + label in a pill */
  variant?: 'icon' | 'pill'
}

export function ThemeToggle({ className, variant = 'icon' }: ThemeToggleProps) {
  const { theme, setTheme, resolvedTheme } = useTheme()
  const [mounted, setMounted] = useState(false)

  // Avoid hydration mismatch — only render after mount
  useEffect(() => setMounted(true), [])

  if (!mounted) {
    // Placeholder with same size so layout doesn't shift
    return (
      <div
        className={cn(
          variant === 'pill'
            ? 'h-9 w-24 rounded-full bg-muted animate-pulse'
            : 'h-9 w-9 rounded-xl bg-muted animate-pulse',
          className
        )}
      />
    )
  }

  const isDark = resolvedTheme === 'dark'

  const toggle = () => setTheme(isDark ? 'light' : 'dark')

  if (variant === 'pill') {
    return (
      <button
        onClick={toggle}
        aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
        className={cn(
          'flex items-center gap-2 px-3 py-2 rounded-xl text-sm font-medium transition-all duration-200',
          'text-muted-foreground hover:text-foreground hover:bg-muted',
          className
        )}
      >
        <span className="relative w-4 h-4 flex items-center justify-center">
          <Sun
            className={cn(
              'absolute w-4 h-4 transition-all duration-300',
              isDark ? 'opacity-0 rotate-90 scale-50' : 'opacity-100 rotate-0 scale-100'
            )}
          />
          <Moon
            className={cn(
              'absolute w-4 h-4 transition-all duration-300',
              isDark ? 'opacity-100 rotate-0 scale-100' : 'opacity-0 -rotate-90 scale-50'
            )}
          />
        </span>
        {isDark ? 'Light mode' : 'Dark mode'}
      </button>
    )
  }

  return (
    <button
      onClick={toggle}
      aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
      className={cn(
        'relative flex items-center justify-center w-9 h-9 rounded-xl border border-border',
        'bg-background hover:bg-muted transition-all duration-200',
        'text-muted-foreground hover:text-foreground',
        className
      )}
    >
      <Sun
        className={cn(
          'absolute w-4 h-4 transition-all duration-300',
          isDark ? 'opacity-0 rotate-90 scale-50' : 'opacity-100 rotate-0 scale-100'
        )}
      />
      <Moon
        className={cn(
          'absolute w-4 h-4 transition-all duration-300',
          isDark ? 'opacity-100 rotate-0 scale-100' : 'opacity-0 -rotate-90 scale-50'
        )}
      />
    </button>
  )
}
