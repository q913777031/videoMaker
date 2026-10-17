import React from "react";
import { AbsoluteFill } from "remotion";
import { FONT_BODY, FONT_FUN } from "./fonts";
import { Background } from "./Main";
import { TL } from "./timeline";
import { Pill } from "./ui";
import { WorldCanvas } from "./WorldCanvas";
import { C, Cam, toScreen } from "./world";

/** 竖屏封面：取景框里的金色冠军，框外是被忽略的灰色人群 */
const COVER_CAM: Cam = { cx: 0, cy: -1.2, s: 150 };
const COVER_T = TL.events.caption;

export const Cover: React.FC = () => {
  const [x0, y0] = toScreen(COVER_CAM, -1.15, -1.05);
  const [x1, y1] = toScreen(COVER_CAM, 1.15, 1.25);
  const arm = 60;
  return (
    <AbsoluteFill style={{ backgroundColor: C.bg }}>
      <Background />
      <WorldCanvas t={COVER_T} cam={COVER_CAM} />
      <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(12,26,56,0.95) 0%, rgba(12,26,56,0.7) 30%, rgba(12,26,56,0) 45%)" }} />
      <svg width={1080} height={1920} style={{ position: "absolute", left: 0, top: 0 }}>
        {[
          [x0, y0, 1, 1],
          [x1, y0, -1, 1],
          [x0, y1, 1, -1],
          [x1, y1, -1, -1],
        ].map(([x, y, dx, dy], i) => (
          <path key={i} d={`M ${x} ${y + dy * arm} L ${x} ${y} L ${x + dx * arm} ${y}`} stroke={C.gold} strokeWidth={10} fill="none" strokeLinecap="round" />
        ))}
      </svg>
      <div style={{ position: "absolute", left: 80, right: 80, top: 210, textAlign: "center", fontFamily: FONT_FUN, lineHeight: 1.15 }}>
        <div style={{ fontSize: 112, color: C.cream }}>他连续赢了10次，</div>
        <div style={{ fontSize: 112, color: C.gold }}>然后开始教你成功</div>
      </div>
      <div style={{ position: "absolute", left: 0, right: 0, top: 520, display: "flex", justifyContent: "center" }}>
        <Pill size={44} bg="rgba(244,234,213,0.16)">
          框外还有 1023 人 · 幸存者偏差
        </Pill>
      </div>
      <div style={{ position: "absolute", left: 0, right: 0, bottom: 330, textAlign: "center", fontFamily: FONT_BODY, fontWeight: 900, fontSize: 56, color: C.cream }}>
        做了同样的事，<span style={{ color: C.gold }}>没成功的人呢？</span>
      </div>
    </AbsoluteFill>
  );
};
