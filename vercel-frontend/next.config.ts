import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Allow large audio file uploads through the proxy route
  api: {
    bodyParser: {
      sizeLimit: "50mb",
    },
  },
};

export default nextConfig;
