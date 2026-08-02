import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  transpilePackages: ["next-auth"],

  eslint: {
    ignoreDuringBuilds: true,
  },

  async rewrites() {
    const backendUrl =
      process.env.BACKEND_INTERNAL_URL ||
      process.env.NEXT_PUBLIC_API_URL?.replace(/\/api\/?$/, "") ||
      "http://localhost:8000";

    return {
      beforeFiles: [
        // Don't rewrite NextAuth routes
        {
          source: "/api/auth/:path*",
          destination: "/api/auth/:path*",
        },
      ],
      fallback: [
        // Everything else goes to FastAPI
        {
          source: "/api/:path*",
          destination: `${backendUrl}/api/:path*`,
        },
      ],
    };
  },
};

export default nextConfig;