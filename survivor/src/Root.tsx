import React from "react";
import { Composition, Still } from "remotion";
import { Cover } from "./Cover";
import { loadFonts } from "./fonts";
import { Main } from "./Main";
import { DURATION_FRAMES, FPS, H, W } from "./timeline";

loadFonts();

export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="SurvivorBias" component={Main} durationInFrames={DURATION_FRAMES} fps={FPS} width={W} height={H} />
    <Still id="Cover" component={Cover} width={W} height={H} />
  </>
);
