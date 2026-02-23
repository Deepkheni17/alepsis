'use client'

import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { supabase } from '@/lib/supabase'
import { FileText, LayoutDashboard, FileCheck, Upload, LogOut } from 'lucide-react'
import { ThemeToggle } from '@/components/ui/theme-toggle'

interface AppSidebarProps {
  userEmail: string
  /** Which nav item is currently active */
  active: 'dashboard' | 'invoices' | 'upload'
}

const nav = [
  { id: 'dashboard' as const, label: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { id: 'invoices'  as const, label: 'All Invoices', href: '/invoices',  icon: FileCheck   },
  { id: 'upload'    as const, label: 'Upload Invoice', href: '/upload', icon: Upload       },
]

export function AppSidebar({ userEmail, active }: AppSidebarProps) {
  const router = useRouter()

  const handleLogout = async () => {
    await supabase.auth.signOut()
    router.push('/login')
  }

  return (
    <aside className="hidden lg:flex w-64 flex-col border-r border-border bg-card/50 backdrop-blur-sm fixed h-full z-10">
      {/* Logo */}
      <div className="p-6 border-b border-border">
        <div className="flex items-center gap-2">
          <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-gradient-to-br from-blue-600 to-indigo-600">
            <FileText className="w-4 h-4 text-white" />
          </div>
          <span className="font-bold text-lg text-foreground tracking-tight">Alepsis</span>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 p-4 space-y-1">
        {nav.map((item) => {
          const isActive = item.id === active
          return (
            <Link
              key={item.id}
              href={item.href}
              className={
                isActive
                  ? 'flex items-center gap-3 px-3 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-medium text-sm shadow-sm'
                  : 'flex items-center gap-3 px-3 py-2.5 rounded-xl text-muted-foreground hover:text-foreground hover:bg-muted transition-colors text-sm font-medium'
              }
            >
              <item.icon className="w-4 h-4 flex-shrink-0" />
              {item.label}
            </Link>
          )
        })}
      </nav>

      {/* Footer — theme toggle + user + sign out */}
      <div className="p-4 border-t border-border space-y-1">
        {/* Theme toggle */}
        <ThemeToggle variant="pill" className="w-full justify-start" />

        {/* User */}
        <div className="flex items-center gap-3 px-3 py-2 rounded-xl">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white text-xs font-bold flex-shrink-0">
            {userEmail ? userEmail.charAt(0).toUpperCase() : '?'}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs font-medium text-foreground truncate">{userEmail}</p>
            <p className="text-xs text-muted-foreground">Account</p>
          </div>
        </div>

        {/* Sign out */}
        <button
          onClick={handleLogout}
          className="flex items-center gap-2 w-full px-3 py-2 rounded-xl text-sm text-muted-foreground hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-950/20 transition-colors font-medium"
        >
          <LogOut className="w-4 h-4" />
          Sign out
        </button>
      </div>
    </aside>
  )
}
