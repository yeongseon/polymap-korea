const nextConfig = {
  output: "export",
  basePath: "/polymap-korea",
  reactStrictMode: true,
  images: {
    unoptimized: true,
    remotePatterns: [
      { protocol: "https", hostname: "**.nec.go.kr" },
      { protocol: "https", hostname: "**.assembly.go.kr" },
      { protocol: "https", hostname: "**.githubusercontent.com" },
    ],
  },
  trailingSlash: true,
};

module.exports = nextConfig;
