'use client';

import React from 'react';
import Link from 'next/link';
import { ArrowRight, ChevronRight, Menu, X, FileText, Zap, Shield, Users } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { AnimatedGroup } from '@/components/ui/animated-group';
import { cn } from '@/lib/utils';

const transitionVariants = {
  item: {
    hidden: {
      opacity: 0,
      filter: 'blur(12px)',
      y: 12,
    },
    visible: {
      opacity: 1,
      filter: 'blur(0px)',
      y: 0,
      transition: {
        type: 'spring',
        bounce: 0.3,
        duration: 1.5,
      },
    },
  },
};

export function HeroSection() {
  return (
    <>
      <HeroHeader />
      <main className="overflow-hidden">
        <div
          aria-hidden
          className="z-[2] absolute inset-0 pointer-events-none isolate opacity-50 contain-strict hidden lg:block"
        >
          <div className="w-[35rem] h-[80rem] -translate-y-[350px] absolute left-0 top-0 -rotate-45 rounded-full bg-[radial-gradient(68.54%_68.72%_at_55.02%_31.46%,hsla(220,100%,70%,.12)_0,hsla(220,100%,60%,.04)_50%,hsla(220,100%,50%,0)_80%)]" />
          <div className="h-[80rem] absolute left-0 top-0 w-56 -rotate-45 rounded-full bg-[radial-gradient(50%_50%_at_50%_50%,hsla(220,100%,70%,.08)_0,hsla(220,100%,50%,.02)_80%,transparent_100%)] [translate:5%_-50%]" />
          <div className="h-[80rem] -translate-y-[350px] absolute left-0 top-0 w-56 -rotate-45 bg-[radial-gradient(50%_50%_at_50%_50%,hsla(220,100%,70%,.06)_0,hsla(220,100%,50%,.02)_80%,transparent_100%)]" />
        </div>

        {/* Hero Section */}
        <section>
          <div className="relative pt-24 md:pt-36">
            <AnimatedGroup
              variants={{
                container: {
                  visible: {
                    transition: {
                      delayChildren: 1,
                    },
                  },
                },
                item: {
                  hidden: { opacity: 0, y: 20 },
                  visible: {
                    opacity: 1,
                    y: 0,
                    transition: { type: 'spring', bounce: 0.3, duration: 2 },
                  },
                },
              }}
              className="absolute inset-0 -z-20"
            >
              {/* Subtle background gradient overlay */}
              <div className="absolute inset-x-0 top-0 -z-20 h-[600px] bg-gradient-to-b from-blue-50/60 via-indigo-50/30 to-transparent dark:from-blue-950/20 dark:via-indigo-950/10 dark:to-transparent" />
            </AnimatedGroup>

            <div
              aria-hidden
              className="absolute inset-0 -z-10 size-full [background:radial-gradient(125%_125%_at_50%_100%,transparent_0%,var(--background)_75%)]"
            />

            <div className="mx-auto max-w-7xl px-6">
              <div className="text-center sm:mx-auto lg:mr-auto lg:mt-0">
                <AnimatedGroup variants={transitionVariants}>
                  {/* Announcement badge */}
                  <Link
                    href="/dashboard"
                    className="hover:bg-background dark:hover:border-t-border bg-muted group mx-auto flex w-fit items-center gap-4 rounded-full border p-1 pl-4 shadow-md shadow-black/5 transition-all duration-300 dark:border-t-white/5 dark:shadow-zinc-950"
                  >
                    <span className="text-foreground text-sm">
                      Powered by Google Gemma AI — Intelligent Invoice Extraction
                    </span>
                    <span className="dark:border-background block h-4 w-0.5 border-l bg-white dark:bg-zinc-700"></span>
                    <div className="bg-background group-hover:bg-muted size-6 overflow-hidden rounded-full duration-500">
                      <div className="flex w-12 -translate-x-1/2 duration-500 ease-in-out group-hover:translate-x-0">
                        <span className="flex size-6">
                          <ArrowRight className="m-auto size-3" />
                        </span>
                        <span className="flex size-6">
                          <ArrowRight className="m-auto size-3" />
                        </span>
                      </div>
                    </div>
                  </Link>

                  <h1 className="mt-8 max-w-4xl mx-auto text-balance text-6xl md:text-7xl lg:mt-16 xl:text-[5.25rem] font-bold tracking-tight text-foreground">
                    Automate Your{' '}
                    <span className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                      Invoice Processing
                    </span>{' '}
                    with AI
                  </h1>
                  <p className="mx-auto mt-8 max-w-2xl text-balance text-lg text-muted-foreground">
                    Upload invoices and let AI extract vendor details, line items, taxes, and totals automatically. Validate, approve, and manage all your invoices in one secure platform.
                  </p>
                </AnimatedGroup>

                <AnimatedGroup
                  variants={{
                    container: {
                      visible: {
                        transition: {
                          staggerChildren: 0.05,
                          delayChildren: 0.75,
                        },
                      },
                    },
                    ...transitionVariants,
                  }}
                  className="mt-12 flex flex-col items-center justify-center gap-2 md:flex-row"
                >
                  <div className="bg-foreground/10 rounded-[14px] border p-0.5">
                    <Button asChild size="lg" className="rounded-xl px-5 text-base bg-blue-600 hover:bg-blue-700 text-white">
                      <Link href="/dashboard">
                        <span className="text-nowrap">Go to Dashboard</span>
                      </Link>
                    </Button>
                  </div>
                  <Button asChild size="lg" variant="ghost" className="h-10.5 rounded-xl px-5">
                    <Link href="/upload">
                      <span className="text-nowrap">Upload Invoice</span>
                    </Link>
                  </Button>
                </AnimatedGroup>
              </div>
            </div>

            {/* App Screenshot / Dashboard Preview */}
            <AnimatedGroup
              variants={{
                container: {
                  visible: {
                    transition: { staggerChildren: 0.05, delayChildren: 0.75 },
                  },
                },
                ...transitionVariants,
              }}
            >
              <div className="relative -mr-56 mt-8 overflow-hidden px-2 sm:mr-0 sm:mt-12 md:mt-20">
                <div
                  aria-hidden
                  className="bg-gradient-to-b to-background absolute inset-0 z-10 from-transparent from-35%"
                />
                <div className="inset-shadow-2xs ring-background dark:inset-shadow-white/20 bg-background relative mx-auto max-w-6xl overflow-hidden rounded-2xl border p-4 shadow-lg shadow-zinc-950/15 ring-1">
                  {/* Dashboard Preview - a stylized mock */}
                  <div className="aspect-[15/8] bg-gradient-to-br from-slate-50 to-blue-50 dark:from-zinc-900 dark:to-blue-950/30 rounded-2xl border border-border/25 overflow-hidden relative">
                    {/* Topbar */}
                    <div className="bg-white dark:bg-zinc-900 border-b border-border px-6 py-3 flex items-center gap-4">
                      <div className="flex gap-1.5">
                        <span className="w-3 h-3 rounded-full bg-red-400" />
                        <span className="w-3 h-3 rounded-full bg-yellow-400" />
                        <span className="w-3 h-3 rounded-full bg-green-400" />
                      </div>
                      <div className="flex-1 bg-muted rounded-md h-6 max-w-xs" />
                      <div className="w-20 h-6 bg-blue-100 dark:bg-blue-900/40 rounded-md" />
                    </div>
                    {/* Content area */}
                    <div className="flex h-full">
                      {/* Sidebar */}
                      <div className="w-48 bg-white dark:bg-zinc-900 border-r border-border p-4 space-y-2 hidden sm:block">
                        {['Dashboard', 'Invoices', 'Upload', 'Settings'].map((item) => (
                          <div key={item} className={`px-3 py-2 rounded-lg text-xs font-medium ${item === 'Dashboard' ? 'bg-blue-600 text-white' : 'text-muted-foreground hover:bg-muted'}`}>
                            {item}
                          </div>
                        ))}
                      </div>
                      {/* Main content */}
                      <div className="flex-1 p-6 space-y-4">
                        <div className="grid grid-cols-3 gap-4">
                          {[
                            { label: 'Total Invoices', value: '142', color: 'bg-blue-500' },
                            { label: 'Approved', value: '98', color: 'bg-green-500' },
                            { label: 'Pending', value: '44', color: 'bg-yellow-500' },
                          ].map((card) => (
                            <div key={card.label} className="bg-white dark:bg-zinc-800 rounded-xl p-4 border border-border shadow-sm">
                              <div className={`w-8 h-1.5 rounded-full ${card.color} mb-2`} />
                              <div className="text-xl font-bold text-foreground">{card.value}</div>
                              <div className="text-xs text-muted-foreground">{card.label}</div>
                            </div>
                          ))}
                        </div>
                        <div className="bg-white dark:bg-zinc-800 rounded-xl border border-border shadow-sm overflow-hidden">
                          <div className="px-4 py-3 border-b border-border text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                            Recent Invoices
                          </div>
                          {[
                            { vendor: 'Acme Corp', amount: '$4,250.00', status: 'Approved', date: 'Feb 20' },
                            { vendor: 'TechSupply Ltd', amount: '$1,899.50', status: 'Pending', date: 'Feb 19' },
                            { vendor: 'Global Services', amount: '$7,320.00', status: 'Review', date: 'Feb 18' },
                          ].map((row) => (
                            <div key={row.vendor} className="flex items-center justify-between px-4 py-3 border-b border-border/50 last:border-0">
                              <div className="text-xs font-medium text-foreground">{row.vendor}</div>
                              <div className="text-xs text-muted-foreground">{row.date}</div>
                              <div className="text-xs font-semibold text-foreground">{row.amount}</div>
                              <div className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                                row.status === 'Approved' ? 'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-400' :
                                row.status === 'Pending' ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/40 dark:text-yellow-400' :
                                'bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-400'
                              }`}>{row.status}</div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </AnimatedGroup>
          </div>
        </section>

        {/* Features Section */}
        <section className="bg-background pb-16 pt-24 md:pb-32">
          <div className="mx-auto max-w-7xl px-6">
            <AnimatedGroup preset="fade">
              <div className="text-center mb-16">
                <h2 className="text-3xl font-bold text-foreground md:text-4xl">
                  Everything You Need to Manage Invoices
                </h2>
                <p className="mt-4 text-muted-foreground max-w-2xl mx-auto">
                  A complete invoice processing platform built for modern teams. AI-powered extraction meets enterprise-grade security.
                </p>
              </div>
            </AnimatedGroup>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {[
                {
                  icon: Shield,
                  title: 'Secure Authentication',
                  description: 'Email/password and Google OAuth login with per-user data isolation.',
                  color: 'text-blue-600 bg-blue-50 dark:bg-blue-950/40',
                },
                {
                  icon: Zap,
                  title: 'AI Extraction',
                  description: 'Google Gemma AI extracts vendor info, line items, taxes, and totals automatically.',
                  color: 'text-indigo-600 bg-indigo-50 dark:bg-indigo-950/40',
                },
                {
                  icon: FileText,
                  title: 'Smart Validation',
                  description: 'Intelligent validation rules detect errors and flag discrepancies for review.',
                  color: 'text-violet-600 bg-violet-50 dark:bg-violet-950/40',
                },
                {
                  icon: Users,
                  title: 'Multi-User',
                  description: 'Fully isolated data per user account with role-based access controls.',
                  color: 'text-cyan-600 bg-cyan-50 dark:bg-cyan-950/40',
                },
              ].map((feature) => (
                <div
                  key={feature.title}
                  className="group relative p-6 bg-card rounded-2xl border border-border shadow-sm hover:shadow-md transition-all duration-300 hover:-translate-y-1"
                >
                  <div className={`inline-flex items-center justify-center w-12 h-12 rounded-xl mb-4 ${feature.color}`}>
                    <feature.icon className="w-6 h-6" />
                  </div>
                  <h3 className="text-base font-semibold text-foreground mb-2">{feature.title}</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">{feature.description}</p>
                </div>
              ))}
            </div>

            {/* Trusted by logos section */}
            <div className="group relative m-auto max-w-5xl mt-24">
              <div className="absolute inset-0 z-10 flex scale-95 items-center justify-center opacity-0 duration-500 group-hover:scale-100 group-hover:opacity-100">
                <Link href="/" className="block text-sm duration-150 hover:opacity-75 text-muted-foreground">
                  <span>Trusted by teams worldwide</span>
                  <ChevronRight className="ml-1 inline-block size-3" />
                </Link>
              </div>
              <div className="group-hover:blur-sm mx-auto mt-12 grid max-w-2xl grid-cols-4 gap-x-12 gap-y-8 transition-all duration-500 group-hover:opacity-50 sm:gap-x-16 sm:gap-y-14">
                <div className="flex items-center justify-center">
                  <img className="mx-auto h-5 w-fit dark:invert opacity-60" src="https://html.tailus.io/blocks/customers/nvidia.svg" alt="Nvidia Logo" height="20" width="auto" />
                </div>
                <div className="flex items-center justify-center">
                  <img className="mx-auto h-4 w-fit dark:invert opacity-60" src="https://html.tailus.io/blocks/customers/github.svg" alt="GitHub Logo" height="16" width="auto" />
                </div>
                <div className="flex items-center justify-center">
                  <img className="mx-auto h-5 w-fit dark:invert opacity-60" src="https://html.tailus.io/blocks/customers/nike.svg" alt="Nike Logo" height="20" width="auto" />
                </div>
                <div className="flex items-center justify-center">
                  <img className="mx-auto h-6 w-fit dark:invert opacity-60" src="https://html.tailus.io/blocks/customers/openai.svg" alt="OpenAI Logo" height="24" width="auto" />
                </div>
                <div className="flex items-center justify-center">
                  <img className="mx-auto h-5 w-fit dark:invert opacity-60" src="https://html.tailus.io/blocks/customers/lemonsqueezy.svg" alt="Lemon Squeezy Logo" height="20" width="auto" />
                </div>
                <div className="flex items-center justify-center">
                  <img className="mx-auto h-4 w-fit dark:invert opacity-60" src="https://html.tailus.io/blocks/customers/laravel.svg" alt="Laravel Logo" height="16" width="auto" />
                </div>
                <div className="flex items-center justify-center">
                  <img className="mx-auto h-7 w-fit dark:invert opacity-60" src="https://html.tailus.io/blocks/customers/lilly.svg" alt="Lilly Logo" height="28" width="auto" />
                </div>
                <div className="flex items-center justify-center">
                  <img className="mx-auto h-4 w-fit dark:invert opacity-60" src="https://html.tailus.io/blocks/customers/column.svg" alt="Column Logo" height="16" width="auto" />
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>
    </>
  );
}

const menuItems = [
  { name: 'Features', href: '#features' },
  { name: 'Dashboard', href: '/dashboard' },
  { name: 'Invoices', href: '/invoices' },
  { name: 'Upload', href: '/upload' },
];

const HeroHeader = () => {
  const [menuState, setMenuState] = React.useState(false);
  const [isScrolled, setIsScrolled] = React.useState(false);

  React.useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <header>
      <nav data-state={menuState && 'active'} className="fixed z-20 w-full px-2 group">
        <div
          className={cn(
            'mx-auto mt-2 max-w-6xl px-6 transition-all duration-300 lg:px-12',
            isScrolled && 'bg-background/80 max-w-4xl rounded-2xl border backdrop-blur-lg lg:px-5'
          )}
        >
          <div className="relative flex flex-wrap items-center justify-between gap-6 py-3 lg:gap-0 lg:py-4">
            <div className="flex w-full justify-between lg:w-auto">
              <Link href="/" aria-label="home" className="flex items-center space-x-2">
                <InvoiceLogo />
              </Link>

              <button
                onClick={() => setMenuState(!menuState)}
                aria-label={menuState ? 'Close Menu' : 'Open Menu'}
                className="relative z-20 -m-2.5 -mr-4 block cursor-pointer p-2.5 lg:hidden"
              >
                <Menu className="in-data-[state=active]:rotate-180 group-data-[state=active]:scale-0 group-data-[state=active]:opacity-0 m-auto size-6 duration-200" />
                <X className="group-data-[state=active]:rotate-0 group-data-[state=active]:scale-100 group-data-[state=active]:opacity-100 absolute inset-0 m-auto size-6 -rotate-180 scale-0 opacity-0 duration-200" />
              </button>
            </div>

            <div className="absolute inset-0 m-auto hidden size-fit lg:block">
              <ul className="flex gap-8 text-sm">
                {menuItems.map((item, index) => (
                  <li key={index}>
                    <Link
                      href={item.href}
                      className="text-muted-foreground hover:text-accent-foreground block duration-150"
                    >
                      <span>{item.name}</span>
                    </Link>
                  </li>
                ))}
              </ul>
            </div>

            <div className="bg-background group-data-[state=active]:block lg:group-data-[state=active]:flex mb-6 hidden w-full flex-wrap items-center justify-end space-y-8 rounded-3xl border p-6 shadow-2xl shadow-zinc-300/20 md:flex-nowrap lg:m-0 lg:flex lg:w-fit lg:gap-6 lg:space-y-0 lg:border-transparent lg:bg-transparent lg:p-0 lg:shadow-none dark:shadow-none dark:lg:bg-transparent">
              <div className="lg:hidden">
                <ul className="space-y-6 text-base">
                  {menuItems.map((item, index) => (
                    <li key={index}>
                      <Link
                        href={item.href}
                        className="text-muted-foreground hover:text-accent-foreground block duration-150"
                      >
                        <span>{item.name}</span>
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
              <div className="flex w-full flex-col space-y-3 sm:flex-row sm:gap-3 sm:space-y-0 md:w-fit">
                <Button
                  asChild
                  variant="outline"
                  size="sm"
                  className={cn(isScrolled && 'lg:hidden')}
                >
                  <Link href="/login">
                    <span>Login</span>
                  </Link>
                </Button>
                <Button asChild size="sm" className={cn(isScrolled && 'lg:hidden', 'bg-blue-600 hover:bg-blue-700 text-white')}>
                  <Link href="/dashboard">
                    <span>Dashboard</span>
                  </Link>
                </Button>
                <Button
                  asChild
                  size="sm"
                  className={cn(isScrolled ? 'lg:inline-flex' : 'hidden', 'bg-blue-600 hover:bg-blue-700 text-white')}
                >
                  <Link href="/dashboard">
                    <span>Get Started</span>
                  </Link>
                </Button>
              </div>
            </div>
          </div>
        </div>
      </nav>
    </header>
  );
};

const InvoiceLogo = ({ className }: { className?: string }) => {
  return (
    <div className={cn('flex items-center gap-2', className)}>
      <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-gradient-to-br from-blue-600 to-indigo-600">
        <FileText className="w-4 h-4 text-white" />
      </div>
      <span className="font-bold text-lg text-foreground tracking-tight">Alepsis</span>
    </div>
  );
};
