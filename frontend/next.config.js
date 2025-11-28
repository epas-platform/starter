/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',

  // Rewrites for API proxy (optional - can call backend directly)
  async rewrites() {
    return [
      {
        source: '/api/backend/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
