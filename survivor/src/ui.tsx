import React from "react";
import { C } from "./world";
import { FONT_BODY } from "./fonts";

/** 把“【重点】”标记解析为高亮片段 */
export const Highlight: React.FC<{ text: string; color?: string }> = ({ text, color = C.gold }) => {
  const parts = text.split(/(【[^】]*】)/).filter(Boolean);
  return (
    <>
      {parts.map((p, i) =>
        p.startsWith("【") ? (
          <span key={i} style={{ color }}>
            {p.slice(1, -1)}
          </span>
        ) : (
          <span key={i}>{p}</span>
        ),
      )}
    </>
  );
};

export const Pill: React.FC<{
  children: React.ReactNode;
  bg?: string;
  color?: string;
  size?: number;
  style?: React.CSSProperties;
}> = ({ children, bg = "rgba(244,234,213,0.12)", color = C.cream, size = 36, style }) => (
  <div
    style={{
      display: "inline-flex",
      alignItems: "center",
      gap: 12,
      padding: `${size * 0.28}px ${size * 0.6}px`,
      borderRadius: size,
      background: bg,
      color,
      fontFamily: FONT_BODY,
      fontWeight: 700,
      fontSize: size,
      lineHeight: 1.2,
      whiteSpace: "nowrap",
      ...style,
    }}
  >
    {children}
  </div>
);

/**
 * 硬币：angle 为绕水平轴的翻转角，cos(angle) ≥ 0 时显示 front 面。
 * 用纵向压缩模拟翻转，纯 SVG 绘制。
 */
export const Coin: React.FC<{ x: number; y: number; d: number; angle: number; front: string; back: string; opacity?: number }> = ({
  x,
  y,
  d,
  angle,
  front,
  back,
  opacity = 1,
}) => {
  const c = Math.cos(angle);
  const sy = Math.max(0.06, Math.abs(c));
  const face = c >= 0 ? front : back;
  const edge = 10;
  return (
    <svg
      width={d + 20}
      height={d + 40}
      style={{ position: "absolute", left: x - d / 2 - 10, top: y - d / 2 - 20, opacity, overflow: "visible" }}
    >
      <defs>
        <radialGradient id="coinG" cx="40%" cy="35%" r="70%">
          <stop offset="0%" stopColor="#FFE8A3" />
          <stop offset="60%" stopColor={C.gold} />
          <stop offset="100%" stopColor={C.goldDeep} />
        </radialGradient>
      </defs>
      <g transform={`translate(${d / 2 + 10} ${d / 2 + 20}) scale(1 ${sy})`}>
        <ellipse cx={0} cy={edge * (c >= 0 ? 1 : -1) * 0.6} rx={d / 2} ry={d / 2} fill={C.goldDeep} />
        <circle r={d / 2} fill="url(#coinG)" />
        <circle r={d / 2 - 9} fill="none" stroke="#FFF1C4" strokeWidth={4} opacity={0.8} />
        <text
          textAnchor="middle"
          dominantBaseline="central"
          fontFamily={FONT_BODY}
          fontWeight={900}
          fontSize={d * 0.48}
          fill="#7A4E0E"
        >
          {face}
        </text>
      </g>
    </svg>
  );
};

export const abs = (x: number, y: number, extra?: React.CSSProperties): React.CSSProperties => ({
  position: "absolute",
  left: x,
  top: y,
  ...extra,
});
