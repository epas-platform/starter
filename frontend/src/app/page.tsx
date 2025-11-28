'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { getAccessToken, isTokenExpired } from '@/lib/auth';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    const token = getAccessToken();

    if (token && !isTokenExpired(token)) {
      router.push('/dashboard');
    } else {
      router.push('/login');
    }
  }, [router]);

  return (
    <main className="flex min-h-screen items-center justify-center">
      <div className="text-center">
        <h1 className="text-2xl font-bold">Cradle</h1>
        <p className="text-gray-500 mt-2">Loading...</p>
      </div>
    </main>
  );
}
