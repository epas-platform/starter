'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import { Plus, Search, Settings, ExternalLink } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { api } from '@/lib/api';
import type { User, HealthResponse } from '@/types';

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [userData, healthData] = await Promise.all([
          api.getCurrentUser(),
          api.health(),
        ]);
        setUser(userData);
        setHealth(healthData);
      } catch (err) {
        console.error('Failed to load dashboard data:', err);
        toast.error('Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  if (loading) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Loading dashboard...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold tracking-tight">Dashboard</h2>

      {/* Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>API Status</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <span
                className={`inline-block w-3 h-3 rounded-full ${
                  health?.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'
                }`}
              />
              <span className="text-2xl font-bold capitalize">
                {health?.status || 'Unknown'}
              </span>
            </div>
            <p className="text-sm text-muted-foreground mt-1">
              v{health?.version || '-'} / {health?.profile || '-'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Logged In As</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold truncate">
              {user?.full_name || user?.email || '-'}
            </p>
            <p className="text-sm text-muted-foreground mt-1">
              Roles: {user?.roles?.join(', ') || 'user'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Tenant ID</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm font-mono truncate">
              {user?.tenant_id || '-'}
            </p>
            <p className="text-sm text-muted-foreground mt-1">
              Created: {user?.created_at ? new Date(user.created_at).toLocaleDateString() : '-'}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Button
              variant="outline"
              className="h-24 flex-col gap-2"
              onClick={() => toast.info('New Project', { description: 'Coming soon!' })}
            >
              <Plus className="h-6 w-6" />
              <span>New Project</span>
            </Button>
            <Button
              variant="outline"
              className="h-24 flex-col gap-2"
              onClick={() => toast.info('Search', { description: 'Coming soon!' })}
            >
              <Search className="h-6 w-6" />
              <span>Search</span>
            </Button>
            <Button
              variant="outline"
              className="h-24 flex-col gap-2"
              onClick={() => router.push('/settings')}
            >
              <Settings className="h-6 w-6" />
              <span>Settings</span>
            </Button>
            <Button
              variant="outline"
              className="h-24 flex-col gap-2"
              onClick={() => window.open('http://localhost:8010/docs', '_blank')}
            >
              <ExternalLink className="h-6 w-6" />
              <span>API Docs</span>
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Getting Started */}
      <Card className="bg-primary/5 border-primary/20">
        <CardHeader>
          <CardTitle>Getting Started</CardTitle>
          <CardDescription>
            Welcome to Cradle! This is a quickstart boilerplate based on the Enterprise
            Multi-Platform Architecture Specification.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ul className="text-sm text-muted-foreground list-disc list-inside space-y-1">
            <li>FastAPI backend with JWT authentication</li>
            <li>Next.js frontend with TypeScript</li>
            <li>LocalStack for AWS service emulation</li>
            <li>PostgreSQL + Redis infrastructure</li>
            <li>Profile-based configuration (dev/prod)</li>
            <li>Audit logging foundation for compliance</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
