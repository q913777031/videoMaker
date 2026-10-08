import React from "react";
import { prog } from "../anim";
import { FONT_BODY } from "../fonts";
import { Line, TL } from "../timeline";
import { Highlight, Pill } from "../ui";
import { C } from "../world";

/** 由大字承担的台词不再重复显示底部字幕 */
const HIDDEN = new Set(["outro4"]);
const MAX_CHARS = 15;

/** 超长字幕在最接近中点的逗号处断成两行，保证语义完整、最多两行 */
const splitLines = (sub: string): string[] => {
  const plain = sub.replace(/[【】]/g, "");
  if (plain.length <= MAX_CHARS) return [sub];
  let best = -1;
  let bestScore = Infinity;
  let plainIdx = 0;
  for (let i = 0; i < sub.length; i++) {
    const ch = sub[i];
    if (ch === "【" || ch === "】") continue;
    plainIdx++;
    if ("，、：".includes(ch)) {
      const score = Math.abs(plainIdx - plain.length / 2);
      if (score < bestScore) {
        bestScore = score;
        best = i + 1;
      }
    }
  }
  if (best < 0) return [sub];
  // 断点落在【】内部时，两侧各自补齐标记
  const head = sub.slice(0, best);
  const tail = sub.slice(best);
  const open = (head.match(/【/g) ?? []).length > (head.match(/】/g) ?? []).length;
  return open ? [head + "】", "【" + tail] : [head, tail];
};

const active = (t: number): Line | undefined => {
  const lines = TL.lines;
  for (let i = 0; i < lines.length; i++) {
    const l = lines[i];
    const next = lines[i + 1];
    const until = Math.min(l.end + 0.35, next ? next.start : Infinity);
    if (t >= l.start - 0.05 && t < until) return l;
  }
  return undefined;
};

export const Subtitles: React.FC<{ t: number }> = ({ t }) => {
  const l = active(t);
  if (!l || HIDDEN.has(l.id)) return null;
  const a = prog(t, l.start - 0.05, l.start + 0.08);
  const rows = splitLines(l.sub);
  return (
    <div
      style={{
        position: "absolute",
        left: 80,
        right: 80,
        bottom: 1920 - 1610,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        opacity: a,
      }}
    >
      {l.speaker === "c" && (
        <Pill size={28} bg={C.gold} color={C.ink} style={{ marginBottom: 10 }}>
          冠军
        </Pill>
      )}
      <div
        style={{
          background: "rgba(6,12,30,0.62)",
          borderRadius: 20,
          padding: "12px 28px",
          textAlign: "center",
          fontFamily: FONT_BODY,
          fontWeight: 900,
          fontSize: 58,
          lineHeight: 1.32,
          color: "#FFFFFF",
        }}
      >
        {rows.map((r, i) => (
          <div key={i} style={{ whiteSpace: "nowrap" }}>
            <Highlight text={r} />
          </div>
        ))}
      </div>
    </div>
  );
};
