import React from "react";
import { backOut, clamp, prog } from "../anim";
import { N } from "../data";
import { FONT_BODY, FONT_FUN } from "../fonts";
import { TL } from "../timeline";
import { Highlight, Pill, abs } from "../ui";
import { BUBBLE_PEOPLE, C, Cam, GURU_CAM, personPos, toScreen, toWorld } from "../world";

const ev = TL.events;
const sc = TL.scenes;

/** 冠军开课时三个“秘诀”卡片：锚定在世界坐标里，镜头拉远时随之缩小 */
const SECRETS: { text: string; x: number; y: number; rot: number }[] = [
  { text: "① 相信自己", x: 290, y: 420, rot: -5 },
  { text: "② 坚持判断", x: 790, y: 540, rot: 4 },
  { text: "③ 保持手感", x: 540, y: 655, rot: -2 },
];
const SECRET_WORLD = SECRETS.map((s) => toWorld(GURU_CAM, s.x, s.y));
const BANNER_WORLD = toWorld(GURU_CAM, 540, 255);

/** 取景框：暂停时屏幕上“你刚才看到的画面”，换算到世界坐标后随镜头拉远而缩小 */
const VF = [toWorld(GURU_CAM, 80, 250), toWorld(GURU_CAM, 1000, 1580)];
export const viewfinderRect = (cam: Cam) => {
  const [x0, y0] = toScreen(cam, VF[0][0], VF[0][1]);
  const [x1, y1] = toScreen(cam, VF[1][0], VF[1][1]);
  return { x0, y0, x1, y1 };
};

export const GuruOverlay: React.FC<{ t: number; cam: Cam }> = ({ t, cam }) => {
  if (t < sc.guru[0] || t > sc.reveal[1]) return null;
  const z = cam.s / GURU_CAM.s;
  const fadeSmall = clamp((z - 0.12) / 0.2);
  const [bx, by] = toScreen(cam, BANNER_WORLD[0], BANNER_WORLD[1]);
  const banner = backOut(prog(t, ev.podium + 0.2, ev.podium + 0.6)) * (1 - prog(t, ev.freeze, ev.freeze + 0.2));
  return (
    <div style={{ opacity: fadeSmall }}>
      {banner > 0 && (
        <div
          style={abs(bx, by, {
            transform: `translate(-50%,-50%) scale(${z * banner})`,
            fontFamily: FONT_FUN,
            fontSize: 64,
            opacity: Math.min(1, banner),
            color: C.gold,
            whiteSpace: "nowrap",
            textShadow: "0 4px 0 rgba(0,0,0,0.35)",
          })}
        >
          ★ 十连胜冠军 · 成功秘诀分享会 ★
        </div>
      )}
      {SECRETS.map((s, i) => {
        const at = ev.secrets[i];
        const k = backOut(prog(t, at, at + 0.35));
        if (k <= 0) return null;
        const [x, y] = toScreen(cam, SECRET_WORLD[i][0], SECRET_WORLD[i][1]);
        return (
          <div
            key={i}
            style={abs(x, y, {
              transform: `translate(-50%,-50%) rotate(${s.rot}deg) scale(${k * z})`,
              background: C.cream,
              color: C.ink,
              borderRadius: 22,
              padding: "16px 36px",
              fontFamily: FONT_BODY,
              fontWeight: 900,
              fontSize: 62,
              whiteSpace: "nowrap",
              boxShadow: "0 10px 0 rgba(0,0,0,0.25)",
            })}
          >
            {s.text}
          </div>
        );
      })}
    </div>
  );
};

/** 暂停：定格标识、取景框、提问 */
export const FreezeOverlay: React.FC<{ t: number; cam: Cam }> = ({ t, cam }) => {
  if (t < ev.freeze || t > sc.name[0] + 1) return null;
  const pause = prog(t, ev.freeze, ev.freeze + 0.1) * (1 - prog(t, ev.zoom1[0], ev.zoom1[0] + 0.3));
  const vfIn = prog(t, ev.viewfinder, ev.viewfinder + 0.35);
  const vfOut = 1 - prog(t, sc.name[0], sc.name[0] + 0.25);
  const { x0, y0, x1, y1 } = viewfinderRect(cam);
  // 括角先从屏幕边缘收拢到取景框位置
  const grow = 1 - backOut(vfIn);
  const gx0 = x0 - grow * 60;
  const gy0 = y0 - grow * 60;
  const gx1 = x1 + grow * 60;
  const gy1 = y1 + grow * 60;
  const w = gx1 - gx0;
  const h = gy1 - gy0;
  const arm = Math.max(10, Math.min(90, Math.min(w, h) * 0.25));
  const lw = Math.max(3, Math.min(10, w * 0.012));
  const q2 = prog(t, TL.lines.find((l) => l.id === "freeze2")!.start, TL.lines.find((l) => l.id === "freeze2")!.start + 0.3);
  const qOut = 1 - prog(t, ev.zoom1[0], ev.zoom1[0] + 0.3);
  const label = prog(t, ev.zoom1[0] + 1.0, ev.zoom1[0] + 1.4);
  return (
    <>
      {pause > 0 && (
        <Pill size={40} bg="rgba(12,26,56,0.75)" style={abs(1000, 186, { transform: "translateX(-100%)", opacity: pause })}>
          ❚❚ 暂停
        </Pill>
      )}
      {vfIn > 0 && (
        <svg width={1080} height={1920} style={abs(0, 0, { opacity: vfIn * vfOut })}>
          <rect x={gx0} y={gy0} width={w} height={h} fill="none" stroke={C.gold} strokeOpacity={0.45} strokeWidth={Math.max(1.5, lw * 0.35)} strokeDasharray="14 10" />
          {[
            [gx0, gy0, 1, 1],
            [gx1, gy0, -1, 1],
            [gx0, gy1, 1, -1],
            [gx1, gy1, -1, -1],
          ].map(([x, y, dx, dy], i) => (
            <path key={i} d={`M ${x} ${y + dy * arm} L ${x} ${y} L ${x + dx * arm} ${y}`} stroke={C.gold} strokeWidth={lw} fill="none" strokeLinecap="round" />
          ))}
        </svg>
      )}
      {label > 0 && (
        <Pill
          size={32}
          bg={C.gold}
          color={C.ink}
          style={abs((x0 + x1) / 2, y0 - 66, { transform: "translateX(-50%)", opacity: label * vfOut })}
        >
          ▼ 刚才的画面只有这里
        </Pill>
      )}
      {q2 * qOut > 0 && (
        <div
          style={abs(540, 300, {
            transform: `translate(-50%,-50%) scale(${backOut(q2)})`,
            opacity: qOut,
            fontFamily: FONT_FUN,
            fontSize: 100,
            color: C.gold,
            whiteSpace: "nowrap",
            textShadow: "0 6px 0 rgba(0,0,0,0.4)",
          })}
        >
          其他人呢？
        </div>
      )}
    </>
  );
};

/** 主反转：字幕卡、人数对照、退出者的“我也……” */
export const RevealOverlay: React.FC<{ t: number; cam: Cam }> = ({ t, cam }) => {
  if (t < ev.zoom1[0] || t > sc.name[0] + 0.6) return null;
  const out = 1 - prog(t, sc.name[0], sc.name[0] + 0.4);
  const cap = backOut(prog(t, ev.caption, ev.caption + 0.35));
  const counts = prog(t, ev.zoom2[1] - 0.4, ev.zoom2[1]);
  return (
    <div style={{ opacity: out }}>
      {cap > 0 && (
        <div
          style={abs(540, 232, {
            transform: `translateX(-50%) scale(${cap})`,
            fontFamily: FONT_BODY,
            fontWeight: 900,
            fontSize: 70,
            color: C.cream,
            whiteSpace: "nowrap",
            textShadow: "0 5px 0 rgba(0,0,0,0.35)",
          })}
        >
          <Highlight text="只看赢家，【漏掉其他人。】" />
        </div>
      )}
      {counts > 0 && (
        <div style={abs(540, 345, { transform: "translateX(-50%)", display: "flex", gap: 24, opacity: counts })}>
          <Pill size={38} bg="rgba(245,192,74,0.2)" color={C.gold}>
            ● 冠军 1 人
          </Pill>
          <Pill size={38} bg="rgba(90,100,126,0.5)">
            ● 出局 {N - 1} 人
          </Pill>
        </div>
      )}
      {BUBBLE_PEOPLE.map((b, i) => {
        const at = ev.bubbles + 0.25 + i * 0.32;
        const k = backOut(prog(t, at, at + 0.3));
        if (k <= 0) return null;
        const [wx, wy] = personPos(b.id, t);
        const [x, y] = toScreen(cam, wx, wy);
        return (
          <div key={i} style={abs(x, y - 0.5 * cam.s - 14, { transform: `translate(-50%,-100%) scale(${k})`, transformOrigin: "50% 100%" })}>
            <div
              style={{
                background: "#E9EDF5",
                color: C.ink,
                fontFamily: FONT_BODY,
                fontWeight: 900,
                fontSize: 34,
                padding: "10px 22px",
                borderRadius: 26,
                whiteSpace: "nowrap",
                boxShadow: "0 6px 0 rgba(0,0,0,0.3)",
              }}
            >
              {b.text}
            </div>
            <div style={{ width: 0, height: 0, margin: "0 auto", borderLeft: "12px solid transparent", borderRight: "12px solid transparent", borderTop: "16px solid #E9EDF5" }} />
          </div>
        );
      })}
    </div>
  );
};
