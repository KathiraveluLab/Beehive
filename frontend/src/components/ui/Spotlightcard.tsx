import React, { useRef, useState } from "react";
import { useTheme } from "../../context/ThemeContext";

// Spotlight color constants
const DARK_THEME_SPOTLIGHT_COLOR = "rgba(255, 255, 255, 0.25)";
const LIGHT_THEME_SPOTLIGHT_COLOR = "rgba(253, 224, 71, 0.35)";

interface Position {
  x: number;
  y: number;
}

interface SpotlightCardProps extends React.PropsWithChildren {
  className?: string;
  spotlightColor?: string;
}

const SpotlightCard: React.FC<SpotlightCardProps> = ({
  children,
  className = "",
  spotlightColor,
}) => {
  const { theme } = useTheme();
  const divRef = useRef<HTMLDivElement>(null);
  const [isFocused, setIsFocused] = useState<boolean>(false);
  const [position, setPosition] = useState<Position>({ x: 0, y: 0 });
  const [opacity, setOpacity] = useState<number>(0);

  const defaultSpotlightColor = theme === "dark"
    ? DARK_THEME_SPOTLIGHT_COLOR
    : LIGHT_THEME_SPOTLIGHT_COLOR;
  const resolvedSpotlightColor = spotlightColor ?? defaultSpotlightColor;

  const handleMouseMove: React.MouseEventHandler<HTMLDivElement> = (e) => {
    if (!divRef.current || isFocused) return;

    const rect = divRef.current.getBoundingClientRect();
    setPosition({ x: e.clientX - rect.left, y: e.clientY - rect.top });
  };

  const handleFocus = () => {
    setIsFocused(true);
    setOpacity(0.6);
  };

  const handleBlur = () => {
    setIsFocused(false);
    setOpacity(0);
  };

  const handleMouseEnter = () => {
    setOpacity(0.6);
  };

  const handleMouseLeave = () => {
    setOpacity(0);
  };

  return (
    <div
      ref={divRef}
      onMouseMove={handleMouseMove}
      onFocus={handleFocus}
      onBlur={handleBlur}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      className={`relative rounded-3xl border bg-white border-neutral-200 text-neutral-900 shadow-lg transition-colors duration-300 overflow-hidden p-8 dark:bg-neutral-900 dark:border-neutral-800 dark:text-white ${className}`}
    >
      <div
        className="pointer-events-none absolute inset-0 opacity-0 transition-opacity duration-500 ease-in-out"
        style={{
          opacity,
          background: `radial-gradient(circle at ${position.x}px ${position.y}px, ${resolvedSpotlightColor}, transparent 80%)`,
        }}
      />
      {children}
    </div>
  );
};

export default SpotlightCard;