'use client';

import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import Link from 'next/link';
import { getAccessToken, isTokenExpired, clearTokens, decodeToken, refreshAccessToken } from '@/lib/auth';
import type { TokenPayload } from '@/types';
import { AIDisclosureBanner } from '@/components/AIDisclosureBanner';
import { ThemeToggle } from '@/components/theme-toggle';
import { Button } from '@/components/ui/button';

const navigation = [
  { name: 'Dashboard', href: '/dashboard' },
  { name: 'Settings', href: '/settings' },
];

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const [user, setUser] = useState<TokenPayload | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      const token = getAccessToken();

      if (!token) {
        router.push('/login');
        return;
      }

      if (isTokenExpired(token)) {
        const refreshed = await refreshAccessToken();
        if (!refreshed) {
          router.push('/login');
          return;
        }
        const newToken = getAccessToken();
        if (newToken) {
          setUser(decodeToken(newToken));
        }
      } else {
        setUser(decodeToken(token));
      }

      setLoading(false);
    };

    checkAuth();
  }, [router]);

  const handleLogout = () => {
    clearTokens();
    router.push('/login');
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-gray-500">Loading...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="bg-card border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-8">
              <h1 className="text-xl font-bold">Cradle</h1>
              <nav className="flex space-x-1">
                {navigation.map((item) => (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                      pathname === item.href
                        ? 'text-primary bg-primary/10'
                        : 'text-muted-foreground hover:text-foreground hover:bg-muted'
                    }`}
                  >
                    {item.name}
                  </Link>
                ))}
              </nav>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-muted-foreground">
                {user?.email}
              </span>
              {user?.roles?.includes('admin') && (
                <span className="px-2 py-1 text-xs bg-primary/10 text-primary rounded">
                  Admin
                </span>
              )}
              <ThemeToggle />
              <Button variant="ghost" size="sm" onClick={handleLogout}>
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>

      {/* AI Disclosure Banner (stub for future) */}
      <AIDisclosureBanner />
    </div>
  );
}
