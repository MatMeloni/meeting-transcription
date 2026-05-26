import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          from: "#6366f1",
          to: "#a855f7",
        },
      },
      keyframes: {
        pulse_ring: {
          "0%, 100%": { transform: "scale(1)", opacity: "0.6" },
          "50%": { transform: "scale(1.15)", opacity: "0" },
        },
        wave: {
          "0%, 100%": { transform: "scaleY(0.4)" },
          "50%": { transform: "scaleY(1)" },
        },
        fadein: {
          from: { opacity: "0", transform: "translateY(12px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
      },
      animation: {
        pulse_ring: "pulse_ring 2s ease-out infinite",
        wave: "wave 1.2s ease-in-out infinite",
        fadein: "fadein 0.4s ease forwards",
      },
    },
  },
  plugins: [],
};

export default config;
