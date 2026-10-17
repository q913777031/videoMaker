import React from "react";
import { backOut, easeOut, prog } from "../anim";
import { PHASE, ROUNDS, coinHeads, currentRound, remainingAt } from "../data";
import { FONT_BODY, FONT_FUN } from "../fonts";
import { TL } from "../timeline";
import { Coin, Pill, abs } from "../ui";
import { C, appearedCount } from "../world";

const ev = TL.events;
const sc = TL.scenes;

/** 开场：先展示赢家——“连续猜中10次”盖章、定格在空中的硬币 */
export const HookOverlay: React.FC<{ t: number }> = ({ t }) => {
  if (t > sc.hook[1] + 0.6) return null;
  const k = prog(t, ev.stamp, ev.stamp + 0.18);
  const scale = 2.3 - 1.3 * easeOut(k);
  const shake = k >= 1 ? Math.sin((t - ev.stamp) * 60) * Math.exp(-(t - ev.stamp - 0.18) * 10) * 6 : 0;
  const fade = 1 - prog(t, sc.hook[1] - 0.25, sc.hook[1] + 0.1);
  const rewind = prog(t, sc.hook[1] - 0.45, sc.hook[1] - 0.3) * (1 - prog(t, sc.hook[1] + 0.3, sc.hook[1] + 0.55));
  return (
    <>
      <div style={{ opacity: fade }}>
        {k > 0 && (
          <div
            style={abs(540, 400, {
              transform: `translate(-50%,-50%) translate(${shake}px,0) rotate(-7deg) scale(${scale})`,
              opacity: Math.min(1, k * 2),
              border: `8px solid ${C.gold}`,
              outline: `3px solid ${C.gold}`,
              outlineOffset: 8,
              borderRadius: 18,
              padding: "14px 40px 10px",
              color: C.gold,
              fontFamily: FONT_FUN,
              fontSize: 108,
              whiteSpace: "nowrap",
              letterSpacing: 4,
            })}
          >
            连续猜中10次
          </div>
        )}
        {/* 定格在空中的硬币与运动线 */}
        <svg width={1080} height={900} style={abs(0, 380)}>
          {[0, 1, 2].map((i) => (
            <path
              key={i}
              d={`M ${700 + i * 22} ${520 - i * 6} q 30 -120 60 -230`}
              stroke={C.cream}
              strokeOpacity={0.35 - i * 0.08}
              strokeWidth={6}
              strokeLinecap="round"
              fill="none"
              strokeDasharray="20 18"
            />
          ))}
        </svg>
        <Coin x={790} y={600} d={150} angle={0.85} front="正" back="反" />
        <Pill size={30} bg="rgba(244,234,213,0.14)" style={abs(960, 585, { transform: "translateX(-50%)" })}>
          ❚❚ 定格
        </Pill>
      </div>
      {rewind > 0 && (
        <>
          <div style={abs(0, 0, { width: 1080, height: 1920, background: C.bg, opacity: rewind * 0.85 })} />
          <Pill size={52} bg="rgba(244,234,213,0.16)" style={abs(540, 960, { transform: "translate(-50%,-50%)", opacity: rewind })}>
            ⏪ 倒回开头
          </Pill>
        </>
      )}
    </>
  );
};

/** 游戏段 HUD：人数、轮次、教学示意、硬币与猜测图例 */
export const GameHud: React.FC<{ t: number }> = ({ t }) => {
  if (t < sc.setup[0] || t > sc.guru[0] + 0.6) return null;
  const fadeIn = prog(t, sc.setup[0] + 0.1, sc.setup[0] + 0.5);
  const fadeOut = 1 - prog(t, sc.guru[0], sc.guru[0] + 0.5);
  const a = fadeIn * fadeOut;
  const inRounds = t >= ev.rounds[0][0];
  const r = currentRound(t);
  const count = inRounds ? remainingAt(t) : appearedCount(t);
  // 计数在揭晓时刻跳变，配一个轻微的放大
  let pop = 1;
  if (inRounds) {
    for (let k = 1; k <= ROUNDS; k++) {
      const rt = ev.rounds[k - 1][0] + PHASE.result * ev.rounds[k - 1][1];
      const p = prog(t, rt, rt + 0.25);
      if (p > 0 && p < 1) pop = 1 + 0.18 * Math.sin(p * Math.PI);
    }
  }
  return (
    <div style={{ opacity: a }}>
      <div style={abs(540, 200, { transform: "translateX(-50%)", display: "flex", alignItems: "center", gap: 28 })}>
        <Pill size={38} bg="rgba(244,234,213,0.12)">
          {inRounds ? (
            <>
              第 <b style={{ color: C.gold, fontWeight: 900 }}>{r}</b> / {ROUNDS} 轮
            </>
          ) : (
            "32 × 32 方阵"
          )}
        </Pill>
        <div
          style={{
            fontFamily: FONT_BODY,
            fontWeight: 900,
            color: C.cream,
            fontSize: 92,
            lineHeight: 1,
            whiteSpace: "nowrap",
            transform: `scale(${pop})`,
            transformOrigin: "left center",
            minWidth: 330,
          }}
        >
          {count}
          <span style={{ fontSize: 44, fontWeight: 700, marginLeft: 8 }}>{inRounds ? "人在场" : "人"}</span>
        </div>
      </div>
      <Pill
        size={34}
        bg="rgba(245,192,74,0.16)"
        color="#FFE3A0"
        style={abs(540, 318, { transform: "translateX(-50%)" })}
      >
        ⓘ 教学示意：每轮按一半晋级
      </Pill>
      <RulesChips t={t} />
      {inRounds && <RoundCoin t={t} />}
    </div>
  );
};

const RulesChips: React.FC<{ t: number }> = ({ t }) => {
  const a = prog(t, ev.rules - 0.1, ev.rules + 0.2) * (1 - prog(t, ev.rounds[0][0], ev.rounds[0][0] + 0.3));
  if (a <= 0) return null;
  const s1 = backOut(prog(t, ev.rules - 0.1, ev.rules + 0.25));
  const s2 = backOut(prog(t, ev.rules + 0.6, ev.rules + 0.95));
  return (
    <div style={abs(540, 430, { transform: "translateX(-50%)", display: "flex", gap: 26, opacity: a })}>
      <Pill size={40} bg="rgba(90,100,126,0.55)" style={{ transform: `scale(${s1})` }}>
        猜错 → 变灰退出
      </Pill>
      <Pill size={40} bg="rgba(244,234,213,0.92)" color={C.ink} style={{ transform: `scale(${s2})` }}>
        猜对 → 继续
      </Pill>
    </div>
  );
};

const RoundCoin: React.FC<{ t: number }> = ({ t }) => {
  const r = Math.max(1, currentRound(t));
  const [st, d] = ev.rounds[r - 1];
  const lp = (t - st) / d;
  const heads = coinHeads[r - 1];
  const prevHeads = r > 1 ? coinHeads[r - 2] : true;
  const fp = prog(lp, PHASE.flip[0], PHASE.flip[1]);
  // 起始面为上一轮结果，旋转若干圈后停在本轮结果
  const turns = 6 * Math.PI + (heads === prevHeads ? 0 : Math.PI);
  const angle = easeOut(fp) * turns;
  const lift = Math.sin(fp * Math.PI) * 45;
  const landed = lp >= PHASE.flip[1];
  const end = 1 - prog(t, ev.rounds[ROUNDS - 1][0] + ev.rounds[ROUNDS - 1][1] + 0.3, sc.guru[0]);
  const legend = 1 - prog(t, ev.rounds[2][0], ev.rounds[2][0] + 0.3);
  return (
    <div style={{ opacity: end }}>
      <Coin x={540} y={488 - lift} d={130} angle={angle} front={prevHeads ? "正" : "反"} back={prevHeads ? "反" : "正"} />
      {landed && lp < 1.2 && (
        <div style={abs(540, 488, { transform: "translate(-50%,-50%)", width: 190, height: 190, borderRadius: 95, border: `4px solid ${C.gold}`, opacity: 1 - prog(lp, PHASE.flip[1], PHASE.flip[1] + 0.25), scale: `${1 + prog(lp, PHASE.flip[1], PHASE.flip[1] + 0.25) * 0.4}` })} />
      )}
      {legend > 0 && (
        <>
          <Pill size={32} style={abs(130, 450, { opacity: legend })}>
            <span style={{ display: "inline-block", width: 26, height: 26, borderRadius: 13, background: C.gold }} /> 猜正面
          </Pill>
          <Pill size={32} style={abs(700, 450, { opacity: legend })}>
            <span style={{ display: "inline-block", width: 20, height: 20, borderRadius: 13, border: `4px solid ${C.cream}` }} /> 猜反面
          </Pill>
        </>
      )}
    </div>
  );
};

