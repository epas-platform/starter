'use client';

import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import Link from 'next/link';
import { getAccessToken, isTokenExpired, clearTokens, decodeToken, refreshAccessToken } from '@/lib/auth';
import type { TokenPayload } from '@/types';
import { AIDisclosureBanner } from '@/components/AIDisclosureBanner';

const navigation = [
  { name: 'Dashboard', href: '/dashboard' },
  { name: 'Workspaces', href: '/workspaces' },
  { name: 'Runs', href: '/runs' },
  { name: 'Settings', href: '/settings' }
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
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-8">
              <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                EPAS Prototype
              </h1>
              <nav className="hidden md:flex space-x-1">
                {navigation.map((item) => (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                      pathname === item.href || pathname.startsWith(item.href + '/')
                        ? 'text-green-600 bg-green-50 dark:text-green-400 dark:bg-green-900/20'
                        : 'text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700'
                    }`}
                  >
                    {item.name}
                  </Link>
                ))}
              </nav>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600 dark:text-gray-400">
                {user?.email}
              </span>
              {user?.roles?.includes('admin') && (
                <span className="px-2 py-1 text-xs bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 rounded">
                  Admin
                </span>
              )}
              <button
                onClick={handleLogout}
                className="text-sm text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>

      {/* AI Disclosure Banner */}
      <AIDisclosureBanner />
    </div>
  );
}
