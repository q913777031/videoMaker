import React from "react";
import { AbsoluteFill, Audio, staticFile, useCurrentFrame } from "remotion";
import { prog } from "./anim";
import { FONT_BODY } from "./fonts";
import { Ending } from "./scenes/Ending";
import { GameHud, HookOverlay } from "./scenes/Game";
import { FreezeOverlay, GuruOverlay, RevealOverlay } from "./scenes/Reveal";
import { Subtitles } from "./scenes/Subtitles";
import { FPS, TL } from "./timeline";
import { WorldCanvas } from "./WorldCanvas";
import { C, camera } from "./world";

const ev = TL.events;

export const Background: React.FC = () => (
  <AbsoluteFill style={{ background: `radial-gradient(ellipse at 50% 45%, ${C.bg2} 0%, ${C.bg} 70%)` }} />
);

export const Main: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  const cam = camera(t);
  // 暂停：画面去色、压暗；反转开始时恢复
  const frozen = prog(t, ev.freeze, ev.freeze + 0.12) * (1 - prog(t, ev.zoom1[0], ev.zoom1[0] + 0.5));
  return (
    <AbsoluteFill style={{ backgroundColor: C.bg, overflow: "hidden" }}>
      <Background />
      <WorldCanvas t={t} cam={cam} style={{ filter: `saturate(${1 - 0.65 * frozen}) brightness(${1 - 0.18 * frozen})` }} />
      <GuruOverlay t={t} cam={cam} />
      <HookOverlay t={t} />
      <GameHud t={t} />
      <RevealOverlay t={t} cam={cam} />
      <FreezeOverlay t={t} cam={cam} />
      <Ending t={t} cam={cam} />
      <Subtitles t={t} />
      {!TL.voiced && (
        <div
          style={{
            position: "absolute",
            left: 40,
            top: 40,
            padding: "8px 18px",
            borderRadius: 12,
            background: "#B3261E",
            color: "#fff",
            fontFamily: FONT_BODY,
            fontWeight: 900,
            fontSize: 30,
          }}
        >
          未配音预览
        </div>
      )}
      <Audio src={staticFile("mix.wav")} />
    </AbsoluteFill>
  );
};
