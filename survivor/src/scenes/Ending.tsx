import React, { useLayoutEffect, useRef } from "react";
import { backOut, easeInOut, lerp, prog } from "../anim";
import { FONT_BODY, FONT_FUN } from "../fonts";
import { TL } from "../timeline";
import { Highlight, Pill, abs } from "../ui";
import { C, Cam, PersonStyle, drawCrown, drawPerson } from "../world";
import { viewfinderRect } from "./Reveal";

const ev = TL.events;
const sc = TL.scenes;

type Figure = { x: number; y: number; u: number; style: PersonStyle; crown?: boolean };

/** 屏幕坐标下的一组小人（与世界层同一套绘制函数） */
export const PeopleCanvas: React.FC<{ figures: Figure[]; width: number; height: number; style?: React.CSSProperties }> = ({
  figures,
  width,
  height,
  style,
}) => {
  const ref = useRef<HTMLCanvasElement>(null);
  useLayoutEffect(() => {
    const ctx = ref.current?.getContext("2d");
    if (!ctx) return;
    ctx.clearRect(0, 0, width, height);
    for (const f of figures) {
      drawPerson(ctx, f.x, f.y, f.u, f.style);
      if (f.crown) drawCrown(ctx, f.x, f.y - 0.38 * f.u, f.u);
    }
  });
  return <canvas ref={ref} width={width} height={height} style={{ position: "absolute", ...style }} />;
};

const PHONE = { cx: 540, cy: 990, w: 520, h: 840 };
const GROUP = [680, 805, 930].flatMap((x, i) => [840, 970, 1100, 1230].map((y, j) => ({ x, y, k: i * 4 + j })));

/** 命名与现实迁移 + 结尾：取景框变成手机经验卡片，再拉远出现“没考上的人”，最后并排比较 */
export const Ending: React.FC<{ t: number; cam: Cam }> = ({ t, cam }) => {
  if (t < ev.phone) return null;
  const dim = prog(t, ev.phone, ev.phone + 0.7);
  const morph = easeInOut(prog(t, ev.phone, ev.phone + 0.75));
  const vf = viewfinderRect(cam);
  const fromW = vf.x1 - vf.x0;
  const fromH = vf.y1 - vf.y0;
  const w = lerp(fromW, PHONE.w, morph);
  const h = lerp(fromH, PHONE.h, morph);
  const cx = lerp((vf.x0 + vf.x1) / 2, PHONE.cx, morph);
  const cy = lerp((vf.y0 + vf.y1) / 2, PHONE.cy, morph);
  const move = easeInOut(prog(t, ev.others, ev.others + 0.6));
  const pScale = lerp(1, 0.68, move);
  const pcx = lerp(cx, 300, move);
  const pcy = lerp(cy, 1000, move);
  const content = prog(t, ev.phone + 0.5, ev.phone + 0.9);
  const finalK = prog(t, ev.final, ev.final + 0.5);
  const sceneDim = 1 - 0.7 * finalK;

  const termK = backOut(prog(t, ev.term, ev.term + 0.4));
  const name2 = TL.lines.find((l) => l.id === "name2")!.start;
  const defK = prog(t, name2, name2 + 0.3);
  const topOut = 1 - prog(t, sc.outro[0] - 0.1, sc.outro[0] + 0.3);

  const checks: [number, string, string][] = [
    [ev.reference, "✓", "经验可以参考"],
    [ev.compare, "？", "做法相同、却没成功的人呢"],
    [ev.compare + 1.1, "？", "还有没有其他解释"],
  ];

  return (
    <>
      <div style={abs(0, 0, { width: 1080, height: 1920, background: C.bg, opacity: 0.84 * dim })} />
      <div style={{ opacity: sceneDim }}>
        {termK > 0 && topOut > 0 && (
          <div style={abs(540, 190, { transform: `translateX(-50%) scale(${termK})`, textAlign: "center", opacity: topOut })}>
            <div style={{ fontFamily: FONT_FUN, fontSize: 124, color: C.gold, lineHeight: 1.05, whiteSpace: "nowrap" }}>幸存者偏差</div>
          </div>
        )}
        {defK > 0 && topOut > 0 && (
          <Pill size={38} style={abs(540, 352, { transform: "translateX(-50%)", opacity: defK * topOut })}>
            只看“留下来”的样本 → 可能误判全貌
          </Pill>
        )}
        {checks.map(([at, mark, text], i) => {
          const k = prog(t, at, at + 0.3);
          if (k <= 0) return null;
          return (
            <div
              key={i}
              style={abs(130, 200 + i * 86, {
                opacity: k,
                transform: `translateX(${(1 - k) * -30}px)`,
                display: "flex",
                alignItems: "center",
                gap: 20,
                fontFamily: FONT_BODY,
                fontWeight: 900,
                fontSize: 46,
                color: C.cream,
                whiteSpace: "nowrap",
              })}
            >
              <span
                style={{
                  display: "inline-flex",
                  width: 62,
                  height: 62,
                  borderRadius: 31,
                  alignItems: "center",
                  justifyContent: "center",
                  background: mark === "✓" ? C.gold : "rgba(244,234,213,0.18)",
                  color: mark === "✓" ? C.ink : C.cream,
                }}
              >
                {mark}
              </span>
              {text}
            </div>
          );
        })}

        {/* 手机经验卡片（虚构） */}
        <div
          style={abs(pcx, pcy, {
            width: w,
            height: h,
            transform: `translate(-50%,-50%) scale(${pScale})`,
            borderRadius: lerp(4, 56, morph),
            border: `${lerp(4, 12, morph)}px solid ${morph < 0.5 ? C.gold : "#2A3B66"}`,
            background: `rgba(244,234,213,${0.97 * content})`,
            overflow: "hidden",
            boxShadow: `0 0 0 6px rgba(245,192,74,${0.6 * move}), 0 24px 60px rgba(0,0,0,0.4)`,
          })}
        >
          {content > 0 && <PhoneContent opacity={content} />}
        </div>

        <Others t={t} />
        <Compare t={t} />
      </div>
      {finalK > 0 && <FinalLine t={t} />}
    </>
  );
};

const PhoneContent: React.FC<{ opacity: number }> = ({ opacity }) => (
  <div style={{ opacity, padding: "34px 40px", fontFamily: FONT_BODY, color: C.ink, position: "relative", height: "100%", boxSizing: "border-box" }}>
    <div style={{ display: "flex", justifyContent: "space-between", fontSize: 26, fontWeight: 700, opacity: 0.55 }}>
      <span>经验分享</span>
      <span>· · ·</span>
    </div>
    <div style={{ display: "flex", alignItems: "center", gap: 20, marginTop: 34 }}>
      <div style={{ width: 96, height: 96, borderRadius: 48, background: C.bg2, position: "relative", overflow: "hidden" }}>
        <PeopleCanvas
          width={96}
          height={96}
          figures={[{ x: 48, y: 62, u: 110, style: { body: C.gold, head: "#FFD772" }, crown: true }]}
        />
      </div>
      <div>
        <div style={{ fontSize: 34, fontWeight: 900 }}>学姐小林</div>
        <div style={{ fontSize: 24, fontWeight: 700, opacity: 0.55 }}>虚构人物 · 仅作示意</div>
      </div>
    </div>
    <div style={{ fontSize: 46, fontWeight: 900, marginTop: 40, lineHeight: 1.25, whiteSpace: "nowrap" }}>我是怎样考上名校的</div>
    <div style={{ fontSize: 34, fontWeight: 700, marginTop: 30, lineHeight: 1.85 }}>
      <div>· 每天早起背单词</div>
      <div>· 错题本反复刷</div>
      <div>· 相信自己，坚持到底</div>
    </div>
    <div
      style={{
        position: "absolute",
        right: 36,
        top: 620,
        transform: "rotate(-10deg)",
        border: `5px solid ${C.goldDeep}`,
        color: C.goldDeep,
        borderRadius: 14,
        padding: "4px 18px",
        fontSize: 40,
        fontWeight: 900,
      }}
    >
      考上了 ✓
    </div>
    <div style={{ position: "absolute", left: 40, right: 40, bottom: 36, display: "flex", justifyContent: "space-between", fontSize: 30, fontWeight: 700, opacity: 0.6 }}>
      <span>♥ 赞</span>
      <span>☆ 收藏</span>
      <span>↗ 转发</span>
    </div>
  </div>
);

/** 采用相似方法、但没考上的人（虚构示意） */
const Others: React.FC<{ t: number }> = ({ t }) => {
  if (t < ev.others) return null;
  const label = prog(t, ev.others + 0.3, ev.others + 0.6);
  const figures: Figure[] = GROUP.map(({ x, y, k }) => {
    const s = backOut(prog(t, ev.others + 0.15 + k * 0.05, ev.others + 0.45 + k * 0.05));
    const bob = Math.sin((t * 1.4 + k * 0.37) * Math.PI * 2) * 2;
    return { x, y: y + bob, u: 120 * s, style: { body: C.grey, head: C.greyHead, look: [-1, 0], sad: true, alpha: s > 0 ? 1 : 0 } };
  });
  return (
    <>
      <PeopleCanvas figures={figures} width={1080} height={1920} style={{ left: 0, top: 0 }} />
      <div
        style={abs(805, 700, {
          transform: "translate(-50%,-50%)",
          opacity: label,
          textAlign: "center",
          fontFamily: FONT_BODY,
          fontWeight: 900,
          fontSize: 38,
          lineHeight: 1.3,
          color: C.cream,
          whiteSpace: "nowrap",
        })}
      >
        采用相似方法
        <br />
        但<span style={{ color: "#AEB8D0" }}>没考上</span>的人
      </div>
      <div style={abs(805, 1300, { transform: "translateX(-50%)", opacity: label * 0.8, fontFamily: FONT_BODY, fontWeight: 700, fontSize: 28, color: "#AEB8D0", whiteSpace: "nowrap" })}>
        （虚构示意）
      </div>
    </>
  );
};

/** 比较标记：把赢家和“同样做法却没成功的人”放在一起看 */
const Compare: React.FC<{ t: number }> = ({ t }) => {
  if (t < ev.compare) return null;
  const k = easeInOut(prog(t, ev.compare, ev.compare + 0.6));
  const x0 = 120;
  const x1 = 1000;
  const y = 1345;
  const mid = 540;
  const len = (x1 - x0) / 2;
  return (
    <>
      <svg width={1080} height={1920} style={abs(0, 0)}>
        <path
          d={`M ${mid - len * k} ${y - 26} L ${mid - len * k} ${y} L ${mid + len * k} ${y} L ${mid + len * k} ${y - 26}`}
          stroke={C.gold}
          strokeWidth={6}
          fill="none"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
      <div style={abs(540, 1000, { transform: `translate(-50%,-50%) scale(${backOut(prog(t, ev.compare + 0.2, ev.compare + 0.5))})` })}>
        <div style={{ width: 92, height: 92, borderRadius: 46, background: C.gold, color: C.ink, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: FONT_BODY, fontWeight: 900, fontSize: 52 }}>
          ⇄
        </div>
      </div>
      <Pill size={36} bg={C.gold} color={C.ink} style={abs(540, y + 18, { transform: "translateX(-50%)", opacity: k })}>
        放在一起比较
      </Pill>
    </>
  );
};

/** 最后一句大字：保留到片尾（≥2 秒） */
const FinalLine: React.FC<{ t: number }> = ({ t }) => {
  const a = prog(t, ev.final, ev.final + 0.4);
  const b = prog(t, ev.final + 0.9, ev.final + 1.3);
  return (
    <div
      style={abs(0, 760, {
        width: 1080,
        height: 420,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        background: `rgba(12,26,56,${0.88 * a})`,
        fontFamily: FONT_BODY,
        fontWeight: 900,
        textAlign: "center",
      })}
    >
      <div style={{ fontSize: 88, color: C.cream, opacity: a, transform: `translateY(${(1 - a) * 20}px)` }}>做了同样的事，</div>
      <div style={{ fontSize: 100, color: C.gold, marginTop: 18, opacity: b, transform: `translateY(${(1 - b) * 20}px)` }}>
        <Highlight text="却没成功的人呢？" />
      </div>
    </div>
  );
};
