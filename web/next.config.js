/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  
  // 环境变量
  env: {
    API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000',
  },
  
  // 输出配置
  output: 'standalone',
  
  // 图片配置
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
    ],
  },
  
  // 实验性功能
  experimental: {
    // 优化包导入
    optimizePackageImports: ['@heroicons/react', '@headlessui/react'],
  },
  
  // Webpack 配置
  webpack: (config) => {
    config.resolve.fallback = {
      ...config.resolve.fallback,
      fs: false,
      net: false,
      tls: false,
    };
    return config;
  },
};

module.exports = nextConfig;
